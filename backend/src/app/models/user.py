"""User model for OtakuHub."""

from sqlmodel import SQLModel, Field, Column, Text, Index
from typing import Optional
from uuid import UUID
from datetime import datetime


class User(SQLModel, table=True):
    """User model for OtakuHub."""
    
    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    username: str = Field(nullable=False, unique=True, max_length=50)
    display_name: Optional[str] = Field(default=None, max_length=100)
    email: str = Field(nullable=False, unique=True, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=2048)
    bio: Optional[str] = Field(default=None, sa_column=Column(Text))
    timezone: str = Field(default="UTC", max_length=64)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    last_seen_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
        
    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)
    
    # Create indexes for performance
    __table_args__ = (
        Index("idx_users_username", "username", postgresql_ops={"username": "varchar_pattern_ops"}),
        Index("idx_users_email", "email", postgresql_ops={"email": "varchar_pattern_ops"}),
    )