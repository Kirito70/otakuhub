"""Base repository class for all repositories."""

from typing import TypeVar, Generic, Type
from sqlmodel import SQLModel, Select, select, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import async_sessionmaker


class BaseRepository(Generic[SQLModel]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[SQLModel]):
        self.model = model
        
    async def get_by_id(self, db: AsyncSession, id: str) -> SQLModel | None:
        """Get item by ID."""
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
        
    async def get_all(self, db: AsyncSession) -> list[SQLModel]:
        """Get all items."""
        statement = select(self.model)
        result = await db.execute(statement)
        return result.scalars().all()
        
    async def create(self, db: AsyncSession, obj_in: SQLModel) -> SQLModel:
        """Create new item."""
        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        return obj_in
        
    async def update(self, db: AsyncSession, id: str, obj_in: SQLModel) -> SQLModel | None:
        """Update existing item."""
        db_obj = await self.get_by_id(db, id)
        if db_obj:
            # Update the object fields
            for key, value in obj_in.model_dump(exclude_unset=True).items():
                setattr(db_obj, key, value)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        return None
        
    async def delete(self, db: AsyncSession, id: str) -> bool:
        """Delete item by ID."""
        db_obj = await self.get_by_id(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return True
        return False