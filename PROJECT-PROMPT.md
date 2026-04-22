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

# PHASE 6 — Flutter App Shell

**Primary tool**: Antigravity (flutter-dev agent) or Claude Code
**Goal**: Flutter app navigates on all 5 platforms, auth flow works end-to-end.

---

### Prompt 6.1–6.4 — Router and HTTP client
```
Read AGENTS.md, docs/flutter-architecture.md, and PROJECT-STATUS.md. Current task: 6.1–6.4.

Use the flutter-dev skill (.claude/skills/flutter-dev/SKILL.md).

Create lib/core/router/app_router.dart:
  - All named routes from docs/flutter-architecture.md
  - ShellRoute with bottom nav (mobile) + side nav (desktop)
  - Auth redirect guard using authStateProvider

Create lib/core/network/dio_client.dart:
  - Base URL from AppConfig
  - AuthInterceptor: attach Bearer token, handle 401 → refresh → retry
  - RetryInterceptor: 3 retries on 5xx with exponential backoff
  - LogInterceptor: debug mode only

Create lib/core/storage/secure_storage.dart:
  - flutter_secure_storage wrapper
  - Methods: saveTokens, getAccessToken, getRefreshToken, clearTokens

Run dart analyze — zero errors.
Update PROJECT-STATUS.md: mark 6.1–6.4 ✅, advance to 6.5.
```

---

### Prompt 6.5–6.9 — Auth feature
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 6.5–6.9.

Use the flutter-screen skill (.antigravity/skills/flutter-screen.md).

Build lib/features/auth/:
  domain/models/user_model.dart (Freezed)
  domain/repositories/auth_repository.dart (abstract)
  data/datasources/auth_remote_datasource.dart (Dio calls to /api/v1/auth/)
  data/repositories/auth_repository_impl.dart
  presentation/providers/auth_provider.dart (@riverpod AuthNotifier, keepAlive: true)
    - States: loading, authenticated(user), unauthenticated
    - Methods: login, register, logout, refreshToken
  presentation/screens/login_screen.dart
    - Email + password fields
    - Login button with loading state
    - Navigate to register
    - Shows error snackbar on failure
  presentation/screens/register_screen.dart
    - Username, email, password fields
    - Register button with loading state

Auth guard in app_router.dart:
  If unauthenticated → redirect to /auth/login
  If authenticated on auth route → redirect to /

Run: dart run build_runner build --delete-conflicting-outputs
Run: dart analyze → zero errors
Run: flutter test test/features/auth/

Update PROJECT-STATUS.md: mark 6.5–6.9 ✅, advance to 6.10.
```

---

### Prompt 6.10 — Platform verification
```
Read PROJECT-STATUS.md. Current task: 6.10.

Verify the app builds and runs correctly on 3 platforms:

1. Web: flutter run -d web-server --web-port 8080
   Confirm: login screen loads, API calls reach backend, navigation works

2. Windows: flutter run -d windows
   Confirm: same as web, window resizes correctly, side nav appears at wide width

3. Android: flutter run -d android (or flutter build apk --debug)
   Confirm: bottom nav shows, login works

Fix any platform-specific issues found.

PHASE 6 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 6.10 ✅
  - Set CURRENT_PHASE to 7, CURRENT_SUB_PHASE to 7.1
  - Add Phase 6 complete to Completion Log
```

---

# PHASE 7 — Flutter Tracking Screens

**Primary tool**: Antigravity (startcycle workflow)

For each screen in this phase, run in Antigravity:
```
/startcycle <screen-name>
```
Then approve each PM spec and Design brief before implementation proceeds.

---

### Prompt 7.1 — Discover screen
```
/startcycle Discover screen — search for anime and manga by title, filter by type and genre, shows cover art and score. Calls GET /api/v1/media/search with debounced input. Results in a responsive grid (2 cols mobile, 4 cols desktop). Tapping a card navigates to media detail.
```

### Prompt 7.2 — Media detail screen
```
/startcycle Media detail screen — shows full anime/manga info: cover, banner, title, synopsis, genres, studios, score, episode count. Has an "Add to list" button that opens a bottom sheet. If already in user's list, shows current status and progress instead. Tapping episodes shows airing schedule.
```

### Prompt 7.3 — Add to list bottom sheet
```
/startcycle Add-to-list bottom sheet — slides up when user taps "Add to list" on detail screen. Lets user pick status (watching/reading/plan to watch/etc), set initial progress, and optionally score. Calls POST /api/v1/lists. Dismisses on success and updates the detail screen state.
```

### Prompt 7.4 — My list screen
```
/startcycle My list screen — shows the user's tracking list. Tabbed by status: Watching, Reading, Completed, Paused, Dropped, Plan to watch. Each tab is a scrollable list of media cards with progress and score. Pull to refresh. Tapping a card opens detail screen.
```

### Prompt 7.5–7.6 — Progress and score widgets
```
Read PROJECT-STATUS.md. Current task: 7.5–7.6.

Create reusable widgets in lib/features/tracking/presentation/widgets/:

ProgressUpdateWidget:
  - Shows current episode/chapter number
  - +1 / -1 buttons
  - Direct number input on long press
  - Calls PATCH /api/v1/lists/{media_id} on change
  - Optimistic update (update UI immediately, revert on error)

ScoreWidget:
  - Star rating or numeric 0.0–10.0 selector
  - Shows average AniList score as reference
  - Saves on dismiss

Both widgets used inline in MyListScreen card items and on DetailScreen.

Run dart analyze, flutter test. Update PROJECT-STATUS.md: mark 7.5–7.6 ✅, advance to 7.7.
```

### Prompt 7.7 — Airing calendar
```
/startcycle Airing calendar screen — shows upcoming episode air dates for anime in user's "Watching" list. Organised by date (today, tomorrow, this week, later). Each row shows anime title, episode number, and countdown. Calls GET /api/v1/media/airing. Tapping navigates to media detail.
```

### Prompt 7.8 — Import list screen
```
/startcycle Import list screen — lets user import their existing list from AniList or MyAnimeList. Shows two option cards. Tapping AniList opens OAuth browser flow. On callback, calls POST /api/v1/sync/import/anilist with the auth code. Shows progress bar during import, then success screen with count of imported titles.
```

### Prompt 7.9–7.10 — Custom lists and widget tests
```
Read PROJECT-STATUS.md. Current task: 7.9–7.10.

1. Build lib/features/tracking/presentation/screens/custom_lists_screen.dart:
   - Lists user's custom lists (GET /api/v1/lists/custom)
   - FAB to create new list
   - Tapping opens list detail with its media items

2. Write widget tests for ALL screens built in Phase 7:
   test/features/tracking/presentation/screens/
     discover_screen_test.dart
     media_detail_screen_test.dart
     my_list_screen_test.dart
     airing_calendar_screen_test.dart

   Each test covers: loading state, data state, error state + retry.

Run: flutter test test/features/tracking/

PHASE 7 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 7.9–7.10 ✅
  - Set CURRENT_PHASE to 8, CURRENT_SUB_PHASE to 8.1
  - Add Phase 7 complete to Completion Log
```

---

# PHASE 8 — Social Features Backend

**Primary tool**: Cline or OpenCode (`@backend-dev` agent)

---

### Prompt 8.1 — Activity feed endpoint
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 8.1.

Create backend/routers/social.py.

GET /api/v1/social/feed:
  - Auth required
  - User must be in a group (use group_id query param, validate membership)
  - Returns recent ListEntryHistory for all group members
  - Fields: user display_name + avatar, media title + cover, event_type, new_status, new_progress, new_score, created_at
  - Cursor-based pagination (limit 20)
  - Include group_id filter: ?group_id=<uuid>

Query: JOIN list_entry_history → users → media_entries
  WHERE user_id IN (SELECT user_id FROM group_members WHERE group_id = ?)
  AND deleted_at IS NULL
  ORDER BY created_at DESC

Write test: feed returns entries for group members, excludes non-members.
Update PROJECT-STATUS.md: mark 8.1 ✅, advance to 8.2.
```

---

### Prompt 8.2–8.4 — Recommendations
```
Read PROJECT-STATUS.md. Current task: 8.2–8.4.

Add to backend/routers/social.py:

POST /api/v1/social/recommend
  body: { to_user_id, media_id, message }
  Validates: both users in same group, not recommending to self, no duplicate

GET /api/v1/social/recommendations/inbox
  Returns pending recommendations for current user (is_acknowledged = false)
  Include: from_user display_name, media title + cover, message, created_at

PATCH /api/v1/social/recommendations/{id}/acknowledge
  Sets is_acknowledged = true
  Only the recipient can acknowledge

Write tests. Update PROJECT-STATUS.md: mark 8.2–8.4 ✅, advance to 8.5.
```

---

### Prompt 8.5–8.8 — Discussions and profiles
```
Read PROJECT-STATUS.md. Current task: 8.5–8.8.

Add to backend/routers/social.py:

POST /api/v1/social/discussions
  body: { media_id, group_id, title, body, episode_number?, has_spoilers }
  Validate: user is group member

GET /api/v1/social/discussions/{media_id}?group_id=
  Returns discussions for this media in the group

POST /api/v1/social/discussions/{id}/replies
  body: { body, has_spoilers, parent_reply_id? }

GET /api/v1/social/discussions/{id}/replies

backend/routers/users.py — add:
GET /api/v1/users/{username}/profile
  Public profile: display_name, avatar, list stats (total watching, completed, etc.)
  Only visible to group members

PHASE 8 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 8.5–8.8 ✅
  - Set CURRENT_PHASE to 9, CURRENT_SUB_PHASE to 9.1
  - Add Phase 8 complete to Completion Log
```

---

# PHASE 9 — Social Features Flutter

**Primary tool**: Antigravity (startcycle workflow)

### Prompt 9.1 — Activity feed screen
```
/startcycle Group activity feed screen — shows what friends have recently been watching or reading. Each item shows: friend avatar + name, anime/manga cover, what they did ("started watching", "completed", "rated 8/10", "reached episode 12"). Cards are tappable to open media detail. Group selector at top if user is in multiple groups. Pulls from GET /api/v1/social/feed with infinite scroll.
```

### Prompt 9.2 — Friend profile screen
```
/startcycle Friend profile screen — shows another user's public profile. Header with avatar and display name. Stats row: total watching, completed, total hours estimated. Below: their recent activity (last 10 history entries). Calls GET /api/v1/users/{username}/profile.
```

### Prompt 9.3–9.4 — Recommendations
```
/startcycle Recommendation system — two screens: (1) Send recommendation: search for a title, pick a friend from the group, add an optional message, send. (2) Recommendations inbox: list of pending recommendations from friends, each showing sender name, media cover, message, and an "Add to list" button that adds it directly and marks as acknowledged.
```

### Prompt 9.5–9.6 — Discussions
```
/startcycle Discussion threads — per-anime discussion screen accessible from the media detail page. Shows list of discussions for this anime in the user's group. Tapping opens a thread view with replies. Spoiler posts are blurred until tapped. New discussion FAB. Reply button on each thread. Episode number tag on episode-specific discussions.
```

### Prompt 9.7 — Group management
```
Read PROJECT-STATUS.md. Current task: 9.7.

Build lib/features/groups/presentation/screens/group_screen.dart:
  - Group name and avatar at top
  - Invite link card (tap to copy, shows the invite code prominently)
  - Members list with avatars and online status (last_seen_at)
  - "Leave group" button (with confirmation dialog)

Run dart analyze, flutter test.

PHASE 9 COMPLETE. Update PROJECT-STATUS.md:
  - Mark 9.7 ✅
  - Set CURRENT_PHASE to 10, CURRENT_SUB_PHASE to 10.1
  - Add Phase 9 complete to Completion Log
```

---

# PHASE 10 — Watch Party

**Primary tool**: Cline (backend) + Antigravity (Flutter)

### Prompt 10.1–10.3 — Watch party backend
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 10.1–10.3.

Create backend/routers/watchparty.py:

POST /api/v1/watchparty
  body: { group_id, media_id, episode_number, title, scheduled_at, stream_url, sync_url, notes }
  Validates group membership. Creates WatchParty. Auto-creates RSVP for host as 'attending'.

GET /api/v1/watchparty?group_id=
  Returns upcoming + recent parties for the group (status != cancelled)
  Ordered by scheduled_at DESC

GET /api/v1/watchparty/{id}
  Full detail including RSVP list

POST /api/v1/watchparty/{id}/rsvp
  body: { status: attending|declined }
  User must be group member

PATCH /api/v1/watchparty/{id} (host only — update details or cancel)

Write tests. Update PROJECT-STATUS.md: mark 10.1–10.3 ✅, advance to 10.4.
```

### Prompt 10.4–10.6 — Watch party Flutter
```
/startcycle Watch party feature — three screens: (1) Watch party list: upcoming events in the group, each showing anime title, episode, date/time, RSVP count, and user's own RSVP status. (2) Create watch party: pick anime from search, episode number, date/time picker, optional stream URL (HiAnime/Crunchyroll link) and sync URL (SyncParty/Rave). (3) Watch party detail: full info, countdown timer, attendee list with avatars, stream link button, RSVP buttons (Attending / Declined).

PHASE 10 COMPLETE. Update PROJECT-STATUS.md:
  - Set CURRENT_PHASE to 11, CURRENT_SUB_PHASE to 11.1
  - Add Phase 10 complete to Completion Log
```

---

# PHASE 11 — Notifications

**Primary tool**: Cline or Claude Code (backend) + Antigravity (Flutter)

### Prompt 11.1–11.7 — Notification backend
```
Read AGENTS.md, docs/sync-pipeline.md, and PROJECT-STATUS.md. Current task: 11.1–11.7.

Create backend/external/apprise_client.py:
  send(title, body, urls: list[str]) — async Apprise notification delivery

Create backend/workers/notification_tasks.py:
  check_new_episodes()
    - Find all users with watch_status = 'watching' for currently-airing anime
    - Check if a new episode aired since last notification
    - Send via Apprise to users who have new_episode = true in preferences
    - Create Notification row in DB

  check_new_chapters()
    - Same pattern for manga/manhwa readers

  watch_party_reminder()
    - Find parties scheduled within next 30 minutes
    - Send reminder to all 'attending' RSVPs

Create backend/routers/notifications.py:
  GET /api/v1/notifications (paginated, unread first)
  PATCH /api/v1/notifications/read (mark all or specific IDs as read)
  GET /api/v1/notifications/preferences
  PATCH /api/v1/notifications/preferences (update discord_webhook, channels, etc.)

Add notification tasks to Celery beat schedule.
Write tests.
Update PROJECT-STATUS.md: mark 11.1–11.7 ✅, advance to 11.8.
```

### Prompt 11.8–11.9 — Notification Flutter screens
```
/startcycle Notifications feature — two screens: (1) Notification bell screen: list of notifications with unread badge count in nav bar. Each item shows icon (episode, chapter, recommendation, watch party), title, body, and time ago. Tap marks as read and navigates to relevant content. (2) Notification preferences screen: toggles for each notification type (new episodes, new chapters, friend activity, recommendations, watch party invites). Fields for Discord webhook URL and Telegram chat ID. Save button.

PHASE 11 COMPLETE. Update PROJECT-STATUS.md:
  - Set CURRENT_PHASE to 12, CURRENT_SUB_PHASE to 12.1
  - Add Phase 11 complete to Completion Log
```

---

# PHASE 12 — Polish, Testing & Deploy

**Primary tool**: Claude Code (tests + security) + Antigravity (Flutter builds)

### Prompt 12.1–12.2 — Test coverage
```
Read AGENTS.md and PROJECT-STATUS.md. Current task: 12.1–12.2.

Backend coverage audit:
  pytest --cov=backend --cov-report=term-missing
  Find all routes/services with < 80% coverage
  Write missing tests until coverage reaches 80%+

Flutter widget test audit:
  flutter test --coverage
  Find all screens missing tests
  Write widget tests for any uncovered screens

Report: list of tests added and final coverage numbers.
Update PROJECT-STATUS.md: mark 12.1–12.2 ✅, advance to 12.3.
```

### Prompt 12.3 — Security audit
```
Read PROJECT-STATUS.md. Current task: 12.3.

Run the full security audit using .claude/commands/audit-security.md.
Run every check in the audit command (secrets scan, auth coverage, IDOR scan, raw SQL check, Flutter external calls, CORS, token security).
Report all findings with severity.
Fix all CRITICAL and HIGH findings before advancing.

Update PROJECT-STATUS.md: mark 12.3 ✅, advance to 12.4.
```

### Prompt 12.4 — Performance check
```
Read PROJECT-STATUS.md. Current task: 12.4.

Run performance checks:
1. Search endpoint: use httpx to send 50 concurrent search requests, measure p95 latency
   Target: < 200ms p95
2. If slow: check EXPLAIN ANALYZE on the search query, add any missing indexes

3. Flutter web: run Lighthouse audit on http://localhost:8080
   Target: Performance score > 85

Fix any issues found.
Update PROJECT-STATUS.md: mark 12.4 ✅, advance to 12.5.
```

### Prompt 12.5 — Platform builds
```
Read PROJECT-STATUS.md. Current task: 12.5.

Build and verify all 5 platforms:

flutter build web --release --wasm
  → Confirm: builds without error, index.html generated

flutter build windows --release
  → Confirm: .exe produced, runs without error

flutter build apk --release
  → Confirm: .apk produced

flutter build ios --release --no-codesign
  → Confirm: .app produced (requires Mac)

flutter build linux --release
  → Confirm: binary produced, runs

Log any platform-specific issues and fix them.
Update PROJECT-STATUS.md: mark 12.5 ✅, advance to 12.6.
```

### Prompt 12.6–12.7 — Production deploy
```
Read PROJECT-STATUS.md. Current task: 12.6–12.7.

1. Test production Docker Compose:
   docker compose -f infra/docker-compose.prod.yml up -d
   Confirm: all services healthy, backend responds, nginx proxies correctly

2. Copy Flutter web build into nginx html dir:
   cp -r mobile/build/web/* infra/nginx/html/

3. Run full smoke test against production stack:
   - Register a user
   - Login
   - Search for anime
   - Add to list
   - Verify in DB

4. Nginx TLS configuration (self-signed for local, placeholder for real cert):
   Generate self-signed cert, configure nginx.conf for HTTPS on 443

Update PROJECT-STATUS.md: mark 12.6–12.7 ✅, advance to 12.8.
```

### Prompt 12.8–12.9 — README and ADRs
```
Read PROJECT-STATUS.md. Current task: 12.8–12.9.

1. Write a comprehensive README.md:
   Project description
   Architecture diagram (ASCII or Mermaid)
   Prerequisites (Docker, Flutter, Python 3.12)
   Quick start: 5 commands to get running
   How to run each platform
   How to run tests
   Environment variables reference
   How to trigger sync jobs manually

2. Write ADRs for all major decisions made during the build:
   docs/adr/001-flutter-over-react-native.md
   docs/adr/002-anilist-as-primary-metadata-source.md
   docs/adr/003-uuid-v7-primary-keys.md
   docs/adr/004-soft-deletes-everywhere.md
   docs/adr/005-fastapi-layered-architecture.md
   docs/adr/006-celery-for-sync-pipeline.md

PHASE 12 COMPLETE — PROJECT COMPLETE.
Update PROJECT-STATUS.md:
  - Mark 12.8–12.9 ✅
  - Set CURRENT_PHASE to COMPLETE
  - Set STATUS to COMPLETE
  - Add final "Project complete" entry to Completion Log
```

---

## Quick Reference: Which Tool for Which Phase

| Phase | Primary Tool | Agent/Mode |
|-------|-------------|------------|
| 1 — Foundation | Claude Code / OpenCode | default |
| 2 — Database | Claude Code / OpenCode | `@db-designer` |
| 3 — Sync pipeline | Cline / OpenCode | `@sync-engineer` |
| 4 — Auth | Cline / Claude Code | `@backend-dev` |
| 5 — Tracking API | Cline / Claude Code | `@backend-dev` |
| 6 — Flutter shell | Antigravity / Claude Code | flutter-dev agent |
| 7 — Flutter tracking | Antigravity | `/startcycle` workflow |
| 8 — Social API | Cline / OpenCode | `@backend-dev` |
| 9 — Social Flutter | Antigravity | `/startcycle` workflow |
| 10 — Watch party | Cline + Antigravity | split |
| 11 — Notifications | Cline + Antigravity | split |
| 12 — Polish | Claude Code | `/review-pr`, `/audit-security` |

---

## Universal Rules for Every Prompt

Every AI agent working on this project must, without exception:
1. Read `PROJECT-STATUS.md` before starting
2. Read `AGENTS.md` for conventions
3. Read the relevant `docs/` file for the domain
4. Only work on the current sub-phase
5. Update `PROJECT-STATUS.md` when done
6. Run lint + tests before marking ✅
7. Never skip a sub-phase
