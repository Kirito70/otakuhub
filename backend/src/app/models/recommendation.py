"""Recommendation model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .media_entry import MediaEntry


class Recommendation(SQLModel, table=True):
    """Friend recommending a title to specific people."""

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    from_user_id: UUID = Field(foreign_key="user.id", nullable=False)
    to_user_id: UUID = Field(foreign_key="user.id", nullable=False)
    media_id: UUID = Field(foreign_key="mediaentry.id", nullable=False)
    message: Optional[str] = Field(default=None)
    is_acknowledged: bool = Field(default=False)
    acknowledged_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    from_user: Optional["User"] = Relationship(back_populates="sent_recommendations", foreign_key_constraint_name="fk_recommendation_from_user")
    to_user: Optional["User"] = Relationship(back_populates="received_recommendations", foreign_key_constraint_name="fk_recommendation_to_user")
    media: Optional["MediaEntry"] = Relationship(back_populates="recommendations")

    # Create indexes for performance
    __table_args__ = (
        Index("idx_recommendations_to_user", "to_user_id", "is_acknowledged", "created_at", postgresql_sort_order="DESC"),
        Index("idx_recommendations_from", "from_user_id"),
        Index("idx_recommendations_user_media", "from_user_id", "to_user_id", "media_id", unique=True),
    )
