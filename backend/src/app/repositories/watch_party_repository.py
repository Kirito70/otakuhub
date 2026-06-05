"""Repository for watch party related database operations."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from datetime import datetime

from src.app.models import WatchParty, WatchPartyRsvp, GroupMember
from src.app.models.enums import PartyStatus
from src.app.repositories.base_repository import BaseRepository


class WatchPartyRepository(BaseRepository[WatchParty]):
    """Repository for WatchParty model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(WatchParty, db_session)

    async def get_by_id(self, party_id: UUID) -> Optional[WatchParty]:
        """Get a watch party by ID (soft-deleted rows excluded)."""
        return await self.query().filter(WatchParty.id == party_id).first()

    async def get_upcoming_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[WatchParty]:
        """Get upcoming watch parties visible to a user in their groups."""
        member_group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        q = (
            self.query()
            .filter(WatchParty.status == PartyStatus.scheduled)
            .filter(WatchParty.group_id.in_(member_group_ids))
        )
        if group_id is not None:
            q = q.filter(WatchParty.group_id == group_id)
        return await q.order_by(WatchParty.scheduled_at.asc()).offset(offset).limit(limit).all()

    async def count_upcoming_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
    ) -> int:
        """Count upcoming watch parties visible to a user."""
        member_group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        q = (
            self.query()
            .filter(WatchParty.status == PartyStatus.scheduled)
            .filter(WatchParty.group_id.in_(member_group_ids))
        )
        if group_id is not None:
            q = q.filter(WatchParty.group_id == group_id)
        return await q.count()

    async def get_past_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[WatchParty]:
        """Get past/completed/cancelled watch parties visible to a user."""
        member_group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        q = (
            self.query()
            .filter(WatchParty.group_id.in_(member_group_ids))
            .filter(
                or_(
                    WatchParty.status == PartyStatus.completed,
                    WatchParty.status == PartyStatus.cancelled,
                    WatchParty.scheduled_at < datetime.utcnow(),
                )
            )
        )
        if group_id is not None:
            q = q.filter(WatchParty.group_id == group_id)
        return await q.order_by(WatchParty.scheduled_at.desc()).offset(offset).limit(limit).all()

    async def count_past_for_user(
        self,
        *,
        user_id: UUID,
        group_id: Optional[UUID] = None,
    ) -> int:
        """Count past/completed/cancelled watch parties visible to a user."""
        member_group_ids = select(GroupMember.group_id).where(GroupMember.user_id == user_id)
        q = (
            self.query()
            .filter(WatchParty.group_id.in_(member_group_ids))
            .filter(
                or_(
                    WatchParty.status == PartyStatus.completed,
                    WatchParty.status == PartyStatus.cancelled,
                    WatchParty.scheduled_at < datetime.utcnow(),
                )
            )
        )
        if group_id is not None:
            q = q.filter(WatchParty.group_id == group_id)
        return await q.count()

    async def soft_delete(self, party_id: UUID) -> bool:
        """Soft-delete a watch party by ID."""
        return await self.delete(party_id)


class WatchPartyRsvpRepository(BaseRepository[WatchPartyRsvp]):
    """Repository for WatchPartyRsvp model operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(WatchPartyRsvp, db_session)

    async def get_by_party_and_user(self, party_id: UUID, user_id: UUID) -> Optional[WatchPartyRsvp]:
        """Get RSVP by party and user."""
        return await (
            self.query()
            .filter(WatchPartyRsvp.party_id == party_id)
            .filter(WatchPartyRsvp.user_id == user_id)
            .first()
        )

    async def list_by_party(self, party_id: UUID) -> List[WatchPartyRsvp]:
        """Get all RSVPs for a watch party."""
        return await self.query().filter(WatchPartyRsvp.party_id == party_id).all()

    async def count_attending(self, party_id: UUID) -> int:
        """Count attending RSVPs for a watch party."""
        return await (
            self.query()
            .filter(WatchPartyRsvp.party_id == party_id)
            .filter(WatchPartyRsvp.status == "attending")
            .count()
        )
