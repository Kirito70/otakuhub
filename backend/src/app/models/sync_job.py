"""Sync job model for OtakuHub."""

from sqlmodel import SQLModel, Field, Index
from typing import Optional
from uuid import UUID
from src.app.core.uuid7 import generate_uuid7
from datetime import datetime


class SyncJob(SQLModel, table=True):
    """Tracks every run of the background sync pipeline."""

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    job_type: str = Field(nullable=False, max_length=50)  # 'seed', 'backfill_anilist', 'weekly_refresh', 'user_import'
    status: str = Field(default="running", max_length=20)  # 'running', 'completed', 'failed', 'partial'
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")  # NULL for system jobs
    total_items: Optional[int] = Field(default=None)
    processed_items: int = Field(default=0)
    failed_items: int = Field(default=0)
    error_log: Optional[str] = Field(default=None)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Create indexes for performance
    __table_args__ = (
        Index("idx_sync_jobs_type", "job_type", "started_at"),
        Index("idx_sync_jobs_status", "status"),
    )
