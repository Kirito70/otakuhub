"""Watch party model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from src.app.models.enums import PartyStatus

if TYPE_CHECKING:
    from .user import User
    from .media_entry import MediaEntry
    from .group import Group


class WatchParty(SQLModel, table=True):
    """Watch party event model."""

    __tablename__ = "watch_party"

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    group_id: UUID = Field(foreign_key="group.id", nullable=False)
    host_user_id: UUID = Field(foreign_key="user.id", nullable=False)
    media_id: UUID = Field(foreign_key="media_entries.id", nullable=False)
    episode_number: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None, max_length=300)
    scheduled_at: datetime = Field(nullable=False)
    status: PartyStatus = Field(default=PartyStatus.scheduled)
    stream_url: Optional[str] = Field(default=None, max_length=2048)  # HiAnime, Crunchyroll, etc. deep link
    sync_url: Optional[str] = Field(default=None, max_length=2048)  # SyncParty / Rave link if using sync tool
    notes: Optional[str] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    group: Optional["Group"] = Relationship()
    host_user: Optional["User"] = Relationship()
    media: Optional["MediaEntry"] = Relationship()

    # Create indexes for performance
    __table_args__ = (
        Index("idx_watch_parties_group", "group_id", "scheduled_at"),
        Index("idx_watch_parties_schedule", "scheduled_at"),
    )
