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
        user_query = self.query()
        user_query = user_query.filter(User.username == username)
        user_query = user_query.filter(User.deleted_at.is_(None))
        
        return await user_query.first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_query = self.query()
        user_query = user_query.filter(User.email == email)
        user_query = user_query.filter(User.deleted_at.is_(None))
        
        return await user_query.first()
    
    async def get_users_in_group(self, group_id: UUID, limit: int = 20, offset: int = 0) -> List[User]:
        """Get users in a specific group."""
        user_query = self.query()
        user_query = user_query.join(GroupMember)
        user_query = user_query.filter(GroupMember.group_id == group_id)
        user_query = user_query.filter(User.deleted_at.is_(None))
        user_query = user_query.limit(limit).offset(offset)
        
        return await user_query.all()
    
    async def get_user_groups(self, user_id: UUID) -> List[GroupMember]:
        """Get all groups a user belongs to."""
        group_query = self.query()
        group_query = group_query.join(GroupMember)
        group_query = group_query.filter(GroupMember.user_id == user_id)
        
        return await group_query.all()
    
    async def get_active_users(self, limit: int = 20) -> List[User]:
        """Get active users."""
        user_query = self.query()
        user_query = user_query.filter(User.is_active == True)
        user_query = user_query.filter(User.deleted_at.is_(None))
        user_query = user_query.limit(limit)
        
        return await user_query.all()
    
    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by username or email."""
        user_query = self.query()
        user_query = user_query.filter(
            (User.username.ilike(f"%{query}%")) | 
            (User.email.ilike(f"%{query}%"))
        )
        user_query = user_query.filter(User.deleted_at.is_(None))
        user_query = user_query.limit(limit)
        
        return await user_query.all()