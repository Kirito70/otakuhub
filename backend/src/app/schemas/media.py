'''Pydantic schemas for media endpoints.'''

from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict


class MediaDetailResponse(BaseModel):
    """Response schema for detailed media information.

    Only the fields accessed by the service layer are defined. Types are
    loosely typed (Any) for related objects to avoid circular imports in the
    test environment.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    title_native: Optional[str] = None
    media_type: Any
    format: Optional[Any] = None
    status: Any
    synopsis: Optional[str] = None
    cover_image_large: Optional[str] = None
    cover_image_medium: Optional[str] = None
    banner_image: Optional[str] = None
    episode_count: Optional[int] = None
    chapter_count: Optional[int] = None
    volume_count: Optional[int] = None
    duration_minutes: Optional[int] = None
    average_score: Optional[float] = None
    popularity: Optional[int] = None
    trending: Optional[int] = None
    season: Optional[Any] = None
    season_year: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_adult: bool = False
    country_of_origin: Optional[str] = None
    external_ids: Optional[Any] = None
    genres: List[Any] = []
    studios: List[Any] = []
    tags: List[Any] = []
    created_at: datetime
    updated_at: datetime
