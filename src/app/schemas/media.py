"""Media schemas stub for testing."""

from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class MediaDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title_romaji: Optional[str] = None
    title_english: Optional[str] = None
    title_native: Optional[str] = None
    media_type: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    synopsis: Optional[str] = None
    cover_image_large: Optional[str] = None
    cover_image_medium: Optional[str] = None
    banner_image: Optional[str] = None
    episode_count: Optional[int] = None
    chapter_count: Optional[int] = None
    volume_count: Optional[int] = None
    average_score: Optional[float] = None
    popularity: Optional[int] = None
    trending: Optional[int] = None
    season: Optional[str] = None
    season_year: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_adult: Optional[bool] = None
    country_of_origin: Optional[str] = None
    genres: List[str] = []
    studios: List[str] = []
    tags: List[str] = []
