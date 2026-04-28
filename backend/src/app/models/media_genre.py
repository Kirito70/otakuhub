"""Media genre relationship model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .media_entry import MediaEntry
    from .genre import Genre


class MediaGenre(SQLModel, table=True):
    """Many-to-many relationship between media entries and genres."""

    media_id: UUID = Field(
        foreign_key="media_entries.id",
        primary_key=True,
        nullable=False
    )
    genre_id: UUID = Field(
        foreign_key="genre.id",
        primary_key=True,
        nullable=False
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    media: Optional["MediaEntry"] = Relationship(back_populates="media_genres")
    genre: Optional["Genre"] = Relationship(back_populates="media_genres")
