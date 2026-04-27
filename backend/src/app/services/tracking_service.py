"""Tracking service for managing user lists and progress tracking."""

from typing import List, Optional, Dict, Any
from sqlmodel import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from src.app.models import UserListEntry, ListEntryHistory, MediaEntry
from src.app.services.base_service import BaseService
from src.app.schemas.tracking import ListEntryCreate, ListEntryUpdate


class TrackingService(BaseService):
    """Service class for tracking-related operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)

    async def get_user_list_entry(self, user_id: UUID, media_id: UUID) -> Optional[UserListEntry]:
        """Get a user's list entry for a specific media."""
        statement = select(UserListEntry).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.media_id == media_id,
                UserListEntry.deleted_at.is_(None)
            )
        )
        result = await self.db_session.exec(statement)
        return result.one_or_none()

    async def get_user_list(self, user_id: UUID, status: Optional[str] = None,
                          media_type: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[UserListEntry]:
        """Get user's list entries with optional filtering."""
        statement = select(UserListEntry).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.deleted_at.is_(None)
            )
        )

        if status:
            statement = statement.where(UserListEntry.status == status)

        if media_type:
            # Join with media_entries to filter by media type
            statement = statement.join(MediaEntry).where(MediaEntry.media_type == media_type)

        statement = statement.offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()

    async def create_list_entry(self, entry_data: ListEntryCreate) -> UserListEntry:
        """Create a new list entry."""
        # Check if entry already exists
        existing_entry = await self.get_user_list_entry(entry_data.user_id, entry_data.media_id)
        if existing_entry:
            raise ValueError("Entry already exists for this user and media")

        entry = UserListEntry(**entry_data.model_dump())
        self.db_session.add(entry)

        # Create history entry
        history = ListEntryHistory(
            entry_id=entry.id,
            user_id=entry.user_id,
            media_id=entry.media_id,
            event_type="added",
            new_status=entry.status,
            new_progress=entry.progress,
            new_score=entry.score,
        )
        self.db_session.add(history)

        await self.db_session.commit()
        await self.db_session.refresh(entry)
        return entry

    async def update_list_entry(self, entry_id: UUID, entry_data: ListEntryUpdate) -> Optional[UserListEntry]:
        """Update a list entry."""
        entry = await self.get_user_list_entry(entry_data.user_id, entry_data.media_id)  # Assuming user_id and media_id are in the update
        if not entry:
            return None

        # Record the change in history
        history = ListEntryHistory(
            entry_id=entry_id,
            user_id=entry.user_id,
            media_id=entry.media_id,
            event_type="status_changed",
            old_status=entry.status,
            new_status=entry_data.status,
        )
        self.db_session.add(history)

        # Update entry
        for key, value in entry_data.model_dump(exclude_unset=True).items():
            setattr(entry, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(entry)
        return entry

    async def delete_list_entry(self, entry_id: UUID) -> bool:
        """Soft delete a list entry."""
        entry = await self.get_user_list_entry(entry_id)
        if not entry:
            return False

        entry.deleted_at = datetime.utcnow()
        await self.db_session.commit()
        return True

    async def get_list_entry_history(self, entry_id: UUID, limit: int = 20) -> List[ListEntryHistory]:
        """Get the history for a specific list entry."""
        statement = select(ListEntryHistory).where(ListEntryHistory.entry_id == entry_id)
        statement = statement.order_by(ListEntryHistory.created_at.desc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_user_activity_feed(self, user_id: UUID, limit: int = 20) -> List[ListEntryHistory]:
        """Get user's activity feed."""
        statement = select(ListEntryHistory).where(ListEntryHistory.user_id == user_id)
        statement = statement.order_by(ListEntryHistory.created_at.desc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_user_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's tracking statistics."""
        # Number of completed items by type
        statement = select(UserListEntry.media_type, func.count(UserListEntry.id)).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.status == "completed",
                UserListEntry.deleted_at.is_(None)
            )
        ).group_by(UserListEntry.media_type)

        result = await self.db_session.exec(statement)
        completed_by_type = dict(result.all())

        # Number of items in progress
        statement = select(func.count(UserListEntry.id)).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.status.in_(["watching", "reading", "rewatching", "rereading"]),
                UserListEntry.deleted_at.is_(None)
            )
        )

        result = await self.db_session.exec(statement)
        in_progress_count = result.one_or_none() or 0

        # Total items tracked
        statement = select(func.count(UserListEntry.id)).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.deleted_at.is_(None)
            )
        )

        result = await self.db_session.exec(statement)
        total_count = result.one_or_none() or 0

        return {
            "completed_by_type": completed_by_type,
            "in_progress_count": in_progress_count,
            "total_count": total_count
        }

    async def get_media_tracking_status(self, media_id: UUID, user_id: UUID) -> Optional[UserListEntry]:
        """Get current tracking status of a media for a specific user."""
        statement = select(UserListEntry).where(
            and_(
                UserListEntry.media_id == media_id,
                UserListEntry.user_id == user_id,
                UserListEntry.deleted_at.is_(None)
            )
        )
        result = await self.db_session.exec(statement)
        return result.one_or_none()
