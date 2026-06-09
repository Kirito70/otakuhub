"""Typed schemas for provider/source sync (ADR 078)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SourceMappingUpsert(BaseModel):
    media_id: UUID | None = None
    source: str = Field(max_length=50)
    source_media_id: str = Field(max_length=128)
    source_slug: str | None = None
    source_url: str | None = None
    source_title: str | None = None
    source_title_normalized: str | None = None
    source_payload_hash: str | None = None
    source_payload: dict | None = None
    source_titles: dict | None = None
    mapping_status: str = "matched"
    match_confidence: Decimal = Decimal("100.00")
    is_streaming_enabled: bool = False
    has_sub: bool = False
    has_dub: bool = False
    episode_count: int | None = None
    details_synced_at: datetime | None = None


class SourceEpisodeUpsert(BaseModel):
    mapping_id: UUID
    media_id: UUID | None = None
    episode_id: UUID | None = None
    source: str = Field(max_length=50)
    source_episode_id: str = Field(max_length=128)
    episode_number: Decimal
    title: str | None = None
    language: str = "sub"
    embed_url: str | None = None
    embed_urls: dict | None = None
    source_payload: dict | None = None
    details_synced_at: datetime | None = None
    is_available: bool = True


class SourceMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    media_id: UUID | None
    source: str
    source_media_id: str
    source_title: str | None
    mapping_status: str
    match_confidence: Decimal
    source_payload: dict | None = None
    source_titles: dict | None = None
    is_streaming_enabled: bool
    has_sub: bool
    has_dub: bool
    episode_count: int | None
    last_seen_at: datetime
    details_synced_at: datetime | None


class SourceEpisodeItem(BaseModel):
    """Episode-level source info for the playback API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    episode_number: float
    title: str | None = None
    language: str = "sub"
    embed_url: str | None = None
    is_available: bool = True


class SourceMappingDetail(BaseModel):
    """Source mapping with embedded episode list for the playback API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    source_title: str | None = None
    mapping_status: str = "matched"
    match_confidence: Decimal = Decimal("100.00")
    is_streaming_enabled: bool = False
    has_sub: bool = False
    has_dub: bool = False
    episode_count: int | None = None
    episode_list: list[SourceEpisodeItem] = []


class MediaSourceResponse(BaseModel):
    """Response for GET /media/{id}/sources."""

    items: list[SourceMappingDetail] = []
    total: int = 0


class ConsolidatedSourceInfo(BaseModel):
    """A single source option for a consolidated episode."""

    source: str
    language: str = "sub"
    embed_url: str | None = None
    is_available: bool = True


class ConsolidatedEpisodeSourceItem(BaseModel):
    """A single episode with all its source options."""

    model_config = ConfigDict(from_attributes=True)

    episode_number: float
    canonical_title: str | None = None
    canonical_air_date: datetime | None = None
    sources: list[ConsolidatedSourceInfo] = []


class ConsolidatedEpisodeSourceResponse(BaseModel):
    """Response for GET /media/{id}/episodes/sources."""

    items: list[ConsolidatedEpisodeSourceItem] = []
    total: int = 0
    limit: int = 20
    offset: int = 0


class AnikotoFullSyncRequest(BaseModel):
    per_page: int = Field(default=20, ge=1, le=50)
    max_pages: int | None = Field(default=None, ge=1, le=500)
    refresh_details: bool = True
    dry_run: bool = False


class AnikotoRecentSyncRequest(BaseModel):
    per_page: int = Field(default=20, ge=1, le=50)
    max_pages: int = Field(default=5, ge=1, le=50)
    refresh_details: bool = True
    dry_run: bool = False


class JobEnqueueResponse(BaseModel):
    job_id: str
    job_type: str
    status: str = "queued"
    message: str = ""


# ── Admin source-mapping management (Phase 25.7) ──────────────────────────────


class AdminSourceMappingItem(BaseModel):
    """Detailed source mapping row for admin list view."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    media_id: UUID | None = None
    source: str
    source_media_id: str
    source_slug: str | None = None
    source_url: str | None = None
    source_title: str | None = None
    source_title_normalized: str | None = None
    mapping_status: str = "matched"
    match_confidence: Decimal = Decimal("100.00")
    is_streaming_enabled: bool = False
    has_sub: bool = False
    has_dub: bool = False
    episode_count: int | None = None
    first_seen_at: datetime
    last_seen_at: datetime
    details_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AdminSourceMappingListResponse(BaseModel):
    """Paginated admin source mapping list."""

    items: list[AdminSourceMappingItem] = []
    total: int = 0
    limit: int = 50
    offset: int = 0


class AdminSourceMappingUpdate(BaseModel):
    """PATCH body for updating a source mapping."""

    media_id: UUID | None = None
    mapping_status: str | None = None
    match_confidence: Decimal | None = None
    is_streaming_enabled: bool | None = None
    has_sub: bool | None = None
    has_dub: bool | None = None
    episode_count: int | None = None
    source_title: str | None = None
    source_url: str | None = None
    source_slug: str | None = None
