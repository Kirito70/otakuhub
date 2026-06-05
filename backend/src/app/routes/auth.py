"""Authentication routes."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated

from src.app.database import get_db_session
from src.app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    LogoutResponse,
)
from src.app.schemas.user import UserProfile
from src.app.services.auth_service import auth_service
from src.app.core.auth import get_current_user
from src.app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return the authenticated user's profile."""
    return UserProfile.model_validate(current_user)


@router.post("/register", response_model=UserProfile, status_code=201)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
):
    user = await auth_service.register(db, payload)
    return UserProfile.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    return await auth_service.login(db, login_request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
):
    return await auth_service.refresh(db, refresh_request)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    refresh_request: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
):
    await auth_service.logout(db, refresh_request.refresh_token)
    return LogoutResponse(success=True)


@router.post("/change-password", response_model=TokenResponse)
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Change the authenticated user's password.

    Validates the current password, revokes all existing refresh tokens,
    and issues a fresh token pair so the current session survives.
    """
    return await auth_service.change_password(db, current_user, payload)
