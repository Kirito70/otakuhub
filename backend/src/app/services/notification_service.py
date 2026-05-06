"""Notification service for inbox retrieval."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from src.app.models import Notification
from src.app.services.base_service import BaseService


class NotificationService(BaseService):
    """Service class for notification inbox operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)

    async def get_user_notifications(
        self,
        *,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        """Get paginated notifications for current user."""
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db_session.exec(statement)
        return result.all()

    async def count_user_notifications(self, *, user_id: UUID) -> int:
        """Count all notifications for current user."""
        statement = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        result = await self.db_session.exec(statement)
        return result.one_or_none() or 0

    async def mark_notifications_as_read(
        self,
        *,
        user_id: UUID,
        notification_ids: list[UUID],
    ) -> int:
        """Mark selected user notifications as read and return updated count."""
        if not notification_ids:
            return 0

        statement = select(Notification).where(
            Notification.user_id == user_id,
            Notification.id.in_(notification_ids),
            Notification.is_read == False,  # noqa: E712
        )
        result = await self.db_session.exec(statement)
        items = result.all()

        now = datetime.utcnow()
        for item in items:
            item.is_read = True
            item.read_at = now

        if items:
            await self.db_session.commit()

        return len(items)
