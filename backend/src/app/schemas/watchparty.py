"""Schemas for watch party endpoints (Phase 10)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
