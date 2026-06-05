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

try:
    from src.app.workers.sync_tasks import seed_database_task, weekly_refresh_task
except Exception:
    seed_database_task = None
    weekly_refresh_task = None

router = APIRouter(prefix="/admin", tags=["admin"])


class SeedRequest(BaseModel):
    """Request to trigger a database seed."""

    batch_size: int = 50


class JobEnqueueResponse(BaseModel):
    """Response for enqueued Celery job."""

    job_id: str
    job_type: str
    status: str = "queued"
    message: str = ""


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
