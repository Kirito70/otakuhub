"""Authentication dependencies."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.security import decode_token
from src.app.database import get_db_session
from src.app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Validate bearer token and return active current user."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise ValueError("Invalid token type")
        user_id = UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None), User.is_active == True)  # noqa: E712
    result = await db.exec(stmt)
    user = result.one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User | None:
    """Best-effort current user resolver for bootstrap/status style endpoints."""
    if credentials is None:
        return None

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        user_id = UUID(payload["sub"])
    except Exception:
        return None

    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None), User.is_active == True)  # noqa: E712
    result = await db.exec(stmt)
    return result.one_or_none()
