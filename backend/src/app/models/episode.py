"""Episode model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime

if TYPE_CHECKING:
    from .media_entry import MediaEntry


class Episode(SQLModel, table=True):
    """Airing schedule data for anime."""

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    media_id: UUID = Field(
        foreign_key="media_entries.id",
        nullable=False
    )
    episode_number: int = Field(nullable=False)
    title: Optional[str] = Field(default=None, max_length=500)
    air_date: Optional[datetime] = Field(default=None)  # TIMESTAMPTZ
    duration_minutes: Optional[int] = Field(default=None)
    thumbnail_url: Optional[str] = Field(default=None, max_length=2048)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    media: Optional["MediaEntry"] = Relationship(back_populates="episodes")

    # Create indexes for performance
    __table_args__ = (
        Index("idx_episodes_media_id", "media_id"),
        Index("idx_episodes_air_date", "air_date"),
    )
