"""Genre model for OtakuHub."""

from sqlmodel import SQLModel, Field, Column, Text
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.app.models.enums import MediaType


class Genre(SQLModel, table=True):
    """Genre model."""
    
    id: UUID = Field(
        default_factory=UUID,
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