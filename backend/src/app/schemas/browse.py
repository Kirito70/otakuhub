"""Pydantic schemas for the Browse endpoint (ADR 094 Section 6.4)."""

from __future__ import annotations

from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BrowseResultItem(BaseModel):
    """Single browse result item for filtered grid display."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_medium: Optional[str] = None
    cover_image_large: Optional[str] = None
    format: Optional[str] = None
    media_type: Optional[str] = None
    season_year: Optional[int] = None
    average_score: Optional[float] = None
    episode_count: Optional[int] = None
    chapter_count: Optional[int] = None


class BrowseResponse(BaseModel):
    """Paginated browse response with cursor-based pagination."""

    items: list[BrowseResultItem] = []
    total: int = 0
    next_cursor: Optional[str] = None  # ISO timestamp for cursor pagination


class CuratedRail(BaseModel):
    """A single curated rail (horizontal scroll section)."""

    title: str
    rail_id: str
    items: list[BrowseResultItem] = []


class CuratedRailsResponse(BaseModel):
    """Curated rails for Discover default state."""

    rails: list[CuratedRail] = []
