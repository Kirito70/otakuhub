"""Studio model for OtakuHub."""

from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime


class Studio(SQLModel, table=True):
    """Studio model."""

    __tablename__ = "studios"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    name: str = Field(nullable=False, unique=True)
    anilist_id: Optional[int] = Field(default=None, unique=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)
