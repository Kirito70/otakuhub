"""Custom list entry model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .custom_list import CustomList
    from .media_entry import MediaEntry


class CustomListEntry(SQLModel, table=True):
    """Entry in a custom list."""

    __tablename__ = "custom_list_entry"

    list_id: UUID = Field(
        foreign_key="custom_list.id",
        primary_key=True,
        nullable=False
    )
    media_id: UUID = Field(
        foreign_key="media_entries.id",
        primary_key=True,
        nullable=False
    )
    sort_order: int = Field(default=0)
    note: Optional[str] = Field(default=None)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    list: Optional["CustomList"] = Relationship()
    media: Optional["MediaEntry"] = Relationship()

    # Create indexes for performance
    __table_args__ = (
        Index("idx_custom_list_entries_list", "list_id", "sort_order"),
    )
