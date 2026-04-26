"""Base repository class for OtakuHub backend repositories."""

from typing import TypeVar, Generic, List, Optional
from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common database operations."""
    
    def __init__(self, model: ModelType, db_session: AsyncSession):
        self.model = model
        self.db_session = db_session
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get a model instance by its ID."""
        statement = select(self.model).where(self.model.id == id)
        result = await self.db_session.exec(statement)
        return result.one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """Get all model instances with pagination."""
        statement = select(self.model).offset(offset).limit(limit)
        result = await self.db_session.exec(statement)
        return result.all()
    
    async def create(self, data: dict) -> ModelType:
        """Create a new model instance."""
        instance = self.model(**data)
        self.db_session.add(instance)
        await self.db_session.commit()
        await self.db_session.refresh(instance)
        return instance
    
    async def update(self, id: UUID, data: dict) -> Optional[ModelType]:
        """Update a model instance."""
        instance = await self.get_by_id(id)
        if not instance:
            return None
        
        for key, value in data.items():
            setattr(instance, key, value)
        
        await self.db_session.commit()
        await self.db_session.refresh(instance)
        return instance
    
    async def delete(self, id: UUID) -> bool:
        """Soft delete a model instance."""
        instance = await self.get_by_id(id)
        if not instance:
            return False
        
        # For soft delete, set deleted_at timestamp
        # Note: This assumes your model has a deleted_at field
        if hasattr(instance, 'deleted_at'):
            instance.deleted_at = func.now()
        
        await self.db_session.commit()
        return True
    
    async def count(self) -> int:
        """Get count of all instances."""
        statement = select(func.count(self.model.id))
        result = await self.db_session.exec(statement)
        return result.one_or_none() or 0