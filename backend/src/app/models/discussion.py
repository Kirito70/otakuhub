"""Discussion model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .media_entry import MediaEntry
    from .group import Group


class Discussion(SQLModel, table=True):
    """Per-title discussion threads, scoped to a group."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    media_id: UUID = Field(foreign_key="media_entries.id", nullable=False)
    group_id: UUID = Field(foreign_key="group.id", nullable=False)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    title: Optional[str] = Field(default=None, max_length=300)
    episode_number: Optional[int] = Field(default=None)  # NULL = general; set = episode-specific discussion
    chapter_number: Optional[float] = Field(default=None)
    body: str = Field(nullable=False)
    has_spoilers: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    media: Optional["MediaEntry"] = Relationship()
    group: Optional["Group"] = Relationship()
    user: Optional["User"] = Relationship()

    # Create indexes for performance
    __table_args__ = (
        Index("idx_discussions_media_group", "media_id", "group_id", "created_at"),
        Index("idx_discussions_user", "user_id"),
    )
