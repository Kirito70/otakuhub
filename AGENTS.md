# OtakuHub — AI Agent Master Instructions

## Project Identity
OtakuHub is a **private friend-group anime/manga/manhwa tracking and social platform**.
It is NOT a public community tool. Every design decision should optimise for a small group
of known users (5–20 people), not scale or strangers.

## Monorepo Structure
```
otakuhub/
├── backend/          # FastAPI Python backend
├── frontend/         # Vue 3 app (REFERENCE — kept for reference only)
│   └── flutter/      # Flutter app (ACTIVE PRIMARY FRONTEND) — mobile, desktop, web, TV
├── infra/            # Docker Compose, Nginx, env configs
├── docs/             # Architecture and design docs
└── scripts/          # DB seed, sync workers, dev utilities
```

## Tech Stack — Non-Negotiable
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.x async, Alembic, Celery + Redis, PostgreSQL 16
- **Frontend (active)**: Flutter 3.x (Dart 3.x) — single codebase for all platforms:
  - Mobile: Android (APK/AAB), iOS (IPA) — native ARM
  - Desktop: Windows, macOS, Linux — native executables
  - Web: Flutter for Web (CanvasKit renderer)
  - TV: Android TV, Fire TV — same APK as mobile with Focus widget navigation
  - Tablet: Same codebase with adaptive LayoutBuilder breakpoints
- **Frontend (reference)**: Vue 3 + Vite + Tailwind (kept at `frontend/` for design/UX reference only)
- **State**: Riverpod 2.x (notifiers, futures, families)
- **HTTP**: Dio with auth interceptor (token attach + 401 refresh)
- **Models**: `freezed` + `json_serializable` for immutable data classes
- **Auth**: JWT (access + refresh tokens), bcrypt password hashing
- **External APIs**: AniList GraphQL (primary), MangaDex REST v5, Jikan v4
- **Notifications**: Apprise (Discord, Telegram, email, push)
- **Container**: Docker + Docker Compose for all environments

## Code Standards

## Test-Driven Development (TDD) Policy — Mandatory
- For **every frontend and backend feature**, follow red → green → refactor.
- Write or update tests **before** implementation changes when feasible.
- If legacy code prevents strict test-first order, add failing regression tests immediately after reproducing the bug, then implement fix.
- Never mark a task complete unless relevant tests were added/updated and executed.
- For frontend UX work, include form-level validation tests (required fields, invalid format, disabled submit, inline error states).

### Dart / Flutter
- Feature-first structure: `lib/features/<name>/` — models, providers, screens, widgets
- Riverpod 2.x for state — NotifierProvider for complex state, FutureProvider for async, StateProvider for simple
- `freezed` + `json_serializable` for all data models — immutable, generated code
- Dio with auth interceptor for all HTTP — never use `http` package directly
- GoRouter with ShellRoute for adaptive layouts — auth guard redirect
- Responsive: `LayoutBuilder` + breakpoints (600/1024) — not hardcoded sizes
- TV: `Focus` widget for D-pad navigation — all interactive elements must be focusable
- AdaptiveScaffold widget: bottom nav (<600), rail (600–1024), drawer (>1024)
- All forms validated before API submission — use Form + TextFormField validator
- Add/update flutter_test + mocktail tests for every screen (loading, error, data states)
- Never use `dynamic` — always explicit types

### Python / FastAPI (unchanged)
- Type hints required on ALL function signatures
- Pydantic v2 models for all request/response schemas
- SQLAlchemy 2.x async sessions — no synchronous DB calls in async routes
- Repository pattern: DB logic in `repositories/`, business logic in `services/`
- All routes return typed Pydantic response models
- Use `Annotated[X, Depends(Y)]` dependency injection style
- Tests: pytest + httpx AsyncClient

### Database (unchanged)
- UUID v7 primary keys on all tables
- All timestamps UTC as TIMESTAMPTZ
- Soft deletes with `deleted_at TIMESTAMPTZ`
- Alembic migrations for every schema change
- GIN index on full-text search columns

### Git Conventions
- Branch naming: `feat/`, `fix/`, `chore/`, `refactor/`, `docs/`
- Commit format: `type(scope): short description` (Conventional Commits)
- PRs must pass: flutter analyze + flutter test (frontend), ruff + mypy (backend), tests

## Agent Roles
| Agent | Primary tool | Responsibility |
|---|---|---|
| architect | Claude Code | System design, ADRs, schema decisions |
| backend-dev | Cline / OpenCode | FastAPI routes, services, repositories |
| flutter-dev | Cline / OpenCode | Flutter/Dart screens, Riverpod providers, GoRouter, widgets |
| db-designer | Claude Code | Schema design, Alembic migrations |
| code-reviewer | Copilot / Claude Code | PR review, quality gates |
| security-auditor | Claude Code | Auth, SQL injection, data exposure checks |
| sync-engineer | Cline / OpenCode | AniList/MangaDex sync pipeline, Celery workers |
| api-designer | Claude Code | OpenAPI spec, endpoint contracts |

## Phase Execution Discipline (Mandatory)
- Before starting implementation, read `PROJECT-STATUS.md` and identify the exact current phase/sub-phase.
- Create a TODO checklist for all sub-phases in the current phase, and create sub-todos for non-trivial items.
- Keep exactly one TODO item `in_progress` at a time.
- Mark each sub-phase complete immediately after verification.
- Do not mark a phase complete until all its sub-phases are implemented and verified.
- Update `PROJECT-STATUS.md` after each completed sub-phase.

## Critical Safety Rules
- NEVER write to production database without explicit user confirmation
- NEVER commit secrets, API keys, or tokens to Git
- NEVER call AniList or MangaDex directly from the frontend — all external API calls go through FastAPI
- NEVER call AniList or MangaDex directly from the frontend — all external API calls go through FastAPI
- ALWAYS run `flutter analyze && flutter test` before marking frontend work done
- ALWAYS run `flutter build web` for web target, `flutter build apk` for Android, `flutter build windows` for desktop before cross-platform release
- ALWAYS check for existing Alembic revision before creating a new one

## File References
- Backend work: `docs/backend-architecture.md`
- Frontend work: `docs/flutter-architecture.md`
- Database work: `docs/database-schema.md`
- Sync pipeline: `docs/sync-pipeline.md`
- API contracts: `docs/api-spec.md`
- Vue reference: `docs/frontend-architecture.md`
