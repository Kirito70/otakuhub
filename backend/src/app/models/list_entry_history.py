"""List entry history model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime
from sqlalchemy import String
from src.app.models.enums import WatchStatus

if TYPE_CHECKING:
    from .user import User
    from .user_list_entry import UserListEntry
    from .media_entry import MediaEntry


class ListEntryHistory(SQLModel, table=True):
    """Append-only log of every status/progress change. Powers the activity feed."""

    __tablename__ = "list_entry_history"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    entry_id: UUID = Field(foreign_key="user_list_entry.id", nullable=False)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    media_id: UUID = Field(foreign_key="media_entries.id", nullable=False)
    event_type: str = Field(nullable=False, max_length=50)  # 'status_changed', 'progress_updated', 'score_set', 'added', 'removed'
    old_status: Optional[WatchStatus] = Field(default=None, sa_type=String(50))
    new_status: Optional[WatchStatus] = Field(default=None, sa_type=String(50))
    old_progress: Optional[int] = Field(default=None)
    new_progress: Optional[int] = Field(default=None)
    old_score: Optional[float] = Field(default=None)
    new_score: Optional[float] = Field(default=None)
    note: Optional[str] = Field(default=None)  # optional note attached to this update

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    entry: Optional["UserListEntry"] = Relationship()
    user: Optional["User"] = Relationship()
    media: Optional["MediaEntry"] = Relationship()

    # Create indexes for performance
    __table_args__ = (
        Index("idx_history_user_id", "user_id", "created_at"),
        Index("idx_history_entry_id", "entry_id"),
        Index("idx_history_media_id", "media_id"),
        # Powers group activity feed
        Index("idx_history_group_feed", "user_id", "created_at"),
    )
