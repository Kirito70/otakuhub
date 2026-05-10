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
) -> dict[str, object]:
    async with AsyncSessionLocal() as session:
        orchestrator = build_seed_orchestrator(session)
        return await orchestrator.run_source(
            source=source,
            batch_size=batch_size,
            limit=limit,
            dry_run=dry_run,
            only_unsynced=only_unsynced,
        )


async def run_seed_all(
    *,
    dry_run: bool = False,
    resume_job_id: str | None = None,
    batch_size: int = 50,
    limit: int = 100,
) -> dict[str, object]:
    async with AsyncSessionLocal() as session:
        orchestrator = build_seed_orchestrator(session)
        return await orchestrator.run_all(
            dry_run=dry_run,
            resume_job_id=resume_job_id,
            batch_size=batch_size,
            limit=limit,
        )
