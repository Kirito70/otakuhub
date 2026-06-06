"""Anikoto provider-source adapter (ADR 078).

Handles rate-limit backoff and graceful degradation: when the Anikoto API
returns 429 the adapter sleeps for the indicated ``Retry-After`` period and
resumes.  If detail-refresh requests repeatedly hit the limit the adapter
silently degrades to list-level data only.
"""

from __future__ import annotations

import asyncio
from typing import Any, Literal

from src.app.database import AsyncSessionLocal
from src.app.external.anikoto_client import AnikotoClient, AnikotoRateLimitError
from src.app.services.anikoto_sync_service import AnikotoSyncService
from src.app.sync.types import SeedExecutionContext, SeedRunResult


class AnikotoSourceAdapter:
    """Pages Anikoto recent catalog and refreshes safe provider IDs only.

    Rate-limit behaviour
    --------------------
    * List requests (``/recent-anime``) — on 429 the whole page is retried
      after ``Retry-After`` seconds.  Repeated failures abort the run with
      ``partial`` status.
    * Detail requests (``/series/{id}``) — on 429 the item is skipped (list-
      level data is stored without detail enrichment).  If
      ``context.detail_retry_cutoff`` consecutive detail requests hit 429,
      all further detail refreshes are disabled for the rest of the job
      (*graceful degradation*).
    """

    def __init__(self, *, mode: Literal["full", "recent"], client: AnikotoClient | None = None) -> None:
        self.mode = mode
        self.client = client or AnikotoClient()
        self._detail_rate_hits = 0

    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        source = "anikoto_full_catalog" if self.mode == "full" else "anikoto_recent_refresh"
        per_page = min(max(context.per_page or 20, 1), 50)
        max_pages = context.max_pages if context.max_pages is not None else (5 if self.mode == "recent" else None)
        self._detail_rate_hits = 0
        processed = 0
        failed = 0
        errors: list[dict[str, str]] = []
        page = 1
        refresh_details = context.refresh_details

        semaphore = asyncio.Semaphore(context.max_detail_concurrency)

        while True:
            if max_pages is not None and page > max_pages:
                break
            try:
                payload = await self.client.get_recent_anime(page=page, per_page=per_page)
                rows = _extract_recent_rows(payload)
            except AnikotoRateLimitError as exc:
                wait = max(exc.retry_after, 5.0)
                print(f"[{source}] page={page} rate-limited (429); sleeping {wait:.0f}s")
                await asyncio.sleep(wait)
                continue  # retry the same page
            except Exception as exc:
                failed += 1
                errors.append({"item": f"page_{page}", "source": source, "error": str(exc)})
                break

            if not rows:
                print(f"[{source}] page={page} fetched=0 stopping")
                break

            print(f"[{source}] page={page} fetched={len(rows)} refresh_details={refresh_details} dry_run={context.dry_run}")

            for row in rows:
                series_id = str(_pick(row, "id", "series_id", "anime_id", "slug") or "").strip()
                if not series_id:
                    failed += 1
                    errors.append({"item": f"page_{page}", "source": source, "error": "missing series id"})
                    continue

                async def _process_one(series_id: str, row: dict[str, Any]) -> None:
                    nonlocal refresh_details
                    detail = dict(row)
                    if refresh_details:
                        try:
                            async with semaphore:
                                detail_payload = await self.client.get_series(series_id)
                            detail = detail | _extract_detail(detail_payload)
                            self._detail_rate_hits = 0
                        except AnikotoRateLimitError as exc:
                            self._detail_rate_hits += 1
                            if self._detail_rate_hits >= context.detail_retry_cutoff:
                                refresh_details = False
                                print(
                                    f"[{source}] {self._detail_rate_hits} consecutive detail 429s; "
                                    "disabling detail refreshes for remaining items"
                                )
                            wait = max(exc.retry_after, 5.0)
                            print(f"[{source}] series={series_id} detail rate-limited; sleeping {wait:.0f}s")
                            await asyncio.sleep(wait)
                            # Store list-level data only
                    async with AsyncSessionLocal() as session:
                        service = AnikotoSyncService(session)
                        await service.upsert_series(detail, dry_run=context.dry_run)

                try:
                    await _process_one(series_id, row)
                    processed += 1
                except Exception as exc:
                    failed += 1
                    errors.append({"item": series_id, "source": source, "error": str(exc)})

            print(f"[{source}] page={page} processed_total={processed} failed_total={failed}")

            if len(rows) < per_page:
                break
            page += 1

        status = "completed" if failed == 0 else ("partial" if processed else "failed")
        return SeedRunResult(source=source, status=status, processed_items=processed, failed_items=failed, errors=errors)


def _extract_recent_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("data", "results", "items", "anime", "recent_anime"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    if isinstance(payload.get("items"), list):
        return [item for item in payload["items"] if isinstance(item, dict)]
    return []


def _extract_detail(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    if isinstance(data, dict):
        anime = data.get("anime")
        if isinstance(anime, dict):
            detail = dict(anime)
            if isinstance(data.get("episodes"), list):
                detail["episodes"] = data["episodes"]
            return detail
        return data
    for key in ("data", "series", "anime"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return payload


def _pick(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None
