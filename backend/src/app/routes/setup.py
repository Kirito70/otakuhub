"""First-run setup routes for Phase 12."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.database import get_db_session
from src.app.schemas.setup import BootstrapAdminRequest, SetupStatusResponse
from src.app.schemas.user import UserProfile
from src.app.services.auth_service import auth_service

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/status", response_model=SetupStatusResponse)
async def get_setup_status(db: AsyncSession = Depends(get_db_session)) -> SetupStatusResponse:
    """Phase 12.4 — returns whether initial bootstrap is required."""
    setup_required = await auth_service.is_setup_required(db)
    return SetupStatusResponse(setup_required=setup_required)


@router.post("/bootstrap-admin", response_model=UserProfile, status_code=201)
async def bootstrap_admin(
    payload: BootstrapAdminRequest,
    db: AsyncSession = Depends(get_db_session),
) -> UserProfile:
    """Phase 12.3 — one-time super-admin bootstrap endpoint."""
    user = await auth_service.bootstrap_super_admin(db, payload.username, payload.email, payload.password)
    return UserProfile.model_validate(user)
