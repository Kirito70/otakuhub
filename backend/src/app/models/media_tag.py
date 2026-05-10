"""Media tag relationship model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .media_entry import MediaEntry
    from .tag import Tag


class MediaTag(SQLModel, table=True):
    """Many-to-many relationship between media entries and tags."""

    media_id: UUID = Field(
        foreign_key="media_entries.id",
        primary_key=True,
        nullable=False
    )
    tag_id: UUID = Field(
        foreign_key="tag.id",
        primary_key=True,
        nullable=False
    )
    rank: int = Field(default=0)  # AniList tag relevance 0–100

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    media: Optional["MediaEntry"] = Relationship()
    tag: Optional["Tag"] = Relationship()
