"""Authentication service for OtakuHub (Phase 5 start)."""

from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.models.user import User
from src.app.models.refresh_token import RefreshToken
from src.app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from src.app.core.security import get_password_hash, verify_password
from src.app.config import settings


class AuthService:
    """Auth business logic: register, login, refresh, logout."""

    async def register(self, db: AsyncSession, payload: RegisterRequest) -> User:
        existing_stmt = select(User).where(
            (User.username == payload.username) | (User.email == payload.email)
        )
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Username or email already exists")

        user = User(
            username=payload.username,
            display_name=payload.username,
            email=payload.email,
            password_hash=get_password_hash(payload.password),
            is_active=True,
            is_admin=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def login(self, db: AsyncSession, payload: LoginRequest) -> TokenResponse:
        stmt = select(User).where(
            (User.username == payload.username) | (User.email == payload.username)
        )
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = token_urlsafe(32)
        refresh_token = token_urlsafe(48)
        refresh_hash = sha256(refresh_token.encode("utf-8")).hexdigest()

        refresh_row = RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        )
        db.add(refresh_row)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def refresh(self, db: AsyncSession, payload: RefreshRequest) -> TokenResponse:
        token_hash = sha256(payload.refresh_token.encode("utf-8")).hexdigest()
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        row = (await db.execute(stmt)).scalar_one_or_none()

        if not row or row.revoked_at is not None or row.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        row.revoked_at = datetime.utcnow()

        new_access = token_urlsafe(32)
        new_refresh = token_urlsafe(48)
        new_hash = sha256(new_refresh.encode("utf-8")).hexdigest()

        rotated = RefreshToken(
            user_id=row.user_id,
            token_hash=new_hash,
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        )
        db.add(rotated)
        await db.commit()

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def logout(self, db: AsyncSession, refresh_token: str) -> None:
        token_hash = sha256(refresh_token.encode("utf-8")).hexdigest()
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        row = (await db.execute(stmt)).scalar_one_or_none()
        if row and row.revoked_at is None:
            row.revoked_at = datetime.utcnow()
            await db.commit()


auth_service = AuthService()
