"""Provider/source episode ID model (ADR 078)."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, Column, UniqueConstraint, text
from sqlmodel import Field, Index, Relationship, SQLModel

from src.app.core.uuid7 import generate_uuid7

if TYPE_CHECKING:
    from .media_source_mapping import MediaSourceMapping


def utc_now() -> datetime:
    # Existing SQLModel mappings use naive UTC datetimes with asyncpg. Keep the
    # provider models consistent to avoid offset-aware/naive binding errors.
    return datetime.utcnow()


class MediaSourceEpisode(SQLModel, table=True):
    """Provider episode-level IDs and language availability."""

    __tablename__ = "media_source_episodes"

    id: UUID = Field(default_factory=generate_uuid7, primary_key=True, nullable=False)
    mapping_id: UUID = Field(foreign_key="media_source_mappings.id", nullable=False)
    media_id: UUID | None = Field(default=None, foreign_key="media_entries.id")
    episode_id: UUID | None = Field(default=None, foreign_key="episode.id")
    source: str = Field(nullable=False, max_length=50)
    source_episode_id: str = Field(nullable=False, max_length=128)
    episode_number: Decimal = Field(nullable=False, max_digits=8, decimal_places=2)
    title: str | None = Field(default=None, max_length=500)
    language: str = Field(default="sub", nullable=False, max_length=20)
    embed_url: str | None = Field(default=None, max_length=2048)
    embed_urls: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    source_payload: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    details_synced_at: datetime | None = Field(default=None)
    is_available: bool = Field(default=True, nullable=False)
    first_seen_at: datetime = Field(default_factory=utc_now, nullable=False)
    last_seen_at: datetime = Field(default_factory=utc_now, nullable=False)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
    deleted_at: datetime | None = Field(default=None)

    mapping: "MediaSourceMapping" = Relationship(back_populates="episodes")

    __table_args__ = (
        UniqueConstraint("source", "source_episode_id", "language", name="uq_media_source_episodes_source_episode_language"),
        Index("idx_media_source_episodes_mapping", "mapping_id", "episode_number"),
        Index("idx_media_source_episodes_media", "media_id", "episode_number", "language", postgresql_where=text("deleted_at IS NULL")),
        Index("idx_media_source_episodes_available", "source", "is_available", "last_seen_at", postgresql_where=text("deleted_at IS NULL")),
    )
