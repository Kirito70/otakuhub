"""User service for managing users and authentication."""

from typing import List, Optional, Dict, Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID
import hashlib
import secrets

from src.app.models import User, RefreshToken, ExternalAuth
from src.app.services.base_service import BaseService
from src.app.schemas.user import UserProfile, UserSettings
from src.app.core.security import verify_password, get_password_hash
from src.app.repositories.user_repository import UserRepository


class UserService(BaseService):
    """Service class for user-related operations."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
        self._user_repository = UserRepository(self.db_session)
    
    @property
    def user_repository(self) -> UserRepository:
        """Get user repository instance."""
        return self._user_repository
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        return await self._user_repository.get_by_id(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return await self._user_repository.get_by_username(username)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return await self._user_repository.get_by_email(email)
    
    async def get_users(self, limit: int = 20, offset: int = 0) -> List[User]:
        """Get list of users with pagination."""
        # Note: This should be updated to use the repository's get_all method with pagination
        statement = select(User).where(User.deleted_at.is_(None)).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        # Hash password if provided
        if 'password_hash' not in user_data and 'password' in user_data:
            user_data['password_hash'] = get_password_hash(user_data['password'])
            del user_data['password']
        
        return await self._user_repository.create(user_data)
    
    async def update_user(self, user_id: UUID, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        # Hash password if it's being updated
        if 'password' in user_data:
            user_data['password_hash'] = get_password_hash(user_data['password'])
            del user_data['password']
            
        return await self._user_repository.update(user_id, user_data)
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Soft delete a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
            
        user.deleted_at = datetime.utcnow()
        await self.db_session.commit()
        return True
    
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
            
        return UserProfile(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            email=user.email,
            avatar_url=user.avatar_url,
            bio=user.bio,
            timezone=user.timezone,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    async def get_user_settings(self, user_id: UUID) -> Optional[UserSettings]:
        """Get user settings."""
        # Note: this would need a separate settings table or model
        # Implementation depends on how settings are stored
        return UserSettings(
            user_id=user_id,
            # Set defaults or fetch from DB if separate settings table exists
        )
    
    async def update_user_settings(self, user_id: UUID, settings_data: Dict[str, Any]) -> Optional[UserSettings]:
        """Update user settings."""
        # Implementation depends on how settings are stored
        # This is a placeholder for now
        return await self.get_user_settings(user_id)
    
    async def get_users_in_group(self, group_id: UUID, limit: int = 20, offset: int = 0) -> List[User]:
        """Get users in a specific group."""
        return await self._user_repository.get_users_in_group(group_id, limit, offset)
    
    async def get_user_groups(self, user_id: UUID) -> List[User]:
        """Get all groups a user belongs to."""
        return await self._user_repository.get_user_groups(user_id)
    
    async def get_active_users(self, limit: int = 20) -> List[User]:
        """Get active users."""
        return await self._user_repository.get_active_users(limit)
    
    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by username or email."""
        return await self._user_repository.search_users(query, limit)