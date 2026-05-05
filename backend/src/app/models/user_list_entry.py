"""User list entry model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from src.app.models.enums import WatchStatus

if TYPE_CHECKING:
    from .user import User
    from .media_entry import MediaEntry


class UserListEntry(SQLModel, table=True):
    """The core tracking table. One row per user per media title."""

    __tablename__ = "user_list_entry"

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    media_id: UUID = Field(foreign_key="media_entries.id", nullable=False)
    status: WatchStatus = Field(nullable=False)
    progress: int = Field(default=0)  # episodes watched / chapters read
    score: Optional[float] = Field(default=None)  # user's personal score 0.0–10.0
    notes: Optional[str] = Field(default=None)
    is_private: bool = Field(default=False)
    repeat_count: int = Field(default=0)  # rewatch/reread count
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship()
    media: Optional["MediaEntry"] = Relationship()

    # Create indexes for performance
    __table_args__ = (
        Index("idx_list_entries_user_id", "user_id"),
        Index("idx_list_entries_media_id", "media_id"),
        Index("idx_list_entries_status", "user_id", "status"),
        Index("idx_list_entries_updated", "user_id", "updated_at"),
        Index("idx_list_entries_user_media", "user_id", "media_id", unique=True),
    )
