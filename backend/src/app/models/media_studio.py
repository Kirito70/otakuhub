"""Media studio relationship model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .media_entry import MediaEntry
    from .studio import Studio


class MediaStudio(SQLModel, table=True):
    """Many-to-many relationship between media entries and studios."""

    media_id: UUID = Field(
        foreign_key="media_entries.id",
        primary_key=True,
        nullable=False
    )
    studio_id: UUID = Field(
        foreign_key="studio.id",
        primary_key=True,
        nullable=False
    )
    is_main: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    media: Optional["MediaEntry"] = Relationship(back_populates="media_studios")
    studio: Optional["Studio"] = Relationship(back_populates="media_studios")
