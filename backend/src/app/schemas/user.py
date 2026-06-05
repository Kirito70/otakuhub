'''User related response schemas.'''

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    """Public profile information for a user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: Optional[str] = None
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Payload for partial update of current user profile."""

    model_config = ConfigDict(from_attributes=True)

    display_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=2048)
    bio: Optional[str] = None
    timezone: Optional[str] = Field(default=None, max_length=64)


class UserSettings(BaseModel):
    """Placeholder for user settings – currently empty but required for type hints."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    # Add any future settings fields here as optional


class PublicUserProfile(BaseModel):
    """Public-safe profile payload for user directory and social screens."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    created_at: datetime


class AdminUserResponse(BaseModel):
    """User summary for admin listing (includes email)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: Optional[str] = None
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Paginated list of users (admin)."""

    items: list[AdminUserResponse]
    total: int
    limit: int
    offset: int


class UserSettingsResponse(BaseModel):
    """User settings response."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    theme: str = "system"
    language: str = "en"
    timezone: str = "UTC"
    updated_at: Optional[datetime] = None


class UserSettingsUpdateRequest(BaseModel):
    """Payload for updating user settings."""

    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
