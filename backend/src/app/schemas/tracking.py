"""Schemas for tracking (user list entries)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.app.models.enums import WatchStatus


class ListEntryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    media_id: UUID
    status: WatchStatus
    progress: int = 0
    score: Optional[float] = None
    notes: Optional[str] = None
    is_private: bool = False
    repeat_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ListEntryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Optional[WatchStatus] = None
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
    user_id: UUID
    media_id: UUID
    status: WatchStatus
    progress: int
    score: Optional[float] = None
    notes: Optional[str] = None
    is_private: bool
    repeat_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[ListEntryResponse]
    total: int
    limit: int
    offset: int


class ListEntryHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entry_id: UUID
    user_id: UUID
    media_id: UUID
    event_type: str
    old_status: Optional[WatchStatus] = None
    new_status: Optional[WatchStatus] = None
    old_progress: Optional[int] = None
    new_progress: Optional[int] = None
    old_score: Optional[float] = None
    new_score: Optional[float] = None
    note: Optional[str] = None
    created_at: datetime


class UserListHistoryResponse(BaseModel):
    items: list[ListEntryHistoryResponse]
    total: int
    limit: int


class CustomListCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    is_public: bool = False
    cover_image: Optional[str] = None
    sort_order: int = 0


class CustomListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: Optional[str] = None
    is_public: bool
    cover_image: Optional[str] = None
    sort_order: int
    created_at: datetime
    updated_at: datetime


class CustomListEntryUpsert(BaseModel):
    media_id: UUID
    sort_order: int = 0
    note: Optional[str] = None


class CustomListEntriesReplaceRequest(BaseModel):
    entries: list[CustomListEntryUpsert]


class CustomListEntriesReplaceResponse(BaseModel):
    list_id: UUID
    total_entries: int
