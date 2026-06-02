"""Tag model for OtakuHub."""

from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime


class Tag(SQLModel, table=True):
    """Tag model."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    is_adult: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)
