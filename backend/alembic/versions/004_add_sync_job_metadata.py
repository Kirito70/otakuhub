"""Add metadata JSON column to sync_jobs for page-level checkpoint/resume.

Revision ID: 004
Revises: 003
Create Date: 2026-06-18

Adds a `metadata` JSON column to the `sync_jobs` table so that the Anikoto
catalog adapter can persist a ``last_completed_page`` checkpoint after each
processed page.  On resume the adapter reads this checkpoint and skips pages
that were already completed, avoiding the need to restart from page 1 on
interruption.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# Portable JSON type: JSONB on PostgreSQL, JSON (→TEXT) on SQLite.
_json_type = sa.JSON().with_variant(JSONB(), "postgresql")

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sync_jobs",
        sa.Column("metadata", _json_type, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sync_jobs", "metadata")
