"""Notification preference model for OtakuHub."""

from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class NotificationPreference(SQLModel, table=True):
    """Notification preferences for users."""

    user_id: UUID = Field(
        foreign_key="user.id",
        primary_key=True,
        nullable=False
    )
    new_episode: bool = Field(default=True)
    new_chapter: bool = Field(default=True)
    friend_activity: bool = Field(default=True)
    recommendations: bool = Field(default=True)
    watch_party_invite: bool = Field(default=True)
    watch_party_reminder: bool = Field(default=True)
    # Delivery channels (via Apprise)
    discord_webhook: Optional[str] = Field(default=None, max_length=2048)
    telegram_chat_id: Optional[str] = Field(default=None, max_length=100)
    email_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=False)

    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)
