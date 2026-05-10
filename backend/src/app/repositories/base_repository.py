"""Base repository class for OtakuHub backend repositories."""

from typing import TypeVar, Generic, List, Optional
from sqlmodel import SQLModel, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.app.repositories.query_builder import QueryBuilderPattern


ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common database operations."""

    def __init__(self, model: ModelType, db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    def query(self) -> QueryBuilderPattern:
        """Get a query builder for this repository's model."""
        return QueryBuilderPattern.build(self.model, self.db_session)

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get a model instance by its ID using the QueryBuilder."""
        return await self.query().filter(self.model.id == id).first()

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """Get all model instances with pagination using the QueryBuilder."""
        return await self.query().offset(offset).limit(limit).all()

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
        """Get count of all instances using the QueryBuilder (no filters)."""
        return await self.query().count()
