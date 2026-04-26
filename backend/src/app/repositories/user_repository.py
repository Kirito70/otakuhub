"""Repository for user-related database operations."""

from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.app.models import User, GroupMember
from src.app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        statement = select(User).where(User.username == username, User.deleted_at.is_(None))
        result = await self.db_session.exec(statement)
        return result.one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.db_session.exec(statement)
        return result.one_or_none()
    
    async def get_users_in_group(self, group_id: UUID, limit: int = 20, offset: int = 0) -> List[User]:
        """Get users in a specific group."""
        statement = select(User).join(GroupMember).where(
            GroupMember.group_id == group_id,
            User.deleted_at.is_(None)
        ).offset(offset).limit(limit)
        
        result = await self.db_session.exec(statement)
        return result.all()
    
    async def get_user_groups(self, user_id: UUID) -> List[GroupMember]:
        """Get all groups a user belongs to."""
        statement = select(GroupMember).where(GroupMember.user_id == user_id)
        result = await self.db_session.exec(statement)
        return result.all()