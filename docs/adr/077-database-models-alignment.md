# ADR 077 — Database & Models Alignment

**Status**: Proposed
**Date**: 2026-06-04

## Context

Phase 0 (cleanup) and Phase 1 (sync pipeline) are complete. The codebase works on SQLite in-memory, but the intended production target is PostgreSQL 16. A systematic audit (AUDIT-PLAN.md) revealed four categories of database and model misalignment:

1. **UUID v7**: `docs/database-schema.md` specifies `uuid_generate_v7()` (time-ordered UUIDs) but all 28 models use `uuid4()` (random). Time-ordered UUIDs provide better B-tree index performance and natural chronological ordering.

2. **Full-Text Search**: The `title_search` column on `media_entries` is declared as `Column(Text)` (plain text) instead of `TSVECTOR`. No GIN indexes, no trigram indexes, no trigger function for auto-populating the tsvector exist. The search endpoint (`GET /api/v1/media/search`) will fail on PostgreSQL.

3. **Alembic Migration System**: No Alembic infrastructure exists. Schema is managed by `SQLModel.metadata.create_all()` in `database.py` — a development-only approach that is incompatible with production deployment, rollback, and team collaboration.

4. **PostgreSQL Default Configuration**: The default `DATABASE_URL` is `sqlite+aiosqlite:///:memory:` but models use PostgreSQL-specific features (`varchar_pattern_ops` on User indexes, `TSVECTOR` intentions). Pool settings (`db_pool_size`, `db_max_overflow`) exist in config but are not wired to `create_async_engine`.

This ADR covers all four areas plus the missing `UniqueConstraint` on `user_list_entry`.

## Decision

### 2.1 UUID v7 Migration

**Strategy**: Create a portable `generate_uuid7()` function in Python that implements RFC 9562. Use it as the default factory for all model PKs. This works identically on SQLite and PostgreSQL, avoiding any dialect branching.

**Rationale**:
- SQLite does not support `uuid_generate_v7()` (a PostgreSQL-only extension).
- A Python implementation of UUID v7 is deterministic and portable — same value on both DBs.
- The `uuid7` PyPI package exists but we avoid an extra dependency for a ~30-line function.
- PostgreSQL's `pg_uuidv7` extension can be used later for server-side generation, but the Python approach gives us portability now.

**Implementation**:
- New module: `backend/src/app/core/uuid7.py`
- Function: `generate_uuid7() -> UUID` — implements RFC 9562 UUID v7 (Unix timestamp ms + random bits)
- All 28 model files: change `default_factory=uuid4` → `default_factory=generate_uuid7`

**Migration**: Since no production data exists (SQLite in-memory is the default), we can simply change model defaults and recreate tables. An Alembic migration will document this for any future existing-data scenario.

### 2.2 Full-Text Search Setup

**Strategy**: Create a portable `TSVector` SQLAlchemy type that maps to `TSVECTOR` on PostgreSQL and `Text` on SQLite. Create GIN indexes, trigram indexes, and the trigger function as PostgreSQL-only migrations.

**Components**:

1. **`TSVector` type** — New file: `backend/src/app/core/tsvector.py`
   - Uses `sqlalchemy.TSVECTOR` on PostgreSQL
   - Falls back to `sqlalchemy.Text` on SQLite (no-op for tsvector operations)
   - Allows the model to declare `title_search: Optional[str] = Field(sa_column=Column(TSVector()))`

2. **`MediaEntry.title_search`** — Change from `Column(Text)` to `Column(TSVector())`

3. **Trigger function** — Raw SQL migration for PostgreSQL only:
   ```sql
   CREATE OR REPLACE FUNCTION update_media_title_search() RETURNS TRIGGER AS $$
   BEGIN
       NEW.title_search :=
           setweight(to_tsvector('simple', unaccent(coalesce(NEW.title_english, ''))), 'A') ||
           setweight(to_tsvector('simple', unaccent(coalesce(NEW.title_romaji, ''))), 'B') ||
           setweight(to_tsvector('simple', unaccent(coalesce(NEW.title_native, ''))), 'C');
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   ```

4. **Indexes** (PostgreSQL-only, created in migration):
   - GIN index on `title_search` (replaces current b-tree index)
   - GIN trigram indexes on `title_romaji` and `title_english` (for `ILIKE` / `%search%` queries)
   - Requires `pg_trgm` and `unaccent` extensions

5. **On SQLite**: The `TSVector` type maps to `Text`, the trigger is never created, and search falls back to `ILIKE`-based matching (existing behavior). This is acceptable for development/testing.

### 2.3 Alembic Migration System

**Strategy**: Initialize Alembic in `backend/` with async configuration. Create a baseline migration that captures all current tables as they exist. Subsequent migrations handle UUID v7, FTS, and constraint changes.

**Implementation**:

1. **Initialize**:
   ```bash
   cd backend/
   alembic init alembic
   ```
   This creates `alembic/` directory and `alembic.ini`.

2. **Configure for async**:
   - Set `sqlalchemy.url` in `alembic.ini` (or use env var)
   - Modify `alembic/env.py` to use `AsyncEngine` from `src.app.database`
   - Import `SQLModel.metadata` as `target_metadata`
   - Use `run_async()` pattern for async migrations

3. **Baseline migration** — `001_initial_tables.py`:
   - Captures all current 28 tables as-is (with `uuid4()` defaults, `Text` title_search, etc.)
   - This gives us a clean starting point for Alembic tracking

4. **UUID v7 migration** — `002_uuid_v7.py`:
   - No schema DDL changes (UUID type is the same)
   - Documents the UUID v7 policy
   - If migrating existing data, adds `UPDATE` statements (not needed for greenfield)

5. **FTS migration** — `003_fulltext_search.py`:
   - Creates `pg_trgm`, `unaccent`, `btree_gin` extensions (PostgreSQL only)
   - Changes `title_search` from `Text` to `TSVECTOR`
   - Creates GIN index on `title_search`
   - Creates trigram indexes on `title_romaji`, `title_english`
   - Creates trigger function and trigger
   - Backfills `title_search` for existing rows

6. **Workflow documented** in `backend/README.md`:
   ```bash
   alembic upgrade head        # Apply all pending migrations
   alembic downgrade -1         # Rollback one step
   alembic revision --autogenerate -m "description"  # Create new migration
   ```

### 2.4 PostgreSQL Default Configuration

**Strategy**: Change the default `DATABASE_URL` to PostgreSQL. Keep SQLite only for test isolation.

**Changes**:

1. **`backend/src/app/config.py`**:
   - Default `database_url` changes to: `postgresql+asyncpg://postgres:postgres@localhost:5432/otakuhub`
   - Wire `db_pool_size` and `db_max_overflow` into `create_async_engine`

2. **`backend/src/app/database.py`**:
   - Pass `pool_size=settings.db_pool_size` and `max_overflow=settings.db_max_overflow` to `create_async_engine`
   - Keep `connect_db()` with `create_all` as fallback (for tests), but Alembic is the canonical path

3. **Tests (`conftest.py`)**:
   - Continue using `sqlite+aiosqlite://` (tempfile-based)
   - No change needed — tests override `DATABASE_URL` via env var

### 2.5 Missing Constraints

**Strategy**: Add explicit `UniqueConstraint` objects to model `__table_args__` where the schema documentation specifies them. The unique indexes already enforce the constraint — this adds declarative clarity.

**Changes**:

1. **`user_list_entry.py`**: Replace `Index("idx_list_entries_user_media", "user_id", "media_id", unique=True)` with:
   ```python
   UniqueConstraint("user_id", "media_id", name="uq_user_list_entry_user_media"),
   Index("idx_list_entries_user_media", "user_id", "media_id"),
   ```
   Keep both — the unique constraint for enforcement and the index for query performance (PostgreSQL creates an index for unique constraints automatically, but being explicit doesn't hurt and keeps the index name consistent).

2. **`recommendation.py`**: Similar treatment for `(from_user_id, to_user_id, media_id)`.

## Consequences

### Good

- **Portable UUID v7**: Works on both SQLite and PostgreSQL without dialect branching. Time-ordered PKs improve B-tree index performance (new rows are inserted at the end of the index rather than random positions).
- **Real full-text search**: The `GET /api/v1/media/search` endpoint will work properly on PostgreSQL with ranked results, trigram partial matching, and accent-insensitive search.
- **Production-grade migrations**: Alembic enables rollback, team collaboration, and CI/CD pipeline integration for schema changes.
- **Dev/prod parity**: Default PostgreSQL config means developers catch PG-specific issues early rather than at deploy time.
- **Clearer model documentation**: Explicit `UniqueConstraint` declarations make the schema intent readable without cross-referencing the schema doc.

### Bad

- **Dependency on `pg_trgm` and `unaccent` extensions**: Production PostgreSQL must have these installed. They are available in the `contrib` package of standard PostgreSQL distributions.
- **SQLite FTS is degraded**: Search on SQLite will use `ILIKE`-based matching instead of full-text search. Acceptable for local development/testing but developers testing search features should use PostgreSQL.
- **Migration learning curve**: Developers need to learn Alembic workflow. Existing `create_all()` habit must be broken.

### Neutral

- **UUID v7 requires a Python implementation** rather than leveraging the PostgreSQL extension. The ~30-line function is minimal maintenance.
- **Existing test suite uses SQLite**: All 206 tests continue to pass unchanged. No test migration needed.

## Layer Boundary Spec

### What each layer owns

| Layer | Owns |
|-------|------|
| **`core/uuid7.py`** | RFC 9562 UUID v7 generation logic. Single `generate_uuid7()` function. Tested independently. |
| **`core/tsvector.py`** | Portable `TSVector` SQLAlchemy type. Handles dialect mapping (TSVECTOR on PG, Text on SQLite). |
| **Models** | Import and use `generate_uuid7` for PKs. Declare `title_search` with `TSVector` type. Declare `UniqueConstraint` in `__table_args__`. |
| **`config.py`** | Default `database_url` to PostgreSQL. Wire pool settings. |
| **`database.py`** | Pass pool config to engine. Keep `create_all` as fallback for tests. |
| **Alembic** | All schema migrations. Baseline + UUID v7 + FTS migrations. |
| **Repository layer** | No changes needed — query builder pattern is unaffected by these changes. |

### Migration order

1. Alembic initialization (no model changes)
2. UUID v7 migration (model defaults change, no DDL change)
3. FTS migration (DDL: extensions, type change, indexes, trigger)
4. Constraint migration (DDL: UniqueConstraint additions)

### Test implications

- All existing tests continue to use SQLite (tempfile-based, set in `conftest.py`)
- New tests: `test_uuid7.py` for `generate_uuid7()` correctness
- New tests: `test_tsvector.py` for `TSVector` type dialect mapping
- Alembic migration tests: `test_migrations.py` using `alembic.command.upgrade` / `downgrade` against a temporary database
