"""Repository for social-related database operations (recommendations, discussions, replies)."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from src.app.models import (
    Recommendation, Discussion, DiscussionReply,
    ListEntryHistory, GroupMember, MediaEntry,
)
from src.app.repositories.base_repository import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    """Repository for Recommendation model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Recommendation, db_session)

    async def get_inbox(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_acknowledged: bool = True,
    ) -> List[Recommendation]:
        """Get paginated recommendation inbox for a user."""
        q = self.query().filter(Recommendation.to_user_id == user_id)
        if not include_acknowledged:
            q = q.filter(Recommendation.is_acknowledged == False)  # noqa: E712
        return await q.order_by(Recommendation.created_at.desc()).offset(offset).limit(limit).all()

    async def count_inbox(
        self,
        user_id: UUID,
        include_acknowledged: bool = True,
    ) -> int:
        """Count inbox recommendations for pagination."""
        q = self.query().filter(Recommendation.to_user_id == user_id)
        if not include_acknowledged:
            q = q.filter(Recommendation.is_acknowledged == False)  # noqa: E712
        return await q.count()

    async def get_sent(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Recommendation]:
        """Get paginated recommendations sent by a user."""
        return await (
            self.query()
            .filter(Recommendation.from_user_id == user_id)
            .order_by(Recommendation.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    async def count_sent(self, user_id: UUID) -> int:
        """Count sent recommendations for pagination."""
        return await self.query().filter(Recommendation.from_user_id == user_id).count()

    async def get_by_id(self, recommendation_id: UUID) -> Optional[Recommendation]:
        """Get a recommendation by ID (including soft-deleted)."""
        return await self.query().filter(Recommendation.id == recommendation_id).first()

    async def soft_delete(self, recommendation_id: UUID) -> bool:
        """Soft-delete a recommendation by ID."""
        return await self.delete(recommendation_id)


class DiscussionRepository(BaseRepository[Discussion]):
    """Repository for Discussion model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Discussion, db_session)

    async def get_for_media(
        self,
        media_id: UUID,
        user_id: UUID,
        group_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Discussion]:
        """Get discussions visible to a user for a media item."""
        member_group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        q = (
            self.query()
            .filter(Discussion.media_id == media_id)
            .filter(Discussion.group_id.in_(member_group_ids))
        )
        if group_id is not None:
            q = q.filter(Discussion.group_id == group_id)
        return await q.order_by(Discussion.created_at.desc()).offset(offset).limit(limit).all()

    async def count_for_media(
        self,
        media_id: UUID,
        user_id: UUID,
        group_id: Optional[UUID] = None,
    ) -> int:
        """Count discussions visible to a user for media pagination."""
        member_group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        q = (
            self.query()
            .filter(Discussion.media_id == media_id)
            .filter(Discussion.group_id.in_(member_group_ids))
        )
        if group_id is not None:
            q = q.filter(Discussion.group_id == group_id)
        return await q.count()

    async def get_by_id(self, discussion_id: UUID) -> Optional[Discussion]:
        """Get a discussion by ID (soft-deleted rows excluded)."""
        return await self.query().filter(Discussion.id == discussion_id).first()

    async def soft_delete(self, discussion_id: UUID) -> bool:
        """Soft-delete a discussion by ID."""
        return await self.delete(discussion_id)


class DiscussionReplyRepository(BaseRepository[DiscussionReply]):
    """Repository for DiscussionReply model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(DiscussionReply, db_session)

    async def get_for_discussion(
        self,
        discussion_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DiscussionReply]:
        """Get paginated replies for a discussion."""
        return await (
            self.query()
            .filter(DiscussionReply.discussion_id == discussion_id)
            .order_by(DiscussionReply.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    async def count_for_discussion(self, discussion_id: UUID) -> int:
        """Count total replies for a discussion."""
        return await self.query().filter(DiscussionReply.discussion_id == discussion_id).count()


class GroupActivityRepository(BaseRepository[ListEntryHistory]):
    """Repository for group activity feed queries."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(ListEntryHistory, db_session)

    async def get_feed(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        media_type: str | None = None,
    ) -> List[ListEntryHistory]:
        """Get recent list activity by group members of the user.

        When ``media_type`` is provided (e.g. ``"anime"``, ``"manga"``), only
        entries whose linked ``MediaEntry.media_type`` matches are returned.
        """
        group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        member_ids = (
            select(GroupMember.user_id)
            .where(GroupMember.group_id.in_(group_ids))
            .where(GroupMember.user_id != user_id)
            .distinct()
        )
        q = self.query().filter(ListEntryHistory.user_id.in_(member_ids))
        if media_type is not None:
            q = (
                q.join(MediaEntry, MediaEntry.id == ListEntryHistory.media_id)
                .filter(MediaEntry.media_type == media_type)
            )
        return await q.order_by(ListEntryHistory.created_at.desc()).offset(offset).limit(limit).all()

    async def count_feed(
        self,
        user_id: UUID,
        media_type: str | None = None,
    ) -> int:
        """Count total feed items visible to user for pagination."""
        group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        member_ids = (
            select(GroupMember.user_id)
            .where(GroupMember.group_id.in_(group_ids))
            .where(GroupMember.user_id != user_id)
            .distinct()
        )
        q = self.query().filter(ListEntryHistory.user_id.in_(member_ids))
        if media_type is not None:
            q = (
                q.join(MediaEntry, MediaEntry.id == ListEntryHistory.media_id)
                .filter(MediaEntry.media_type == media_type)
            )
        return await q.count()
