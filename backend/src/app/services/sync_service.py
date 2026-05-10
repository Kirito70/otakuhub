"""Sync service for managing data synchronization from external APIs."""

from typing import List, Optional, Dict, Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from src.app.models import SyncJob, MediaEntry, MediaExternalIds
from src.app.services.base_service import BaseService
from src.app.external.anilist_client import AniListClient
from src.app.external.mangadex_client import MangaDexClient


class SyncService(BaseService):
    """Service class for data synchronization operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
        self.anilist_client = AniListClient()
        self.mangadex_client = MangaDexClient()

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
        job.completed_at = datetime.utcnow()
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
        """Synchronize media data from AniList."""
        # Create a sync job
        job = await self.create_sync_job("anilist_sync", total_items=limit)

        try:
            # In a real implementation, this would fetch media from AniList and update our database
            # This is a simplified placeholder

            count = 0
            # Add your sync logic here
            # For example:
            # media_list = await self.anilist_client.get_trending_media(media_type, limit)
            # for media_data in media_list:
            #     await self.update_or_create_media_from_anilist(media_data)
            #     count += 1

            # Update job status
            await self.update_sync_job(job.id, {
                "processed_items": count,
                "status": "completed",
                "completed_at": datetime.utcnow()
            })

            return count
        except Exception as e:
            # Mark job as failed
            await self.update_sync_job(job.id, {
                "status": "failed",
                "error_log": str(e),
                "completed_at": datetime.utcnow()
            })
            raise

    async def backfill_missing_metadata(self, media_id: UUID) -> bool:
        """Backfill missing metadata for a media item using external APIs."""
        statement = select(MediaEntry).where(MediaEntry.id == media_id)
        result = await self.db_session.exec(statement)
        media = result.one_or_none()

        if not media:
            return False

        try:
            # In a real implementation, this would fetch missing data from external APIs
            # and update the media entry

            # Placeholder logic:
            # If needed, update external IDs, etc.
            return True
        except Exception as e:
            print(f"Error backfilling metadata: {e}")
            return False

    async def update_or_create_media_from_anilist(self, media_data: Dict[str, Any]) -> MediaEntry:
        """Update or create a media entry from AniList data."""
        # This would be implemented to:
        # 1. Check if media exists by AniList ID
        # 2. Update if exists or create new entry
        # 3. Update external IDs table

        # Placeholder - this would be fully implemented in a real system
        return MediaEntry(**media_data)
