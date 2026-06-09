"""Repository for tracking/list-related database operations."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.app.models import (
    UserListEntry, ListEntryHistory, CustomList, CustomListEntry,
)
from src.app.repositories.base_repository import BaseRepository


class UserListEntryRepository(BaseRepository[UserListEntry]):
    """Repository for UserListEntry model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(UserListEntry, db_session)

    async def get_by_user_and_media(self, user_id: UUID, media_id: UUID) -> Optional[UserListEntry]:
        """Get a specific list entry by user and media."""
        return await (
            self.query()
            .filter(UserListEntry.user_id == user_id)
            .filter(UserListEntry.media_id == media_id)
            .first()
        )

    async def get_user_list(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        statuses: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[UserListEntry]:
        """Get a user's list entries with optional status filter and pagination.

        Args:
            user_id: The user's UUID.
            status: Single status filter (legacy).
            statuses: Comma-separated status list (e.g. "watching,reading").
            limit: Maximum number of results.
            offset: Number of results to skip.
        """
        q = self.query().filter(UserListEntry.user_id == user_id)
        if status is not None:
            q = q.filter(UserListEntry.status == status)
        if statuses is not None:
            status_list = [s.strip() for s in statuses.split(",") if s.strip()]
            if status_list:
                q = q.filter(UserListEntry.status.in_(status_list))
        return await (
            q
            .options(joinedload(UserListEntry.media))
            .order_by(UserListEntry.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    async def count_user_list(self, user_id: UUID, status: Optional[str] = None) -> int:
        """Count a user's list entries with optional status filter."""
        q = self.query().filter(UserListEntry.user_id == user_id)
        if status is not None:
            q = q.filter(UserListEntry.status == status)
        return await q.count()

    async def get_statistics(self, user_id: UUID) -> dict:
        """Get tracking statistics for a user."""
        total = await self.query().filter(UserListEntry.user_id == user_id).count()

        watching = await (
            self.query()
            .filter(UserListEntry.user_id == user_id)
            .filter(UserListEntry.status.in_(["watching", "reading"]))
            .count()
        )

        completed = await (
            self.query()
            .filter(UserListEntry.user_id == user_id)
            .filter(UserListEntry.status == "completed")
            .count()
        )

        return {"total": total, "watching": watching, "completed": completed}


class ListEntryHistoryRepository(BaseRepository[ListEntryHistory]):
    """Repository for ListEntryHistory model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(ListEntryHistory, db_session)

    async def get_for_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ListEntryHistory]:
        """Get history entries for a user with pagination."""
        return await (
            self.query()
            .filter(ListEntryHistory.user_id == user_id)
            .order_by(ListEntryHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


class CustomListRepository(BaseRepository[CustomList]):
    """Repository for CustomList model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(CustomList, db_session)

    async def get_by_user(self, user_id: UUID) -> List[CustomList]:
        """Get all custom lists for a user."""
        return await (
            self.query()
            .filter(CustomList.user_id == user_id)
            .order_by(CustomList.sort_order.asc())
            .order_by(CustomList.created_at.desc())
            .all()
        )

    async def get_by_id(self, list_id: UUID) -> Optional[CustomList]:
        """Get a custom list by ID."""
        return await self.query().filter(CustomList.id == list_id).first()


class CustomListEntryRepository(BaseRepository[CustomListEntry]):
    """Repository for CustomListEntry model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(CustomListEntry, db_session)

    async def get_entries(self, list_id: UUID) -> List[CustomListEntry]:
        """Get all entries in a custom list, ordered."""
        return await (
            self.query()
            .filter(CustomListEntry.list_id == list_id)
            .order_by(CustomListEntry.sort_order.asc())
            .all()
        )

    async def replace_entries(self, list_id: UUID, media_ids: List[UUID]) -> None:
        """Replace all entries in a custom list with new ordered list."""
        existing = await self.get_entries(list_id)
        for entry in existing:
            await self.db_session.delete(entry)
        for idx, media_id in enumerate(media_ids):
            entry = CustomListEntry(list_id=list_id, media_id=media_id, sort_order=idx)
            self.db_session.add(entry)
        await self.db_session.commit()
