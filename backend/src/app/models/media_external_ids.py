"""Media external IDs model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .media_entry import MediaEntry


class MediaExternalIds(SQLModel, table=True):
    """Cross-reference table mapping internal UUID to external platform IDs."""

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    media_id: UUID = Field(
        foreign_key="mediaentry.id",
        nullable=False
    )
    anilist_id: Optional[int] = Field(default=None, unique=True)
    mal_id: Optional[int] = Field(default=None, unique=True)
    mangadex_id: Optional[str] = Field(default=None, max_length=64, unique=True)  # UUID string from MangaDex
    anidb_id: Optional[int] = Field(default=None)
    kitsu_id: Optional[str] = Field(default=None, max_length=64)
    anime_planet_slug: Optional[str] = Field(default=None, max_length=256)
    simkl_id: Optional[int] = Field(default=None)
    livechart_id: Optional[int] = Field(default=None)
    notify_moe_id: Optional[str] = Field(default=None, max_length=64)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    media: Optional["MediaEntry"] = Relationship(back_populates="external_ids")
