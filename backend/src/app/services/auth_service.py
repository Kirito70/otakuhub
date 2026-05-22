"""Authentication service for OtakuHub Phase 5."""

from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.config import settings
from src.app.core.security import create_access_token, get_password_hash, needs_password_rehash, verify_password
from src.app.models.refresh_token import RefreshToken
from src.app.models.user import User
from src.app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse


class AuthService:
    """Auth business logic: register, login, refresh, logout."""

    async def _revoke_all_active_refresh_tokens(self, db: AsyncSession, user_id) -> None:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        rows = (await db.execute(stmt)).scalars().all()
        if not rows:
            return
        now = datetime.utcnow()
        for token_row in rows:
            token_row.revoked_at = now

    async def is_setup_required(self, db: AsyncSession) -> bool:
        """Returns True when there are no active users yet."""
        user_stmt = select(User.id).where(User.deleted_at.is_(None)).limit(1)
        existing_user_id = (await db.execute(user_stmt)).scalar_one_or_none()
        return existing_user_id is None

    async def bootstrap_super_admin(self, db: AsyncSession, username: str, email: str, password: str) -> User:
        """Create first super admin exactly once."""
        setup_required = await self.is_setup_required(db)
        if not setup_required:
            raise HTTPException(status_code=409, detail="Setup already completed")

        user = User(
            username=username,
            display_name=username,
            email=email,
            password_hash=get_password_hash(password),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="Setup already completed")
        await db.refresh(user)
        return user

    async def create_user_by_admin(self, db: AsyncSession, payload: RegisterRequest) -> User:
        """Create user from admin-only endpoint once setup is complete."""
        existing_stmt = select(User).where((User.username == payload.username) | (User.email == payload.email))
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

    async def register(self, db: AsyncSession, payload: RegisterRequest) -> User:
        setup_required = await self.is_setup_required(db)
        if not setup_required:
            raise HTTPException(status_code=403, detail="Public registration disabled after setup")

        existing_stmt = select(User).where((User.username == payload.username) | (User.email == payload.email))
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
        stmt = select(User).where((User.username == payload.username) | (User.email == payload.username))
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if needs_password_rehash(user.password_hash):
            user.password_hash = get_password_hash(payload.password)

        access_token = create_access_token(str(user.id))
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

        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        if row.revoked_at is not None:
            await self._revoke_all_active_refresh_tokens(db, row.user_id)
            await db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token reuse detected")

        if row.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        row.revoked_at = datetime.utcnow()

        user_stmt = select(User).where(User.id == row.user_id, User.deleted_at.is_(None), User.is_active == True)  # noqa: E712
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token user")

        new_access = create_access_token(str(user.id))
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
