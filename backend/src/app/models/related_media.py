"""Related media model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from src.app.models.enums import RelationType

if TYPE_CHECKING:
    from .media_entry import MediaEntry


class RelatedMedia(SQLModel, table=True):
    """Relationships between media entries (sequel/prequel, etc)."""

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    source_media_id: UUID = Field(
        foreign_key="media_entries.id",
        nullable=False
    )
    related_media_id: UUID = Field(
        foreign_key="media_entries.id",
        nullable=False
    )
    relation_type: RelationType = Field(nullable=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships intentionally omitted to avoid ambiguous FK mapper setup

    # Create indexes for performance
    __table_args__ = (
        Index("idx_related_media_source", "source_media_id"),
        Index("idx_related_media_target", "related_media_id"),
    )
