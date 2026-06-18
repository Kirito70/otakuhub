"""Recommendation model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index, UniqueConstraint
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .media_entry import MediaEntry


class Recommendation(SQLModel, table=True):
    """Friend recommending a title to specific people."""

    __tablename__ = "recommendations"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    from_user_id: UUID = Field(foreign_key="users.id", nullable=False)
    to_user_id: UUID = Field(foreign_key="users.id", nullable=False)
    media_id: UUID = Field(foreign_key="media_entries.id", nullable=False)
    message: Optional[str] = Field(default=None)
    is_acknowledged: bool = Field(default=False)
    acknowledged_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships intentionally omitted to avoid ambiguous FK mapper setup

    # Create indexes for performance
    __table_args__ = (
        Index("idx_recommendations_to_user", "to_user_id", "is_acknowledged", "created_at"),
        Index("idx_recommendations_from", "from_user_id"),
        UniqueConstraint("from_user_id", "to_user_id", "media_id", name="uq_recommendation_users_media"),
    )
