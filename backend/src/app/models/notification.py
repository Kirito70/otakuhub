"""Notification model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from src.app.models.enums import NotificationType

if TYPE_CHECKING:
    from .user import User
    from .media_entry import MediaEntry
    from .user import User as RelatedUser


class Notification(SQLModel, table=True):
    """Notification inbox for users."""

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    type: NotificationType = Field(nullable=False)
    title: str = Field(nullable=False, max_length=300)
    body: Optional[str] = Field(default=None)
    action_url: Optional[str] = Field(default=None, max_length=2048)
    related_media_id: Optional[UUID] = Field(default=None, foreign_key="media_entries.id")
    related_user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    is_read: bool = Field(default=False)
    read_at: Optional[datetime] = Field(default=None)
    sent_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships intentionally omitted to avoid ambiguous FK mapper setup

    # Create indexes for performance
    __table_args__ = (
        Index("idx_notifications_user", "user_id", "is_read", "created_at"),
        Index("idx_notifications_cleanup", "created_at"),
    )
