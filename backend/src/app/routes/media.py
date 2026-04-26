"""API routes for media management."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from src.app.services.media_service import MediaService
from src.app.services.user_service import UserService
from src.app.schemas.media import MediaDetailResponse, MediaSearchResponse
from src.app.core.auth import get_current_user
from src.app.models import User

router = APIRouter()

# Dependency injection for media service
def get_media_service():
    """Get MediaService instance."""
    return MediaService()

# Dependency injection for user service (only needed for auth)
def get_user_service():
    """Get UserService instance."""
    return UserService()

@router.get("/media/{media_id}", response_model=MediaDetailResponse)
async def get_media_detail(
    media_id: UUID,
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user)
):
    """Get detailed information about a specific media entry."""
    media = await media_service.get_media_detail(media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media

@router.get("/media/search")
async def search_media(
    query: Optional[str] = None,
    media_type: Optional[str] = None,
    status: Optional[str] = None,
    genres: Optional[str] = None,  # Will be comma-separated string
    year: Optional[int] = None,
    season: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user)
):
    """Search for media entries with various filters."""
    genre_list = genres.split(",") if genres else None
    media_list = await media_service.search_media(
        query=query,
        media_type=media_type,
        status=status,
        genres=genre_list,
        year=year,
        season=season,
        limit=limit,
        offset=offset
    )
    
    return {
        "items": media_list,
        "total": len(media_list),
        "limit": limit,
        "offset": offset
    }

@router.get("/media/popular")
async def get_popular_media(
    media_type: Optional[str] = None,
    limit: int = 20,
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user)
):
    """Get popular media entries."""
    media_list = await media_service.get_popular_media(media_type=media_type, limit=limit)
    return {
        "items": media_list,
        "total": len(media_list)
    }

@router.get("/media/trending")
async def get_trending_media(
    media_type: Optional[str] = None,
    limit: int = 20,
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user)
):
    """Get trending media entries."""
    media_list = await media_service.get_trending_media(media_type=media_type, limit=limit)
    return {
        "items": media_list,
        "total": len(media_list)
    }

@router.get("/media/airing")
async def get_airing_calendar(
    media_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user)
):
    """Get airing schedule/episode calendar."""
    # This would be implemented to return upcoming episodes
    # Placeholder for now
    return {
        "items": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }