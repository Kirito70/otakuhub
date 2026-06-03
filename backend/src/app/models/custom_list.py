"""Custom list model for OtakuHub."""

from sqlmodel import SQLModel, Field, Index
from typing import Optional
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime


class CustomList(SQLModel, table=True):
    """User-created curated lists ("Best Isekai", "Watch with friends")."""

    __tablename__ = "custom_list"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    name: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None)
    is_public: bool = Field(default=False)  # visible to group members
    cover_image: Optional[str] = Field(default=None, max_length=2048)
    sort_order: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Create indexes for performance
    __table_args__ = (
        Index("idx_custom_lists_user", "user_id"),
    )
