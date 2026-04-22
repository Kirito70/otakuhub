# OtakuHub Backend

FastAPI backend for the OtakuHub platform.

## Project Structure
```
backend/
├── main.py                    ← FastAPI app factory, middleware, router registration
├── core/
│   ├── config.py              ← Pydantic Settings — all config from env vars
│   ├── database.py            ← AsyncEngine, AsyncSession, get_db dependency
│   ├── auth.py                ← JWT creation, verification, get_current_user dep
│   ├── security.py            ← bcrypt hashing, token utilities
│   ├── redis.py               ← Redis connection pool
│   └── rate_limiter.py        ← Token bucket rate limiter for external APIs
├── models/
│   ├── base.py                ← DeclarativeBase, TimestampMixin
│   ├── media.py               ← MediaEntry, MediaExternalIds, Genre, Studio, Tag
│   ├── user.py                ← User, RefreshToken, ExternalAuth
│   ├── tracking.py            ← UserListEntry, ListEntryHistory, CustomList
│   ├── social.py              ← Recommendation, Discussion, DiscussionReply
│   ├── watchparty.py          ← WatchParty, WatchPartyRsvp
│   └── notification.py        ← NotificationPreference, Notification
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

## Development Setup

### Prerequisites
- Python 3.12+
- Docker and Docker Compose

### Setup
1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
pip install -e ".[dev]"
```

3. Run the development server:
```bash
# Option 1: Using Docker Compose (recommended)
docker compose up

# Option 2: Local development
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
pytest tests/
```

### Migrations
```bash
# Initialize Alembic
alembic init alembic

# Upgrade to latest migration
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "Migration message"
```

## Environment Variables
Copy `.env.example` to `.env` and configure accordingly.

## API Endpoints
See `docs/api-spec.md` for the complete API specification.