"""Tracking service for managing user lists and progress tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.models import CustomList, CustomListEntry, ListEntryHistory, MediaEntry, UserListEntry
from src.app.services.base_service import BaseService
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

    async def get_user_list_entry(self, user_id: UUID, media_id: UUID) -> Optional[UserListEntry]:
        """Get a user's list entry for a specific media."""
        statement = select(UserListEntry).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.media_id == media_id,
                UserListEntry.deleted_at.is_(None),
            )
        )
        result = await self.db_session.exec(statement)
        return result.one_or_none()

    async def get_user_list(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        media_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UserListEntry]:
        """Get user's list entries with optional filtering."""
        statement = select(UserListEntry).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.deleted_at.is_(None),
            )
        )

        if status:
            statement = statement.where(UserListEntry.status == status)

        if media_type:
            statement = statement.join(MediaEntry, MediaEntry.id == UserListEntry.media_id).where(
                MediaEntry.media_type == media_type
            )

        statement = statement.order_by(UserListEntry.updated_at.desc()).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()

    async def create_list_entry(self, user_id: UUID, entry_data: ListEntryCreate) -> UserListEntry:
        """Create a new list entry for the current user."""
        existing_entry = await self.get_user_list_entry(user_id, entry_data.media_id)
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
        entry = await self.get_user_list_entry(user_id, media_id)
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
        entry = await self.get_user_list_entry(user_id, media_id)
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
        statement = (
            select(ListEntryHistory)
            .where(ListEntryHistory.entry_id == entry_id)
            .order_by(ListEntryHistory.created_at.desc())
            .limit(limit)
        )

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_user_activity_feed(self, user_id: UUID, limit: int = 20) -> List[ListEntryHistory]:
        """Get user's activity feed."""
        statement = (
            select(ListEntryHistory)
            .where(ListEntryHistory.user_id == user_id)
            .order_by(ListEntryHistory.created_at.desc())
            .limit(limit)
        )

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_user_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's tracking statistics."""
        completed_stmt = (
            select(func.count(UserListEntry.id))
            .where(
                and_(
                    UserListEntry.user_id == user_id,
                    UserListEntry.status == "completed",
                    UserListEntry.deleted_at.is_(None),
                )
            )
        )
        completed_result = await self.db_session.exec(completed_stmt)
        completed_count = completed_result.one_or_none() or 0

        in_progress_stmt = (
            select(func.count(UserListEntry.id))
            .where(
                and_(
                    UserListEntry.user_id == user_id,
                    UserListEntry.status.in_(["watching", "reading", "rewatching", "rereading"]),
                    UserListEntry.deleted_at.is_(None),
                )
            )
        )
        in_progress_result = await self.db_session.exec(in_progress_stmt)
        in_progress_count = in_progress_result.one_or_none() or 0

        total_stmt = select(func.count(UserListEntry.id)).where(
            and_(
                UserListEntry.user_id == user_id,
                UserListEntry.deleted_at.is_(None),
            )
        )
        total_result = await self.db_session.exec(total_stmt)
        total_count = total_result.one_or_none() or 0

        return {
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
            "total_count": total_count,
        }

    async def create_custom_list(self, user_id: UUID, payload: CustomListCreate) -> CustomList:
        """Create a custom list for the current user."""
        custom_list = CustomList(user_id=user_id, **payload.model_dump())
        self.db_session.add(custom_list)
        await self.db_session.commit()
        await self.db_session.refresh(custom_list)
        return custom_list

    async def replace_custom_list_entries(
        self,
        user_id: UUID,
        list_id: UUID,
        payload: CustomListEntriesReplaceRequest,
    ) -> Optional[int]:
        """Replace all entries in a custom list owned by current user."""
        list_stmt = select(CustomList).where(
            and_(
                CustomList.id == list_id,
                CustomList.user_id == user_id,
                CustomList.deleted_at.is_(None),
            )
        )
        list_result = await self.db_session.exec(list_stmt)
        custom_list = list_result.one_or_none()
        if not custom_list:
            return None

        delete_stmt = select(CustomListEntry).where(CustomListEntry.list_id == list_id)
        delete_result = await self.db_session.exec(delete_stmt)
        for item in delete_result.all():
            await self.db_session.delete(item)

        for entry in payload.entries:
            self.db_session.add(
                CustomListEntry(
                    list_id=list_id,
                    media_id=entry.media_id,
                    sort_order=entry.sort_order,
                    note=entry.note,
                )
            )

        custom_list.updated_at = datetime.utcnow()
        await self.db_session.commit()
        return len(payload.entries)

    async def get_media_tracking_status(self, media_id: UUID, user_id: UUID) -> Optional[UserListEntry]:
        """Get current tracking status of a media for a specific user."""
        return await self.get_user_list_entry(user_id=user_id, media_id=media_id)
