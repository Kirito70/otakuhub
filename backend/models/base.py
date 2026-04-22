"""
Base classes for all database models.
"""
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import Any
from core.database import Base

class TimestampMixin:
    """Mixin class for models that need created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SoftDeleteMixin:
    """Mixin class for models that support soft deletes."""
    deleted_at = Column(DateTime(timezone=True), nullable=True)

# Create a base model class with both mixins
class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """Base class for all models with timestamp and soft delete support."""
    __abstract__ = True
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}