"""Watch party service for managing watch parties and RSVPs."""

from typing import List, Optional, Dict, Any
from sqlmodel import select, and_, func
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import UTC, datetime
from uuid import UUID

from src.app.models import GroupMember, WatchParty, WatchPartyRsvp, MediaEntry, User
from src.app.models.enums import PartyStatus
from src.app.services.base_service import BaseService


class WatchPartyService(BaseService):
    """Service class for watch party related operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)

    async def get_watch_party(self, party_id: UUID) -> Optional[WatchParty]:
        """Get a watch party by ID."""
        statement = select(WatchParty).where(WatchParty.id == party_id, WatchParty.deleted_at.is_(None))
        result = await self.db_session.exec(statement)
        return result.one_or_none()

    async def get_user_watch_parties(self, user_id: UUID, limit: int = 20) -> List[WatchParty]:
        """Get watch parties for a user."""
        # Get parties where user is the host or has RSVP'd
        statement = select(WatchParty).where(
            and_(
                WatchParty.deleted_at.is_(None),
                or_(
                    WatchParty.host_user_id == user_id,
                    WatchParty.id.in_(
                        select(WatchPartyRsvp.party_id).where(WatchPartyRsvp.user_id == user_id)
                    )
                )
            )
        ).order_by(WatchParty.scheduled_at.desc()).limit(limit)

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_upcoming_watch_parties(self, group_id: Optional[UUID] = None,
                                       limit: int = 20) -> List[WatchParty]:
        """Get upcoming watch parties."""
        statement = select(WatchParty).where(
            and_(
                WatchParty.deleted_at.is_(None),
                WatchParty.status == "scheduled"
            )
        ).order_by(WatchParty.scheduled_at.asc()).limit(limit)

        if group_id:
            statement = statement.where(WatchParty.group_id == group_id)

        result = await self.db_session.exec(statement)
        return result.all()

    async def get_upcoming_watch_parties_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[WatchParty]:
        """Get upcoming watch parties visible to a user in their groups."""
        if group_id is not None:
            membership_stmt = select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
            membership = (await self.db_session.exec(membership_stmt)).one_or_none()
            if membership is None:
                raise PermissionError("User is not a member of this group")

        member_group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        statement = select(WatchParty).where(
            WatchParty.deleted_at.is_(None),
            WatchParty.status == PartyStatus.scheduled,
            WatchParty.group_id.in_(member_group_ids_stmt),
        )
        if group_id is not None:
            statement = statement.where(WatchParty.group_id == group_id)

        statement = statement.order_by(WatchParty.scheduled_at.asc()).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()

    async def count_upcoming_watch_parties_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
    ) -> int:
        """Count upcoming watch parties visible to a user."""
        if group_id is not None:
            membership_stmt = select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
            membership = (await self.db_session.exec(membership_stmt)).one_or_none()
            if membership is None:
                raise PermissionError("User is not a member of this group")

        member_group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        statement = select(func.count(WatchParty.id)).where(
            WatchParty.deleted_at.is_(None),
            WatchParty.status == PartyStatus.scheduled,
            WatchParty.group_id.in_(member_group_ids_stmt),
        )
        if group_id is not None:
            statement = statement.where(WatchParty.group_id == group_id)

        result = await self.db_session.exec(statement)
        return result.one_or_none() or 0

    async def get_past_watch_parties_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[WatchParty]:
        """Get past/completed/cancelled watch parties visible to a user in their groups."""
        if group_id is not None:
            membership_stmt = select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
            membership = (await self.db_session.exec(membership_stmt)).one_or_none()
            if membership is None:
                raise PermissionError("User is not a member of this group")

        member_group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        statement = select(WatchParty).where(
            WatchParty.deleted_at.is_(None),
            WatchParty.group_id.in_(member_group_ids_stmt),
            or_(
                WatchParty.status == PartyStatus.completed,
                WatchParty.status == PartyStatus.cancelled,
                WatchParty.scheduled_at < datetime.utcnow(),
            ),
        )
        if group_id is not None:
            statement = statement.where(WatchParty.group_id == group_id)

        statement = statement.order_by(WatchParty.scheduled_at.desc()).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()

    async def count_past_watch_parties_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
    ) -> int:
        """Count past/completed/cancelled watch parties visible to a user."""
        if group_id is not None:
            membership_stmt = select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
            )
            membership = (await self.db_session.exec(membership_stmt)).one_or_none()
            if membership is None:
                raise PermissionError("User is not a member of this group")

        member_group_ids_stmt = select(GroupMember.group_id).where(GroupMember.user_id == user_id)

        statement = select(func.count(WatchParty.id)).where(
            WatchParty.deleted_at.is_(None),
            WatchParty.group_id.in_(member_group_ids_stmt),
            or_(
                WatchParty.status == PartyStatus.completed,
                WatchParty.status == PartyStatus.cancelled,
                WatchParty.scheduled_at < datetime.utcnow(),
            ),
        )
        if group_id is not None:
            statement = statement.where(WatchParty.group_id == group_id)

        result = await self.db_session.exec(statement)
        return result.one_or_none() or 0

    async def create_watch_party(self, host_user_id: UUID, group_id: UUID, media_id: UUID,
                                title: str, scheduled_at: datetime,
                                episode_number: Optional[int] = None,
                                stream_url: Optional[str] = None,
                                notes: Optional[str] = None) -> WatchParty:
        """Create a new watch party."""
        party = WatchParty(
            host_user_id=host_user_id,
            group_id=group_id,
            media_id=media_id,
            title=title,
            scheduled_at=scheduled_at,
            episode_number=episode_number,
            stream_url=stream_url,
            notes=notes
        )
        self.db_session.add(party)
        await self.db_session.commit()
        await self.db_session.refresh(party)
        return party

    async def create_watch_party_for_group_member(
        self,
        *,
        host_user_id: UUID,
        group_id: UUID,
        media_id: UUID,
        scheduled_at: datetime,
        title: Optional[str] = None,
        episode_number: Optional[int] = None,
        stream_url: Optional[str] = None,
        sync_url: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> WatchParty:
        """Create watch party if host belongs to group."""
        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == host_user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this group")

        party = WatchParty(
            host_user_id=host_user_id,
            group_id=group_id,
            media_id=media_id,
            scheduled_at=(scheduled_at.astimezone(UTC).replace(tzinfo=None) if scheduled_at.tzinfo else scheduled_at),
            title=title,
            episode_number=episode_number,
            stream_url=stream_url,
            sync_url=sync_url,
            notes=notes,
        )
        self.db_session.add(party)
        try:
            await self.db_session.commit()
        except IntegrityError as exc:
            await self.db_session.rollback()
            raise ValueError("Media not found yet; sync/seed required") from exc

        await self.db_session.refresh(party)
        return party

    async def update_watch_party(self, party_id: UUID, updates: Dict[str, Any]) -> Optional[WatchParty]:
        """Update a watch party."""
        party = await self.get_watch_party(party_id)
        if not party:
            return None

        for key, value in updates.items():
            setattr(party, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(party)
        return party

    async def delete_watch_party(self, party_id: UUID) -> bool:
        """Soft delete a watch party."""
        party = await self.get_watch_party(party_id)
        if not party:
            return False

        party.deleted_at = datetime.utcnow()
        await self.db_session.commit()
        return True

    async def get_rsvps_for_party(self, party_id: UUID) -> List[WatchPartyRsvp]:
        """Get all RSVPs for a watch party."""
        statement = select(WatchPartyRsvp).where(WatchPartyRsvp.party_id == party_id)
        result = await self.db_session.exec(statement)
        return result.all()

    async def rsvp_to_watch_party(self, party_id: UUID, user_id: UUID,
                                status: str = "pending") -> WatchPartyRsvp:
        """RSVP to a watch party."""
        # Check if user is already RSVP'd
        statement = select(WatchPartyRsvp).where(
            and_(
                WatchPartyRsvp.party_id == party_id,
                WatchPartyRsvp.user_id == user_id
            )
        )
        result = await self.db_session.exec(statement)
        existing_rsvp = result.one_or_none()

        if existing_rsvp:
            # Update existing RSVP
            existing_rsvp.status = status
            existing_rsvp.responded_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(existing_rsvp)
            return existing_rsvp
        else:
            # Create new RSVP
            rsvp = WatchPartyRsvp(
                party_id=party_id,
                user_id=user_id,
                status=status
            )
            self.db_session.add(rsvp)
            await self.db_session.commit()
            await self.db_session.refresh(rsvp)
            return rsvp

    async def rsvp_to_watch_party_for_group_member(
        self,
        *,
        party_id: UUID,
        user_id: UUID,
        status: str,
    ) -> WatchPartyRsvp:
        """RSVP only if user is member of the party's group."""
        party = await self.get_watch_party(party_id)
        if party is None:
            raise LookupError("Watch party not found")

        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == party.group_id,
            GroupMember.user_id == user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this watch party group")

        return await self.rsvp_to_watch_party(party_id=party_id, user_id=user_id, status=status)

    async def get_party_attendee_count(self, party_id: UUID) -> int:
        """Get the count of people attending a watch party."""
        statement = select(func.count(WatchPartyRsvp.id)).where(
            and_(
                WatchPartyRsvp.party_id == party_id,
                WatchPartyRsvp.status == "attending"
            )
        )
        result = await self.db_session.exec(statement)
        return result.one_or_none() or 0

    async def get_watch_party_detail(
        self,
        *,
        party_id: UUID,
        user_id: UUID,
    ) -> dict:
        """Get watch party detail with media title, host info, and RSVP summary.

        Raises LookupError if party not found.
        Raises PermissionError if user is not a member of the party's group.
        """
        # Fetch party joined with media and host user
        statement = (
            select(
                WatchParty,
                MediaEntry.title_romaji,
                MediaEntry.title_english,
                MediaEntry.cover_image_medium,
                User.username,
                User.display_name,
            )
            .join(MediaEntry, MediaEntry.id == WatchParty.media_id)
            .join(User, User.id == WatchParty.host_user_id)
            .where(
                WatchParty.id == party_id,
                WatchParty.deleted_at.is_(None),
            )
        )
        result = await self.db_session.exec(statement)
        row = result.one_or_none()

        if row is None:
            raise LookupError("Watch party not found")

        party, title_romaji, title_english, cover_medium, host_username, host_display_name = row

        # Check group membership
        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == party.group_id,
            GroupMember.user_id == user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this group")

        # Fetch RSVPs
        rsvps = await self.get_rsvps_for_party(party_id)

        # Build RSVP summary
        rsvp_summary: dict[str, int] = {"attending": 0, "pending": 0, "declined": 0}
        for rsvp in rsvps:
            status_key = rsvp.status.value if hasattr(rsvp.status, "value") else str(rsvp.status)
            if status_key in rsvp_summary:
                rsvp_summary[status_key] += 1

        return {
            "id": party.id,
            "group_id": party.group_id,
            "host_user_id": party.host_user_id,
            "host_username": host_username,
            "host_display_name": host_display_name,
            "media_id": party.media_id,
            "media_title": title_english or title_romaji,
            "media_cover": cover_medium,
            "episode_number": party.episode_number,
            "title": party.title,
            "scheduled_at": party.scheduled_at,
            "status": party.status.value if hasattr(party.status, "value") else str(party.status),
            "stream_url": party.stream_url,
            "sync_url": party.sync_url,
            "notes": party.notes,
            "created_at": party.created_at,
            "updated_at": party.updated_at,
            "rsvp_summary": rsvp_summary,
            "attendee_count": rsvp_summary["attending"],
        }
