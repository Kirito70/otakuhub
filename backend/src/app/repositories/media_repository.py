"""Repository for media-related database operations."""

from typing import List, Optional
from sqlmodel import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.app.models import MediaEntry, MediaExternalIds, Genre, Studio, Tag
from src.app.repositories.base_repository import BaseRepository


class MediaRepository(BaseRepository[MediaEntry]):
    """Repository for media entry operations."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(MediaEntry, db_session)
    
    async def get_by_external_id(self, external_id: int, external_source: str) -> Optional[MediaEntry]:
        """Get media by external ID and source."""
        statement = select(MediaEntry).join(MediaExternalIds).where(
            getattr(MediaExternalIds, f"{external_source}_id") == external_id
        )
        result = await self.db_session.exec(statement)
        return result.one_or_none()
    
    async def search_media(
        self,
        query: Optional[str] = None,
        media_type: Optional[str] = None,
        status: Optional[str] = None,
        genres: Optional[List[str]] = None,
        year: Optional[int] = None,
        season: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MediaEntry]:
        """Search media entries with various filters."""
        statement = select(MediaEntry).where(MediaEntry.deleted_at.is_(None))
        
        # Apply filters
        if query:
            # Full text search using the title_search tsvector
            statement = statement.where(
                func.to_tsvector('simple', func.unaccent(MediaEntry.title_search)).match(
                    func.unaccent(query)
                )
            )
        
        if media_type:
            statement = statement.where(MediaEntry.media_type == media_type)
        
        if status:
            statement = statement.where(MediaEntry.status == status)
        
        if year:
            statement = statement.where(MediaEntry.season_year == year)
        
        if season:
            statement = statement.where(MediaEntry.season == season)
        
        # Add genre filter if specified
        if genres:
            # This requires joining with media_genres table
            statement = statement.join(MediaEntry).join(Genre).where(Genre.name.in_(genres))
        
        # Apply pagination
        statement = statement.offset(offset).limit(limit)
        
        result = await self.db_session.exec(statement)
        return result.all()
    
    async def get_popular_media(self, media_type: Optional[str] = None, limit: int = 20) -> List[MediaEntry]:
        """Get popular media entries ordered by popularity."""
        statement = select(MediaEntry).where(MediaEntry.deleted_at.is_(None))
        
        if media_type:
            statement = statement.where(MediaEntry.media_type == media_type)
        
        statement = statement.order_by(MediaEntry.popularity.desc()).limit(limit)
        
        result = await self.db_session.exec(statement)
        return result.all()
    
    async def get_trending_media(self, media_type: Optional[str] = None, limit: int = 20) -> List[MediaEntry]:
        """Get trending media entries ordered by trending score."""
        statement = select(MediaEntry).where(MediaEntry.deleted_at.is_(None))
        
        if media_type:
            statement = statement.where(MediaEntry.media_type == media_type)
        
        statement = statement.order_by(MediaEntry.trending.desc()).limit(limit)
        
        result = await self.db_session.exec(statement)
        return result.all()