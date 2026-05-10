"""User schemas stub for testing."""

from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    display_name: str | None = None
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    timezone: str = "UTC"
    is_active: bool = True
    is_admin: bool = False


class UserSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    timezone: str = "UTC"
    # Add other settings fields as needed
