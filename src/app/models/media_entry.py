# ruff: noqa
"""Media entry model for OtakuHub."""

from sqlmodel import SQLModel, Field, Column, Text, Index, Relationship
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from src.app.models.enums import MediaType, MediaFormat, MediaStatus, Season
from .media_genre import MediaGenre  # noqa: F401
from .media_studio import MediaStudio  # noqa: F401
from .media_tag import MediaTag  # noqa: F401
from .episode import Episode  # noqa: F401
from .chapter import Chapter  # noqa: F401
from .related_media import RelatedMedia  # noqa: F401

if TYPE_CHECKING:
    from .media_external_ids import MediaExternalIds


class MediaEntry(SQLModel, table=True):
    """Media entry model - The canonical table for every anime, manga, and manhwa."""

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    title_romaji: str = Field(nullable=False, max_length=500)
    title_english: Optional[str] = Field(default=None, max_length=500)
    title_native: Optional[str] = Field(default=None, max_length=500)
    title_search: Optional[str] = Field(default=None, sa_column=Column(Text))  # GIN indexed, auto-updated via trigger
    media_type: MediaType = Field(nullable=False)
    format: Optional[MediaFormat] = Field(default=None)
    status: MediaStatus = Field(default=MediaStatus.not_yet_released)
    synopsis: Optional[str] = Field(default=None, sa_column=Column(Text))
    cover_image_large: Optional[str] = Field(default=None, max_length=2048)
    cover_image_medium: Optional[str] = Field(default=None, max_length=2048)
    banner_image: Optional[str] = Field(default=None, max_length=2048)
    episode_count: Optional[int] = Field(default=None)
    chapter_count: Optional[int] = Field(default=None)
    volume_count: Optional[int] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None)  # per-episode duration for anime
    average_score: Optional[float] = Field(default=None)  # 0.0–10.0, from AniList
    popularity: Optional[int] = Field(default=None)  # AniList popularity rank
    trending: Optional[int] = Field(default=None)  # AniList trending score
    season: Optional[Season] = Field(default=None)
    season_year: Optional[int] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)  # DATE type in database
    end_date: Optional[datetime] = Field(default=None)  # DATE type in database
    is_adult: bool = Field(default=False)
    country_of_origin: Optional[str] = Field(default=None, max_length=2)  # ISO 3166-1 alpha-2 (JP, KR, CN)
    metadata_synced_at: Optional[datetime] = Field(default=None)  # NULL = needs backfill

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    external_ids: Optional["MediaExternalIds"] = Relationship(back_populates="media")
    media_genres: list["MediaGenre"] = Relationship(back_populates="media")
    media_studios: list["MediaStudio"] = Relationship(back_populates="media")
    media_tags: list["MediaTag"] = Relationship(back_populates="media")
    episodes: list["Episode"] = Relationship(back_populates="media")
    chapters: list["Chapter"] = Relationship(back_populates="media")
    related_media_source: list["RelatedMedia"] = Relationship(
        back_populates="source_media",

    )
    related_media_target: list["RelatedMedia"] = Relationship(
        back_populates="related_media",

    )

    # Create indexes - these will be handled by Alembic since they're defined in separate SQL files
    __table_args__ = (
        Index("idx_media_entries_title_search", "title_search", postgresql_using="gin"),
        Index("idx_media_entries_media_type", "media_type"),
        Index("idx_media_entries_status", "status"),
        Index("idx_media_entries_season", "season_year", "season"),
        Index("idx_media_entries_score", "average_score"),
        Index("idx_media_entries_synced_at", "metadata_synced_at"),
    )
