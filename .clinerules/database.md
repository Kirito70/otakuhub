---
paths:
  - "backend/models/**"
  - "backend/repositories/**"
  - "alembic/**"
  - "docs/database-schema.md"
---
# Database Rules

## Schema Conventions
- Primary keys: `uuid_generate_v7()` (install `pg_uuidv7` extension) — time-sortable UUIDs
- All timestamps: `TIMESTAMPTZ NOT NULL DEFAULT NOW()` — UTC only
- Soft delete: `deleted_at TIMESTAMPTZ` — NULL means active, set to NOW() to delete
- Foreign keys: always add `ON DELETE RESTRICT` unless you explicitly mean cascade
- Boolean columns: `NOT NULL DEFAULT FALSE` — never nullable booleans
- VARCHAR lengths: be explicit (255 for names, 2048 for URLs, TEXT for freeform)
- Enum types: use PostgreSQL native `CREATE TYPE ... AS ENUM` for fixed sets

## Naming Conventions
- Tables: `snake_case`, plural (e.g., `media_entries`, `user_lists`)
- Columns: `snake_case`
- FK columns: `<referenced_table_singular>_id` (e.g., `media_id`, `user_id`)
- Indexes: `idx_<table>_<column>` (e.g., `idx_media_entries_anilist_id`)
- Unique constraints: `uq_<table>_<column>` (e.g., `uq_users_email`)

## Required Indexes (always add these)
- All FK columns: B-tree index
- `email`, `username`: unique index
- `anilist_id`, `mal_id`, `mangadex_id` in external_ids table: unique indexes
- Full-text search columns (`title_romaji`, `title_english`, `title_native`): GIN tsvector index
- `status` + `media_type` combo: composite B-tree for filtering
- `user_id` + `media_id` in tracking tables: composite unique constraint

## Alembic Workflow
1. Make model change in `backend/models/`
2. `alembic revision --autogenerate -m "add_<description>"`
3. Review generated migration — autogenerate is not always perfect
4. Test upgrade: `alembic upgrade head`
5. Test downgrade: `alembic downgrade -1`
6. Never modify existing migrations — always create new ones

## Join Table Pattern (many-to-many)
```python
# Association table — no extra columns
media_genres = Table(
    "media_genres",
    Base.metadata,
    Column("media_id", UUID, ForeignKey("media_entries.id"), primary_key=True),
    Column("genre_id", UUID, ForeignKey("genres.id"), primary_key=True),
)

# Association object — with extra columns
class UserListEntry(Base):
    __tablename__ = "user_list_entries"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    media_id: Mapped[UUID] = mapped_column(ForeignKey("media_entries.id"), primary_key=True)
    status: Mapped[WatchStatus]
    progress: Mapped[int] = mapped_column(default=0)
    score: Mapped[Optional[float]]
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())
```
