"""Notification service for inbox retrieval."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Notification, NotificationPreference
from src.app.services.base_service import BaseService
from src.app.repositories.notification_repository import (
    NotificationRepository,
    NotificationPreferenceRepository,
)


class NotificationService(BaseService):
    """Service class for notification inbox operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
        self._notification_repo = NotificationRepository(self.db_session)
        self._pref_repo = NotificationPreferenceRepository(self.db_session)

    async def get_user_notifications(
        self,
        *,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        """Get paginated notifications for current user."""
        return await self._notification_repo.get_for_user(user_id, limit=limit, offset=offset)

    async def count_user_notifications(self, *, user_id: UUID) -> int:
        """Count all notifications for current user."""
        return await self._notification_repo.count_for_user(user_id)

    async def mark_notifications_as_read(
        self,
        *,
        user_id: UUID,
        notification_ids: list[UUID],
    ) -> int:
        """Mark selected user notifications as read and return updated count."""
        if not notification_ids:
            return 0

        count = 0
        for nid in notification_ids:
            if await self._notification_repo.mark_as_read(nid, user_id):
                count += 1
        return count

    async def mark_all_notifications_as_read(self, *, user_id: UUID) -> int:
        """Mark all of the current user's unread notifications as read."""
        return await self._notification_repo.mark_all_as_read(user_id)

    async def delete_notification(
        self,
        *,
        user_id: UUID,
        notification_id: UUID,
    ) -> bool:
        """Delete a single notification by ID. Only the owner can delete."""
        return await self._notification_repo.hard_delete(notification_id, user_id)

    async def get_notification_preferences(self, *, user_id: UUID) -> NotificationPreference:
        """Get current user's notification preferences, creating defaults if absent."""
        return await self._pref_repo.get_by_user_id(user_id)

    async def update_notification_preferences(
        self,
        *,
        user_id: UUID,
        updates: dict[str, object],
    ) -> NotificationPreference:
        """Partially update current user's notification preferences."""
        preference = await self._pref_repo.get_by_user_id(user_id)
        for key, value in updates.items():
            setattr(preference, key, value)
        preference.updated_at = datetime.utcnow()
        await self.db_session.commit()
        await self.db_session.refresh(preference)
        return preference
