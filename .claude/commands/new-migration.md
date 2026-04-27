# Create a New Alembic Migration

Given a description of what schema change is needed, produce:

## Step 1 — SQLAlchemy Model Changes
Show the exact additions/modifications to files in `backend/models/`.
Follow all conventions from AGENTS.md:
- UUID v7 PKs
- TIMESTAMPTZ timestamps
- deleted_at soft delete
- Explicit VARCHAR lengths
- Required indexes in `__table_args__`

## Step 2 — Generate the Migration
Run:
```bash
cd backend
alembic revision --autogenerate -m "$MIGRATION_NAME"
```

## Step 3 — Review and Fix Migration
Read the generated file. Autogenerate misses:
- Server defaults (`server_default=sa.text("uuid_generate_v7()")`)
- GIN indexes for full-text search
- Custom PostgreSQL types (enums)
- `onupdate` for `updated_at`

Fix any issues and show the corrected migration.

## Step 4 — Test Round-Trip
```bash
alembic upgrade head       # apply
alembic downgrade -1       # revert
alembic upgrade head       # re-apply
```
Confirm no errors.

## Step 5 — Update docs/database-schema.md
Add the new/modified table(s) to the schema documentation.

## Migration Template for Reference
```python
def upgrade() -> None:
    # Create enum type first if needed
    op.execute("CREATE TYPE watch_status AS ENUM ('watching','completed','paused','dropped','plan_to_watch')")

    op.create_table(
        "user_list_entries",
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("media_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("media_entries.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("status", postgresql.ENUM(name="watch_status"), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("idx_user_list_entries_user_id", "user_list_entries", ["user_id"])
    op.create_index("idx_user_list_entries_status", "user_list_entries", ["status"])

def downgrade() -> None:
    op.drop_index("idx_user_list_entries_status")
    op.drop_index("idx_user_list_entries_user_id")
    op.drop_table("user_list_entries")
    op.execute("DROP TYPE IF EXISTS watch_status")
```
