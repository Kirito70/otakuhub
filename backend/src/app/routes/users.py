"""User profile routes for Phase 5."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models.user import User
from src.app.schemas.common import DeleteResponse
from src.app.schemas.user import (
    AdminUserResponse,
    PublicUserProfile,
    UserListResponse,
    UserProfile,
    UserSettingsResponse,
    UserSettingsUpdateRequest,
    UserUpdate,
)
from src.app.schemas.auth import RegisterRequest
from src.app.services.user_service import UserService
from src.app.services.auth_service import auth_service
from src.app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("", response_model=UserListResponse)
async def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> UserListResponse:
    """Admin: List all users with pagination."""
    user_service = UserService(db)
    items = await user_service.get_users(limit=limit, offset=offset)
    total = len(items)
    return UserListResponse(
        items=[AdminUserResponse.model_validate(u) for u in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_my_settings(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> UserSettingsResponse:
    """Get current user's settings."""
    user_service = UserService(db)
    settings = await user_service.get_user_settings(current_user.id)
    return UserSettingsResponse.model_validate(settings)


@router.patch("/me/settings", response_model=UserSettingsResponse)
async def patch_my_settings(
    payload: UserSettingsUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> UserSettingsResponse:
    """Update current user's settings."""
    user_service = UserService(db)
    settings = await user_service.update_user_settings(
        current_user.id,
        payload.model_dump(exclude_unset=True),
    )
    return UserSettingsResponse.model_validate(settings)


@router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> DeleteResponse:
    """Admin: Soft delete a user."""
    user_service = UserService(db)
    deleted = await user_service.delete_user(user_id)
    return DeleteResponse(deleted=deleted)


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)) -> UserProfile:
    return UserProfile.model_validate(current_user)


@router.patch("/me", response_model=UserProfile)
async def patch_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> UserProfile:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(current_user, key, value)
    current_user.updated_at = datetime.utcnow()
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return UserProfile.model_validate(current_user)


@router.get("/{username}/profile", response_model=PublicUserProfile)
async def get_public_profile(
    username: str,
    db: AsyncSession = Depends(get_db_session),
) -> PublicUserProfile:
    """Phase 9.8 — public-safe profile lookup by username."""
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")

    return PublicUserProfile.model_validate(user)


@router.post("", response_model=UserProfile, status_code=201)
async def create_user_by_admin(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_admin),
) -> UserProfile:
    """Phase 12.5 — create a user after setup (super-admin only)."""
    user = await auth_service.create_user_by_admin(db, payload)
    return UserProfile.model_validate(user)
