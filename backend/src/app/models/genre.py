"""Genre model for OtakuHub."""

from sqlmodel import SQLModel, Field, Column, Text
from typing import Optional
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime


class Genre(SQLModel, table=True):
    """Genre model."""

    __tablename__ = "genres"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    name: str = Field(sa_column=Column(Text, nullable=False))
    slug: str = Field(sa_column=Column(Text, nullable=False))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)
