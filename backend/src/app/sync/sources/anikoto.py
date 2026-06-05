"""Anikoto provider-source adapter (ADR 078)."""

from __future__ import annotations

from typing import Any, Literal

from src.app.database import AsyncSessionLocal
from src.app.external.anikoto_client import AnikotoClient
from src.app.services.anikoto_sync_service import AnikotoSyncService
from src.app.sync.types import SeedExecutionContext, SeedRunResult


class AnikotoSourceAdapter:
    """Pages Anikoto recent catalog and refreshes safe provider IDs only."""

    def __init__(self, *, mode: Literal["full", "recent"], client: AnikotoClient | None = None) -> None:
        self.mode = mode
        self.client = client or AnikotoClient()

    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        source = "anikoto_full_catalog" if self.mode == "full" else "anikoto_recent_refresh"
        per_page = min(max(context.per_page or 20, 1), 50)
        max_pages = context.max_pages if context.max_pages is not None else (5 if self.mode == "recent" else None)
        processed = 0
        failed = 0
        errors: list[dict[str, str]] = []
        page = 1

        while True:
            if max_pages is not None and page > max_pages:
                break
            try:
                payload = await self.client.get_recent_anime(page=page, per_page=per_page)
                rows = _extract_recent_rows(payload)
            except Exception as exc:
                failed += 1
                errors.append({"item": f"page_{page}", "source": source, "error": str(exc)})
                break

            if not rows:
                break

            for row in rows:
                series_id = str(_pick(row, "id", "series_id", "anime_id", "slug") or "").strip()
                if not series_id:
                    failed += 1
                    errors.append({"item": f"page_{page}", "source": source, "error": "missing series id"})
                    continue
                try:
                    detail = dict(row)
                    if context.refresh_details:
                        detail_payload = await self.client.get_series(series_id)
                        detail = _extract_detail(detail_payload) | detail if _extract_detail(detail_payload) else detail_payload | detail
                    async with AsyncSessionLocal() as session:
                        service = AnikotoSyncService(session)
                        await service.upsert_series(detail, dry_run=context.dry_run)
                    processed += 1
                except Exception as exc:
                    failed += 1
                    errors.append({"item": series_id, "source": source, "error": str(exc)})

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
