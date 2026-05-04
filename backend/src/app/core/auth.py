"""Authentication dependencies (Phase 5 bootstrap)."""

from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.database import get_db_session
from src.app.models.user import User


async def get_current_user(db: AsyncSession = Depends(get_db_session)) -> User:
    """Return a current user for protected routes.

    Phase 5 bootstrap behavior:
    - loads the first active, non-deleted user in DB
    - returns 401 if none exists

    NOTE: This is an interim implementation until header-based JWT auth is added.
    """
    stmt = select(User).where(User.deleted_at.is_(None), User.is_active == True).limit(1)  # noqa: E712
    result = await db.exec(stmt)
    user = result.one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user
