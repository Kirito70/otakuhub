"""Tracking service for managing user lists and progress tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.models import CustomList, CustomListEntry, ListEntryHistory, MediaEntry, UserListEntry
from src.app.services.base_service import BaseService
from src.app.repositories.tracking_repository import (
    UserListEntryRepository,
    ListEntryHistoryRepository,
    CustomListRepository,
    CustomListEntryRepository,
)
from src.app.schemas.tracking import (
    CustomListCreate,
    CustomListEntriesReplaceRequest,
    ListEntryCreate,
    ListEntryUpdate,
)


class TrackingService(BaseService):
    """Service class for tracking-related operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
        self._entry_repo = UserListEntryRepository(self.db_session)
        self._history_repo = ListEntryHistoryRepository(self.db_session)
        self._custom_list_repo = CustomListRepository(self.db_session)
        self._custom_entry_repo = CustomListEntryRepository(self.db_session)

    async def get_user_list_entry(self, user_id: UUID, media_id: UUID) -> Optional[UserListEntry]:
        """Get a user's list entry for a specific media."""
        return await self._entry_repo.get_by_user_and_media(user_id, media_id)

    async def get_user_list(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        media_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UserListEntry]:
        """Get user's list entries with optional filtering."""
        if media_type:
            # media_type filter requires a join — use raw query
            statement = (
                select(UserListEntry)
                .join(MediaEntry, MediaEntry.id == UserListEntry.media_id)
                .where(
                    UserListEntry.user_id == user_id,
                    UserListEntry.deleted_at.is_(None),
                    MediaEntry.media_type == media_type,
                )
            )
            if status:
                statement = statement.where(UserListEntry.status == status)
            statement = statement.order_by(UserListEntry.updated_at.desc()).offset(offset).limit(limit)
            result = await self.db_session.exec(statement)
            return result.all()

        return await self._entry_repo.get_user_list(user_id, status=status, limit=limit, offset=offset)

    async def create_list_entry(self, user_id: UUID, entry_data: ListEntryCreate) -> UserListEntry:
        """Create a new list entry for the current user."""
        existing_entry = await self._entry_repo.get_by_user_and_media(user_id, entry_data.media_id)
        if existing_entry:
            raise ValueError("Entry already exists for this user and media")

        payload = entry_data.model_dump()
        payload["user_id"] = user_id
        entry = UserListEntry(**payload)
        self.db_session.add(entry)

        await self.db_session.flush()

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

    async def update_list_entry(self, user_id: UUID, media_id: UUID, entry_data: ListEntryUpdate) -> Optional[UserListEntry]:
        """Update a list entry by media ID for the current user."""
        entry = await self._entry_repo.get_by_user_and_media(user_id, media_id)
        if not entry:
            return None

        changes = entry_data.model_dump(exclude_unset=True)
        if not changes:
            return entry

        if "status" in changes:
            event_type = "status_changed"
        elif "progress" in changes:
            event_type = "progress_updated"
        elif "score" in changes:
            event_type = "score_set"
        else:
            event_type = "updated"

        history = ListEntryHistory(
            entry_id=entry.id,
            user_id=entry.user_id,
            media_id=entry.media_id,
            event_type=event_type,
            old_status=entry.status,
            old_progress=entry.progress,
            old_score=entry.score,
            new_status=changes.get("status", entry.status),
            new_progress=changes.get("progress", entry.progress),
            new_score=changes.get("score", entry.score),
        )
        self.db_session.add(history)

        for key, value in changes.items():
            setattr(entry, key, value)
        entry.updated_at = datetime.utcnow()

        await self.db_session.commit()
        await self.db_session.refresh(entry)
        return entry

    async def delete_list_entry(self, user_id: UUID, media_id: UUID) -> bool:
        """Soft delete a list entry by media ID for current user."""
        entry = await self._entry_repo.get_by_user_and_media(user_id, media_id)
        if not entry:
            return False

        entry.deleted_at = datetime.utcnow()
        entry.updated_at = datetime.utcnow()
        self.db_session.add(
            ListEntryHistory(
                entry_id=entry.id,
                user_id=entry.user_id,
                media_id=entry.media_id,
                event_type="removed",
                old_status=entry.status,
                old_progress=entry.progress,
                old_score=entry.score,
            )
        )
        await self.db_session.commit()
        return True

    async def get_list_entry_history(self, entry_id: UUID, limit: int = 20) -> List[ListEntryHistory]:
        """Get the history for a specific list entry."""
        q = (
            self._history_repo.query()
            .filter(ListEntryHistory.entry_id == entry_id)
            .order_by(ListEntryHistory.created_at.desc())
            .limit(limit)
        )
        return await q.all()

    async def get_user_activity_feed(self, user_id: UUID, limit: int = 20) -> List[ListEntryHistory]:
        """Get user's activity feed."""
        return await self._history_repo.get_for_user(user_id, limit=limit)

    async def get_user_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's tracking statistics."""
        stats = await self._entry_repo.get_statistics(user_id)
        return {
            "completed_count": stats.get("completed", 0),
            "in_progress_count": stats.get("watching", 0),
            "total_count": stats.get("total", 0),
        }

    async def create_custom_list(self, user_id: UUID, payload: CustomListCreate) -> CustomList:
        """Create a custom list for the current user."""
        data = payload.model_dump()
        data["user_id"] = user_id
        return await self._custom_list_repo.create(data)

    async def replace_custom_list_entries(
        self,
        user_id: UUID,
        list_id: UUID,
        payload: CustomListEntriesReplaceRequest,
    ) -> Optional[int]:
        """Replace all entries in a custom list owned by current user."""
        custom_list = await self._custom_list_repo.get_by_id(list_id)
        if not custom_list or custom_list.user_id != user_id:
            return None

        await self._custom_entry_repo.replace_entries(
            list_id,
            [e.media_id for e in payload.entries],
        )
        custom_list.updated_at = datetime.utcnow()
        await self.db_session.commit()
        return len(payload.entries)

    async def get_media_tracking_status(self, media_id: UUID, user_id: UUID) -> Optional[UserListEntry]:
        """Get current tracking status of a media for a specific user."""
        return await self._entry_repo.get_by_user_and_media(user_id, media_id)
