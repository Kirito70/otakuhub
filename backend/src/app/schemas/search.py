"""Pydantic schemas for the grouped Global Search endpoint (ADR 094 Section 6.2)."""

from __future__ import annotations

from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SearchResultItem(BaseModel):
    """Single search result item returned in grouped results."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_small: Optional[str] = None
    format: Optional[str] = None
    season_year: Optional[int] = None
    average_score: Optional[float] = None


class SearchResponse(BaseModel):
    """Grouped search response.

    Each media type (anime, manga, manhwa, light_novel) is a separate key
    containing a list of results, plus an *_count key for total count.
    """

    anime: list[SearchResultItem] = []
    anime_count: int = 0
    manga: list[SearchResultItem] = []
    manga_count: int = 0
    manhwa: list[SearchResultItem] = []
    manhwa_count: int = 0
    light_novel: list[SearchResultItem] = []
    light_novel_count: int = 0
