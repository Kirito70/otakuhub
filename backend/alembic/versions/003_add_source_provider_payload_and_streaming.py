"""Add full source payload JSONB columns and streaming options.

Revision ID: 003
Revises: 002
Create Date: 2026-06-06

Adds `source_payload` (JSONB) and `source_titles` (JSONB) to
`media_source_mappings` for full API response archival and structured multilingual
titles.  On `media_source_episodes`: renames `embed_path` → `embed_url`,
widens to VARCHAR(2048), adds `embed_urls` (JSONB) for all language→URL
mappings, `source_payload` (JSONB) for raw episode payload, and
`details_synced_at` for per-episode detail-sync tracking.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import sqlite

# Portable JSON type: JSONB on PostgreSQL, TEXT on SQLite.
# SQLAlchemy's generic sa.JSON is used for the column type in the migration;
# the actual DB type is determined by the dialect (JSON on PG which accepts
# JSONB-compatible data, TEXT on SQLite).
_json_type = sa.JSON().with_variant(JSONB(), "postgresql")

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # media_source_mappings — add source_payload + source_titles
    op.add_column(
        "media_source_mappings",
        sa.Column("source_payload", _json_type, nullable=True),
    )
    op.add_column(
        "media_source_mappings",
        sa.Column("source_titles", _json_type, nullable=True),
    )

    # media_source_episodes — rename embed_path → embed_url, widen, add columns
    op.alter_column(
        "media_source_episodes",
        "embed_path",
        new_column_name="embed_url",
        existing_type=sa.String(512),
    )
    op.alter_column(
        "media_source_episodes",
        "embed_url",
        type_=sa.String(2048),
        existing_type=sa.String(512),
    )
    op.add_column(
        "media_source_episodes",
        sa.Column("embed_urls", _json_type, nullable=True),
    )
    op.add_column(
        "media_source_episodes",
        sa.Column("source_payload", _json_type, nullable=True),
    )
    op.add_column(
        "media_source_episodes",
        sa.Column("details_synced_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # media_source_episodes — drop new columns, revert embed_url → embed_path
    op.drop_column("media_source_episodes", "details_synced_at")
    op.drop_column("media_source_episodes", "source_payload")
    op.drop_column("media_source_episodes", "embed_urls")
    op.alter_column(
        "media_source_episodes",
        "embed_url",
        new_column_name="embed_path",
        existing_type=sa.String(2048),
    )
    op.alter_column(
        "media_source_episodes",
        "embed_path",
        type_=sa.String(512),
        existing_type=sa.String(2048),
    )

    # media_source_mappings — drop new columns
    op.drop_column("media_source_mappings", "source_titles")
    op.drop_column("media_source_mappings", "source_payload")
