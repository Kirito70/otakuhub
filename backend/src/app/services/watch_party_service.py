"""Watch party service for managing watch parties and RSVPs."""

from typing import List, Optional, Dict, Any
from sqlmodel import select
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import UTC, datetime
from uuid import UUID

from src.app.models import GroupMember, WatchParty, WatchPartyRsvp, MediaEntry, User
from src.app.models.enums import PartyStatus
from src.app.services.base_service import BaseService
from src.app.repositories.watch_party_repository import WatchPartyRepository, WatchPartyRsvpRepository


class WatchPartyService(BaseService):
    """Service class for watch party related operations."""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
        self._watch_party_repo = WatchPartyRepository(self.db_session)
        self._rsvp_repo = WatchPartyRsvpRepository(self.db_session)

    async def get_watch_party(self, party_id: UUID) -> Optional[WatchParty]:
        """Get a watch party by ID."""
        return await self._watch_party_repo.get_by_id(party_id)

    async def get_user_watch_parties(self, user_id: UUID, limit: int = 20) -> List[WatchParty]:
        """Get watch parties for a user."""
        return await (
            self._watch_party_repo.query()
            .filter(WatchParty.deleted_at.is_(None))
            .filter(
                or_(
                    WatchParty.host_user_id == user_id,
                    WatchParty.id.in_(
                        select(WatchPartyRsvp.party_id).where(WatchPartyRsvp.user_id == user_id)
                    )
                )
            )
            .order_by(WatchParty.scheduled_at.desc())
            .limit(limit)
            .all()
        )

    async def get_upcoming_watch_parties(self, group_id: Optional[UUID] = None,
                                       limit: int = 20) -> List[WatchParty]:
        """Get upcoming watch parties."""
        q = (
            self._watch_party_repo.query()
            .filter(WatchParty.status == "scheduled")
            .order_by(WatchParty.scheduled_at.asc())
            .limit(limit)
        )
        if group_id:
            q = q.filter(WatchParty.group_id == group_id)
        return await q.all()

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

        return await self._watch_party_repo.get_upcoming_for_user(
            user_id=user_id, group_id=group_id, limit=limit, offset=offset,
        )

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

        return await self._watch_party_repo.count_upcoming_for_user(
            user_id=user_id, group_id=group_id,
        )

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

        return await self._watch_party_repo.get_past_for_user(
            user_id=user_id, group_id=group_id, limit=limit, offset=offset,
        )

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

        return await self._watch_party_repo.count_past_for_user(
            user_id=user_id, group_id=group_id,
        )

    async def create_watch_party(self, host_user_id: UUID, group_id: UUID, media_id: UUID,
                                title: str, scheduled_at: datetime,
                                episode_number: Optional[int] = None,
                                stream_url: Optional[str] = None,
                                notes: Optional[str] = None) -> WatchParty:
        """Create a new watch party."""
        return await self._watch_party_repo.create(
            {
                "host_user_id": host_user_id,
                "group_id": group_id,
                "media_id": media_id,
                "title": title,
                "scheduled_at": scheduled_at,
                "episode_number": episode_number,
                "stream_url": stream_url,
                "notes": notes,
            }
        )

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
        """Create watch party if host belongs to group and media exists."""
        membership_stmt = select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == host_user_id,
        )
        membership = (await self.db_session.exec(membership_stmt)).one_or_none()
        if membership is None:
            raise PermissionError("User is not a member of this group")

        # Explicit media existence check (works on SQLite which doesn't enforce FK)
        media_stmt = select(MediaEntry).where(MediaEntry.id == media_id)
        media = (await self.db_session.exec(media_stmt)).one_or_none()
        if media is None:
            raise ValueError("Media not found yet; sync/seed required")

        party_data = {
            "host_user_id": host_user_id,
            "group_id": group_id,
            "media_id": media_id,
            "scheduled_at": (scheduled_at.astimezone(UTC).replace(tzinfo=None) if scheduled_at.tzinfo else scheduled_at),
            "title": title,
            "episode_number": episode_number,
            "stream_url": stream_url,
            "sync_url": sync_url,
            "notes": notes,
        }
        try:
            return await self._watch_party_repo.create(party_data)
        except IntegrityError:
            raise ValueError("Media not found yet; sync/seed required")

    async def update_watch_party(
        self, party_id: UUID, updates: Dict[str, Any], *, user_id: UUID | None = None
    ) -> Optional[WatchParty]:
        """Update a watch party. If user_id is provided, only host can update."""
        party = await self._watch_party_repo.get_by_id(party_id)
        if not party:
            return None

        if user_id is not None and party.host_user_id != user_id:
            return None  # caller should raise 403

        for key, value in updates.items():
            setattr(party, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(party)
        return party

    async def delete_watch_party(self, party_id: UUID, *, user_id: UUID | None = None) -> bool:
        """Soft delete a watch party. If user_id is provided, only host can delete."""
        party = await self._watch_party_repo.get_by_id(party_id)
        if not party:
            return False

        if user_id is not None and party.host_user_id != user_id:
            return False  # caller should raise 403

        return await self._watch_party_repo.soft_delete(party_id)

    async def get_rsvps_for_party(self, party_id: UUID) -> List[WatchPartyRsvp]:
        """Get all RSVPs for a watch party."""
        return await self._rsvp_repo.list_by_party(party_id)

    async def rsvp_to_watch_party(self, party_id: UUID, user_id: UUID,
                                status: str = "pending") -> WatchPartyRsvp:
        """RSVP to a watch party."""
        existing_rsvp = await self._rsvp_repo.get_by_party_and_user(party_id, user_id)
        if existing_rsvp:
            existing_rsvp.status = status
            existing_rsvp.responded_at = datetime.utcnow()
            await self.db_session.commit()
            await self.db_session.refresh(existing_rsvp)
            return existing_rsvp
        else:
            return await self._rsvp_repo.create(
                {"party_id": party_id, "user_id": user_id, "status": status}
            )

    async def rsvp_to_watch_party_for_group_member(
        self,
        *,
        party_id: UUID,
        user_id: UUID,
        status: str,
    ) -> WatchPartyRsvp:
        """RSVP only if user is member of the party's group."""
        party = await self._watch_party_repo.get_by_id(party_id)
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
        return await self._rsvp_repo.count_attending(party_id)

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

        # Fetch RSVPs via repo
        rsvps = await self._rsvp_repo.list_by_party(party_id)

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
