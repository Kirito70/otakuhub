from __future__ import annotations

from src.app.database import AsyncSessionLocal
from src.app.sync.factory import build_seed_orchestrator


async def run_seed_source(
    *,
    source: str,
    batch_size: int | None = None,
    limit: int | None = None,
    dry_run: bool = False,
    only_unsynced: bool = False,
    user_id: str | None = None,
    per_page: int | None = None,
    max_pages: int | None = None,
    refresh_details: bool = True,
) -> dict[str, object]:
    async with AsyncSessionLocal() as session:
        orchestrator = build_seed_orchestrator(session)
        return await orchestrator.run_source(
            source=source,
            batch_size=batch_size,
            limit=limit,
            dry_run=dry_run,
            only_unsynced=only_unsynced,
            user_id=user_id,
            per_page=per_page,
            max_pages=max_pages,
            refresh_details=refresh_details,
        )


async def run_seed_all(
    *,
    dry_run: bool = False,
    resume_job_id: str | None = None,
    batch_size: int = 50,
    limit: int = 100,
    user_id: str | None = None,
) -> dict[str, object]:
    async with AsyncSessionLocal() as session:
        orchestrator = build_seed_orchestrator(session)
        return await orchestrator.run_all(
            dry_run=dry_run,
            resume_job_id=resume_job_id,
            batch_size=batch_size,
            limit=limit,
            user_id=user_id,
        )
