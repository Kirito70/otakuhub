"""Repository for media-related database operations."""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import desc, or_, and_
from sqlmodel import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import MediaEntry, MediaExternalIds, Genre, MediaGenre, Episode, Chapter
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
            # Cross-dialect search: uses ILIKE which works on both SQLite and PostgreSQL.
            # On PostgreSQL, trigram indexes (from FTS migration) make ILIKE fast.
            search_pattern = f"%{query_text}%"
            media_query = media_query.filter(
                or_(
                    MediaEntry.title_romaji.ilike(search_pattern),
                    MediaEntry.title_english.ilike(search_pattern),
                    MediaEntry.title_native.ilike(search_pattern),
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

    async def get_airing_schedule(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        media_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Tuple[Episode, MediaEntry]], int]:
        """Get airing schedule episodes with media metadata.

        Returns a tuple of (items, total_count).
        Each item is a tuple of (Episode, MediaEntry).
        """
        from datetime import datetime as dt

        now = dt.utcnow()

        # Default time window: today to 7 days from now
        if start_date is None:
            start_date = now
        if end_date is None:
            end_date = dt(now.year + 1, 12, 31)  # Far future default

        # Build base query for episodes joined with media_entries
        statement = (
            select(Episode, MediaEntry)
            .join(MediaEntry, Episode.media_id == MediaEntry.id)
            .where(Episode.air_date >= start_date)
            .where(Episode.air_date <= end_date)
            .where(MediaEntry.deleted_at.is_(None))
            .order_by(Episode.air_date.asc())
        )

        if media_type:
            statement = statement.where(MediaEntry.media_type == media_type)

        # Get total count first
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.db_session.exec(count_statement)
        total = count_result.one() or 0

        # Apply pagination
        paginated = statement.limit(limit).offset(offset)

        result = await self.db_session.exec(paginated)
        items = result.all()

        return items, total

    async def get_seasonal_media(
        self,
        season_year: int,
        season: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[MediaEntry], int]:
        """Get seasonal media entries ordered by average score descending."""
        from sqlmodel import and_

        # Get total count
        count_query = (
            self.query()
            .filter(MediaEntry.season_year == season_year)
            .filter(MediaEntry.season == season)
        )
        total = await count_query.count()

        # Get paginated results ordered by score
        items_query = (
            self.query()
            .filter(MediaEntry.season_year == season_year)
            .filter(MediaEntry.season == season)
            .order_by(desc(MediaEntry.average_score))
            .nulls_last()
            .offset(offset)
            .limit(limit)
        )

        items = await items_query.all()
        return items, total

    async def get_genre_rails_for_type(
        self,
        media_type: str,
        max_genres: int = 8,
        items_per_genre: int = 10,
    ) -> List[tuple]:
        """Get top genres and their media entries for a given media type.

        Returns a list of (genre_id, genre_name, list[MediaEntry]) for the
        ``max_genres`` most-populated genres ordered by popularity descending.
        """
        from sqlalchemy import func as sa_func, desc as sa_desc

        # Step 1 — top genres by media count for this media type
        genre_count_stmt = (
            select(
                Genre.id,
                Genre.name,
                sa_func.count(MediaGenre.media_id).label("cnt"),
            )
            .join(MediaGenre, Genre.id == MediaGenre.genre_id)
            .join(MediaEntry, MediaGenre.media_id == MediaEntry.id)
            .where(MediaEntry.media_type == media_type)
            .where(MediaEntry.deleted_at.is_(None))
            .group_by(Genre.id, Genre.name)
            .order_by(sa_desc("cnt"))
            .limit(max_genres)
        )

        genre_rows = (await self.db_session.exec(genre_count_stmt)).all()

        result: list[tuple] = []
        for genre_id, genre_name, _ in genre_rows:
            media_stmt = (
                select(MediaEntry)
                .join(MediaGenre, MediaEntry.id == MediaGenre.media_id)
                .where(MediaGenre.genre_id == genre_id)
                .where(MediaEntry.media_type == media_type)
                .where(MediaEntry.deleted_at.is_(None))
                .order_by(sa_desc(MediaEntry.popularity))
                .limit(items_per_genre)
            )
            media_items = (await self.db_session.exec(media_stmt)).all()
            result.append((genre_id, genre_name, list(media_items)))

        return result

    async def get_genres(self) -> List[Genre]:
        """Get all genres ordered by name."""
        statement = select(Genre).order_by(Genre.name.asc())
        result = await self.db_session.exec(statement)
        return list(result.all())

    async def get_chapters_by_media_id(
        self,
        media_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Chapter], int]:
        """Get canonical chapters for a media entry ordered by chapter number.

        Returns (items, total_count). Chapters are sorted ascending by number.
        """
        statement = (
            select(Chapter)
            .where(Chapter.media_id == media_id)
            .order_by(Chapter.chapter_number.asc())
        )

        # Total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.db_session.exec(count_statement)
        total = count_result.one() or 0

        # Apply pagination
        paginated = statement.limit(limit).offset(offset)
        result = await self.db_session.exec(paginated)
        items = result.all()

        return items, total

    async def get_episodes_by_media_id(
        self,
        media_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Episode], int]:
        """Get canonical episodes for a media entry ordered by episode number.

        Returns (items, total_count). Episodes are sorted ascending by number.
        """
        statement = (
            select(Episode)
            .where(Episode.media_id == media_id)
            .order_by(Episode.episode_number.asc())
        )

        # Total count
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.db_session.exec(count_statement)
        total = count_result.one() or 0

        # Apply pagination
        paginated = statement.limit(limit).offset(offset)
        result = await self.db_session.exec(paginated)
        items = result.all()

        return items, total
