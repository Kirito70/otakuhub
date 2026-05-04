"""Repository for refresh token operations."""

from sqlmodel import select, AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.refresh_token import RefreshToken
from app.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for refresh token operations."""
    
    def __init__(self):
        super().__init__(RefreshToken)
    
    async def get_by_hash(self, db: AsyncSession, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by its hash."""
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def revoke(self, db: AsyncSession, token_id: str) -> None:
        """Revoke a refresh token."""
        statement = select(RefreshToken).where(RefreshToken.id == token_id)
        result = await db.execute(statement)
        token = result.scalar_one_or_none()
        
        if token:
            token.revoked_at = datetime.utcnow()
            db.add(token)
            await db.commit()
    
    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> list[RefreshToken]:
        """Get all active (non-revoked) refresh tokens for a user."""
        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow()
        )
        result = await db.execute(statement)
        return result.scalars().all()