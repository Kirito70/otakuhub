"""Group model for OtakuHub."""

from sqlmodel import SQLModel, Field, Index
from typing import Optional
from uuid import UUID
from datetime import datetime


class Group(SQLModel, table=True):
    """Group model for friend groups."""
    
    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    name: str = Field(nullable=False, max_length=100)
    description: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None, max_length=2048)
    invite_code: str = Field(nullable=False, unique=True, max_length=32)
    owner_id: UUID = Field(foreign_key="user.id", nullable=False)
    is_private: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
        
    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)
    
    # Create indexes for performance
    __table_args__ = (
        Index("idx_groups_invite_code", "invite_code"),
    )