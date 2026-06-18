"""Repositories for ADR 078 provider/source mappings and episodes."""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, insert as sa_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.models.media_source_episode import MediaSourceEpisode
from src.app.models.media_source_mapping import MediaSourceMapping
from src.app.repositories.base_repository import BaseRepository
from src.app.schemas.source_provider import SourceEpisodeUpsert, SourceMappingUpsert

_logger = logging.getLogger(__name__)


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

    async def upsert(self, payload: SourceMappingUpsert, *, commit: bool = True) -> MediaSourceMapping:
        now = utc_now()
        existing = await self.get_by_source_media_id(source=payload.source, source_media_id=payload.source_media_id)
        values = payload.model_dump()
        if existing is None:
            mapping = MediaSourceMapping(**values, first_seen_at=now, last_seen_at=now, created_at=now, updated_at=now)
            self.db_session.add(mapping)
            if commit:
                await self.db_session.commit()
                await self.db_session.refresh(mapping)
            else:
                await self.db_session.flush()
                await self.db_session.refresh(mapping)
            return mapping

        for key, value in values.items():
            if key == "media_id" and value is None and existing.media_id is not None:
                continue
            setattr(existing, key, value)
        existing.last_seen_at = now
        existing.updated_at = now
        existing.deleted_at = None
        if commit:
            await self.db_session.commit()
            await self.db_session.refresh(existing)
        else:
            await self.db_session.flush()
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

    async def bulk_upsert_episodes(
        self,
        *,
        mapping_id: UUID,
        media_id: UUID | None,
        episodes_data: list[SourceEpisodeUpsert],
        source: str,
        now: datetime | None = None,
    ) -> int:
        """True SQL bulk upsert — one SELECT + one INSERT for all rows.

        1. Fetch ALL existing episodes for this mapping in a single SELECT.
        2. Partition into *new* (insert) and *existing* (update).
        3. Insert new rows via ``INSERT INTO ... VALUES (...), (...)``.
        4. Update existing rows in bulk (setattr loop, usually <50).

        On PostgreSQL the INSERT uses ``ON CONFLICT DO UPDATE`` so it's safe
        against concurrent inserts.  On SQLite it's a plain multi-row INSERT.
        """
        now = now or utc_now()
        if not episodes_data:
            return 0

        # 1. Single fetch of existing episodes for this mapping
        unique_keys = {(e.source_episode_id, e.language) for e in episodes_data}
        result = await self.db_session.exec(
            select(MediaSourceEpisode).where(
                MediaSourceEpisode.mapping_id == mapping_id,
                MediaSourceEpisode.deleted_at.is_(None),
                MediaSourceEpisode.source_episode_id.in_([k[0] for k in unique_keys]),
            )
        )
        existing_rows = result.all()
        existing_lookup: dict[tuple[str, str], MediaSourceEpisode] = {}
        for row in existing_rows:
            existing_lookup[(row.source_episode_id, row.language)] = row

        # 2. Partition into new vs existing
        new_values: list[dict] = []
        update_count = 0
        for payload in episodes_data:
            key = (payload.source_episode_id, payload.language)
            existing = existing_lookup.get(key)
            values = payload.model_dump()
            values["mapping_id"] = mapping_id
            values["media_id"] = media_id

            if existing is None:
                values["first_seen_at"] = now
                values["last_seen_at"] = now
                values["created_at"] = now
                values["updated_at"] = now
                new_values.append(values)
            else:
                for k, v in values.items():
                    if k == "media_id" and v is None and existing.media_id is not None:
                        continue
                    setattr(existing, k, v)
                existing.is_available = payload.is_available
                existing.last_seen_at = now
                existing.updated_at = now
                existing.deleted_at = None
                update_count += 1

        # 3. Bulk insert all new rows in one statement
        if new_values:
            is_pg = "postgresql" in (self.db_session.bind.dialect.name if self.db_session.bind else "")
            if is_pg:
                stmt = pg_insert(MediaSourceEpisode).values(new_values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["source", "source_episode_id", "language"],
                    set_={
                        c.key: stmt.excluded[c.key]
                        for c in MediaSourceEpisode.__table__.columns
                        if c.key not in ("id", "created_at", "first_seen_at", "deleted_at")
                        and c.key in values
                    },
                )
                await self.db_session.execute(stmt)
            else:
                await self.db_session.execute(sa_insert(MediaSourceEpisode).values(new_values))
            _logger.debug("bulk_upsert_episodes: inserted=%d updated=%d", len(new_values), update_count)

        # 4. Single commit for all changes
        await self.db_session.commit()
        return len(new_values) + update_count

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
