"""Pydantic schemas for the unified Calendar endpoint (ADR 094 Section 6.4)."""

from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CalendarEvent(BaseModel):
    """A single calendar event — either an episode airing or a chapter release."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    media_id: UUID
    title: str
    cover_image: Optional[str] = None
    media_type: Optional[str] = None
    episode_number: Optional[int] = None
    chapter_number: Optional[int] = None
    airing_at: datetime
    format: Optional[str] = None
    event_type: str = "episode"  # "episode" or "chapter"


class CalendarResponse(BaseModel):
    """Response for the unified calendar endpoint."""

    items: list[CalendarEvent] = []
    total: int = 0
    limit: int = 100
