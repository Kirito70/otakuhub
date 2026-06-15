# OtakuHub — Backend Architecture

## Overview
FastAPI async Python backend. Serves a Vue 3 + Tailwind CSS + shadcn-vue frontend for web and desktop (Electron).
Handles all anime/manga metadata, user tracking, social features, and sync pipeline.

## Project Structure
```
backend/
├── src/
│   └── app/
│       ├── main.py                    ← FastAPI app factory, middleware, router registration
│       ├── config.py                  ← Pydantic Settings — all config from env vars (NOT core/)
│       ├── database.py                ← AsyncEngine, AsyncSession, get_db dependency (NOT core/)
│       ├── core/
│       │   ├── auth.py                ← JWT creation, verification, get_current_user dep
│       │   ├── security.py            ← bcrypt hashing, token utilities
│       │   ├── rate_limiter.py        ← Token bucket rate limiter for external APIs
│       │   ├── uuid7.py              ← RFC 9562 UUID v7 generator
│       │   └── tsvector.py           ← Portable TSVECTOR type (PG → TSVECTOR, SQLite → Text)
│       ├── models/                    ← One file per table model (no base.py)
│       │   ├── enums.py              ← All Python StrEnum types
│       │   ├── media_entry.py
│       │   ├── media_external_ids.py
│       │   ├── genre.py, media_genre.py
│       │   ├── studio.py, media_studio.py
│       │   ├── tag.py, media_tag.py
│       │   ├── related_media.py, episode.py, chapter.py
│       │   ├── user.py, refresh_token.py, external_auth.py
│       │   ├── group.py, group_member.py
│       │   ├── user_list_entry.py, list_entry_history.py
│       │   ├── custom_list.py, custom_list_entry.py
│       │   ├── recommendation.py, discussion.py, discussion_reply.py
│       │   ├── watch_party.py, watch_party_rsvp.py
│       │   ├── notification.py, notification_preference.py
│       │   └── sync_job.py
├── schemas/
│   ├── media.py               ← MediaDetailResponse, MediaSearchResponse, etc.
│   ├── user.py                ← UserProfile, UserSettings
│   ├── tracking.py            ← ListEntryCreate, ListEntryResponse
│   ├── social.py              ← RecommendationCreate, DiscussionResponse
│   ├── auth.py                ← LoginRequest, TokenResponse
│   └── common.py              ← PaginatedResponse, ErrorResponse
├── repositories/
│   ├── media_repository.py
│   ├── user_repository.py
│   ├── tracking_repository.py
│   ├── social_repository.py
│   └── sync_repository.py
├── services/
│   ├── media_service.py
│   ├── auth_service.py
│   ├── tracking_service.py
│   ├── social_service.py
│   ├── notification_service.py
│   └── sync_service.py
├── routers/
│   ├── auth.py                ← /api/v1/auth/
│   ├── media.py               ← /api/v1/media/
│   ├── lists.py               ← /api/v1/lists/
│   ├── social.py              ← /api/v1/social/
│   ├── watchparty.py          ← /api/v1/watchparty/
│   ├── notifications.py       ← /api/v1/notifications/
│   ├── sync.py                ← /api/v1/sync/
│   └── admin.py               ← /api/v1/admin/
├── workers/
│   ├── celery_app.py          ← Celery app factory
│   ├── sync_tasks.py          ← AniList/MangaDex sync Celery tasks
│   ├── notification_tasks.py  ← Apprise notification delivery
│   └── cleanup_tasks.py       ← Old notification purge, token cleanup
├── external/
│   ├── anilist_client.py      ← AniList GraphQL client with rate limiter
│   ├── mangadex_client.py     ← MangaDex REST client with rate limiter
│   ├── jikan_client.py        ← Jikan MAL supplement client
│   └── apprise_client.py      ← Notification delivery via Apprise
└── alembic/
    ├── env.py
    └── versions/              ← Migration files
```

## Request Flow

### Auth & Group Layer Boundary
- **Router** validates request bodies (Pydantic schemas) and enforces JWT auth via `Depends(get_current_user)`. It delegates to the corresponding service.
- **Service** contains business rules: password verification, token rotation, group ownership checks, role validation, and orchestrates multiple repositories.
- **Repository** read‑only operations use `self.query()` (QueryBuilder) which automatically filters out soft‑deleted rows. Write‑operations (`create`, `update`, `soft_delete`) remain direct async SQLAlchemy calls.
- **Worker** (future) may handle email verification or invitation expiry.
- **External** – no direct external API calls from the frontend for auth; all go through FastAPI.

## Request Flow
```
Vue 3 App (web/Electron)
    ↓  HTTPS (JWT in Authorization header)
Nginx (reverse proxy + TLS termination)
    ↓
FastAPI Router
    ↓  parse + validate input (Pydantic)
    ↓  auth check (Depends(get_current_user))
Service Layer
    ↓  business logic
Repository Layer
    ↓  async SQLAlchemy queries
PostgreSQL
```

## Layered Architecture Rules
| Layer | What it owns | What it NEVER does |
|-------|-------------|-------------------|
| Router | Parse request, call service, return response | DB queries, business logic |
| Service | Business rules, orchestrate repos, return schemas | Direct DB calls, HTTP details |
| Repository | **All SELECT‑type reads must go through the fluent `QueryBuilder`** (exposed via `self.query()`). Write operations (`create`, `update`, `soft_delete`) remain direct async SQLAlchemy calls. | Business logic, HTTP types |
| Worker | Background tasks, external API calls | Responding to HTTP requests |
| External | API client logic, rate limiting | Business logic, DB access |

> **Note:** `BaseRepository` now implements `query()` which returns a `QueryBuilder` that automatically filters out soft‑deleted rows (see ADR 006). All concrete repositories should use this builder for reads.


## Auth Flow
```
POST /api/v1/auth/login
  → verify password (bcrypt via passlib)
  → if stored hash is legacy SHA-256, rehash to bcrypt on successful login
  → issue access_token (15min JWT) + refresh_token (30d, stored SHA-256 hash in DB)
  → Frontend stores both in localStorage (Pinia persisted state)

Request to protected endpoint:
  → Frontend sends: Authorization: Bearer <access_token>
  → FastAPI: verify JWT signature + expiry
  → get_current_user: load User from DB by sub claim

Access token expires:
  → Frontend calls POST /api/v1/auth/refresh with refresh_token in body
  → Validate refresh_token hash against DB
  → Rotate: revoke current token and issue a new refresh token
  → Replay protection: if a revoked refresh token is reused, revoke all active refresh tokens for that user
```

## Environment Variables (all required)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/otakuhub
REDIS_URL=redis://:password@redis:6379/0
JWT_SECRET=<64+ random bytes; required, insecure defaults rejected>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
ANILIST_CLIENT_ID=<from AniList developer settings>
ANILIST_CLIENT_SECRET=<from AniList developer settings>
MAL_CLIENT_ID=<from MAL developer settings>
MANGADEX_USERNAME=<optional — for authenticated MangaDex calls>
MANGADEX_PASSWORD=<optional>
APPRISE_URLS=discord://...  # comma-separated Apprise notification URLs
FRONTEND_URL=https://otakuhub.local
CORS_ORIGINS=https://otakuhub.local,http://localhost:8080  # wildcard '*' rejected by settings validation
```

## Dependency Injection Pattern
```python
# src/app/database.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Usage in router
@router.get("/media/{id}")
async def get_media(
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    media_svc: Annotated[MediaService, Depends(get_media_service)],
):
    ...
```

## Error Handling
```python
# main.py
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    logger.error(f"DB error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Database error"})
```

## Testing Strategy
```
tests/
├── conftest.py              ← app, db_session, auth_headers fixtures
├── routers/                 ← httpx AsyncClient integration tests
├── services/                ← unit tests with mocked repositories
├── repositories/            ← tests against real test DB
└── workers/                 ← Celery task unit tests (mocked external APIs)
```
Run: `pytest tests/ -v --asyncio-mode=auto --cov=backend --cov-report=term`

## Sync Jobs Runbook (developer)

From `backend/` with uv:

```bash
# API server
uv run otakuhub-dev

# Celery processes
uv run otakuhub celery worker --loglevel info --queue sync
uv run otakuhub celery beat --loglevel info

# Trigger jobs
uv run otakuhub celery seed --batch-size 50
uv run otakuhub celery weekly-refresh
```

Design note: routers should enqueue sync jobs; workers own external API calls, retries, rate limits, and progress persistence in `sync_jobs`.

## Security Hardening Notes (Phase 24)
- `Settings` performs fail-fast validation for security-critical config:
  - rejects insecure `JWT_SECRET` values (empty/test placeholders)
  - rejects wildcard `CORS_ORIGINS=*`
- Password policy is bcrypt/passlib for all new hashes.
- Legacy SHA-256 password hashes are only accepted for verification and are upgraded to bcrypt on successful login.
- Refresh-token replay protection revokes all active user refresh tokens when a revoked token is reused.
