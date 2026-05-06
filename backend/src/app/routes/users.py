"""User profile routes for Phase 5."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models.user import User
from src.app.schemas.user import PublicUserProfile, UserProfile, UserUpdate
from src.app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


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
