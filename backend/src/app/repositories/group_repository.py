"""Repository for group‑related database operations using the QueryBuilder."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Group
from src.app.repositories.base_repository import BaseRepository


class GroupRepository(BaseRepository[Group]):
    """Concrete repository for the ``Group`` model.

    All read operations go through ``self.query()`` which automatically
    applies the soft‑delete filter (see ADR 006). Write operations use the
    base class helpers.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Group, db_session)

    async def get_by_id(self, group_id: UUID) -> Optional[Group]:
        """Fetch a group by its primary key (soft‑deleted rows are excluded)."""
        return await self.query().filter(Group.id == group_id).first()

    async def get_by_invite_code(self, code: str) -> Optional[Group]:
        """Lookup a group via its unique ``invite_code``."""
        return await self.query().filter(Group.invite_code == code).first()

    async def list_by_owner(self, owner_id: UUID, limit: int = 20, offset: int = 0) -> List[Group]:
        """Return groups owned by a specific user with pagination."""
        return await (
            self.query()
            .filter(Group.owner_id == owner_id)
            .limit(limit)
            .offset(offset)
            .all()
        )

    async def list_public(self, limit: int = 20, offset: int = 0) -> List[Group]:
        """Return public groups (``is_private=False``) with pagination."""
        return await (
            self.query()
            .filter(Group.is_private == False)  # noqa: E712 – intentional boolean comparison
            .limit(limit)
            .offset(offset)
            .all()
        )

    async def exists_by_name(self, name: str) -> bool:
        """Check whether a group with the given name already exists (case‑insensitive)."""
        return await self.query().filter(Group.name.ilike(name)).exists()
