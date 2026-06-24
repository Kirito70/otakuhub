"""Media service for managing anime, manga, and other media entries."""

from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from src.app.models import MediaEntry, MediaExternalIds, Genre, Studio, Tag, MediaGenre, MediaStudio, MediaTag, Episode, RelatedMedia
from src.app.services.base_service import BaseService
from src.app.schemas.media import (
    MediaDetailResponse,
    AiringEpisodeItem,
    AiringResponse,
    RelatedMediaItem,
    EpisodeItem,
    EpisodeListResponse,
    ChapterItem,
    ChapterListResponse,
    GenreItem,
    GenreListResponse,
    SeasonalMediaItem,
    SeasonalResponse,
)
from src.app.schemas.home import (
    HomeData,
    HomeSpotlightItem,
    HomeContinueItem,
    HomeFriendRecItem,
    HomeGroupWatchingItem,
    HomeAiringSoonItem,
    HomeTrendingItem,
    GenreRailItem,
    GenreRail,
    MediaTypeSection,
)
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

    async def get_home_data(self, user_id: UUID) -> HomeData:
        """Get the composite home page payload.

        Returns a ``HomeData`` with:
        - ``spotlight`` — top trending media across all types
        - ``media_type_sections`` — genre-based rails per media type
        """
        # --- Spotlight: top trending ---
        trending = await self._media_repository.get_trending_media(limit=10)
        spotlight: list[HomeSpotlightItem] = [
            HomeSpotlightItem(
                id=m.id,
                title_romaji=m.title_romaji,
                title_english=m.title_english,
                format=m.format.value if m.format else None,
                season_year=m.season_year,
                average_score=m.average_score,
                synopsis=m.synopsis,
                cover_image_large=m.cover_image_large,
                banner_image=m.banner_image,
                media_type=m.media_type.value if m.media_type else None,
            )
            for m in trending
        ]

        # --- Genre-based browse sections ---
        media_types = ["anime", "manga", "manhwa"]
        sections: list[MediaTypeSection] = []

        for mt in media_types:
            genre_data = await self._media_repository.get_genre_rails_for_type(
                media_type=mt, max_genres=8, items_per_genre=10
            )
            genre_rails: list[GenreRail] = []
            for genre_id, genre_name, items in genre_data:
                rail_items = [
                    GenreRailItem(
                        id=m.id,
                        title_romaji=m.title_romaji,
                        title_english=m.title_english,
                        cover_image_large=m.cover_image_large,
                        average_score=m.average_score,
                        format=m.format.value if m.format else None,
                    )
                    for m in items
                ]
                genre_rails.append(
                    GenreRail(
                        genre_id=genre_id,
                        genre_name=genre_name,
                        items=rail_items,
                    )
                )

            sections.append(
                MediaTypeSection(
                    media_type=mt,
                    media_type_label=mt.capitalize(),
                    genre_rails=genre_rails,
                )
            )

        return HomeData(
            spotlight=spotlight,
            media_type_sections=sections,
        )

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

    async def get_related_media(
        self,
        media_id: UUID,
        relation_type: Optional[str] = None,
    ) -> List[RelatedMediaItem]:
        """Get related media entries with relation type from the related_media table."""
        statement = (
            select(MediaEntry, RelatedMedia.relation_type)
            .join(RelatedMedia, RelatedMedia.related_media_id == MediaEntry.id)
            .where(
                RelatedMedia.source_media_id == media_id,
                MediaEntry.deleted_at.is_(None),
            )
        )
        if relation_type is not None:
            statement = statement.where(RelatedMedia.relation_type == relation_type)

        statement = statement.order_by(RelatedMedia.created_at.asc())
        result = await self.db_session.exec(statement)
        rows = result.all()

        return [
            RelatedMediaItem(
                id=media.id,
                title_romaji=media.title_romaji,
                title_english=media.title_english,
                cover_image_medium=media.cover_image_medium,
                media_type=media.media_type.value if hasattr(media.media_type, "value") else str(media.media_type),
                relation_type=rt.value if hasattr(rt, "value") else str(rt),
            )
            for media, rt in rows
        ]

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
        """Soft delete a media entry (delegates to repository)."""
        return await self._media_repository.delete(media_id)

    async def get_by_external_id(self, external_id: int, external_source: str) -> Optional[MediaEntry]:
        """Get media by external ID and source."""
        return await self._media_repository.get_by_external_id(external_id, external_source)

    async def get_by_title(self, title: str) -> Optional[MediaEntry]:
        """Get media by title."""
        return await self._media_repository.get_by_title(title)

    async def get_by_status(self, status: str, limit: int = 20) -> List[MediaEntry]:
        """Get media by status."""
        return await self._media_repository.get_by_status(status, limit)

    async def get_airing_schedule(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        media_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> AiringResponse:
        """Get airing schedule with media metadata."""
        items, total = await self._media_repository.get_airing_schedule(
            start_date=start_date,
            end_date=end_date,
            media_type=media_type,
            limit=limit,
            offset=offset
        )

        episode_items = [
            AiringEpisodeItem(
                id=episode.id,
                media_id=media.id,
                media_title=media.title_romaji,
                media_cover=media.cover_image_medium,
                media_type=media.media_type,
                episode_number=episode.episode_number,
                title=episode.title,
                air_date=episode.air_date,
                duration_minutes=episode.duration_minutes,
            )
            for episode, media in items
        ]

        return AiringResponse(
            items=episode_items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_seasonal_media(
        self,
        season_year: int,
        season: str,
        limit: int = 20,
        offset: int = 0,
    ) -> SeasonalResponse:
        """Get seasonal media entries ordered by average score descending."""
        from datetime import datetime

        if season_year is None:
            season_year = datetime.utcnow().year
        if season is None:
            month = datetime.utcnow().month
            if month in (3, 4, 5):
                season = "spring"
            elif month in (6, 7, 8):
                season = "summer"
            elif month in (9, 10, 11):
                season = "fall"
            else:
                season = "winter"

        items, total = await self._media_repository.get_seasonal_media(
            season_year=season_year,
            season=season,
            limit=limit,
            offset=offset,
        )

        media_items = [SeasonalMediaItem.model_validate(m) for m in items]

        return SeasonalResponse(
            items=media_items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_genres(self) -> GenreListResponse:
        """Get all genres ordered by name."""
        genres = await self._media_repository.get_genres()
        items = [GenreItem.model_validate(g) for g in genres]
        return GenreListResponse(items=items)

    async def get_episodes(
        self,
        media_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> EpisodeListResponse:
        """Get canonical episodes for a media entry, ordered by number."""
        items, total = await self._media_repository.get_episodes_by_media_id(
            media_id=media_id,
            limit=limit,
            offset=offset,
        )

        episode_items = [
            EpisodeItem(
                id=ep.id,
                episode_number=ep.episode_number,
                title=ep.title,
                air_date=ep.air_date,
                duration_minutes=ep.duration_minutes,
                thumbnail_url=ep.thumbnail_url,
            )
            for ep in items
        ]

        return EpisodeListResponse(
            items=episode_items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_chapters(
        self,
        media_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> ChapterListResponse:
        """Get canonical chapters for a media entry, ordered by number."""
        items, total = await self._media_repository.get_chapters_by_media_id(
            media_id=media_id,
            limit=limit,
            offset=offset,
        )

        chapter_items = [
            ChapterItem(
                id=ch.id,
                chapter_number=ch.chapter_number,
                volume_number=ch.volume_number,
                title=ch.title,
                published_at=ch.published_at,
                mangadex_chapter_id=ch.mangadex_chapter_id,
            )
            for ch in items
        ]

        return ChapterListResponse(
            items=chapter_items,
            total=total,
            limit=limit,
            offset=offset,
        )
