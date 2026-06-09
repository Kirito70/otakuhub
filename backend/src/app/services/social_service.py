"""Social service for managing recommendations, discussions, and notifications."""

from typing import List, Optional, Dict, Any
from sqlmodel import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from uuid import UUID

from src.app.models import (
    Recommendation, Discussion, DiscussionReply,
    Notification, NotificationPreference, ListEntryHistory, GroupMember, User,
    WatchParty, MediaEntry,
)
from src.app.services.base_service import BaseService
from src.app.repositories.social_repository import (
    RecommendationRepository,
    DiscussionRepository,
    DiscussionReplyRepository,
    GroupActivityRepository,
)
from src.app.repositories.notification_repository import (
    NotificationRepository,
    NotificationPreferenceRepository,
)
from src.app.repositories.watch_party_repository import WatchPartyRepository


class SocialService(BaseService):
    """Service class for social-related operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
        self._recommendation_repo = RecommendationRepository(self.db_session)
        self._discussion_repo = DiscussionRepository(self.db_session)
        self._discussion_reply_repo = DiscussionReplyRepository(self.db_session)
        self._activity_repo = GroupActivityRepository(self.db_session)
        self._notification_repo = NotificationRepository(self.db_session)
        self._notification_pref_repo = NotificationPreferenceRepository(self.db_session)
        self._watch_party_repo = WatchPartyRepository(self.db_session)

    # ── Recommendations ──────────────────────────────────────────────────

    async def get_user_recommendations(self, user_id: UUID, limit: int = 20) -> List[Recommendation]:
        """Get recommendations for a user."""
        return await self._recommendation_repo.get_inbox(user_id, limit=limit)

    async def get_user_recommendations_inbox(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        include_acknowledged: bool = True,
    ) -> List[Recommendation]:
        """Get paginated recommendation inbox for a user."""
        return await self._recommendation_repo.get_inbox(
            user_id, limit=limit, offset=offset, include_acknowledged=include_acknowledged,
        )

    async def count_user_recommendations_inbox(
        self,
        user_id: UUID,
        include_acknowledged: bool = True,
    ) -> int:
        """Count inbox recommendations for pagination metadata."""
        return await self._recommendation_repo.count_inbox(user_id, include_acknowledged=include_acknowledged)

    async def get_group_activity_feed(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        media_type: str | None = None,
    ) -> List[ListEntryHistory]:
        """Return recent list activity by members who share a group with the user."""
        return await self._activity_repo.get_feed(user_id, limit=limit, offset=offset, media_type=media_type)

    async def count_group_activity_feed(
        self,
        user_id: UUID,
        media_type: str | None = None,
    ) -> int:
        """Count total feed items visible to user for pagination metadata."""
        return await self._activity_repo.count_feed(user_id, media_type=media_type)

    async def get_user_sent_recommendations(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Recommendation]:
        """Get paginated recommendations sent by a user (non-deleted)."""
        return await self._recommendation_repo.get_sent(user_id, limit=limit, offset=offset)

    async def count_user_sent_recommendations(self, user_id: UUID) -> int:
        """Count sent recommendations for pagination metadata."""
        return await self._recommendation_repo.count_sent(user_id)

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

        existing = await self._recommendation_repo.get_inbox(
            to_user_id, limit=1, include_acknowledged=True,
        )
        for rec in existing:
            if rec.from_user_id == from_user_id and rec.media_id == media_id:
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
        recommendation = await self._recommendation_repo.get_by_id(recommendation_id)
        if not recommendation or recommendation.to_user_id != user_id:
            return None

        recommendation.is_acknowledged = True
        recommendation.acknowledged_at = datetime.utcnow()
        await self.db_session.commit()
        await self.db_session.refresh(recommendation)
        return recommendation

    # ── Discussions ──────────────────────────────────────────────────────

    async def get_discussions(self, media_id: UUID, group_id: Optional[UUID] = None,
                            limit: int = 20, offset: int = 0) -> List[Discussion]:
        """Get discussions for a media item."""
        q = self._discussion_repo.query().filter(Discussion.media_id == media_id)
        if group_id:
            q = q.filter(Discussion.group_id == group_id)
        return await q.order_by(Discussion.created_at.desc()).offset(offset).limit(limit).all()

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
        return await self._discussion_repo.get_for_media(
            media_id, user_id, group_id=group_id, limit=limit, offset=offset,
        )

    async def count_discussions_for_user_media(
        self,
        *,
        user_id: UUID,
        media_id: UUID,
        group_id: Optional[UUID] = None,
    ) -> int:
        """Count discussions visible to user for media pagination."""
        return await self._discussion_repo.count_for_media(media_id, user_id, group_id=group_id)

    async def get_discussion_replies(self, discussion_id: UUID, limit: int = 20) -> List[DiscussionReply]:
        """Get replies for a discussion."""
        return await self._discussion_reply_repo.get_for_discussion(discussion_id, limit=limit)

    async def get_discussion_replies_for_user(
        self,
        *,
        discussion_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DiscussionReply]:
        """Get paginated replies if user is member of the discussion's group."""
        discussion = await self._discussion_repo.get_by_id(discussion_id)
        if discussion is None:
            raise LookupError("Discussion not found")

        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == discussion.group_id,
            GroupMember.user_id == user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this discussion group")

        return await self._discussion_reply_repo.get_for_discussion(
            discussion_id, limit=limit, offset=offset,
        )

    async def count_discussion_replies_for_user(
        self,
        *,
        discussion_id: UUID,
        user_id: UUID,
    ) -> int:
        """Count replies visible to a user for a discussion thread."""
        discussion = await self._discussion_repo.get_by_id(discussion_id)
        if discussion is None:
            raise LookupError("Discussion not found")

        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == discussion.group_id,
            GroupMember.user_id == user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this discussion group")

        return await self._discussion_reply_repo.count_for_discussion(discussion_id)

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
        """Create discussion only when user belongs to group and media exists."""
        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this group")

        media_stmt = select(MediaEntry).where(MediaEntry.id == media_id)
        media = (await self.db_session.exec(media_stmt)).one_or_none()
        if media is None:
            raise ValueError("Media not found yet; sync/seed required")

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
        discussion = await self._discussion_repo.get_by_id(discussion_id)
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
            parent = await self._discussion_reply_repo.get_for_discussion(discussion_id)
            parent_exists = any(p.id == parent_reply_id for p in parent)
            if not parent_exists:
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

    async def delete_recommendation(
        self,
        recommendation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Soft delete a recommendation. Only the sender can delete."""
        recommendation = await self._recommendation_repo.get_by_id(recommendation_id)
        if not recommendation:
            return False

        if recommendation.from_user_id != user_id:
            raise PermissionError("Only the sender can delete this recommendation")

        return await self._recommendation_repo.soft_delete(recommendation_id)

    async def delete_discussion(
        self,
        discussion_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Soft delete a discussion. Only the author can delete."""
        discussion = await self._discussion_repo.get_by_id(discussion_id)
        if not discussion:
            return False

        if discussion.user_id != user_id:
            raise PermissionError("Only the author can delete this discussion")

        return await self._discussion_repo.soft_delete(discussion_id)

    # ── Notifications ────────────────────────────────────────────────────

    async def get_user_notifications(self, user_id: UUID, limit: int = 20,
                                   is_read: Optional[bool] = None) -> List[Notification]:
        """Get notifications for a user."""
        return await self._notification_repo.get_for_user(user_id, limit=limit, is_read=is_read)

    async def mark_notification_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Mark a notification as read."""
        return await self._notification_repo.mark_as_read(notification_id, user_id)

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
        return await self._notification_pref_repo.get_by_user_id(user_id)

    async def update_notification_preferences(self, user_id: UUID,
                                           preferences: Dict[str, Any]) -> NotificationPreference:
        """Update user's notification preferences."""
        pref = await self._notification_pref_repo.get_by_user_id(user_id)
        for key, value in preferences.items():
            setattr(pref, key, value)
        await self.db_session.commit()
        await self.db_session.refresh(pref)
        return pref

    # ── Watch Parties ────────────────────────────────────────────────────

    async def get_user_watch_parties(self, user_id: UUID, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's upcoming watch parties visible through shared group membership."""
        member_group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        statement = (
            select(WatchParty, MediaEntry.title_romaji, MediaEntry.title_english)
            .join(MediaEntry, MediaEntry.id == WatchParty.media_id)
            .where(
                WatchParty.group_id.in_(member_group_ids_stmt),
                WatchParty.deleted_at.is_(None),
                WatchParty.scheduled_at >= datetime.utcnow(),
            )
            .order_by(WatchParty.scheduled_at.asc())
            .limit(limit)
        )

        result = await self.db_session.exec(statement)
        rows = result.all()

        parties: List[Dict[str, Any]] = []
        for party, title_romaji, title_english in rows:
            parties.append(
                {
                    "id": str(party.id),
                    "host_user_id": str(party.host_user_id),
                    "media_id": str(party.media_id),
                    "group_id": str(party.group_id),
                    "title": party.title,
                    "media_title": title_english or title_romaji,
                    "scheduled_at": party.scheduled_at,
                    "status": str(party.status),
                    "stream_url": party.stream_url,
                    "sync_url": party.sync_url,
                }
            )

        return parties
