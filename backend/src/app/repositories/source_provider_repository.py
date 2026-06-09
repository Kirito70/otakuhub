"""Repositories for ADR 078 provider/source mappings and episodes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.models.media_source_episode import MediaSourceEpisode
from src.app.models.media_source_mapping import MediaSourceMapping
from src.app.repositories.base_repository import BaseRepository
from src.app.schemas.source_provider import SourceEpisodeUpsert, SourceMappingUpsert


def utc_now() -> datetime:
    return datetime.utcnow()


class SourceMappingRepository(BaseRepository[MediaSourceMapping]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(MediaSourceMapping, db_session)

    async def get_by_source_media_id(self, *, source: str, source_media_id: str) -> MediaSourceMapping | None:
        return await self.query().filter(MediaSourceMapping.source == source).filter(
            MediaSourceMapping.source_media_id == source_media_id
        ).first()

    async def list_by_source(self, *, source: str, limit: int = 100, offset: int = 0) -> list[MediaSourceMapping]:
        return await self.query().filter(MediaSourceMapping.source == source).offset(offset).limit(limit).all()

    async def upsert(self, payload: SourceMappingUpsert) -> MediaSourceMapping:
        now = utc_now()
        existing = await self.get_by_source_media_id(source=payload.source, source_media_id=payload.source_media_id)
        values = payload.model_dump()
        if existing is None:
            mapping = MediaSourceMapping(**values, first_seen_at=now, last_seen_at=now, created_at=now, updated_at=now)
            self.db_session.add(mapping)
            await self.db_session.commit()
            await self.db_session.refresh(mapping)
            return mapping

        for key, value in values.items():
            if key == "media_id" and value is None and existing.media_id is not None:
                continue
            setattr(existing, key, value)
        existing.last_seen_at = now
        existing.updated_at = now
        existing.deleted_at = None
        await self.db_session.commit()
        await self.db_session.refresh(existing)
        return existing

    async def get_mappings_by_media(self, *, media_id: UUID) -> list[MediaSourceMapping]:
        """Get all non-deleted source mappings for a media entry."""
        return await self.query().filter(MediaSourceMapping.media_id == media_id).all()

    async def list_all_with_filters(
        self,
        *,
        source: str | None = None,
        mapping_status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MediaSourceMapping]:
        """List all non-deleted source mappings with optional filters."""
        q = self.query()
        if source is not None:
            q = q.filter(MediaSourceMapping.source == source)
        if mapping_status is not None:
            q = q.filter(MediaSourceMapping.mapping_status == mapping_status)
        q = q.order_by(MediaSourceMapping.last_seen_at.desc())
        return await q.offset(offset).limit(limit).all()

    async def count_all_with_filters(
        self,
        *,
        source: str | None = None,
        mapping_status: str | None = None,
    ) -> int:
        """Count all non-deleted source mappings with optional filters."""
        q = self.query()
        if source is not None:
            q = q.filter(MediaSourceMapping.source == source)
        if mapping_status is not None:
            q = q.filter(MediaSourceMapping.mapping_status == mapping_status)
        return await q.count()

    async def mark_stale_not_seen_since(self, *, source: str, cutoff: datetime) -> int:
        result = await self.db_session.exec(
            select(MediaSourceMapping).where(
                MediaSourceMapping.source == source,
                MediaSourceMapping.deleted_at.is_(None),
                MediaSourceMapping.last_seen_at < cutoff,
            )
        )
        rows = result.all()
        for row in rows:
            row.mapping_status = "stale"
            row.updated_at = utc_now()
        await self.db_session.commit()
        return len(rows)


class SourceEpisodeRepository(BaseRepository[MediaSourceEpisode]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(MediaSourceEpisode, db_session)

    async def get_by_source_episode_id(self, *, source: str, source_episode_id: str, language: str) -> MediaSourceEpisode | None:
        return await self.query().filter(MediaSourceEpisode.source == source).filter(
            MediaSourceEpisode.source_episode_id == source_episode_id
        ).filter(MediaSourceEpisode.language == language).first()

    async def list_for_mapping(self, *, mapping_id: UUID) -> list[MediaSourceEpisode]:
        return await self.query().filter(MediaSourceEpisode.mapping_id == mapping_id).all()

    async def get_episodes_by_media(
        self, *, media_id: UUID
    ) -> list[MediaSourceEpisode]:
        """Get all non-deleted source episodes for a media entry.

        Joins through media_source_mappings to find all episodes across
        all providers for this media.
        """
        result = await self.db_session.exec(
            select(MediaSourceEpisode)
            .join(
                MediaSourceMapping,
                and_(
                    MediaSourceEpisode.mapping_id == MediaSourceMapping.id,
                    MediaSourceMapping.deleted_at.is_(None),
                ),
            )
            .where(
                MediaSourceMapping.media_id == media_id,
                MediaSourceEpisode.deleted_at.is_(None),
                MediaSourceEpisode.is_available.is_(True),
            )
        )
        return result.all()

    async def upsert(self, payload: SourceEpisodeUpsert) -> MediaSourceEpisode:
        now = utc_now()
        existing = await self.get_by_source_episode_id(
            source=payload.source,
            source_episode_id=payload.source_episode_id,
            language=payload.language,
        )
        values = payload.model_dump()
        if existing is None:
            episode = MediaSourceEpisode(**values, first_seen_at=now, last_seen_at=now, created_at=now, updated_at=now)
            self.db_session.add(episode)
            await self.db_session.commit()
            await self.db_session.refresh(episode)
            return episode

        for key, value in values.items():
            if key == "media_id" and value is None and existing.media_id is not None:
                continue
            setattr(existing, key, value)
        existing.is_available = payload.is_available
        existing.last_seen_at = now
        existing.updated_at = now
        existing.deleted_at = None
        await self.db_session.commit()
        await self.db_session.refresh(existing)
        return existing
