"""Repository for group‑member operations using the QueryBuilder."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import GroupMember
from src.app.repositories.base_repository import BaseRepository


class GroupMemberRepository(BaseRepository[GroupMember]):
    """Concrete repository for the ``GroupMember`` model.

    ``GroupMember`` does **not** have a ``deleted_at`` column, so the
    QueryBuilder will not apply a soft‑delete filter automatically.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(GroupMember, db_session)

    async def list_by_group(self, group_id: UUID, limit: int = 20, offset: int = 0) -> List[GroupMember]:
        """Return members of a group with pagination."""
        return await (
            self.query()
            .filter(GroupMember.group_id == group_id)
            .limit(limit)
            .offset(offset)
            .all()
        )

    async def list_by_user(self, user_id: UUID) -> List[GroupMember]:
        """Return all group memberships for a user."""
        return await self.query().filter(GroupMember.user_id == user_id).all()

    async def is_member(self, group_id: UUID, user_id: UUID) -> bool:
        """Check if a user is a member of a specific group."""
        return await self.query().filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id).exists()

    async def add_member(self, group_id: UUID, user_id: UUID, role: str = "member") -> GroupMember:
        """Create a new ``GroupMember`` row.

        The ``BaseRepository.create`` method is used for the actual insert.
        """
        data = {"group_id": group_id, "user_id": user_id, "role": role}
        return await self.create(data)

    async def remove_member(self, group_id: UUID, user_id: UUID) -> bool:
        """Soft‑delete a membership (if ``deleted_at`` existed) or hard‑delete.

        ``GroupMember`` currently has no ``deleted_at`` column, so we perform a
        direct delete via a raw statement for efficiency.
        """
        # Direct delete – no soft‑delete column on this table
        stmt = select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        result = await self.db_session.exec(stmt)
        instance = result.one_or_none()
        if not instance:
            return False
        await self.db_session.delete(instance)
        await self.db_session.commit()
        return True
