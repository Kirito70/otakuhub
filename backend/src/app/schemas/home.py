"""Pydantic schemas for the composite Home endpoint (ADR 094 Section 8.1)."""

from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class HomeSpotlightItem(BaseModel):
    """Hero/spotlight media item — top trending media with full metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    format: Optional[str] = None
    season_year: Optional[int] = None
    average_score: Optional[float] = None
    synopsis: Optional[str] = None
    cover_image_large: Optional[str] = None
    banner_image: Optional[str] = None
    media_type: Optional[str] = None


class HomeContinueItem(BaseModel):
    """Continue-watching/reading item — user's in-progress list entries."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID  # UserListEntry id
    media_id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_large: Optional[str] = None
    progress: int = 0
    max_progress: Optional[int] = None  # episode_count or chapter_count
    next_episode_number: Optional[int] = None
    status: Optional[str] = None


class HomeFriendRecItem(BaseModel):
    """Friend recommendation item — recommendation from a group member."""

    id: UUID  # Recommendation id
    media_id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_large: Optional[str] = None
    average_score: Optional[float] = None
    from_user_id: Optional[str] = None
    from_username: Optional[str] = None
    from_display_name: Optional[str] = None
    from_avatar_url: Optional[str] = None
    message: Optional[str] = None


class WatchingFriend(BaseModel):
    """Friend who is watching/reading a title."""

    user_id: UUID
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = False


class HomeGroupWatchingItem(BaseModel):
    """Group-watching item — what friends are watching together."""

    media_id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_large: Optional[str] = None
    friends: list[WatchingFriend] = []


class HomeAiringSoonItem(BaseModel):
    """Airing-soon item — upcoming episode."""

    media_id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_large: Optional[str] = None
    episode_number: Optional[int] = None
    airing_at: Optional[datetime] = None


class HomeTrendingItem(BaseModel):
    """Trending-in-group item — what's popular among group members."""

    id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_large: Optional[str] = None
    average_score: Optional[float] = None
    format: Optional[str] = None


class GenreRailItem(BaseModel):
    """A media item within a genre-based rail on the home page."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title_romaji: str
    title_english: Optional[str] = None
    cover_image_large: Optional[str] = None
    average_score: Optional[float] = None
    format: Optional[str] = None


class GenreRail(BaseModel):
    """A genre-based horizontal rail with media items."""

    genre_id: UUID
    genre_name: str
    items: list[GenreRailItem] = []


class MediaTypeSection(BaseModel):
    """A media type section containing genre-based rails."""

    media_type: str
    media_type_label: str
    genre_rails: list[GenreRail] = []


class HomeData(BaseModel):
    """Composite response for GET /api/v1/home."""

    spotlight: list[HomeSpotlightItem] = []
    continue_watching: list[HomeContinueItem] = []
    friend_recommendations: list[HomeFriendRecItem] = []
    group_watching_now: list[HomeGroupWatchingItem] = []
    airing_soon: list[HomeAiringSoonItem] = []
    trending_in_group: list[HomeTrendingItem] = []
    media_type_sections: list[MediaTypeSection] = []
