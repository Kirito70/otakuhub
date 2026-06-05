"""Repository for notification-related database operations."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Notification, NotificationPreference
from src.app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Notification, db_session)

    async def get_for_user(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        is_read: Optional[bool] = None,
    ) -> List[Notification]:
        """Get notifications for a user with optional read filter and pagination."""
        q = self.query().filter(Notification.user_id == user_id)
        if is_read is not None:
            q = q.filter(Notification.is_read == is_read)
        return await q.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    async def count_for_user(
        self,
        user_id: UUID,
        is_read: Optional[bool] = None,
    ) -> int:
        """Count notifications for a user with optional read filter."""
        q = self.query().filter(Notification.user_id == user_id)
        if is_read is not None:
            q = q.filter(Notification.is_read == is_read)
        return await q.count()

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Mark a single notification as read, scoped to user."""
        instance = await self.query().filter(Notification.id == notification_id).first()
        if not instance or instance.user_id != user_id:
            return False
        instance.is_read = True
        from datetime import datetime
        instance.read_at = datetime.utcnow()
        await self.db_session.commit()
        return True

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications for user as read. Returns count updated."""
        q = self.query().filter(Notification.user_id == user_id).filter(Notification.is_read == False)  # noqa: E712
        results = await q.all()
        count = len(results)
        from datetime import datetime
        for notif in results:
            notif.is_read = True
            notif.read_at = datetime.utcnow()
        await self.db_session.commit()
        return count

    async def hard_delete(self, notification_id: UUID, user_id: UUID) -> bool:
        """Hard-delete a notification by ID, scoped to user."""
        q = self.query().filter(Notification.id == notification_id).filter(Notification.user_id == user_id)
        instance = await q.first()
        if not instance:
            return False
        await self.db_session.delete(instance)
        await self.db_session.commit()
        return True


class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    """Repository for NotificationPreference model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(NotificationPreference, db_session)

    async def get_by_user_id(self, user_id: UUID) -> Optional[NotificationPreference]:
        """Get preferences for a user, creating defaults if absent."""
        q = self.query().filter(NotificationPreference.user_id == user_id)
        pref = await q.first()
        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.db_session.add(pref)
            await self.db_session.commit()
            await self.db_session.refresh(pref)
        return pref
