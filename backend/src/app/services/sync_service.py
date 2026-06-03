"""Sync service for managing data synchronization from external APIs."""

from typing import List, Optional, Dict, Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC
from uuid import UUID, uuid4

from src.app.models import SyncJob, MediaEntry, MediaExternalIds, UserListEntry, Episode, Chapter, Notification
from src.app.models.enums import NotificationType, WatchStatus, MediaType
from src.app.services.base_service import BaseService


# ---- helper: parse raw AniList API response into normalized dict ----

def _parse_anilist_media(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw AniList GraphQL response into a MediaEntry-compatible dict.

    Mirrors the mapping contract from ADR 076 §2b / AniListSeedAdapter._parse_item.
    """
    def _parse_date(d: Any) -> datetime | None:
        if d and isinstance(d, dict) and d.get("year") and d.get("month") and d.get("day"):
            try:
                return datetime(d["year"], d["month"], d["day"])
            except (ValueError, TypeError):
                return None
        return None

    return {
        "title_romaji": raw.get("title", {}).get("romaji") or "",
        "title_english": raw.get("title", {}).get("english"),
        "title_native": raw.get("title", {}).get("native"),
        "media_type": raw.get("type", "").lower(),
        "format": raw.get("format"),
        "status": raw.get("status", "").lower() if raw.get("status") else "not_yet_released",
        "synopsis": raw.get("description"),
        "cover_image_large": raw.get("coverImage", {}).get("large"),
        "cover_image_medium": raw.get("coverImage", {}).get("medium"),
        "banner_image": raw.get("bannerImage"),
        "episode_count": raw.get("episodes"),
        "chapter_count": raw.get("chapters"),
        "volume_count": raw.get("volumes"),
        "duration_minutes": raw.get("duration"),
        "average_score": float(raw["averageScore"]) / 10.0 if raw.get("averageScore") else None,
        "popularity": raw.get("popularity"),
        "trending": raw.get("trending"),
        "season": raw.get("season", "").lower() if raw.get("season") else None,
        "season_year": raw.get("seasonYear"),
        "start_date": _parse_date(raw.get("startDate")),
        "end_date": _parse_date(raw.get("endDate")),
        "is_adult": raw.get("isAdult", False),
        "country_of_origin": raw.get("countryOfOrigin"),
        # Store the AniList ID separately so the upsert logic can use it
        "anilist_id": raw.get("id"),
    }


class SyncService(BaseService):
    """Service class for data synchronization operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)

    async def create_sync_job(self, job_type: str, user_id: Optional[UUID] = None,
                            total_items: Optional[int] = None) -> SyncJob:
        """Create a new sync job entry."""
        job = SyncJob(
            job_type=job_type,
            user_id=user_id,
            total_items=total_items,
            status="running"
        )
        self.db_session.add(job)
        await self.db_session.commit()
        await self.db_session.refresh(job)
        return job

    async def update_sync_job(self, job_id: UUID, updates: Dict[str, Any]) -> Optional[SyncJob]:
        """Update a sync job."""
        statement = select(SyncJob).where(SyncJob.id == job_id)
        result = await self.db_session.exec(statement)
        job = result.one_or_none()

        if not job:
            return None

        for key, value in updates.items():
            setattr(job, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(job)
        return job

    async def complete_sync_job(self, job_id: UUID) -> bool:
        """Mark a sync job as completed."""
        statement = select(SyncJob).where(SyncJob.id == job_id)
        result = await self.db_session.exec(statement)
        job = result.one_or_none()

        if not job:
            return False

        job.status = "completed"
        job.completed_at = datetime.now(UTC)
        await self.db_session.commit()
        return True

    async def get_sync_jobs(self, job_type: Optional[str] = None,
                          status: Optional[str] = None,
                          limit: int = 20) -> List[SyncJob]:
        """Get sync jobs with optional filtering."""
        statement = select(SyncJob).order_by(SyncJob.started_at.desc()).limit(limit)

        if job_type:
            statement = statement.where(SyncJob.job_type == job_type)

        if status:
            statement = statement.where(SyncJob.status == status)

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_recent_sync_jobs(self, limit: int = 10) -> List[SyncJob]:
        """Get recent sync jobs."""
        statement = select(SyncJob).order_by(SyncJob.started_at.desc()).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()

    async def get_recent_external_ids(self, external_id_type: str, limit: int = 50) -> List[MediaExternalIds]:
        """Get recent external IDs from a specific provider."""
        statement = select(MediaExternalIds).where(
            getattr(MediaExternalIds, f"{external_id_type}_id").is_not(None)
        ).order_by(MediaExternalIds.created_at.desc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def sync_media_from_anilist(self, media_type: Optional[str] = None,
                                     limit: int = 100) -> int:
        """Synchronize media data from AniList using the sync pipeline adapter."""
        from src.app.sync.sources.anilist import AniListSeedAdapter
        from src.app.sync.types import SeedExecutionContext

        # Create a sync job for observability
        job = await self.create_sync_job("anilist_sync", total_items=limit)

        try:
            context = SeedExecutionContext(
                source="anilist",
                job_id=str(job.id),
                limit=limit,
                only_unsynced=True,
            )
            adapter = AniListSeedAdapter()
            result = await adapter.run(context)

            # Update job status based on adapter result
            await self.update_sync_job(job.id, {
                "processed_items": result.processed_items,
                "failed_items": result.failed_items,
                "status": result.status,
                "completed_at": datetime.now(UTC),
            })

            return result.processed_items
        except Exception as e:
            # Mark job as failed
            await self.update_sync_job(job.id, {
                "status": "failed",
                "error_log": str(e),
                "completed_at": datetime.now(UTC),
            })
            raise

    async def backfill_missing_metadata(self, media_id: UUID) -> bool:
        """Backfill missing metadata for a media item using external APIs."""
        from src.app.sync.sources.anilist import AniListSeedAdapter
        from src.app.sync.sources.mangadex import MangaDexSeedAdapter
        from src.app.sync.types import SeedExecutionContext

        # Load media entry
        statement = select(MediaEntry).where(MediaEntry.id == media_id)
        result = await self.db_session.exec(statement)
        media = result.one_or_none()

        if not media:
            return False

        # Load external IDs
        stmt = select(MediaExternalIds).where(MediaExternalIds.media_id == media_id)
        result = await self.db_session.exec(stmt)
        ext_ids = result.one_or_none()

        if not ext_ids:
            return False

        # Determine which adapter to use
        if ext_ids.anilist_id and media.metadata_synced_at is None:
            context = SeedExecutionContext(
                source="backfill_anilist",
                job_id=str(uuid4()),
                limit=1,
                only_unsynced=True,
            )
            adapter = AniListSeedAdapter()
            adapter_result = await adapter.run(context)
            return adapter_result.processed_items > 0

        # For manga types, also try MangaDex
        manga_types = ("manga", "manhwa", "manhua", "light_novel", "novel")
        if ext_ids.mangadex_id and media.media_type in manga_types:
            context = SeedExecutionContext(
                source="backfill_mangadex",
                job_id=str(uuid4()),
                limit=1,
                only_unsynced=True,
            )
            adapter = MangaDexSeedAdapter()
            adapter_result = await adapter.run(context)
            return adapter_result.processed_items > 0

        # No applicable adapter — consider it already backfilled
        return True

    async def update_or_create_media_from_anilist(
        self, media_data: Dict[str, Any]
    ) -> MediaEntry:
        """Update or create a media entry and external IDs from raw AniList API data.

        Steps:
        1. Parse raw AniList response into a normalized dict
        2. Look up existing entry by anilist_id in media_external_ids
        3. Create new or update existing MediaEntry
        4. Create or update MediaExternalIds row
        5. Commit and return the MediaEntry
        """
        parsed = _parse_anilist_media(media_data)
        anilist_id = parsed.pop("anilist_id", None)

        if not anilist_id:
            raise ValueError("AniList data missing 'id' field; cannot upsert")

        # Look up by anilist_id
        stmt = select(MediaExternalIds).where(
            MediaExternalIds.anilist_id == anilist_id
        )
        result = await self.db_session.exec(stmt)
        existing_ext_ids = result.one_or_none()

        if existing_ext_ids:
            # Update existing MediaEntry
            stmt = select(MediaEntry).where(MediaEntry.id == existing_ext_ids.media_id)
            result = await self.db_session.exec(stmt)
            media = result.one_or_none()
            if not media:
                raise ValueError(
                    f"MediaExternalIds references media_id {existing_ext_ids.media_id} "
                    f"but MediaEntry not found"
                )

            for field, value in parsed.items():
                if value is not None and hasattr(media, field):
                    setattr(media, field, value)

            media.updated_at = datetime.now(UTC)
            media.metadata_synced_at = datetime.now(UTC)

            await self.db_session.commit()
            await self.db_session.refresh(media)
            return media
        else:
            # Create new MediaEntry
            create_fields = {k: v for k, v in parsed.items() if v is not None and hasattr(MediaEntry, k)}
            media = MediaEntry(**create_fields)
            media.metadata_synced_at = datetime.now(UTC)
            self.db_session.add(media)
            await self.db_session.flush()  # get media.id

            # Create MediaExternalIds row
            ext_ids = MediaExternalIds(
                media_id=media.id,
                anilist_id=anilist_id,
            )
            self.db_session.add(ext_ids)

            await self.db_session.commit()
            await self.db_session.refresh(media)
            return media
