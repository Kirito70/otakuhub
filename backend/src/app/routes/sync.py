"""API routes for sync and import operations."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.sync import SyncImportRequest, SyncImportResponse, SyncJobStatusResponse
from src.app.services.sync_service import SyncService

try:
    from src.app.workers.sync_tasks import import_user_list_task
except Exception:
    import_user_list_task = None  # Celery not available

router = APIRouter(prefix="/sync", tags=["sync"])


def get_sync_service(db: AsyncSession = Depends(get_db_session)) -> SyncService:
    """Get SyncService instance with request-scoped DB session."""
    return SyncService(db)


def _enqueue_import_task(user_id: UUID, provider: str, username: str | None) -> None:
    """Enqueue a Celery import task if available."""
    if import_user_list_task is not None:
        import_user_list_task.delay(
            user_id=str(user_id),
            provider=provider,
            username=username or "",
        )


@router.post("/import/anilist", response_model=SyncImportResponse, status_code=202)
async def import_anilist_list(
    payload: SyncImportRequest,
    sync_service: SyncService = Depends(get_sync_service),
    user: User = Depends(get_current_user),
) -> SyncImportResponse:
    """Phase 6.6 — create a user AniList import job."""
    job = await sync_service.create_sync_job(
        job_type="user_import_anilist",
        user_id=user.id,
    )
    _enqueue_import_task(user_id=user.id, provider="anilist", username=payload.username)
    return SyncImportResponse(
        job_id=job.id,
        provider="anilist",
        status=job.status,
        job_type=job.job_type,
        started_at=job.started_at,
        message="AniList import job created and task enqueued",
    )


@router.post("/import/mal", response_model=SyncImportResponse, status_code=202)
async def import_mal_list(
    payload: SyncImportRequest,
    sync_service: SyncService = Depends(get_sync_service),
    user: User = Depends(get_current_user),
) -> SyncImportResponse:
    """Phase 6.7 — create a user MAL import job."""
    job = await sync_service.create_sync_job(
        job_type="user_import_mal",
        user_id=user.id,
    )
    _enqueue_import_task(user_id=user.id, provider="mal", username=payload.username)
    return SyncImportResponse(
        job_id=job.id,
        provider="mal",
        status=job.status,
        job_type=job.job_type,
        started_at=job.started_at,
        message="MAL import job created and task enqueued",
    )


@router.get("/jobs/{job_id}", response_model=SyncJobStatusResponse)
async def get_sync_job_status(
    job_id: UUID,
    sync_service: SyncService = Depends(get_sync_service),
    user: User = Depends(get_current_user),
) -> SyncJobStatusResponse:
    """Get the status of an import sync job scoped to the current user."""
    job = await sync_service.get_sync_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Sync job not found")
    if job.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")
    return SyncJobStatusResponse(
        id=str(job.id),
        job_type=job.job_type,
        status=job.status,
        total_items=job.total_items,
        processed_items=job.processed_items or 0,
        failed_items=job.failed_items or 0,
        error_log=job.error_log,
        started_at=str(job.started_at),
        completed_at=str(job.completed_at) if job.completed_at else None,
    )
