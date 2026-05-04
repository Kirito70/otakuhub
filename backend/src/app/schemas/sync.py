"""Schemas for sync import endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SyncImportRequest(BaseModel):
    """Request payload for external list import."""

    username: Optional[str] = Field(default=None, min_length=1, max_length=255)
    overwrite_existing: bool = False


class SyncImportResponse(BaseModel):
    """Response for queued/started sync import jobs."""

    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    provider: str
    status: str
    job_type: str
    started_at: datetime
    message: str
