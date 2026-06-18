"""External auth model for OtakuHub."""

from sqlmodel import SQLModel, Field, Index
from typing import Optional
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime


class ExternalAuth(SQLModel, table=True):
    """External auth model for future AniList/MAL OAuth."""

    __tablename__ = "external_auth"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    provider: str = Field(nullable=False, max_length=50)  # 'anilist', 'myanimelist'
    provider_user_id: str = Field(nullable=False, max_length=255)
    access_token: Optional[str] = Field(default=None)  # encrypted at rest
    refresh_token: Optional[str] = Field(default=None)  # encrypted at rest
    token_expires_at: Optional[datetime] = Field(default=None)
    provider_username: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Create indexes for performance
    __table_args__ = (
        Index("idx_external_auth_user_provider", "user_id", "provider"),
    )
