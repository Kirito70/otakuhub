"""Provider/source series mapping model (ADR 078)."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, Column, UniqueConstraint, text
from sqlmodel import Field, Index, Relationship, SQLModel

from src.app.core.uuid7 import generate_uuid7

if TYPE_CHECKING:
    from .media_source_episode import MediaSourceEpisode


def utc_now() -> datetime:
    # Existing SQLModel mappings use naive UTC datetimes with asyncpg. Keep the
    # provider models consistent to avoid offset-aware/naive binding errors.
    return datetime.utcnow()


class MediaSourceMapping(SQLModel, table=True):
    """One row per canonical media title per provider/source catalog ID."""

    __tablename__ = "media_source_mappings"

    id: UUID = Field(default_factory=generate_uuid7, primary_key=True, nullable=False)
    media_id: UUID | None = Field(default=None, foreign_key="media_entries.id")
    source: str = Field(nullable=False, max_length=50)
    source_media_id: str = Field(nullable=False, max_length=128)
    source_slug: str | None = Field(default=None, max_length=300)
    source_url: str | None = Field(default=None, max_length=2048)
    source_title: str | None = Field(default=None, max_length=500)
    source_title_normalized: str | None = Field(default=None, max_length=500)
    source_payload_hash: str | None = Field(default=None, max_length=64)
    source_payload: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    source_titles: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    mapping_status: str = Field(default="matched", nullable=False, max_length=20)
    match_confidence: Decimal = Field(default=Decimal("100.00"), nullable=False, max_digits=5, decimal_places=2)
    is_streaming_enabled: bool = Field(default=False, nullable=False)
    has_sub: bool = Field(default=False, nullable=False)
    has_dub: bool = Field(default=False, nullable=False)
    episode_count: int | None = Field(default=None)
    first_seen_at: datetime = Field(default_factory=utc_now, nullable=False)
    last_seen_at: datetime = Field(default_factory=utc_now, nullable=False)
    details_synced_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
    deleted_at: datetime | None = Field(default=None)

    episodes: list["MediaSourceEpisode"] = Relationship(back_populates="mapping")

    __table_args__ = (
        UniqueConstraint("source", "source_media_id", name="uq_media_source_mappings_source_media"),
        Index("idx_media_source_mappings_media", "media_id", "source", postgresql_where=text("deleted_at IS NULL")),
        Index("idx_media_source_mappings_source_seen", "source", "last_seen_at", postgresql_where=text("deleted_at IS NULL")),
        Index("idx_media_source_mappings_status", "source", "mapping_status", postgresql_where=text("deleted_at IS NULL")),
        Index(
            "idx_media_source_mappings_title_trgm",
            "source_title_normalized",
            postgresql_using="gin",
            postgresql_ops={"source_title_normalized": "gin_trgm_ops"},
        ),
    )
