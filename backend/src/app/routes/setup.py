"""First-run setup routes for Phase 12."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user_optional
from src.app.database import check_db_connection
from src.app.database import get_db_session
from src.app.models.user import User
from src.app.schemas.setup import AppBootstrapResponse, BootstrapAdminRequest, BootstrapLoggedInUser, SetupStatusResponse
from src.app.schemas.user import UserProfile
from src.app.services.auth_service import auth_service

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/status", response_model=SetupStatusResponse, response_model_exclude_none=True)
async def get_setup_status(db: AsyncSession = Depends(get_db_session)) -> SetupStatusResponse:
    """Phase 12.4 — returns whether initial bootstrap is required."""
    setup_required = await auth_service.is_setup_required(db)
    return SetupStatusResponse(setup_required=True if setup_required else None)


@router.post("/bootstrap-admin", response_model=UserProfile, status_code=201)
async def bootstrap_admin(
    payload: BootstrapAdminRequest,
    db: AsyncSession = Depends(get_db_session),
) -> UserProfile:
    """Phase 12.3 — one-time super-admin bootstrap endpoint."""
    user = await auth_service.bootstrap_super_admin(db, payload.username, payload.email, payload.password)
    return UserProfile.model_validate(user)


@router.get("/bootstrap", response_model=AppBootstrapResponse, response_model_exclude_none=True)
async def get_app_bootstrap(
    db: AsyncSession = Depends(get_db_session),
    current_user: User | None = Depends(get_current_user_optional),
) -> AppBootstrapResponse:
    """Unified frontend bootstrap payload for routing decisions.

    - Always returns site_status
    - Returns logged_in_user when valid access token is supplied
    - Returns setup_required only when first-run setup is still needed
    """
    site_status = "up" if await check_db_connection() else "degraded"
    setup_required = await auth_service.is_setup_required(db)

    logged_in_user = None
    if current_user is not None:
        logged_in_user = BootstrapLoggedInUser.model_validate(current_user)

    return AppBootstrapResponse(
        site_status=site_status,
        logged_in_user=logged_in_user,
        setup_required=True if setup_required else None,
    )
