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


class UserService(BaseService):
    """Service class for user-related operations."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        super().__init__(db_session)
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        statement = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self.db_session.exec(statement)
        return result.one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        statement = select(User).where(User.username == username, User.deleted_at.is_(None))
        result = await self.db_session.exec(statement)
        return result.one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        statement = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.db_session.exec(statement)
        return result.one_or_none()
    
    async def get_users(self, limit: int = 20, offset: int = 0) -> List[User]:
        """Get list of users with pagination."""
        statement = select(User).where(User.deleted_at.is_(None)).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        # Hash password if provided
        if 'password_hash' not in user_data and 'password' in user_data:
            user_data['password_hash'] = get_password_hash(user_data['password'])
            del user_data['password']
        
        user = User(**user_data)
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user
    
    async def update_user(self, user_id: UUID, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
            
        # Hash password if it's being updated
        if 'password' in user_data:
            user_data['password_hash'] = get_password_hash(user_data['password'])
            del user_data['password']
            
        for key, value in user_data.items():
            setattr(user, key, value)
            
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user
    
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
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
            
        # This would include fetching from a settings table or joining with user table
        return UserSettings(
            user_id=user.id,
            # Set defaults or fetch from DB if separate settings table exists
        )
    
    async def update_user_settings(self, user_id: UUID, settings_data: Dict[str, Any]) -> Optional[UserSettings]:
        """Update user settings."""
        # Implementation depends on how settings are stored
        # This is a placeholder for now
        return await self.get_user_settings(user_id)