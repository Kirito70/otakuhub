"""Repository for media-related database operations."""

from typing import List, Optional
from sqlmodel import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.app.models import MediaEntry, MediaExternalIds, Genre, Studio, Tag, MediaGenre, MediaStudio, MediaTag
from src.app.repositories.base_repository import BaseRepository


class MediaRepository(BaseRepository[MediaEntry]):
    """Repository for media entry operations."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(MediaEntry, db_session)
    
    async def get_by_external_id(self, external_id: int, external_source: str) -> Optional[MediaEntry]:
        """Get media by external ID and source."""
        # Using the query builder pattern
        query = self.query()
        query = query.join(MediaExternalIds)
        query = query.filter(getattr(MediaExternalIds, f"{external_source}_id") == external_id)
        
        return await query.first()
    
    async def search_media(
        self,
        query_text: Optional[str] = None,
        media_type: Optional[str] = None,
        status: Optional[str] = None,
        genres: Optional[List[str]] = None,
        year: Optional[int] = None,
        season: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MediaEntry]:
        """Search media entries with various filters."""
        # Using the new query builder pattern
        media_query = self.query()
        media_query = media_query.filter(MediaEntry.deleted_at.is_(None))
        
        # Apply filters
        if query_text:
            # Full text search using the title_search tsvector
            media_query = media_query.filter(
                func.to_tsvector('simple', func.unaccent(MediaEntry.title_search)).match(
                    func.unaccent(query_text)
                )
            )
        
        if media_type:
            media_query = media_query.filter(MediaEntry.media_type == media_type)
        
        if status:
            media_query = media_query.filter(MediaEntry.status == status)
        
        if year:
            media_query = media_query.filter(MediaEntry.season_year == year)
        
        if season:
            media_query = media_query.filter(MediaEntry.season == season)
        
        # Add genre filter if specified
        if genres:
            # Join with media_genres table
            media_query = media_query.join(MediaGenre)
            media_query = media_query.join(Genre)
            media_query = media_query.filter(Genre.name.in_(genres))
        
        # Apply pagination
        media_query = media_query.limit(limit).offset(offset)
        
        return await media_query.all()
    
    async def get_popular_media(self, media_type: Optional[str] = None, limit: int = 20) -> List[MediaEntry]:
        """Get popular media entries ordered by popularity."""
        media_query = self.query()
        media_query = media_query.filter(MediaEntry.deleted_at.is_(None))
        
        if media_type:
            media_query = media_query.filter(MediaEntry.media_type == media_type)
        
        media_query = media_query.order_by(desc(MediaEntry.popularity)).limit(limit)
        
        return await media_query.all()
    
    async def get_trending_media(self, media_type: Optional[str] = None, limit: int = 20) -> List[MediaEntry]:
        """Get trending media entries ordered by trending score."""
        media_query = self.query()
        media_query = media_query.filter(MediaEntry.deleted_at.is_(None))
        
        if media_type:
            media_query = media_query.filter(MediaEntry.media_type == media_type)
        
        media_query = media_query.order_by(desc(MediaEntry.trending)).limit(limit)
        
        return await media_query.all()
    
    async def get_by_title(self, title: str) -> Optional[MediaEntry]:
        """Get media by title."""
        media_query = self.query()
        media_query = media_query.filter(MediaEntry.title_romaji == title)
        media_query = media_query.filter(MediaEntry.deleted_at.is_(None))
        
        return await media_query.first()
    
    async def get_by_status(self, status: str, limit: int = 20) -> List[MediaEntry]:
        """Get media by status."""
        media_query = self.query()
        media_query = media_query.filter(MediaEntry.status == status)
        media_query = media_query.filter(MediaEntry.deleted_at.is_(None))
        media_query = media_query.limit(limit)
        
        return await media_query.all()