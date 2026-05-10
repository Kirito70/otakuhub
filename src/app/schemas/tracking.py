"""Tracking schemas stub for testing."""

from uuid import UUID
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ListEntryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    media_id: UUID
    status: Any
    progress: Optional[int] = None
    score: Optional[float] = None
    notes: Optional[str] = None
    is_private: bool = False
    repeat_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ListEntryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: Optional[Any] = None
    progress: Optional[int] = None
    score: Optional[float] = None
    notes: Optional[str] = None
    is_private: Optional[bool] = None
    repeat_count: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ListEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    media_id: UUID
    status: Any
    progress: Optional[int] = None
    score: Optional[float] = None
    notes: Optional[str] = None
    is_private: bool = False
    repeat_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
