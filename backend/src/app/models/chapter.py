"""Chapter model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

if TYPE_CHECKING:
    from .media_entry import MediaEntry


class Chapter(SQLModel, table=True):
    """Chapter release data for manga."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    media_id: UUID = Field(
        foreign_key="media_entries.id",
        nullable=False
    )
    chapter_number: float = Field(nullable=False)  # float allows 12.5 for sub-chapters
    volume_number: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None, max_length=500)
    published_at: Optional[datetime] = Field(default=None)  # TIMESTAMPTZ
    mangadex_chapter_id: Optional[str] = Field(default=None, max_length=64)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    media: Optional["MediaEntry"] = Relationship(back_populates="chapters")

    # Create indexes for performance
    __table_args__ = (
        Index("idx_chapters_media_id", "media_id"),
        Index("idx_chapters_published_at", "published_at"),
    )
