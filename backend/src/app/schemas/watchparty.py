"""Schemas for watch party endpoints (Phase 10)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.app.models.enums import RsvpStatus


class WatchPartyCreateRequest(BaseModel):
    """Payload to create a watch party."""

    group_id: UUID
    media_id: UUID
    scheduled_at: datetime
    title: str | None = Field(default=None, max_length=300)
    episode_number: int | None = None
    stream_url: str | None = Field(default=None, max_length=2048)
    sync_url: str | None = Field(default=None, max_length=2048)
    notes: str | None = None


class WatchPartyResponse(BaseModel):
    """Watch party response model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_id: UUID
    host_user_id: UUID
    media_id: UUID
    episode_number: int | None = None
    title: str | None = None
    scheduled_at: datetime
    status: str
    stream_url: str | None = None
    sync_url: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class WatchPartyListResponse(BaseModel):
    """Paginated upcoming watch parties visible to current user."""

    items: list[WatchPartyResponse]
    total: int
    limit: int
    offset: int


class WatchPartyDetailResponse(BaseModel):
    """Watch party detail response with media, host, and RSVP info."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    group_id: UUID
    host_user_id: UUID
    host_username: str | None = None
    host_display_name: str | None = None
    media_id: UUID
    media_title: str | None = None
    media_cover: str | None = None
    episode_number: int | None = None
    title: str | None = None
    scheduled_at: datetime
    status: str
    stream_url: str | None = None
    sync_url: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    rsvp_summary: dict = Field(default_factory=lambda: {"attending": 0, "pending": 0, "declined": 0})
    attendee_count: int = 0


class WatchPartyRsvpRequest(BaseModel):
    """Payload to RSVP to a watch party."""

    status: RsvpStatus = RsvpStatus.pending


class WatchPartyRsvpResponse(BaseModel):
    """Watch party RSVP response model."""

    model_config = ConfigDict(from_attributes=True)

    party_id: UUID
    user_id: UUID
    status: RsvpStatus
    responded_at: datetime | None = None
    created_at: datetime
