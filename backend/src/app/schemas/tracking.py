'''Schemas for tracking (user list entries).'''

from uuid import UUID
from datetime import datetime
from typing import Optional, Any

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
    pass

class ListEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # Minimal fields for response – include id and status
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

    model_config = ConfigDict(from_attributes=True)

    status: Optional[Any] = None
    progress: Optional[int] = None
    score: Optional[float] = None
    notes: Optional[str] = None
    is_private: Optional[bool] = None
    repeat_count: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
