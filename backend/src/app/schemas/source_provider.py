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
    embed_path: str | None = None
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
    is_streaming_enabled: bool
    has_sub: bool
    has_dub: bool
    episode_count: int | None
    last_seen_at: datetime
    details_synced_at: datetime | None


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
