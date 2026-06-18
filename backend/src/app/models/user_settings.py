"""UserSettings model for per-user preferences."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from src.app.core.uuid7 import generate_uuid7


class UserSettings(SQLModel, table=True):
    """Per-user settings/preferences model."""

    __tablename__ = "user_settings"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False,
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        unique=True,
        nullable=False,
        index=True,
    )
    theme: str = Field(default="system", max_length=20)
    language: str = Field(default="en", max_length=10)
    timezone: str = Field(default="UTC", max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
