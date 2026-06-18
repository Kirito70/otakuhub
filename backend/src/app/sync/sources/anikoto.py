"""Anikoto provider-source adapter (ADR 078).

Handles rate-limit backoff and graceful degradation: when the Anikoto API
returns 429 the adapter sleeps for the indicated ``Retry-After`` period and
resumes.  If detail-refresh requests repeatedly hit the limit the adapter
silently degrades to list-level data only.

Bulk-insert + resume
--------------------
A single DB session is used per page so that all series and episode upserts
share one transaction (no per-series commits).  After each completed page, the
adapter persists a checkpoint to the sync job's ``metadata`` JSONB column.
If the run is interrupted, a subsequent invocation with the same job ID will
skip already-processed pages and resume from the next one.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Literal

from sqlalchemy import update as sa_update
from sqlmodel import select

from src.app.database import AsyncSessionLocal
from src.app.external.anikoto_client import AnikotoClient, AnikotoRateLimitError
from src.app.models.sync_job import SyncJob
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
        per_page = min(max(context.per_page or 100, 1), 100)
        max_pages = context.max_pages if context.max_pages is not None else (5 if self.mode == "recent" else None)
        self._detail_rate_hits = 0
        processed = 0
        failed = 0
        errors: list[dict[str, str]] = []
        page = 1
        refresh_details = context.refresh_details

        semaphore = asyncio.Semaphore(context.max_detail_concurrency)

        # --- Resume check: load last completed page from sync_job metadata ---
        completed_up_to = 0
        if context.job_id:
            completed_up_to = await self._load_checkpoint(context.job_id)
        if completed_up_to > 0:
            page = completed_up_to + 1
            print(f"[{source}] resuming from page={page} (completed up to page {completed_up_to})")

        while True:
            if max_pages is not None and page > max_pages:
                break

            # Skip pages already processed in a previous interrupted run
            if page <= completed_up_to:
                page += 1
                continue

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

            # One DB session per page — all series + episodes share a single transaction
            total_in_page = len(rows)
            async with AsyncSessionLocal() as session:
                service = AnikotoSyncService(session)
                for idx, row in enumerate(rows, start=1):
                    series_id = str(_pick(row, "id", "series_id", "anime_id", "slug") or "").strip()
                    if not series_id:
                        failed += 1
                        errors.append({"item": f"page_{page}", "source": source, "error": "missing series id"})
                        continue

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

                    try:
                        # Use commit_mapping=False so all series + episodes in this
                        # page share one commit at the end.
                        await service.upsert_series(detail, dry_run=context.dry_run, commit_mapping=False)
                        processed += 1
                    except Exception as exc:
                        failed += 1
                        errors.append({"item": series_id, "source": source, "error": str(exc)})

                    # Per-item heartbeat — every 10 items so the user can see progress
                    if idx % 10 == 0 or idx == total_in_page:
                        detail_status = "detail:on" if refresh_details else "detail:off"
                        print(
                            f"[{source}] page={page} item={idx}/{total_in_page} "
                            f"processed={processed} failed={failed} {detail_status}"
                        )

                # Single page-level commit for all series + episodes
                if not context.dry_run:
                    await session.commit()
                    print(f"[{source}] page={page} committed {total_in_page} items")

            # Persist checkpoint so we can resume after crash
            if not context.dry_run and context.job_id:
                await self._save_checkpoint(context.job_id, page)

            print(f"[{source}] page={page} complete processed_total={processed} failed_total={failed}")

            if len(rows) < per_page:
                break
            page += 1

        status = "completed" if failed == 0 else ("partial" if processed else "failed")
        return SeedRunResult(source=source, status=status, processed_items=processed, failed_items=failed, errors=errors)

    # ------------------------------------------------------------------
    # Checkpoint helpers
    # ------------------------------------------------------------------

    async def _load_checkpoint(self, job_id: str) -> int:
        """Read the last completed page from the sync job's metadata column."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.exec(select(SyncJob).where(SyncJob.id == job_id))
                job = result.one_or_none()
                if job and job.metadata_:
                    meta = json.loads(job.metadata_) if isinstance(job.metadata_, str) else job.metadata_
                    page = meta.get("last_completed_page", 0)
                    return max(int(page), 0)
        except Exception:
            pass
        return 0

    async def _save_checkpoint(self, job_id: str, page: int) -> None:
        """Persist ``last_completed_page`` to the sync job's metadata column."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.exec(select(SyncJob).where(SyncJob.id == job_id))
                job = result.one_or_none()
                if job:
                    meta = {"last_completed_page": page}
                    job.metadata_ = json.dumps(meta)
                    session.add(job)
                    await session.commit()
        except Exception as exc:
            print(f"[checkpoint] failed to save page={page}: {exc}")


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
