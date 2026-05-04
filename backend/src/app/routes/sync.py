"""API routes for sync and import operations."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.sync import SyncImportRequest, SyncImportResponse
from src.app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


def get_sync_service(db: AsyncSession = Depends(get_db_session)) -> SyncService:
    """Get SyncService instance with request-scoped DB session."""
    return SyncService(db)


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
    return SyncImportResponse(
        job_id=job.id,
        provider="anilist",
        status=job.status,
        job_type=job.job_type,
        started_at=job.started_at,
        message="AniList import job created",
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
    return SyncImportResponse(
        job_id=job.id,
        provider="mal",
        status=job.status,
        job_type=job.job_type,
        started_at=job.started_at,
        message="MAL import job created",
    )
