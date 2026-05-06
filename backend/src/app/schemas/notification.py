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
