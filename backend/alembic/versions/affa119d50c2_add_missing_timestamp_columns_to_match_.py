"""Add missing timestamp columns to match SQLModel definitions.

Migration 001 created the initial tables but omitted several timestamp
columns that the models define (``created_at``, ``updated_at``,
``deleted_at``).  This migration backfills those columns so the DB
schema matches the model definitions.

Affected tables:
- ``genres``: add created_at, updated_at, deleted_at
- ``media_external_ids``: add deleted_at
- ``media_genre``: add created_at
- ``media_studio``: add created_at
- ``media_tag``: add created_at
- ``recommendations``: add updated_at
- ``related_media``: add created_at
- ``studios``: add created_at, updated_at, deleted_at
- ``tags``: add created_at, updated_at, deleted_at

Revision ID: affa119d50c2
Revises: 8e3bc1b26516
Create Date: 2026-06-18 04:07:49.521308
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'affa119d50c2'
down_revision: Union[str, Sequence[str], None] = '8e3bc1b26516'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing timestamp columns to match model definitions."""

    # ---- genres ----
    op.add_column("genres", sa.Column("created_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))
    op.add_column("genres", sa.Column("updated_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))
    op.add_column("genres", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # ---- media_external_ids (only deleted_at is missing) ----
    op.add_column("media_external_ids", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # ---- media_genre ----
    op.add_column("media_genre", sa.Column("created_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))

    # ---- media_studio ----
    op.add_column("media_studio", sa.Column("created_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))

    # ---- media_tag ----
    op.add_column("media_tag", sa.Column("created_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))

    # ---- recommendations (only updated_at is missing) ----
    op.add_column("recommendations", sa.Column("updated_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))

    # ---- related_media ----
    op.add_column("related_media", sa.Column("created_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))

    # ---- studios ----
    op.add_column("studios", sa.Column("created_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))
    op.add_column("studios", sa.Column("updated_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))
    op.add_column("studios", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # ---- tags ----
    op.add_column("tags", sa.Column("created_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))
    op.add_column("tags", sa.Column("updated_at", sa.DateTime(timezone=True),
                   nullable=False, server_default=sa.func.now()))
    op.add_column("tags", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Remove the timestamp columns that were added (reverse order)."""
    op.drop_column("tags", "deleted_at")
    op.drop_column("tags", "updated_at")
    op.drop_column("tags", "created_at")

    op.drop_column("studios", "deleted_at")
    op.drop_column("studios", "updated_at")
    op.drop_column("studios", "created_at")

    op.drop_column("related_media", "created_at")

    op.drop_column("recommendations", "updated_at")

    op.drop_column("media_tag", "created_at")
    op.drop_column("media_studio", "created_at")
    op.drop_column("media_genre", "created_at")

    op.drop_column("media_external_ids", "deleted_at")

    op.drop_column("genres", "deleted_at")
    op.drop_column("genres", "updated_at")
    op.drop_column("genres", "created_at")
