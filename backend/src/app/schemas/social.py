"""Schemas for social endpoints (Phase 9)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.app.models.enums import WatchStatus


class SocialFeedItemResponse(BaseModel):
    """Single activity item in group social feed."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entry_id: UUID
    user_id: UUID
    media_id: UUID
    event_type: str
    old_status: WatchStatus | None = None
    new_status: WatchStatus | None = None
    old_progress: int | None = None
    new_progress: int | None = None
    old_score: float | None = None
    new_score: float | None = None
    note: str | None = None
    created_at: datetime


class SocialFeedResponse(BaseModel):
    """Paginated group activity feed response."""

    items: list[SocialFeedItemResponse]
    total: int
    limit: int
    offset: int


class RecommendationCreateRequest(BaseModel):
    """Payload to recommend a media title to another user."""

    to_user_id: UUID
    media_id: UUID
    message: str | None = None


class RecommendationResponse(BaseModel):
    """Recommendation response model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    media_id: UUID
    message: str | None = None
    is_acknowledged: bool
    acknowledged_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RecommendationInboxResponse(BaseModel):
    """Paginated inbox recommendations for current user."""

    items: list[RecommendationResponse]
    total: int
    limit: int
    offset: int
