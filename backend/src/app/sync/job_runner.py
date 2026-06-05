from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.models.sync_job import SyncJob
from src.app.sync.observability import build_sync_job_error_payload


def sanitize_error_message(message: str) -> str:
    patterns = [
        r"(?i)(token\s*=\s*)([^\s,;]+)",
        r"(?i)(secret\s*=\s*)([^\s,;]+)",
        r"(?i)(password\s*=\s*)([^\s,;]+)",
    ]
    sanitized = message
    for pattern in patterns:
        sanitized = re.sub(pattern, r"\1[REDACTED]", sanitized)
    return sanitized


class SyncJobRunner:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_job(self, *, source: str, total_items: int | None = None, user_id: str | None = None) -> str:
        job_type_map = {
            "all": "seed",
            "anime-offline": "seed",
            "anilist": "backfill_anilist",
            "mangadex": "mangadex_detail",
            "jikan": "weekly_refresh",
            "anikoto_full_catalog": "anikoto_full_catalog",
            "anikoto_recent_refresh": "anikoto_recent_refresh",
        }
        job_type = job_type_map.get(source, "seed")
        job = SyncJob(
            job_type=job_type,
            status="running",
            total_items=total_items,
            user_id=user_id,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return str(job.id)

    async def progress(self, *, job_id: str, processed_items: int, failed_items: int) -> None:
        job = await self._get(job_id)
        if not job:
            return
        job.processed_items = processed_items
        job.failed_items = failed_items
        await self.db.commit()

    async def finish_completed(
        self,
        *,
        job_id: str,
        source: str = "unknown",
        resume_sources: list[str] | None = None,
    ) -> None:
        await self._finish(job_id=job_id, source=source, status="completed", errors=[], resume_sources=resume_sources)

    async def finish_partial(self, *, job_id: str, errors: list[dict[str, Any]], source: str = "unknown") -> None:
        await self._finish(job_id=job_id, source=source, status="partial", errors=errors)

    async def finish_failed(self, *, job_id: str, errors: list[dict[str, Any]], source: str = "unknown") -> None:
        await self._finish(job_id=job_id, source=source, status="failed", errors=errors)

    async def _finish(
        self,
        *,
        job_id: str,
        source: str,
        status: str,
        errors: list[dict[str, Any]],
        resume_sources: list[str] | None = None,
    ) -> None:
        job = await self._get(job_id)
        if not job:
            return
        job.status = status
        job.completed_at = datetime.utcnow()
        sanitized_errors = []
        for item in errors:
            sanitized_errors.append(
                {
                    "item": str(item.get("item", "unknown")),
                    "source": str(item.get("source", source)),
                    "error": sanitize_error_message(str(item.get("error", "unknown"))),
                }
            )
        job.error_log = json.dumps(
            build_sync_job_error_payload(
                source=source,
                status=status,
                errors=sanitized_errors,
                completed_sources=resume_sources,
            )
        )
        await self.db.commit()

    async def get_completed_sources_for_resume(self, *, job_id: str) -> list[str]:
        job = await self._get(job_id)
        if not job or not job.error_log:
            return []
        try:
            payload = json.loads(job.error_log)
        except json.JSONDecodeError:
            return []
        if isinstance(payload, dict):
            sources = payload.get("completed_sources", [])
            if isinstance(sources, list):
                return [str(source) for source in sources]
        return []

    async def _get(self, job_id: str) -> SyncJob | None:
        result = await self.db.exec(select(SyncJob).where(SyncJob.id == job_id))
        return result.one_or_none()
