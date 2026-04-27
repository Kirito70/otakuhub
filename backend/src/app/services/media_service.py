"""Media service for managing anime, manga, and other media entries."""

from typing import List, Optional, Dict, Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from src.app.models import MediaEntry, MediaExternalIds, Genre, Studio, Tag, MediaGenre, MediaStudio, MediaTag
from src.app.services.base_service import BaseService
from src.app.schemas.media import MediaDetailResponse
from src.app.repositories.media_repository import MediaRepository


class MediaService(BaseService):
    """Service class for media-related operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
        self._media_repository = MediaRepository(self.db_session)

    @property
    def media_repository(self) -> MediaRepository:
        """Get media repository instance."""
        return self._media_repository

    async def get_media_by_id(self, media_id: UUID) -> Optional[MediaEntry]:
        """Get a media entry by its ID."""
        return await self._media_repository.get_by_id(media_id)

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
        return await self._media_repository.search_media(
            query_text=query,
            media_type=media_type,
            status=status,
            genres=genres,
            year=year,
            season=season,
            limit=limit,
            offset=offset
        )

    async def get_media_detail(self, media_id: UUID) -> Optional[MediaDetailResponse]:
        """Get detailed media information including related data."""
        media = await self.get_media_by_id(media_id)
        if not media:
            return None

        # Get external IDs
        statement = select(MediaExternalIds).where(MediaExternalIds.media_id == media_id)
        external_ids = await self.db_session.exec(statement)
        external_ids_record = external_ids.one_or_none()

        # Get genres
        genre_statement = select(Genre).join(MediaGenre).where(MediaGenre.media_id == media_id)
        genre_result = await self.db_session.exec(genre_statement)
        genres = genre_result.all()

        # Get studios
        studio_statement = select(Studio).join(MediaStudio).where(MediaStudio.media_id == media_id)
        studio_result = await self.db_session.exec(studio_statement)
        studios = studio_result.all()

        # Get tags
        tag_statement = select(Tag).join(MediaTag).where(MediaTag.media_id == media_id)
        tag_result = await self.db_session.exec(tag_statement)
        tags = tag_result.all()

        # Convert to response schema
        return MediaDetailResponse(
            id=media.id,
            title_romaji=media.title_romaji,
            title_english=media.title_english,
            title_native=media.title_native,
            media_type=media.media_type,
            format=media.format,
            status=media.status,
            synopsis=media.synopsis,
            cover_image_large=media.cover_image_large,
            cover_image_medium=media.cover_image_medium,
            banner_image=media.banner_image,
            episode_count=media.episode_count,
            chapter_count=media.chapter_count,
            volume_count=media.volume_count,
            duration_minutes=media.duration_minutes,
            average_score=media.average_score,
            popularity=media.popularity,
            trending=media.trending,
            season=media.season,
            season_year=media.season_year,
            start_date=media.start_date,
            end_date=media.end_date,
            is_adult=media.is_adult,
            country_of_origin=media.country_of_origin,
            external_ids=external_ids_record,
            genres=genres,
            studios=studios,
            tags=tags,
            created_at=media.created_at,
            updated_at=media.updated_at,
        )

    async def get_related_media(self, media_id: UUID, relation_type: Optional[str] = None) -> List[MediaEntry]:
        """Get related media entries."""
        # Note: This is a simplified placeholder - the actual implementation
        # would need a proper relationship mapping
        return []

    async def get_popular_media(self, media_type: Optional[str] = None, limit: int = 20) -> List[MediaEntry]:
        """Get popular media entries ordered by popularity."""
        return await self._media_repository.get_popular_media(media_type=media_type, limit=limit)

    async def get_trending_media(self, media_type: Optional[str] = None, limit: int = 20) -> List[MediaEntry]:
        """Get trending media entries ordered by trending score."""
        return await self._media_repository.get_trending_media(media_type=media_type, limit=limit)

    async def create_media(self, media_data: Dict[str, Any]) -> MediaEntry:
        """Create a new media entry."""
        return await self._media_repository.create(media_data)

    async def update_media(self, media_id: UUID, media_data: Dict[str, Any]) -> Optional[MediaEntry]:
        """Update an existing media entry."""
        return await self._media_repository.update(media_id, media_data)

    async def delete_media(self, media_id: UUID) -> bool:
        """Soft delete a media entry."""
        media = await self.get_media_by_id(media_id)
        if not media:
            return False

        media.deleted_at = datetime.utcnow()
        await self.db_session.commit()
        return True

    async def get_by_external_id(self, external_id: int, external_source: str) -> Optional[MediaEntry]:
        """Get media by external ID and source."""
        return await self._media_repository.get_by_external_id(external_id, external_source)

    async def get_by_title(self, title: str) -> Optional[MediaEntry]:
        """Get media by title."""
        return await self._media_repository.get_by_title(title)

    async def get_by_status(self, status: str, limit: int = 20) -> List[MediaEntry]:
        """Get media by status."""
        return await self._media_repository.get_by_status(status, limit)
