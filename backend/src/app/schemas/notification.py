"""Schemas for notification endpoints (Phase 11)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.app.models.enums import NotificationType


class NotificationResponse(BaseModel):
    """Single notification item in user inbox."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    body: str | None = None
    action_url: str | None = None
    related_media_id: UUID | None = None
    related_user_id: UUID | None = None
    is_read: bool
    read_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated notifications visible to current user."""

    items: list[NotificationResponse]
    total: int
    limit: int
    offset: int


class NotificationMarkReadRequest(BaseModel):
    """Payload for marking notification items as read."""

    notification_ids: list[UUID] = Field(default_factory=list)


class NotificationMarkReadResponse(BaseModel):
    """Response for mark-as-read operation."""

    updated_count: int


class NotificationPreferencesResponse(BaseModel):
    """Current user's notification preference settings."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    new_episode: bool
    new_chapter: bool
    friend_activity: bool
    recommendations: bool
    watch_party_invite: bool
    watch_party_reminder: bool
    discord_webhook: str | None = None
    telegram_chat_id: str | None = None
    email_enabled: bool
    push_enabled: bool
    updated_at: datetime


class NotificationPreferencesUpdateRequest(BaseModel):
    """Patch payload for notification preferences."""

    new_episode: bool | None = None
    new_chapter: bool | None = None
    friend_activity: bool | None = None
    recommendations: bool | None = None
    watch_party_invite: bool | None = None
    watch_party_reminder: bool | None = None
    discord_webhook: str | None = None
    telegram_chat_id: str | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
