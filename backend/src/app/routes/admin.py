"""Admin routes for system management (Phase 13+)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.services.sync_service import SyncService
from src.app.schemas.source_provider import AnikotoFullSyncRequest, AnikotoRecentSyncRequest, JobEnqueueResponse

try:
    from src.app.workers.sync_tasks import anikoto_full_catalog_task, anikoto_recent_refresh_task, seed_database_task, weekly_refresh_task
except Exception:
    seed_database_task = None
    weekly_refresh_task = None
    anikoto_full_catalog_task = None
    anikoto_recent_refresh_task = None

router = APIRouter(prefix="/admin", tags=["admin"])


class SeedRequest(BaseModel):
    """Request to trigger a database seed."""

    batch_size: int = 50


class SyncJobDetail(BaseModel):
    """Detailed sync job info."""

    id: str
    job_type: str
    status: str
    user_id: str | None = None
    total_items: int | None = None
    processed_items: int = 0
    failed_items: int = 0
    error_log: str | None = None
    started_at: str
    completed_at: str | None = None


class SyncJobsResponse(BaseModel):
    """Paginated sync job list."""

    items: list[SyncJobDetail]
    total: int
    limit: int
    offset: int


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def get_sync_service(db: AsyncSession = Depends(get_db_session)) -> SyncService:
    """Get SyncService instance with request-scoped DB session."""
    return SyncService(db)


@router.post("/sync/seed", response_model=JobEnqueueResponse, status_code=202)
async def admin_trigger_seed(
    payload: SeedRequest = SeedRequest(),
    _: User = Depends(require_admin),
) -> JobEnqueueResponse:
    """Phase 13 — enqueue a seed database Celery task."""
    if seed_database_task is not None:
        try:
            result = seed_database_task.delay(batch_size=payload.batch_size)
            return JobEnqueueResponse(
                job_id=str(result.id),
                job_type="seed",
                status="queued",
                message=f"Seed task enqueued with batch_size={payload.batch_size}",
            )
        except Exception as exc:
            # Celery backend unavailable (e.g. no Redis in test/dev)
            return JobEnqueueResponse(
                job_id="",
                job_type="seed",
                status="unavailable",
                message=f"Seed task could not be enqueued: {exc}",
            )
    return JobEnqueueResponse(
        job_id="",
        job_type="seed",
        status="unavailable",
        message="Celery worker not available",
    )


@router.post("/sync/weekly-refresh", response_model=JobEnqueueResponse, status_code=202)
async def admin_trigger_weekly_refresh(
    _: User = Depends(require_admin),
) -> JobEnqueueResponse:
    """Phase 13 — enqueue a weekly refresh Celery task."""
    if weekly_refresh_task is not None:
        try:
            result = weekly_refresh_task.delay()
            return JobEnqueueResponse(
                job_id=str(result.id),
                job_type="weekly_refresh",
                status="queued",
                message="Weekly refresh task enqueued",
            )
        except Exception as exc:
            return JobEnqueueResponse(
                job_id="",
                job_type="weekly_refresh",
                status="unavailable",
                message=f"Weekly refresh task could not be enqueued: {exc}",
            )
    return JobEnqueueResponse(
        job_id="",
        job_type="weekly_refresh",
        status="unavailable",
        message="Celery worker not available",
    )


@router.post("/sync/providers/anikoto/full", response_model=JobEnqueueResponse, status_code=202)
async def admin_trigger_anikoto_full(
    payload: AnikotoFullSyncRequest = AnikotoFullSyncRequest(),
    _: User = Depends(require_admin),
) -> JobEnqueueResponse:
    """ADR 078 — enqueue full Anikoto provider catalog sync."""
    if anikoto_full_catalog_task is not None:
        try:
            result = anikoto_full_catalog_task.delay(
                per_page=payload.per_page,
                max_pages=payload.max_pages,
                refresh_details=payload.refresh_details,
                dry_run=payload.dry_run,
            )
            return JobEnqueueResponse(
                job_id=str(result.id),
                job_type="anikoto_full_catalog",
                status="queued",
                message="Anikoto full catalog sync enqueued",
            )
        except Exception as exc:
            import logging

            logging.getLogger(__name__).warning("Anikoto full sync could not be enqueued", exc_info=exc)
            return JobEnqueueResponse(
                job_id="",
                job_type="anikoto_full_catalog",
                status="unavailable",
                message="Anikoto full sync could not be enqueued",
            )
    return JobEnqueueResponse(job_id="", job_type="anikoto_full_catalog", status="unavailable", message="Celery worker not available")


@router.post("/sync/providers/megaplay/full", response_model=JobEnqueueResponse, status_code=202)
async def admin_trigger_megaplay_full(
    payload: AnikotoFullSyncRequest = AnikotoFullSyncRequest(),
    current_user: User = Depends(require_admin),
) -> JobEnqueueResponse:
    """ADR 078 — enqueue full MegaPlay provider catalog sync via Anikoto discovery."""
    return await admin_trigger_anikoto_full(payload=payload, _=current_user)


@router.post("/sync/providers/anikoto/recent", response_model=JobEnqueueResponse, status_code=202)
async def admin_trigger_anikoto_recent(
    payload: AnikotoRecentSyncRequest = AnikotoRecentSyncRequest(),
    _: User = Depends(require_admin),
) -> JobEnqueueResponse:
    """ADR 078 — enqueue bounded recent Anikoto provider refresh."""
    if anikoto_recent_refresh_task is not None:
        try:
            result = anikoto_recent_refresh_task.delay(
                per_page=payload.per_page,
                max_pages=payload.max_pages,
                refresh_details=payload.refresh_details,
                dry_run=payload.dry_run,
            )
            return JobEnqueueResponse(
                job_id=str(result.id),
                job_type="anikoto_recent_refresh",
                status="queued",
                message="Anikoto recent refresh enqueued",
            )
        except Exception as exc:
            import logging

            logging.getLogger(__name__).warning("Anikoto recent refresh could not be enqueued", exc_info=exc)
            return JobEnqueueResponse(
                job_id="",
                job_type="anikoto_recent_refresh",
                status="unavailable",
                message="Anikoto recent refresh could not be enqueued",
            )
    return JobEnqueueResponse(job_id="", job_type="anikoto_recent_refresh", status="unavailable", message="Celery worker not available")


@router.post("/sync/providers/megaplay/recent", response_model=JobEnqueueResponse, status_code=202)
async def admin_trigger_megaplay_recent(
    payload: AnikotoRecentSyncRequest = AnikotoRecentSyncRequest(),
    current_user: User = Depends(require_admin),
) -> JobEnqueueResponse:
    """ADR 078 — enqueue recent MegaPlay provider refresh via Anikoto discovery."""
    return await admin_trigger_anikoto_recent(payload=payload, _=current_user)


@router.get("/sync/jobs", response_model=SyncJobsResponse)
async def admin_list_sync_jobs(
    job_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sync_service: SyncService = Depends(get_sync_service),
    _: User = Depends(require_admin),
) -> SyncJobsResponse:
    """Phase 13 — list sync jobs."""
    items = await sync_service.get_sync_jobs(
        job_type=job_type,
        status=status,
        limit=limit,
    )
    # Apply offset manually
    sliced = items[offset:offset + limit]
    return SyncJobsResponse(
        items=[_job_to_detail(j) for j in sliced],
        total=len(items),
        limit=limit,
        offset=offset,
    )


@router.get("/sync/jobs/{job_id}", response_model=SyncJobDetail)
async def admin_get_sync_job(
    job_id: UUID,
    sync_service: SyncService = Depends(get_sync_service),
    _: User = Depends(require_admin),
) -> SyncJobDetail:
    """Phase 13 — get a single sync job detail."""
    job = await sync_service.get_sync_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Sync job not found")
    return _job_to_detail(job)


def _job_to_detail(job: Any) -> SyncJobDetail:
    """Convert a SyncJob ORM object to SyncJobDetail schema."""
    return SyncJobDetail(
        id=str(job.id),
        job_type=job.job_type,
        status=job.status,
        user_id=str(job.user_id) if job.user_id else None,
        total_items=job.total_items,
        processed_items=job.processed_items or 0,
        failed_items=job.failed_items or 0,
        error_log=job.error_log,
        started_at=str(job.started_at),
        completed_at=str(job.completed_at) if job.completed_at else None,
    )
