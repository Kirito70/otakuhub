"""User profile routes for Phase 5."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models.user import User
from src.app.schemas.user import PublicUserProfile, UserProfile, UserUpdate
from src.app.schemas.auth import RegisterRequest
from src.app.services.auth_service import auth_service
from src.app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


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
