"""Add created_at column to sync_jobs.

The SyncJob model has a ``created_at`` timestamp field, but migration 001
(which created the table) did not include it. This migration adds the
missing column.

Also fixes the model-side FK reference ``user.id`` → ``users.id`` (no
DB-level change needed — the migration-001 FK already references
``users.id`` correctly; only the model annotation was wrong).

Revision ID: 8e3bc1b26516
Revises: 004
Create Date: 2026-06-18 03:44:50.391611
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e3bc1b26516'
down_revision: Union[str, Sequence[str], None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add created_at column to sync_jobs."""
    op.add_column(
        "sync_jobs",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Remove created_at column from sync_jobs."""
    op.drop_column("sync_jobs", "created_at")
