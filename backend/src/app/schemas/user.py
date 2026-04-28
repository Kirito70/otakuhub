'''User related response schemas.'''

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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


class UserSettings(BaseModel):
    """Placeholder for user settings – currently empty but required for type hints."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    # Add any future settings fields here as optional
