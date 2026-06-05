"""Add ADR 078 media source provider mapping tables.

Revision ID: 002
Revises: 001
Create Date: 2026-06-06

Adds media_source_mappings and media_source_episodes for backend-only provider
catalog/episode IDs. These tables store availability metadata only, not raw
stream segment URLs.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "media_source_mappings",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_media_id", sa.String(128), nullable=False),
        sa.Column("source_slug", sa.String(300), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("source_title", sa.String(500), nullable=True),
        sa.Column("source_title_normalized", sa.String(500), nullable=True),
        sa.Column("source_payload_hash", sa.String(64), nullable=True),
        sa.Column("mapping_status", sa.String(20), nullable=False, server_default="matched"),
        sa.Column("match_confidence", sa.Numeric(5, 2), nullable=False, server_default="100.00"),
        sa.Column("is_streaming_enabled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("has_sub", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("has_dub", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("episode_count", sa.Integer(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("details_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("source", "source_media_id", name="uq_media_source_mappings_source_media"),
    )
    op.create_index(
        "idx_media_source_mappings_media",
        "media_source_mappings",
        ["media_id", "source"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_media_source_mappings_source_seen",
        "media_source_mappings",
        ["source", "last_seen_at"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_media_source_mappings_status",
        "media_source_mappings",
        ["source", "mapping_status"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_media_source_mappings_title_trgm",
        "media_source_mappings",
        ["source_title_normalized"],
        postgresql_using="gin",
        postgresql_ops={"source_title_normalized": "gin_trgm_ops"},
    )

    op.create_table(
        "media_source_episodes",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("mapping_id", sa.Uuid(), sa.ForeignKey("media_source_mappings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("episode_id", sa.Uuid(), sa.ForeignKey("episodes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_episode_id", sa.String(128), nullable=False),
        sa.Column("episode_number", sa.Numeric(8, 2), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("language", sa.String(20), nullable=False, server_default="sub"),
        sa.Column("embed_path", sa.String(512), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("source", "source_episode_id", "language", name="uq_media_source_episodes_source_episode_language"),
    )
    op.create_index("idx_media_source_episodes_mapping", "media_source_episodes", ["mapping_id", "episode_number"])
    op.create_index(
        "idx_media_source_episodes_media",
        "media_source_episodes",
        ["media_id", "episode_number", "language"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_media_source_episodes_available",
        "media_source_episodes",
        ["source", "is_available", "last_seen_at"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_media_source_episodes_available", table_name="media_source_episodes")
    op.drop_index("idx_media_source_episodes_media", table_name="media_source_episodes")
    op.drop_index("idx_media_source_episodes_mapping", table_name="media_source_episodes")
    op.drop_table("media_source_episodes")
    op.drop_index("idx_media_source_mappings_title_trgm", table_name="media_source_mappings")
    op.drop_index("idx_media_source_mappings_status", table_name="media_source_mappings")
    op.drop_index("idx_media_source_mappings_source_seen", table_name="media_source_mappings")
    op.drop_index("idx_media_source_mappings_media", table_name="media_source_mappings")
    op.drop_table("media_source_mappings")
