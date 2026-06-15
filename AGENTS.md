# OtakuHub — AI Agent Master Instructions

## Project Identity
OtakuHub is a **private friend-group anime/manga/manhwa tracking and social platform**.
It is NOT a public community tool. Every design decision should optimise for a small group
of known users (5–20 people), not scale or strangers.

## Monorepo Structure
```
otakuhub/
├── backend/          # FastAPI Python backend
├── frontend/         # Quasar (Vue 3) app — web, Electron desktop, Capacitor mobile
├── infra/            # Docker Compose, Nginx, env configs
├── docs/             # Architecture and design docs
└── scripts/          # DB seed, sync workers, dev utilities
```

## Tech Stack — Non-Negotiable
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.x async, Alembic, Celery + Redis, PostgreSQL 16
- **Frontend**: Quasar 2.x (Vue 3 + Vite) — single codebase for all platforms:
  - Web: SPA / PWA / SSR via `quasar build`
  - Android + iOS: Capacitor 6
  - Windows + Linux desktop: Electron
- **State**: Pinia (with pinia-plugin-persistedstate for auth tokens)
- **HTTP**: Axios with request/response interceptors
- **Language**: TypeScript strict mode throughout
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

### TypeScript / Vue 3 / Quasar
- `<script setup lang="ts">` on every component — no Options API
- Strict TypeScript: `"strict": true` in tsconfig — no implicit `any`
- Pinia stores in `src/stores/<name>.ts` — one store per domain
- Composables in `src/composables/use<Name>.ts` for reusable logic
- All API responses typed with Zod schemas or hand-written interfaces
- `vue-router` 4.x with typed routes — no untyped `$route` access
- Quasar components preferred over custom HTML — use `QCard`, `QList`, `QItem`, etc.
- Responsive: use Quasar's `$q.screen` breakpoints and `col-*` grid — not raw CSS media queries
- Never use `any` — use `unknown` and narrow, or write proper interfaces
- All async operations in composables: expose `isLoading`, `error`, and `data` refs
- All forms must have client-side validation for required fields and basic format constraints before API submission
- Use Quasar form primitives (`QForm`, `QInput` rules, `lazy-rules`) and show actionable validation messages
- Add/update Vitest tests for form validation flows (empty submit, invalid input, successful submit)

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
- PRs must pass: eslint + vue-tsc (frontend), ruff + mypy (backend), tests

## Agent Roles
| Agent | Primary tool | Responsibility |
|---|---|---|
| architect | Claude Code | System design, ADRs, schema decisions |
| backend-dev | Cline / OpenCode | FastAPI routes, services, repositories |
| quasar-dev | Antigravity | Quasar pages, components, Pinia stores |
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
- NEVER use `any` in TypeScript without a comment explaining why
- ALWAYS run `quasar build` in all target modes before marking frontend work done
- ALWAYS check for existing Alembic revision before creating a new one

## File References
- Backend work: `docs/backend-architecture.md`
- Frontend work: `docs/frontend-architecture.md`
- Database work: `docs/database-schema.md`
- Sync pipeline: `docs/sync-pipeline.md`
- API contracts: `docs/api-spec.md`
