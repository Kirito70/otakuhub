# OtakuHub — Project Prompt Sequence

> This file contains every prompt needed to build OtakuHub from scratch.
> Read PROJECT-STATUS.md first to find the current phase.
> Each phase has a designated primary tool and a "next phase" advance command.
> Copy the prompt for the current sub-phase and paste it into the designated tool.

---

## How to Use This File

1. Open `PROJECT-STATUS.md` — find `CURRENT_PHASE` and `CURRENT_SUB_PHASE`
2. Find that phase section below
3. Read the **Primary tool** for that phase
4. Copy the prompt block and paste it into that tool
5. When the sub-phase is done, run the **advance command** in that tool
6. The AI will update `PROJECT-STATUS.md` and move to the next sub-phase

---

## Advance Commands (copy-paste into any tool at phase end)

These are the universal "move to next" commands for each tool:

### Claude Code
```
/next-phase
```
*(defined in .claude/commands/next-phase.md — created in Phase 1.1)*

### Cline
```
Read PROJECT-STATUS.md, mark the current sub-phase as complete, advance to the next sub-phase, and tell me what the next task is.
```

### OpenCode (terminal)
```
@architect Read PROJECT-STATUS.md, mark the current sub-phase ✅, set CURRENT_SUB_PHASE to the next pending item, add a Completion Log entry, and summarise the next task.
```

### Antigravity
```
/advance-phase
```
*(defined as a workflow in .agents/workflows/)*

### GitHub Copilot (VS Code chat)
```
Read PROJECT-STATUS.md and tell me what the next task is. Mark the current sub-phase complete first.
```

---

# PHASE 1 — Foundation & Infrastructure

**Primary tool**: Claude Code or OpenCode
**Goal**: Monorepo skeleton, Docker dev environment, all tools wired up.

---

### Prompt 1.1 — Monorepo structure
```
Read AGENTS.md and PROJECT-STATUS.md.

Create the complete OtakuHub monorepo directory structure:

backend/
  main.py
  core/__init__.py
  models/__init__.py
  schemas/__init__.py
  repositories/__init__.py
  services/__init__.py
  routers/__init__.py
  workers/__init__.py
  external/__init__.py
  alembic/
    env.py
    versions/
  requirements.txt
  requirements-dev.txt
  pytest.ini
  mypy.ini
  .ruff.toml

mobile/
  (empty — Flutter init comes in 1.6)

infra/
  docker-compose.dev.yml
  docker-compose.prod.yml
  nginx/
    nginx.conf
  postgres/
    init.sql

scripts/
  seed_anime_db.py
  trigger_backfill.py
  weekly_refresh.py

docs/
  adr/

.env.example
.gitignore
README.md

Create placeholder files (not full implementations yet — just correct structure).
After creating, update PROJECT-STATUS.md: mark 1.1 ✅, set CURRENT_SUB_PHASE to 1.2.
```

---

### Prompt 1.2 — Docker Compose dev stack
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 1.2.

Create infra/docker-compose.dev.yml with these services:
- postgres:16-alpine — port 5432, volume for data, health check
- redis:8-alpine — port 6379, password from env, health check
- backend — builds from backend/, uvicorn --reload, depends on postgres+redis
- worker — same image as backend, runs celery worker, depends on postgres+redis
- flower — celery monitoring UI on port 5555

Create infra/docker-compose.prod.yml with:
- Same services but no --reload
- nginx service (port 80+443) using infra/nginx/nginx.conf
- restart: unless-stopped on all services
- No port exposure except nginx

Create .env.example with ALL required variables:
DATABASE_URL, REDIS_URL, JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
REFRESH_TOKEN_EXPIRE_DAYS, ANILIST_CLIENT_ID, ANILIST_CLIENT_SECRET,
MAL_CLIENT_ID, MANGADEX_USERNAME, MANGADEX_PASSWORD, APPRISE_URLS,
FRONTEND_URL, ALLOWED_ORIGINS, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

Create backend/Dockerfile (python:3.12-slim, installs requirements, runs uvicorn).

After creating, update PROJECT-STATUS.md: mark 1.2 ✅, advance to 1.3.
```

---

### Prompt 1.3 — Docker Compose prod + Nginx
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 1.3.

Create infra/nginx/nginx.conf:
- Upstream to backend on port 8000
- /api/ → proxy to backend
- / → serve Flutter web build from /var/www/html
- Gzip enabled
- Security headers: X-Frame-Options, X-Content-Type-Options, HSTS
- WebSocket support for Celery Flower

Create infra/postgres/init.sql:
- CREATE EXTENSION IF NOT EXISTS "pg_uuidv7";
- CREATE EXTENSION IF NOT EXISTS "pg_trgm";
- CREATE EXTENSION IF NOT EXISTS "unaccent";
- CREATE EXTENSION IF NOT EXISTS "btree_gin";

Update docker-compose.prod.yml to mount nginx.conf and Flutter web build.

After creating, update PROJECT-STATUS.md: mark 1.3 ✅, advance to 1.4.
```

---

### Prompt 1.4 — FastAPI app skeleton
```
Read AGENTS.md, docs/backend-architecture.md, and PROJECT-STATUS.md. Current task: 1.4.

Create the FastAPI application skeleton:

backend/core/config.py — Pydantic Settings reading from env:
  DATABASE_URL, REDIS_URL, JWT_SECRET, JWT_ALGORITHM, token expiry,
  external API keys, ALLOWED_ORIGINS list, DEBUG bool

backend/core/database.py — AsyncEngine + AsyncSessionLocal + get_db dependency

backend/core/redis.py — Redis connection pool using REDIS_URL from config

backend/core/auth.py — JWT create_access_token, verify_token, get_current_user dependency

backend/core/security.py — bcrypt hash_password, verify_password

backend/models/base.py — DeclarativeBase + TimestampMixin (created_at, updated_at, deleted_at)

backend/main.py — FastAPI app factory:
  - CORSMiddleware with ALLOWED_ORIGINS from config
  - Include all routers (placeholder imports for now)
  - Lifespan handler for startup/shutdown

backend/routers/health.py:
  GET /health → {"status": "ok"}
  GET /api/v1/status → check DB + Redis connections → {"db": "ok", "redis": "ok"}

backend/requirements.txt:
  fastapi, uvicorn[standard], sqlalchemy[asyncio], asyncpg, alembic,
  pydantic[email], pydantic-settings, python-jose[cryptography], passlib[bcrypt],
  httpx, celery[redis], redis, apprise

backend/requirements-dev.txt:
  pytest, pytest-asyncio, httpx, ruff, mypy, coverage

After creating, run: cd backend && python -m pytest --collect-only (should find 0 tests, no errors).
Update PROJECT-STATUS.md: mark 1.4 ✅, advance to 1.5.
```

---

### Prompt 1.5 — Alembic configuration
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 1.5.

Configure Alembic for async SQLAlchemy:

backend/alembic/env.py — async-compatible env.py:
  - Imports all models from backend/models/ so autogenerate sees them
  - Uses AsyncEngine from core/database.py
  - Sets target_metadata = Base.metadata
  - Runs migrations in async context

backend/alembic.ini — points to backend/alembic/versions/

Create the first migration: alembic revision -m "initial_setup"
  - upgrade(): CREATE EXTENSION statements (pg_uuidv7, pg_trgm, unaccent, btree_gin)
  - downgrade(): DROP EXTENSION statements

Test: alembic upgrade head → alembic downgrade -1 → alembic upgrade head (all must succeed).

Update PROJECT-STATUS.md: mark 1.5 ✅, advance to 1.6.
```

---

### Prompt 1.6 — Flutter project init
**Primary tool**: Antigravity or Claude Code
```
Read AGENTS.md, docs/flutter-architecture.md, and PROJECT-STATUS.md. Current task: 1.6.

Create the Flutter app:

  flutter create mobile --org com.otakuhub --project-name otakuhub --platforms android,ios,web,windows,linux

Then set up pubspec.yaml with ALL required dependencies:
  flutter_riverpod, riverpod_annotation, go_router, dio, freezed_annotation,
  json_annotation, cached_network_image, flutter_secure_storage,
  flutter_adaptive_scaffold, intl, envied

Dev dependencies:
  riverpod_generator, freezed, json_serializable, build_runner,
  flutter_test, mocktail, flutter_lints

Create mobile/analysis_options.yaml — strict lints.

Create the folder structure from docs/flutter-architecture.md:
  lib/core/config/, lib/core/network/, lib/core/router/,
  lib/core/storage/, lib/core/theme/, lib/core/widgets/
  lib/features/ (empty, sub-folders created per feature)

Create lib/main.dart — ProviderScope wrapping the app.
Create lib/app.dart — MaterialApp.router with GoRouter placeholder.
Create lib/core/theme/app_theme.dart — Material 3 light + dark theme.

Run: flutter pub get && dart analyze
Must complete with zero errors.

Update PROJECT-STATUS.md: mark 1.6 ✅, advance to 1.7.
```

---

### Prompt 1.7 — GitHub Actions CI
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 1.7.

Create .github/workflows/ci.yml with two jobs:

Job 1: backend
  - ubuntu-latest, Python 3.12
  - Install: pip install -r backend/requirements.txt -r backend/requirements-dev.txt
  - Run: cd backend && ruff check . && mypy . && pytest tests/ --asyncio-mode=auto

Job 2: flutter
  - ubuntu-latest, Flutter stable
  - Run: cd mobile && flutter pub get && dart analyze && flutter test

Trigger: push to main, pull_request to main.

Also create .github/workflows/build-flutter-web.yml:
  - On push to main only
  - Build Flutter web: flutter build web --release --wasm
  - Upload to GitHub Pages (or artifact for manual deploy)

Update PROJECT-STATUS.md: mark 1.7 ✅, advance to 1.8.
```

---

### Prompt 1.8 — Environment files
```
Read PROJECT-STATUS.md. Current task: 1.8.

Create backend/.env.example — copy from root .env.example, backend-specific:
  DATABASE_URL=postgresql+asyncpg://otakuhub:changeme@localhost:5432/otakuhub_dev
  REDIS_URL=redis://:changeme@localhost:6379/0
  JWT_SECRET=change-this-to-32-random-bytes
  ... (all vars)

Create mobile/.env.example:
  API_BASE_URL=http://localhost:8000
  API_BASE_URL_PROD=https://otakuhub.yourdomain.com

Create mobile/lib/core/config/app_config.dart — reads from env using envied.

Add to .gitignore: .env, *.env, !*.env.example

Create README.md with:
  - Project description
  - Setup steps (clone → copy .env.example → docker compose up → seed DB)
  - How to run backend locally
  - How to run Flutter on each platform
  - How to run tests

PHASE 1 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 1.8 ✅
  - Set CURRENT_PHASE to 2, CURRENT_SUB_PHASE to 2.1
  - Set STATUS to IN_PROGRESS
  - Add Phase 1 complete entry to Completion Log
```

---

# PHASE 2 — Database & Backend Core

**Primary tool**: Claude Code or OpenCode (use `@db-designer` agent)
**Goal**: All 28 tables live in PostgreSQL.

---

### Prompt 2.1–2.2 — Extensions and enums
```
Read AGENTS.md, docs/database-schema.md, and PROJECT-STATUS.md. Current task: 2.1–2.2.

Use the db-migrations skill (.claude/skills/db-migrations/SKILL.md).

Create Alembic migration "create_enums_and_extensions":
  upgrade():
    - Ensure all 4 extensions exist (pg_uuidv7, pg_trgm, unaccent, btree_gin)
    - CREATE TYPE for all enums from docs/database-schema.md:
      media_type_enum, media_format_enum, media_status_enum, season_enum,
      watch_status_enum, relation_type_enum, notif_type_enum,
      party_status_enum, rsvp_status_enum
  downgrade():
    - DROP TYPE for all enums in reverse order

Test round-trip: upgrade → downgrade → upgrade.
Update PROJECT-STATUS.md: mark 2.1 and 2.2 ✅, advance to 2.3.
```

---

### Prompt 2.3 — Media catalogue tables
```
Read AGENTS.md, docs/database-schema.md, and PROJECT-STATUS.md. Current task: 2.3.

Use the db-migrations skill.

Create SQLAlchemy models in backend/models/media.py for:
  MediaEntry, MediaExternalIds, Genre, Studio, Tag
  Association tables: media_genres, media_studios, media_tags
  RelatedMedia, Episode, Chapter

Follow docs/database-schema.md exactly — every column, type, index, constraint.
Include the tsvector trigger for full-text search on MediaEntry.

Create Alembic migration "create_media_catalogue_tables".
Test round-trip.
Update PROJECT-STATUS.md: mark 2.3 ✅, advance to 2.4.
```

---

### Prompt 2.4–2.5 — User, auth, group tables
```
Read AGENTS.md, docs/database-schema.md, and PROJECT-STATUS.md. Current task: 2.4–2.5.

Create SQLAlchemy models:
  backend/models/user.py — User, RefreshToken, ExternalAuth
  backend/models/group.py — Group, GroupMember

Follow docs/database-schema.md exactly for all columns, constraints, and indexes.
Note: users table uses case-insensitive unique indexes on username and email.

Create Alembic migration "create_user_auth_group_tables".
Test round-trip.
Update PROJECT-STATUS.md: mark 2.4 and 2.5 ✅, advance to 2.6.
```

---

### Prompt 2.6–2.10 — Tracking, social, watchparty, notifications, sync tables
```
Read AGENTS.md, docs/database-schema.md, and PROJECT-STATUS.md. Current task: 2.6–2.10.

Create SQLAlchemy models:
  backend/models/tracking.py — UserListEntry, ListEntryHistory, CustomList, CustomListEntry
  backend/models/social.py — Recommendation, Discussion, DiscussionReply
  backend/models/watchparty.py — WatchParty, WatchPartyRsvp
  backend/models/notification.py — NotificationPreference, Notification
  backend/models/sync.py — SyncJob

Follow docs/database-schema.md exactly.

Create single Alembic migration "create_all_remaining_tables" for all of these.
Test round-trip.

After migration succeeds, confirm table count:
  docker exec otakuhub-db psql -U otakuhub -c "\dt" | grep -c "public"
  Expected: 28 tables

Update PROJECT-STATUS.md: mark 2.6–2.10 ✅, advance to 2.11.
```

---

### Prompt 2.11–2.14 — Models, repositories, health endpoints
```
Read AGENTS.md, docs/backend-architecture.md, and PROJECT-STATUS.md. Current task: 2.11–2.14.

1. Ensure all models are imported in backend/models/__init__.py

2. Create repository base class backend/repositories/base.py:
   class BaseRepository with generic get_by_id, create, update, soft_delete methods

3. Scaffold (empty method stubs) repositories for each domain:
   backend/repositories/media_repository.py
   backend/repositories/user_repository.py
   backend/repositories/tracking_repository.py
   backend/repositories/social_repository.py

4. Create health endpoints in backend/routers/health.py:
   GET /health → {"status": "ok", "version": "1.0.0"}
   GET /api/v1/status →
     check DB with "SELECT 1"
     check Redis with redis.ping()
     return {"db": "ok|error", "redis": "ok|error", "timestamp": "..."}

5. Register health router in backend/main.py

6. Write test: tests/routers/test_health.py
   - GET /health returns 200
   - GET /api/v1/status returns 200 with both services ok

Run tests: pytest tests/ -v

PHASE 2 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 2.11–2.14 ✅
  - Set CURRENT_PHASE to 3, CURRENT_SUB_PHASE to 3.1
  - Add Phase 2 complete to Completion Log
```

---

# PHASE 3 — Anime Metadata Pipeline

**Primary tool**: Cline or OpenCode (use `@sync-engineer` agent)
**Goal**: 29k+ entries seeded, AniList metadata backfilled.

---

### Prompt 3.1–3.3 — External API clients
```
Read AGENTS.md, docs/sync-pipeline.md, and PROJECT-STATUS.md. Current task: 3.1–3.3.

Use the sync-pipeline skill (.claude/skills/sync-pipeline/SKILL.md).

Create backend/external/anilist_client.py:
  - httpx AsyncClient
  - fetch_media_batch(anilist_ids: list[int]) → list[AniListMedia]
  - search_media(query: str, type: str) → list[AniListMedia]
  - fetch_user_list(access_token: str) → list[AniListUserEntry]
  - Redis token bucket rate limiter (80 req/min)
  - Raises AniListRateLimitError on 429

Create backend/external/mangadex_client.py:
  - fetch_manga_detail(mangadex_id: str) → MangaDexManga
  - fetch_chapter_list(mangadex_id: str) → list[MangaDexChapter]
  - Rate limit: 4 req/s (asyncio.sleep(0.25))

Create backend/external/jikan_client.py:
  - fetch_anime(mal_id: int) → JikanAnime
  - Rate limit: 50 req/min

All clients return typed Pydantic models. All raise typed exceptions.
Write unit tests with httpx mock for each client.

Update PROJECT-STATUS.md: mark 3.1–3.3 ✅, advance to 3.4.
```

---

### Prompt 3.4 — Seed script
```
Read AGENTS.md, docs/sync-pipeline.md, and PROJECT-STATUS.md. Current task: 3.4.

Use the seed-db command context (.claude/commands/seed-db.md).

Create scripts/seed_anime_db.py:
  - Download latest anime-offline-database-minified.json from GitHub releases
  - Parse all entries
  - Bulk upsert into media_entries (title_romaji, media_type, format, status, episode_count)
  - Bulk upsert cross-references into media_external_ids (anilist_id, mal_id, kitsu_id, etc.)
  - Use PostgreSQL INSERT ... ON CONFLICT DO NOTHING for idempotency
  - Mark metadata_synced_at = NULL on all (triggers backfill)
  - Log progress every 1000 entries
  - Create a sync_jobs row (type='seed') and update it on completion
  - Support --dry-run flag

Test with --dry-run first.
Run for real and confirm: SELECT COUNT(*) FROM media_entries; → ~29000+

Update PROJECT-STATUS.md: mark 3.4 ✅, advance to 3.5.
```

---

### Prompt 3.5–3.8 — Celery workers
```
Read AGENTS.md, docs/sync-pipeline.md, and PROJECT-STATUS.md. Current task: 3.5–3.8.

Create backend/workers/celery_app.py:
  - Celery app with Redis broker and backend
  - Beat schedule from docs/sync-pipeline.md (weekly refresh, airing schedule, cleanup)

Create backend/workers/sync_tasks.py:
  backfill_anilist_batch(anilist_ids: list[int])
    - Fetch batch from AniList
    - Upsert titles, synopsis, cover images, genres, studios, tags, episodes
    - Mark metadata_synced_at = NOW() on success
    - bind=True, max_retries=3, acks_late=True
    - Update sync_jobs table

  backfill_all_anilist()
    - Query all entries where metadata_synced_at IS NULL
    - Chunk into batches of 50
    - Dispatch backfill_anilist_batch.delay() for each chunk

  refresh_airing_schedule()
    - Query all entries where status = 'releasing'
    - Re-fetch from AniList
    - Update episodes table with new air dates

  weekly_refresh()
    - Download new anime-offline-database release
    - Diff against current DB (find new anilist_ids)
    - Upsert new entries
    - Dispatch backfill for new entries only

Test: backfill a small batch (10 IDs) manually and confirm metadata appears in DB.

Update PROJECT-STATUS.md: mark 3.5–3.8 ✅, advance to 3.9.
```

---

### Prompt 3.9–3.13 — Media API endpoints
```
Read AGENTS.md, docs/backend-architecture.md, and PROJECT-STATUS.md. Current task: 3.9–3.13.

Use the fastapi-dev skill (.claude/skills/fastapi-dev/SKILL.md).

Create backend/repositories/media_repository.py (full implementation):
  search(query, media_type, genre, status, limit, after_cursor) → paginated results
    - Use tsvector full-text search for query
    - Fallback to trigram similarity for short queries
  get_by_id(media_id) → MediaEntry with genres, studios, tags, external_ids
  get_by_anilist_id(anilist_id) → MediaEntry or None
  get_airing_calendar(days_ahead=14) → episodes with air dates

Create backend/services/media_service.py with on-demand fetch:
  If search miss from DB → call anilist_client.search_media → upsert → return result

Create backend/schemas/media.py:
  MediaSearchResult, MediaDetailResponse, AiringCalendarEntry

Create backend/routers/media.py:
  GET /api/v1/media/search?q=&media_type=&genre=&status=&limit=&after=
  GET /api/v1/media/{media_id}
  GET /api/v1/media/airing?days=14

Write tests: tests/routers/test_media.py
  - search returns results
  - detail returns full metadata
  - 404 for unknown ID
  - auth required on all endpoints

Run seed + backfill for ~500 entries, test search manually.

PHASE 3 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 3.9–3.13 ✅
  - Set CURRENT_PHASE to 4, CURRENT_SUB_PHASE to 4.1
  - Add Phase 3 complete to Completion Log
```

---

# PHASE 4 — User Auth & Groups

**Primary tool**: Cline or Claude Code
**Goal**: Register, login, refresh, groups with invite codes.

---

### Prompt 4.1–4.6 — Auth endpoints
```
Read AGENTS.md, docs/backend-architecture.md, and PROJECT-STATUS.md. Current task: 4.1–4.6.

Use the fastapi-dev skill.

Create backend/repositories/user_repository.py:
  get_by_email, get_by_username, create, update, get_with_refresh_token

Create backend/services/auth_service.py:
  register(email, username, password) → User + tokens
  login(email, password) → tokens
  refresh(refresh_token_string) → new access_token + rotated refresh_token
  logout(refresh_token_string) → revoke token

Create backend/schemas/auth.py:
  RegisterRequest, LoginRequest, TokenResponse, RefreshRequest

Create backend/routers/auth.py:
  POST /api/v1/auth/register
  POST /api/v1/auth/login
  POST /api/v1/auth/refresh
  POST /api/v1/auth/logout (requires auth)

Create backend/routers/users.py:
  GET /api/v1/users/me (requires auth)
  PATCH /api/v1/users/me (update display_name, bio, avatar_url, timezone)

Write tests: register, login, wrong password → 401, expired token → 401, refresh works.

Update PROJECT-STATUS.md: mark 4.1–4.6 ✅, advance to 4.7.
```

---

### Prompt 4.7–4.11 — Group endpoints
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 4.7–4.11.

Create backend/repositories/group_repository.py:
  create, get_by_id, get_by_invite_code, add_member, get_members, is_member

Create backend/services/group_service.py:
  create_group(owner_id, name, description) → Group
  join_by_invite(user_id, invite_code) → GroupMember
  get_group_with_members(group_id, requesting_user_id) → GroupDetail

Create backend/schemas/group.py:
  GroupCreate, GroupResponse, GroupDetailResponse, MemberResponse

Create backend/routers/groups.py:
  POST /api/v1/groups
  GET /api/v1/groups/{id}
  POST /api/v1/groups/join/{invite_code}
  GET /api/v1/groups/{id}/members
  DELETE /api/v1/groups/{id}/members/me (leave group)

Write tests: create, join by invite, non-member can't see group details.

PHASE 4 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 4.7–4.11 ✅
  - Set CURRENT_PHASE to 5, CURRENT_SUB_PHASE to 5.1
  - Add Phase 4 complete to Completion Log
```

---

# PHASE 5 — Tracking & Lists

**Primary tool**: Cline or Claude Code
**Goal**: Full list management API with history logging.

---

### Prompt 5.1–5.7 — List endpoints
```
Read AGENTS.md, docs/backend-architecture.md, and PROJECT-STATUS.md. Current task: 5.1–5.7.

Use the fastapi-dev skill.

Create backend/repositories/tracking_repository.py:
  get_user_list(user_id, status_filter, cursor, limit)
  get_entry(user_id, media_id)
  upsert_entry(user_id, media_id, status, progress, score, notes)
    - Auto-creates ListEntryHistory row on every change
    - Soft delete: set deleted_at, log 'removed' event
  get_history(user_id, cursor, limit)
  get_group_feed(group_id, cursor, limit)
    - Queries list_entry_history for all members of the group

Create backend/services/tracking_service.py:
  add_to_list / update_entry / remove_from_list
  import_from_anilist(user_id, anilist_access_token)
  import_from_mal(user_id, mal_access_token)

Create backend/routers/lists.py:
  GET /api/v1/lists/me
  POST /api/v1/lists
  PATCH /api/v1/lists/{media_id}
  DELETE /api/v1/lists/{media_id}
  GET /api/v1/lists/me/history
  POST /api/v1/sync/import/anilist
  POST /api/v1/sync/import/mal

Write tests for all endpoints. Include: can't update another user's list.

Update PROJECT-STATUS.md: mark 5.1–5.7 ✅, advance to 5.8.
```

---

### Prompt 5.8–5.10 — Custom lists
```
Read PROJECT-STATUS.md. Current task: 5.8–5.10.

Add to backend/routers/lists.py:
  POST /api/v1/lists/custom
  GET /api/v1/lists/custom (user's custom lists)
  GET /api/v1/lists/custom/{id}
  PUT /api/v1/lists/custom/{id} (rename, update description)
  DELETE /api/v1/lists/custom/{id}
  POST /api/v1/lists/custom/{id}/entries (add media)
  DELETE /api/v1/lists/custom/{id}/entries/{media_id}

Confirm history auto-logging: every status/progress/score change creates a ListEntryHistory row.
Write tests.

PHASE 5 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 5.8–5.10 ✅
  - Set CURRENT_PHASE to 6, CURRENT_SUB_PHASE to 6.1
  - Add Phase 5 complete to Completion Log
```

---

# OtakuHub — PROJECT-PROMPT.md Replacement: Phases 6–12 (Quasar)

> Replace phases 6–12 in your existing PROJECT-PROMPT.md with this content.
> Phases 1–5 (backend, database, sync, auth, tracking API) are unchanged.

---

# PHASE 6 — Quasar App Shell

**Primary tool**: Antigravity or Claude Code
**Goal**: Quasar app navigates correctly on all 5 platforms, auth flow works, Axios talks to backend.

---

### Prompt 6.1 — Quasar project init
```
Read AGENTS.md, docs/quasar-architecture.md, and PROJECT-STATUS.md. Current task: 6.1.

Create the Quasar frontend:
  npm create quasar@latest frontend
  Wizard choices:
    ✓ Quasar App with Vite
    ✓ Vue 3 Composition API with <script setup>
    ✓ TypeScript: Yes
    ✓ Quasar CLI with Vite as build tool

After init, install all additional dependencies:
  npm install pinia pinia-plugin-persistedstate axios zod

  npm install -D vitest @vue/test-utils @pinia/testing \
    @quasar/quasar-app-extension-testing-unit-vitest \
    vue-tsc eslint eslint-plugin-vue

Create the folder structure from docs/quasar-architecture.md:
  src/types/, src/stores/, src/composables/, src/components/shared/

Set up tsconfig.json with "strict": true.
Set up .eslintrc.cjs with eslint-plugin-vue + typescript rules.

Run: vue-tsc --noEmit && quasar build
Must complete with zero errors.

Update PROJECT-STATUS.md: mark 6.1 ✅, advance to 6.2.
```

---

### Prompt 6.2 — Axios boot + auth interceptor
```
Read AGENTS.md, docs/quasar-architecture.md, and PROJECT-STATUS.md. Current task: 6.2.

Create src/boot/axios.ts:
  - Axios instance with baseURL from process.env.API_BASE_URL
  - Request interceptor: attach Bearer token from auth store
  - Response interceptor: on 401 → call auth.refreshToken() → retry original request
  - Export the api instance for use across the app

Create src/boot/pinia.ts:
  - Configure pinia-plugin-persistedstate
  - On Capacitor: use Capacitor Preferences as storage
  - On web/Electron: use localStorage (default)

Register both boot files in quasar.config.ts.

Create src/types/api.ts:
  interface PaginatedResponse<T> { items: T[]; nextCursor: string | null; total: number }
  function getErrorMessage(error: unknown): string (extracts message from Axios errors)

Run: vue-tsc --noEmit
Update PROJECT-STATUS.md: mark 6.2 ✅, advance to 6.3.
```

---

### Prompt 6.3 — Router + auth guard
```
Read docs/quasar-architecture.md and PROJECT-STATUS.md. Current task: 6.3.

Create src/router/routes.ts with ALL named routes from docs/quasar-architecture.md.
Set meta: { requiresAuth: true } on all protected routes.
Use lazy imports: component: () => import('pages/...')

Create src/router/index.ts:
  - Auth guard: if route.meta.requiresAuth && !auth.accessToken → redirect to login
  - If already logged in and on auth route → redirect to discover

Run: vue-tsc --noEmit
Update PROJECT-STATUS.md: mark 6.3 ✅, advance to 6.4.
```

---

### Prompt 6.4 — Auth Pinia store
```
Read PROJECT-STATUS.md. Current task: 6.4.

Create src/types/auth.ts:
  User interface (id, username, displayName, email, avatarUrl)
  LoginRequest, RegisterRequest, TokenResponse interfaces

Create src/stores/auth.ts (persisted):
  State: accessToken, refreshToken, user
  Actions:
    login(email, password) → calls POST /api/v1/auth/login → stores tokens
    register(username, email, password) → POST /api/v1/auth/register
    refreshToken() → POST /api/v1/auth/refresh → updates accessToken
    logout() → POST /api/v1/auth/logout → clears state
    fetchMe() → GET /api/v1/users/me → updates user
  persist: true

Write store test: src/stores/__tests__/auth.test.ts
  - login action stores token
  - logout action clears state

Run: vue-tsc --noEmit
Update PROJECT-STATUS.md: mark 6.4 ✅, advance to 6.5.
```

---

### Prompt 6.5–6.6 — Auth pages
```
Read PROJECT-STATUS.md. Current task: 6.5–6.6.

Use the quasar-page skill (.antigravity/skills/quasar-page.md).

Create src/layouts/AuthLayout.vue:
  Centered card layout, no navigation, brand logo at top.

Create src/pages/auth/LoginPage.vue:
  QCard with QInput (email + password, outlined, lazy-rules)
  QBtn "Login" with loading state
  Link to register page
  On submit: call authStore.login() → redirect to discover on success
  Show QBanner with error message on failure

Create src/pages/auth/RegisterPage.vue:
  QCard with QInput (username, email, password, confirm password)
  Client-side validation with Quasar rules
  On submit: authStore.register() → redirect to login on success

Write component tests: loading state, error banner, success redirect.

Run: vue-tsc --noEmit && quasar build
Update PROJECT-STATUS.md: mark 6.5–6.6 ✅, advance to 6.7.
```

---

### Prompt 6.7 — MainLayout (responsive shell)
```
Read docs/quasar-architecture.md and PROJECT-STATUS.md. Current task: 6.7.

Create src/layouts/MainLayout.vue using docs/quasar-architecture.md pattern:
  QLayout with QDrawer (desktop persistent side nav) + QFooter (mobile bottom tabs)
  Side nav items: Discover, My List, Feed, Watch Party, Notifications, Profile
  Bottom tabs (mobile, $q.screen.lt.md): same 5 items as icons only
  Notification badge on bell icon (from notifications store count)
  User avatar in top of side nav → click → profile page
  Logout button at bottom of side nav

Quasar theme:
  Create src/css/quasar.variables.scss with anime-appropriate brand colours:
    $primary: #6C63FF (purple)
    $secondary: #1DB954 (teal-green)
    $accent: #FF6B6B (coral)

Run: quasar dev → visually confirm layout on wide and narrow viewport.
Update PROJECT-STATUS.md: mark 6.7 ✅, advance to 6.8.
```

---

### Prompt 6.8 — Platform verification
```
Read PROJECT-STATUS.md. Current task: 6.8.

Verify the app builds and runs on all targets:

1. Web SPA: quasar build → serve dist/spa/ → confirm login → discover works
2. Electron: quasar build -m electron → confirm .exe/.AppImage produced, app launches
3. Android: quasar build -m capacitor -T android → confirm APK produced
   (or quasar dev -m capacitor -T android if device available)

Fix any platform-specific issues.

PHASE 6 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 6.8 ✅
  - Set CURRENT_PHASE to 7, CURRENT_SUB_PHASE to 7.1
  - Add Phase 6 complete to Completion Log
```

---

# PHASE 7 — Quasar Tracking Pages

**Primary tool**: Antigravity (`/startcycle` workflow)

For each page, run in Antigravity: `/startcycle <description>`

---

### Prompt 7.1 — Discover page
```
/startcycle Discover page — search for anime and manga by title. QInput with debounced search (300ms), calls GET /api/v1/media/search. Results in a responsive QCard grid (1 col mobile, 2 col tablet, 4 col desktop). Each card shows q-img cover art, title, format badge (TV/Manga), score chip. QVirtualScroll for infinite scroll. Tapping a card navigates to media-detail route.
```

### Prompt 7.2 — Media detail page
```
/startcycle Media detail page — full info for an anime or manga. q-img banner at top, cover image overlapping, title, native title, synopsis (expandable with See more). Chips for genres. Studio and season info. Score (QRating). Episode count. "Add to list" QBtn → opens QDialog to pick status and set initial progress. If already in user's list, shows current status and quick +1 episode/chapter button instead.
```

### Prompt 7.3 — My list page
```
/startcycle My list page — user's tracking list. QTabs across the top: Watching, Reading, Completed, Paused, Dropped, Plan to watch. Each tab shows a QList of entries with cover thumbnail, title, progress (ep X/Y or ch X/Y), and score. QBtn +1 per entry for quick progress increment. Pull-to-refresh on mobile. Calls GET /api/v1/lists/me?status=<tab>.
```

### Prompt 7.4 — Progress + score widgets
```
Read PROJECT-STATUS.md. Current task: 7.4.

Create src/components/tracking/ProgressWidget.vue:
  Props: mediaId, currentProgress, maxProgress (episode/chapter count)
  Shows: "Ep 5 / 12" or "Ch 23 / 100"
  Buttons: –1, +1 (calls PATCH /api/v1/lists/{mediaId})
  Long-press on number: opens QDialog for direct number input
  Optimistic update: update local store immediately, revert on API error

Create src/components/tracking/ScoreWidget.vue:
  Props: mediaId, currentScore, averageScore
  QRating (max 10, half-star precision)
  Shows AniList average score as reference text
  Saves on value change (debounced 500ms)

Export both from src/components/tracking/index.ts.
Write Vitest tests for both components.

Update PROJECT-STATUS.md: mark 7.4 ✅, advance to 7.5.
```

### Prompt 7.5 — Airing calendar
```
/startcycle Airing calendar page — upcoming episode air dates for anime in user's Watching list. Grouped by date section headers (Today, Tomorrow, This week, Later). Each QItem shows: anime cover thumbnail, title, episode number, air time, countdown chip (e.g. "in 3h"). QBadge if the episode has already aired. Calls GET /api/v1/media/airing. Tapping navigates to media detail.
```

### Prompt 7.6 — Import list page
```
/startcycle Import list page — import existing list from AniList or MyAnimeList. Two QCard options with logos. Tapping AniList opens OAuth in browser (Capacitor Browser plugin on mobile, window.open on web). On redirect callback, calls POST /api/v1/sync/import/anilist with the auth code. QLinearProgress bar during import. QBanner success with count ("Imported 347 titles"). QBanner error with retry.
```

### Prompt 7.7 — Custom lists
```
/startcycle Custom lists — user's curated lists ("Best Isekai", "Watch with friends"). Main page: QList of custom lists with title, item count, cover mosaic (4 tiny covers). FAB to create new list (QDialog: name + description). Clicking a list opens its detail page: QList of media items with drag-to-reorder (VueDraggable). Remove item with swipe-to-delete action. Share button copies a shareable link.

PHASE 7 COMPLETE after this. Update PROJECT-STATUS.md:
  - Set CURRENT_PHASE to 8, CURRENT_SUB_PHASE to 8.1
  - Add Phase 7 complete to Completion Log
```

---

# PHASE 8 — Social Features Backend
**Unchanged from the original PROJECT-PROMPT.md — copy Prompts 8.1–8.8 from there.**

---

# PHASE 9 — Social Features Frontend

**Primary tool**: Antigravity (`/startcycle` workflow)

### Prompt 9.1 — Activity feed
```
/startcycle Group activity feed page — what friends have been watching/reading. QList with avatar, friend name, media cover, action text ("started watching Attack on Titan", "rated Berserk 9/10", "reached episode 12 of One Piece"). Infinite scroll with QInfiniteScroll. Group selector QSelect at top if user is in multiple groups. Calls GET /api/v1/social/feed. Tapping a card navigates to media detail.
```

### Prompt 9.2 — Friend profile
```
/startcycle Friend profile page — another user's public profile. QCard header with q-avatar, display name, member since. Row of stat chips: X watching, Y completed, Z hours estimated. QList of recent activity (last 10 history entries). Calls GET /api/v1/users/{username}/profile.
```

### Prompt 9.3–9.4 — Recommendations
```
/startcycle Recommendations feature — two pages: (1) Send recommendation: QInput to search for a title (reuse discover composable), QSelect to pick a friend from group, QInput optional message, QBtn send. (2) Recommendations inbox: QList of pending recs. Each item shows sender avatar, media cover, message text, QBtn "Add to list" (adds + marks acknowledged), QBtn "Dismiss".
```

### Prompt 9.5–9.6 — Discussions
```
/startcycle Discussion threads — per-media discussions accessible from media detail page. QList of threads with title, author, reply count, episode tag chip. Tapping opens thread detail with QChat-style replies. Spoiler content blurred with QBtn to reveal. New discussion FAB opens QDialog: title, body QEditor, episode number QInput, spoiler QToggle. Reply QInput at bottom of thread page.
```

### Prompt 9.7 — Group management
```
Read PROJECT-STATUS.md. Current task: 9.7.

Create src/pages/social/GroupPage.vue:
  QCard: group name, avatar, member count
  QCard: invite code displayed large, QBtn to copy link, QBtn to regenerate
  QList: members with q-avatar, username, last seen
  QBtn "Leave group" → QDialog confirmation → calls DELETE /api/v1/groups/{id}/members/me

PHASE 9 COMPLETE. Update PROJECT-STATUS.md:
  - Set CURRENT_PHASE to 10, CURRENT_SUB_PHASE to 10.1
  - Add Phase 9 complete to Completion Log
```

---

# PHASE 10 — Watch Party
**Backend prompts 10.1–10.3 unchanged from original PROJECT-PROMPT.md.**

### Prompt 10.4–10.6 — Watch party frontend
```
/startcycle Watch party feature — three pages: (1) Watch party list: upcoming events, QCard per party showing anime cover, title, episode, scheduled date/time, RSVP count chips (attending/declined), user's own RSVP status chip. (2) Create watch party: QSelect to search anime, QInput episode number, QDatetimePicker for scheduled time, QInput optional stream URL and sync URL, QBtn create. (3) Watch party detail: countdown QCard, attendee QList with avatars, QBtnGroup RSVP (Attending / Declined), QBtn "Open stream" linking to stream URL.

PHASE 10 COMPLETE. Update PROJECT-STATUS.md:
  - Set CURRENT_PHASE to 11, CURRENT_SUB_PHASE to 11.1
```

---

# PHASE 11 — Notifications
**Backend prompts 11.1–11.7 unchanged.**

### Prompt 11.8–11.9 — Notification frontend
```
/startcycle Notifications feature — two pages: (1) Notification page: QList with unread badge count in nav. Each QItem: q-avatar with type icon (episode=play_circle, chapter=menu_book, rec=thumb_up, party=groups), title bold, body, timeago chip. Swipe to mark as read. QBtn "Mark all read". (2) Preferences page: QToggle for each notification type. QInput for Discord webhook URL. QInput for Telegram chat ID. QBtn Save.

PHASE 11 COMPLETE. Update PROJECT-STATUS.md:
  - Set CURRENT_PHASE to 12, CURRENT_SUB_PHASE to 12.1
```

---

# PHASE 12 — First-Run Setup & Super Admin Bootstrap

### Prompt 12.1–12.3 — Setup architecture + backend bootstrap API
```
Read PROJECT-STATUS.md. Current task: 12.1–12.3.

Perform gap analysis first:
  - confirm whether initial super-admin creation is currently possible without direct DB access
  - identify race/security risks for first-run bootstrap endpoint
  - document lock-after-first-admin behavior

Design and implement:
  - GET /api/v1/setup/status  -> { setup_required: boolean }
  - POST /api/v1/setup/bootstrap-admin (one-time only)

Rules:
  - Endpoint must be publicly callable only until first super-admin exists
  - After bootstrap completes, endpoint must always reject
  - Add idempotency/race-safety protection

Update PROJECT-STATUS.md: mark 12.1–12.3 ✅, advance to 12.4.
```

### Prompt 12.4–12.9 — Setup frontend, guards, and tests
```
Read PROJECT-STATUS.md. Current task: 12.4–12.9.

Frontend:
  - Create setup screen (QForm/QInput/lazy-rules)
  - Validate username/email/password/confirm-password client-side
  - Disable submit until form is valid
  - Add setup route + router guard using GET /setup/status

Backend:
  - enforce post-bootstrap admin-only user creation policies

Tests:
  - frontend: empty submit, invalid email, short password, mismatch password, successful setup
  - backend: unauthorized after bootstrap, duplicate/concurrent bootstrap protection

Update PROJECT-STATUS.md: mark 12.4–12.9 ✅, advance to 13.1.
```

---

# PHASE 13 — Backend Seed/Sync Command Consolidation

### Prompt 13.1–13.5 — Gap analysis + unified backend command architecture
```
Read PROJECT-STATUS.md. Current task: 13.1–13.5.

Perform full inventory/gap analysis:
  - root scripts seeding paths
  - backend seeding/sync entrypoints
  - data sources: anime-offline database, AniList, MangaDex, Jikan

Design unified backend-only structure:
  - shared ingestion core (parse/upsert/retry)
  - per-source adapters
  - commands: otakuhub seed anime-offline|anilist|mangadex|jikan
  - umbrella command: otakuhub seed all

Deprecation requirement:
  - if root src/ is unused, deprecate and document migration path
  - move root scripts seeding entrypoints into backend command layer

Update PROJECT-STATUS.md: mark 13.1–13.5 ✅, advance to 13.6.
```

### Prompt 13.6–13.10 — Celery runnable seed tasks + schedules + tests
```
Read PROJECT-STATUS.md. Current task: 13.6–13.10.

Implement each source as both:
  1) direct backend command
  2) celery task using same shared code path

Add:
  - daily refresh schedule(s)
  - sync_jobs observability consistency
  - command+task tests for idempotency and retry safety

Update PROJECT-STATUS.md: mark 13.6–13.10 ✅, advance to 14.1.
```

---

# PHASE 14 — Frontend Validation Hardening + Unit Test Expansion

### Prompt 14.1–14.6 — Validation implementation across all forms
```
Read PROJECT-STATUS.md. Current task: 14.1–14.6.

Perform form-by-form gap analysis first.
Then implement Quasar validation everywhere:
  - QForm + QInput rules + lazy-rules
  - required, format, range, and cross-field checks
  - inline actionable error messages
  - disable submit when invalid

No form should rely on backend validation as first line.
Backend validation still remains mandatory as defense in depth.

Update PROJECT-STATUS.md: mark 14.1–14.6 ✅, advance to 14.7.
```

### Prompt 14.7–14.9 — Unit tests for frontend validation + page states
```
Read PROJECT-STATUS.md. Current task: 14.7–14.9.

Add/update Vitest suites to cover every major page/form:
  - empty submit
  - invalid format
  - inline validation errors
  - successful submit path
  - loading/error/data states for pages

Update PROJECT-STATUS.md: mark 14.7–14.9 ✅, advance to 15.1.
```

---

# PHASE 15 — Polish, Testing & Deploy

### Prompt 15.1–15.2 — Test coverage
```
Read PROJECT-STATUS.md. Current task: 15.1–15.2.

Backend coverage:
  pytest --cov=backend --cov-report=term-missing
  Target: 80%+ coverage. Write missing tests.

Frontend coverage:
  npx vitest run --coverage
  Find all pages missing component tests.
  Write Vitest tests for any uncovered pages.
  Target: loading, error, data state covered for every page.

Update PROJECT-STATUS.md: mark 15.1–15.2 ✅, advance to 15.3.
```

### Prompt 15.3 — Security audit
```
Read PROJECT-STATUS.md. Current task: 15.3.
Run .claude/commands/audit-security.md full audit.
Add frontend-specific checks:
  grep -rn "anilist\|mangadex\|jikan" frontend/src/ --include="*.ts" --include="*.vue"
  → Any hit outside boot/axios.ts is a BLOCKER
  grep -rn "any" frontend/src/stores/ frontend/src/pages/ --include="*.ts"
  → Review each hit — should be eliminated or commented

Fix all CRITICAL and HIGH findings. Update PROJECT-STATUS.md: mark 15.3 ✅.
```

### Prompt 15.4 — Performance
```
Read PROJECT-STATUS.md. Current task: 15.4.

Backend: p95 search latency < 200ms under 50 concurrent requests.

Frontend:
  quasar build
  npx lighthouse dist/spa/index.html --output json | jq '.categories.performance.score'
  Target: > 0.85

Check bundle size: quasar build produces a report — ensure no single chunk > 500KB.
Enable code splitting for heavy pages if needed (already handled by lazy route imports).

Update PROJECT-STATUS.md: mark 15.4 ✅.
```

### Prompt 15.5 — Platform builds
```
Read PROJECT-STATUS.md. Current task: 15.5.

Build and verify all 5 platforms:

quasar build              → dist/spa/ → serve and confirm login + discover works
quasar build -m pwa       → confirm service worker registered, offline works
quasar build -m electron  → confirm Electron app launches on Windows or Linux
quasar build -m capacitor -T android → confirm APK builds in Android Studio
quasar build -m capacitor -T ios     → confirm IPA builds in Xcode (requires Mac)

Fix any platform-specific issues found.
Update PROJECT-STATUS.md: mark 15.5 ✅, advance to 15.6.
```

### Prompts 15.6–15.10
**Unchanged from original PROJECT-PROMPT.md** — Docker prod, Nginx, README, ADRs.
Add one extra ADR: `docs/adr/001-quasar-over-flutter.md`
  - Context: needed web + desktop (Windows/Linux) + mobile from one codebase
  - Decision: Quasar (Vue 3 + Electron + Capacitor) over Flutter
  - Rationale: team knows TypeScript/Vue, faster development, Electron covers both desktop targets
  - Tradeoffs: larger desktop bundle (Electron ~150MB vs Flutter ~30MB), WebView on mobile
```

---

## Updated Tool Table for Phases 6–15

| Phase | Primary Tool | Agent/Mode |
|-------|-------------|------------|
| 6 — Quasar shell | Antigravity / Claude Code | quasar-dev agent |
| 7 — Tracking pages | Antigravity | `/startcycle` workflow |
| 8 — Social API | Cline / OpenCode | `@backend-dev` |
| 9 — Social pages | Antigravity | `/startcycle` workflow |
| 10 — Watch party | Cline + Antigravity | split |
| 11 — Notifications | Cline + Antigravity | split |
| 12 — Setup bootstrap | Cline + Antigravity | split |
| 13 — Seed/sync consolidation | Cline / OpenCode | `@sync-engineer` + backend commands |
| 14 — Frontend validation/tests | Antigravity | `/startcycle` + Vitest |
| 15 — Polish | Claude Code | `/review-pr`, `/audit-security` |
