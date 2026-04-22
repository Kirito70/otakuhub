# OtakuHub — AI Agent Master Instructions

## Project Identity
OtakuHub is a **private friend-group anime/manga/manhwa tracking and social platform**.
It is NOT a public community tool. Every design decision should optimise for a small group
of known users (5–20 people), not scale or strangers.

## Monorepo Structure
```
otakuhub/
├── backend/          # FastAPI Python backend
├── mobile/           # Flutter app (web + Windows + Android + iOS + Linux)
├── infra/            # Docker Compose, Nginx, env configs
├── docs/             # Architecture and design docs
└── scripts/          # DB seed, sync workers, dev utilities
```

## Tech Stack — Non-Negotiable
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, Celery + Redis, PostgreSQL 16
- **Frontend**: Flutter 3.x / Dart 3.x — single codebase for all 5 platforms
- **Auth**: JWT (access + refresh tokens), bcrypt password hashing
- **External APIs**: AniList GraphQL (primary), MangaDex REST v5 (manga), Jikan v4 (MAL supplement)
- **Notifications**: Apprise (Discord, Telegram, email, push)
- **Container**: Docker + Docker Compose for all environments

## Code Standards

### Python / FastAPI
- Type hints required on ALL function signatures — no bare `Any` without comment
- Pydantic v2 models for all request/response schemas
- SQLAlchemy 2.x async sessions — no synchronous DB calls in async routes
- Repository pattern: DB logic lives in `repositories/`, NOT in routers
- Services layer: business logic in `services/`, called by routers
- All routes return typed Pydantic response models
- HTTP status codes must be explicit — never rely on FastAPI defaults silently
- Use `Annotated[X, Depends(Y)]` dependency injection style
- Errors: raise `HTTPException` with clear detail messages; use custom exception handlers
- Tests: pytest + httpx `AsyncClient`; every new endpoint needs at minimum a happy-path test

### Dart / Flutter
- Riverpod 2.x for all state management — no Provider, no setState in screens
- Feature-first folder structure: `lib/features/<feature>/`
- Each feature: `data/`, `domain/`, `presentation/` sub-layers
- Dio for HTTP with interceptors for auth token refresh
- `go_router` for navigation
- No hardcoded strings in UI — all user-visible text in `l10n/` ARB files
- Responsive layouts: use `LayoutBuilder` / `AdaptiveScaffold` for web vs mobile vs desktop
- All async operations must handle loading + error states — never a bare `then()`

### Database
- UUID v7 primary keys on all tables (time-sortable)
- All timestamps in UTC, stored as `TIMESTAMPTZ`
- Soft deletes with `deleted_at TIMESTAMPTZ` — never hard DELETE user-created content
- Alembic migrations for every schema change — no manual `ALTER TABLE`
- Index strategy: GIN index on full-text search columns, B-tree on all FK and filter columns

### Git Conventions
- Branch naming: `feat/`, `fix/`, `chore/`, `refactor/`, `docs/`
- Commit format: `type(scope): short description` (Conventional Commits)
- PRs must pass: linting (ruff, dart analyze), type check (mypy strict, dart analyze), tests
- Never commit `.env` files — use `.env.example` as template

## Agent Roles (see .claude/commands/ and .opencode/agents/)
| Agent | Primary tool | Responsibility |
|---|---|---|
| architect | Claude Code | System design, ADRs, schema decisions |
| backend-dev | Cline / OpenCode | FastAPI routes, services, repositories |
| flutter-dev | Antigravity | Flutter screens, widgets, Riverpod providers |
| db-designer | Claude Code | Schema design, Alembic migrations |
| code-reviewer | Copilot / Claude Code | PR review, quality gates |
| security-auditor | Claude Code | Prompt injection, auth, data exposure checks |
| sync-engineer | Cline / OpenCode | AniList/MangaDex sync pipeline, Celery workers |
| api-designer | Claude Code | OpenAPI spec, endpoint contracts |

## Critical Safety Rules
- NEVER write to the production database without explicit user confirmation
- NEVER commit secrets, API keys, or tokens to Git
- NEVER delete user tracking data or progress without a soft-delete + confirmation
- NEVER call AniList or MangaDex directly from Flutter — all external API calls go through FastAPI
- ALWAYS run `alembic upgrade head` in a transaction; wrap migrations in `op.execute("BEGIN")`
- ALWAYS check for existing Alembic revision before creating a new one

## File References
Read these files before starting any task in their domain:
- Backend work: `docs/backend-architecture.md`
- Flutter work: `docs/flutter-architecture.md`
- Database work: `docs/database-schema.md`
- Sync pipeline: `docs/sync-pipeline.md`
- API contracts: `docs/api-spec.md`
