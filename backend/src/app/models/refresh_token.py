"""Refresh token model for OtakuHub."""

from sqlmodel import SQLModel, Field, Index
from typing import Optional
from uuid import UUID
from datetime import datetime


class RefreshToken(SQLModel, table=True):
    """Refresh token model for OtakuHub."""

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    token_hash: str = Field(nullable=False, unique=True, max_length=255)  # SHA-256 of the actual token
    device_name: Optional[str] = Field(default=None, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    expires_at: datetime = Field(nullable=False)
    revoked_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Create indexes for performance
    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_expires", "expires_at"),
    )
