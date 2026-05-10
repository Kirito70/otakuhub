"""Social service for managing recommendations, discussions, and notifications."""

from typing import List, Optional, Dict, Any
from sqlmodel import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from uuid import UUID

from src.app.models import (
    Recommendation, Discussion, DiscussionReply,
    Notification, NotificationPreference, ListEntryHistory, GroupMember, User
)
from src.app.services.base_service import BaseService


class SocialService(BaseService):
    """Service class for social-related operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)

    # Recommendations

    async def get_user_recommendations(self, user_id: UUID, limit: int = 20) -> List[Recommendation]:
        """Get recommendations for a user."""
        statement = select(Recommendation).where(Recommendation.to_user_id == user_id)
        statement = statement.order_by(Recommendation.created_at.desc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_user_recommendations_inbox(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_acknowledged: bool = True,
    ) -> List[Recommendation]:
        """Get paginated recommendation inbox for a user."""
        statement = select(Recommendation).where(
            Recommendation.to_user_id == user_id,
            Recommendation.deleted_at.is_(None),
        )
        if not include_acknowledged:
            statement = statement.where(Recommendation.is_acknowledged == False)  # noqa: E712

        statement = statement.order_by(Recommendation.created_at.desc()).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()

    async def count_user_recommendations_inbox(
        self,
        user_id: UUID,
        include_acknowledged: bool = True,
    ) -> int:
        """Count inbox recommendations for pagination metadata."""
        statement = select(func.count(Recommendation.id)).where(
            Recommendation.to_user_id == user_id,
            Recommendation.deleted_at.is_(None),
        )
        if not include_acknowledged:
            statement = statement.where(Recommendation.is_acknowledged == False)  # noqa: E712

        result = await self.db_session.exec(statement)
        return result.one_or_none() or 0

    async def get_group_activity_feed(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ListEntryHistory]:
        """Return recent list activity by members who share a group with the user."""
        group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        member_ids_stmt = (
            select(GroupMember.user_id)
            .where(GroupMember.group_id.in_(group_ids_stmt))
            .where(GroupMember.user_id != user_id)
            .distinct()
        )

        statement = (
            select(ListEntryHistory)
            .where(ListEntryHistory.user_id.in_(member_ids_stmt))
            .order_by(ListEntryHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db_session.exec(statement)
        return result.all()

    async def count_group_activity_feed(self, user_id: UUID) -> int:
        """Count total feed items visible to user for pagination metadata."""
        group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        member_ids_stmt = (
            select(GroupMember.user_id)
            .where(GroupMember.group_id.in_(group_ids_stmt))
            .where(GroupMember.user_id != user_id)
            .distinct()
        )

        count_stmt = select(func.count(ListEntryHistory.id)).where(ListEntryHistory.user_id.in_(member_ids_stmt))
        count_result = await self.db_session.exec(count_stmt)
        return count_result.one_or_none() or 0

    async def get_user_sent_recommendations(self, user_id: UUID, limit: int = 20) -> List[Recommendation]:
        """Get recommendations sent by a user."""
        statement = select(Recommendation).where(Recommendation.from_user_id == user_id)
        statement = statement.order_by(Recommendation.created_at.desc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def create_recommendation(self, from_user_id: UUID, to_user_id: UUID,
                                  media_id: UUID, message: str) -> Recommendation:
        """Create a new recommendation."""
        recommendation = Recommendation(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            media_id=media_id,
            message=message
        )
        self.db_session.add(recommendation)
        await self.db_session.commit()
        await self.db_session.refresh(recommendation)
        return recommendation

    async def create_recommendation_for_shared_group(
        self,
        from_user_id: UUID,
        to_user_id: UUID,
        media_id: UUID,
        message: str | None = None,
    ) -> Recommendation:
        """Create recommendation only when users share a group and refs exist."""
        if from_user_id == to_user_id:
            raise ValueError("Cannot recommend media to yourself")

        to_user_stmt = select(User).where(
            User.id == to_user_id,
            User.deleted_at.is_(None),
            User.is_active == True,  # noqa: E712
        )
        to_user = (await self.db_session.exec(to_user_stmt)).one_or_none()
        if to_user is None:
            raise ValueError("Recipient user not found")

        shared_group_stmt = (
            select(GroupMember.group_id)
            .where(GroupMember.user_id == from_user_id)
            .where(
                GroupMember.group_id.in_(
                    select(GroupMember.group_id).where(GroupMember.user_id == to_user_id)
                )
            )
            .limit(1)
        )
        shared_group = (await self.db_session.exec(shared_group_stmt)).one_or_none()
        if shared_group is None:
            raise ValueError("Users must share at least one group")

        existing_stmt = select(Recommendation).where(
            Recommendation.from_user_id == from_user_id,
            Recommendation.to_user_id == to_user_id,
            Recommendation.media_id == media_id,
            Recommendation.deleted_at.is_(None),
        )
        existing = (await self.db_session.exec(existing_stmt)).one_or_none()
        if existing is not None:
            raise ValueError("Recommendation already exists for this user and media")

        recommendation = Recommendation(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            media_id=media_id,
            message=message,
        )
        self.db_session.add(recommendation)
        await self.db_session.commit()
        await self.db_session.refresh(recommendation)
        return recommendation

    async def acknowledge_recommendation(
        self,
        recommendation_id: UUID,
        user_id: UUID,
    ) -> Recommendation | None:
        """Mark a recommendation as acknowledged and return updated row."""
        statement = select(Recommendation).where(Recommendation.id == recommendation_id)
        result = await self.db_session.exec(statement)
        recommendation = result.one_or_none()

        if not recommendation or recommendation.to_user_id != user_id:
            return None

        recommendation.is_acknowledged = True
        recommendation.acknowledged_at = datetime.utcnow()
        await self.db_session.commit()
        await self.db_session.refresh(recommendation)
        return recommendation

    # Discussions

    async def get_discussions(self, media_id: UUID, group_id: Optional[UUID] = None,
                            limit: int = 20, offset: int = 0) -> List[Discussion]:
        """Get discussions for a media item."""
        statement = select(Discussion).where(Discussion.media_id == media_id)

        if group_id:
            statement = statement.where(Discussion.group_id == group_id)

        statement = statement.order_by(Discussion.created_at.desc()).offset(offset).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_discussions_for_user_media(
        self,
        *,
        user_id: UUID,
        media_id: UUID,
        group_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Discussion]:
        """Return discussions visible to a user for a media item."""
        member_group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        statement = select(Discussion).where(
            Discussion.media_id == media_id,
            Discussion.deleted_at.is_(None),
            Discussion.group_id.in_(member_group_ids_stmt),
        )

        if group_id is not None:
            statement = statement.where(Discussion.group_id == group_id)

        statement = statement.order_by(Discussion.created_at.desc()).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()

    async def count_discussions_for_user_media(
        self,
        *,
        user_id: UUID,
        media_id: UUID,
        group_id: Optional[UUID] = None,
    ) -> int:
        """Count discussions visible to user for media pagination."""
        member_group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        statement = select(func.count(Discussion.id)).where(
            Discussion.media_id == media_id,
            Discussion.deleted_at.is_(None),
            Discussion.group_id.in_(member_group_ids_stmt),
        )

        if group_id is not None:
            statement = statement.where(Discussion.group_id == group_id)

        result = await self.db_session.exec(statement)
        return result.one_or_none() or 0

    async def get_discussion_replies(self, discussion_id: UUID, limit: int = 20) -> List[DiscussionReply]:
        """Get replies for a discussion."""
        statement = select(DiscussionReply).where(DiscussionReply.discussion_id == discussion_id)
        statement = statement.order_by(DiscussionReply.created_at.asc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def create_discussion(self, user_id: UUID, media_id: UUID, group_id: UUID,
                              title: str, body: str, has_spoilers: bool = False,
                              episode_number: Optional[int] = None,
                              chapter_number: Optional[float] = None) -> Discussion:
        """Create a new discussion."""
        discussion = Discussion(
            user_id=user_id,
            media_id=media_id,
            group_id=group_id,
            title=title,
            body=body,
            has_spoilers=has_spoilers,
            episode_number=episode_number,
            chapter_number=chapter_number
        )
        self.db_session.add(discussion)
        await self.db_session.commit()
        await self.db_session.refresh(discussion)
        return discussion

    async def create_discussion_for_group_member(
        self,
        user_id: UUID,
        media_id: UUID,
        group_id: UUID,
        title: str | None,
        body: str,
        has_spoilers: bool = False,
        episode_number: Optional[int] = None,
        chapter_number: Optional[float] = None,
    ) -> Discussion:
        """Create discussion only when user belongs to group."""
        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this group")

        discussion = Discussion(
            user_id=user_id,
            media_id=media_id,
            group_id=group_id,
            title=title,
            body=body,
            has_spoilers=has_spoilers,
            episode_number=episode_number,
            chapter_number=chapter_number,
        )
        self.db_session.add(discussion)
        try:
            await self.db_session.commit()
        except IntegrityError as exc:
            await self.db_session.rollback()
            raise ValueError("Media not found yet; sync/seed required") from exc

        await self.db_session.refresh(discussion)
        return discussion

    async def create_discussion_reply(self, user_id: UUID, discussion_id: UUID,
                                     parent_reply_id: Optional[UUID] = None,
                                     body: str = "", has_spoilers: bool = False) -> DiscussionReply:
        """Create a reply to a discussion."""
        reply = DiscussionReply(
            user_id=user_id,
            discussion_id=discussion_id,
            parent_reply_id=parent_reply_id,
            body=body,
            has_spoilers=has_spoilers
        )
        self.db_session.add(reply)
        await self.db_session.commit()
        await self.db_session.refresh(reply)
        return reply

    async def create_discussion_reply_for_group_member(
        self,
        *,
        user_id: UUID,
        discussion_id: UUID,
        body: str,
        has_spoilers: bool = False,
        parent_reply_id: Optional[UUID] = None,
    ) -> DiscussionReply:
        """Create reply only if user can view the discussion's group."""
        discussion_stmt = select(Discussion).where(
            Discussion.id == discussion_id,
            Discussion.deleted_at.is_(None),
        )
        discussion = (await self.db_session.exec(discussion_stmt)).one_or_none()
        if discussion is None:
            raise LookupError("Discussion not found")

        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == discussion.group_id,
            GroupMember.user_id == user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this discussion group")

        if parent_reply_id is not None:
            parent_stmt = select(DiscussionReply).where(
                DiscussionReply.id == parent_reply_id,
                DiscussionReply.discussion_id == discussion_id,
                DiscussionReply.deleted_at.is_(None),
            )
            parent = (await self.db_session.exec(parent_stmt)).one_or_none()
            if parent is None:
                raise LookupError("Parent reply not found")

        reply = DiscussionReply(
            user_id=user_id,
            discussion_id=discussion_id,
            parent_reply_id=parent_reply_id,
            body=body,
            has_spoilers=has_spoilers,
        )
        self.db_session.add(reply)
        await self.db_session.commit()
        await self.db_session.refresh(reply)
        return reply

    # Notifications

    async def get_user_notifications(self, user_id: UUID, limit: int = 20,
                                   is_read: Optional[bool] = None) -> List[Notification]:
        """Get notifications for a user."""
        statement = select(Notification).where(Notification.user_id == user_id)

        if is_read is not None:
            statement = statement.where(Notification.is_read == is_read)

        statement = statement.order_by(Notification.created_at.desc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def mark_notification_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Mark a notification as read."""
        statement = select(Notification).where(Notification.id == notification_id)
        result = await self.db_session.exec(statement)
        notification = result.one_or_none()

        if not notification or notification.user_id != user_id:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await self.db_session.commit()
        return True

    async def create_notification(self, user_id: UUID, notification_type: str,
                                title: str, body: str,
                                related_media_id: Optional[UUID] = None,
                                related_user_id: Optional[UUID] = None,
                                action_url: Optional[str] = None) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            related_media_id=related_media_id,
            related_user_id=related_user_id,
            action_url=action_url
        )
        self.db_session.add(notification)
        await self.db_session.commit()
        await self.db_session.refresh(notification)
        return notification

    async def get_notification_preferences(self, user_id: UUID) -> NotificationPreference:
        """Get user's notification preferences."""
        statement = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.db_session.exec(statement)
        preference = result.one_or_none()

        # If no preferences exist, return default ones
        if not preference:
            preference = NotificationPreference(user_id=user_id)
            self.db_session.add(preference)
            await self.db_session.commit()

        return preference

    async def update_notification_preferences(self, user_id: UUID,
                                           preferences: Dict[str, Any]) -> NotificationPreference:
        """Update user's notification preferences."""
        statement = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.db_session.exec(statement)
        preference = result.one_or_none()

        if not preference:
            preference = NotificationPreference(user_id=user_id)
            self.db_session.add(preference)

        for key, value in preferences.items():
            setattr(preference, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(preference)
        return preference

    # Watch Parties

    async def get_user_watch_parties(self, user_id: UUID, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's upcoming watch parties."""
        # This is a simplified version - in practice you'd want more details
        statement = select(
            "host_user_id", "media_id", "group_id", "title",
            "scheduled_at", "status", "stream_url"
        ).where(
            and_(
                NotificationPreference.user_id == user_id  # This is just an example path
            )
        )

        # This needs to be implemented based on your actual database relationships
        return []
