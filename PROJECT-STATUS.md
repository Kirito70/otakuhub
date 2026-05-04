# OtakuHub — Project Status

> This file is the single source of truth for build progress.
> Every AI agent MUST read this file before starting any task.
> Update this file at the end of every phase or sub-task completion.
> Never skip ahead — complete the current phase before marking it done.

---

## Current State

```
CURRENT_PHASE:     7
CURRENT_SUB_PHASE: 7.10
STATUS:            IN_PROGRESS
LAST_UPDATED:      2026-05-05
BLOCKED_BY:        Android release build environment missing (JAVA_HOME / JDK)
NEXT_ACTION:       Set JAVA_HOME and rerun: quasar build -m capacitor -T android
```

---

## Phase Overview

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation & Infrastructure | ✅ Complete |
| 2 | Database & Backend Core | ✅ Complete |
| 3 | Anime Metadata Pipeline | ✅ Complete |
| 4 | Query Builder Pattern Implementation | ✅ Complete |
| 5 | User Auth & Groups | ✅ Complete |
| 6 | Tracking & Lists | ✅ Complete |
| 7 | Flutter App Shell | 🔄 In progress |
| 8 | Flutter Tracking Screens | ⏳ Not started |
| 9 | Social Features — Backend | ⏳ Not started |
| 10 | Social Features — Flutter | ⏳ Not started |
| 11 | Watch Party | ⏳ Not started |
| 12 | Notifications | ⏳ Not started |
| 13 | Polish, Testing & Deploy | ⏳ Not started |
| 14 | Type‑Checking Cleanup (MyPy) | ⏳ Not started |

---

## Detailed Phase Tracking

### Phase 1 — Foundation & Infrastructure
**Goal**: Monorepo skeleton, Docker environment, CI skeleton, all tools reading agent config.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 1.1 | Monorepo directory structure created | ✅ | backend/, frontend/, infra/, scripts/, docs/ |
| 1.2 | Docker Compose dev stack (postgres, redis, backend, worker) | ✅ | |
| 1.3 | Docker Compose prod stack | ✅ | |
| 1.4 | FastAPI app skeleton (main.py, core/, routers/) | ✅ | |
| 1.5 | Alembic configured, initial empty migration | ✅ | |
| 1.6 | Flutter project init, package.json (Quasar) with all deps | ✅ | |
| 1.7 | GitHub Actions CI: lint + test on PR | ✅ | |
| 1.8 | .env.example files for backend and mobile | ✅ | |

### Phase 2 — Database & Backend Core
**Goal**: All 28 tables migrated, repositories scaffolded, health check endpoint live.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 2.1 | PostgreSQL extensions (pg_uuidv7, pg_trgm, unaccent) | ✅ | |
| 2.2 | All enums created (media_type, watch_status, etc.) | ✅ | |
| 2.3 | Media catalogue tables migrated (media_entries, external_ids, genres, studios, tags, episodes, chapters, related_media) | ✅ | |
| 2.4 | User & auth tables migrated (users, refresh_tokens, external_auth) | ✅ | |
| 2.5 | Group tables migrated (groups, group_members) | ✅ | |
| 2.6 | Tracking tables migrated (user_list_entries, list_entry_history, custom_lists, custom_list_entries) | ✅ | |
| 2.7 | Social tables migrated (recommendations, discussions, discussion_replies) | ✅ | |
| 2.8 | Watch party tables migrated | ✅ | |
| 2.9 | Notification tables migrated | ✅ | |
| 2.10 | Sync jobs table migrated | ✅ | |
| 2.11 | All SQLAlchemy models written | ✅ | |
| 2.12 | Repository base classes scaffolded | ✅ | |
| 2.13 | GET /health endpoint | ✅ | |
| 2.14 | GET /api/v1/status endpoint (DB + Redis check) | ✅ | |

### Phase 3 — Anime Metadata Pipeline
**Goal**: 29k+ anime/manga entries in local DB, full AniList metadata backfilled.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 3.1 | AniList GraphQL client (with rate limiter) | ✅ | |
| 3.2 | MangaDex REST client (with rate limiter) | ✅ | |
| 3.3 | Jikan client (supplement) | ✅ | |
| 3.4 | Seed script: download + import anime-offline-database | ✅ | |
| 3.5 | Celery app + Redis broker configured | ✅ | |
| 3.6 | Backfill worker: AniList batch fetch (50 IDs/query) | ✅ | |
| 3.7 | MangaDex detail worker (chapters, cover art) | ✅ | |
| 3.8 | Weekly refresh cron task | ✅ | |
| 3.9 | On-demand fetch (search miss handler) | ✅ | |
| 3.10 | Media search endpoint: GET /api/v1/media/search | ✅ | |
| 3.11 | Media detail endpoint: GET /api/v1/media/{id} | ✅ | |
| 3.12 | Airing calendar endpoint: GET /api/v1/media/airing | ✅ | |
| 3.13 | Seed script tested, 29k entries confirmed in DB | ✅ | |

### Phase 4 — Query Builder Pattern Implementation
**Goal**: Implement consistent query builder pattern across all repositories, reducing points of failure and improving maintainability.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 4.1 | Create unified base query builder class | ✅ | |
| 4.2 | Implement fluent filtering methods (where, and_, or_) | ✅ | |
| 4.3 | Add support for ordering, pagination, and joins | ✅ | |
| 4.4 | Replace all existing repository queries with new pattern | ✅ | |
| 4.5 | Add method chaining for all repository operations | ✅ | |
| 4.6 | Test all repository methods with new API | ✅ | |
| 4.7 | Document the query builder pattern for future developers | ✅ | |

### Phase 5 — User Auth & Groups
**Goal**: Register, login, JWT refresh, group creation and invite system working end-to-end.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 5.1 | POST /api/v1/auth/register | ✅ | |
| 5.2 | POST /api/v1/auth/login | ✅ | |
| 5.3 | POST /api/v1/auth/refresh | ✅ | |
| 5.4 | POST /api/v1/auth/logout | ✅ | |
| 5.5 | GET /api/v1/users/me | ✅ | |
| 5.6 | PATCH /api/v1/users/me | ✅ | |
| 5.7 | POST /api/v1/groups | ✅ | |
| 5.8 | GET /api/v1/groups/{id} | ✅ | |
| 5.9 | POST /api/v1/groups/join/{invite_code} | ✅ | |
| 5.10 | GET /api/v1/groups/{id}/members | ✅ | |
| 5.11 | Auth tests (happy path, wrong password, expired token) | ✅ | |

### Phase 6 — Tracking & Lists
**Goal**: Full list CRUD — add, update progress, score, remove, custom lists.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 6.1 | GET /api/v1/lists/me (user's full list) | ✅ | Implemented endpoint, filters, and response schema |
| 6.2 | POST /api/v1/lists (add to list) | ✅ | Added root endpoint with legacy /entries alias for compatibility |
| 6.3 | PATCH /api/v1/lists/{media_id} (update status/progress/score) | ✅ | Added root endpoint with /entries compatibility alias |
| 6.4 | DELETE /api/v1/lists/{media_id} (soft delete) | ✅ | Added root endpoint with /entries compatibility alias |
| 6.5 | GET /api/v1/lists/me/history (activity history) | ✅ | Added authenticated history endpoint with limit query |
| 6.6 | POST /api/v1/sync/import/anilist (user list import) | ✅ | Added authenticated sync import endpoint returning created job metadata |
| 6.7 | POST /api/v1/sync/import/mal | ✅ | Added authenticated sync import endpoint returning created job metadata |
| 6.8 | POST /api/v1/lists/custom (create custom list) | ✅ | Added authenticated custom-list create endpoint and schema |
| 6.9 | PUT /api/v1/lists/custom/{id}/entries | ✅ | Added ownership-checked replace-all entries endpoint |
| 6.10 | List entry history auto-logged on every update | ✅ | Added explicit event_type mapping for status/progress/score updates |

### Phase 7 — Flutter App Shell
**Goal**: Flutter app navigates correctly on all 5 platforms, auth flow works, Dio talks to backend.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 7.1 | GoRouter setup: all named routes defined | ✅ | Implemented Quasar router named-route map in frontend/src/router/routes.ts with auth/public route split |
| 7.2 | AdaptiveScaffold shell: bottom nav (mobile), side nav (desktop) | ✅ | Implemented responsive MainLayout with desktop drawer + mobile bottom tabs navigation |
| 7.3 | Dio client + auth interceptor (token attach + refresh on 401) | ✅ | Implemented Quasar Axios boot client with bearer attach and 401 refresh retry flow |
| 7.4 | flutter_secure_storage wrapper | ✅ | Implemented secure storage service wrapper for token persistence and auth store hydration |
| 7.5 | Auth feature: login screen | ✅ | Implemented LoginPage with auth store integration, loading state, and error banner |
| 7.6 | Auth feature: register screen | ✅ | Implemented RegisterPage with auth store integration and post-auth redirect |
| 7.7 | Auth Riverpod provider (AuthNotifier) | ✅ | Implemented Quasar-equivalent Pinia auth store with login/register/refresh/logout + hydration |
| 7.8 | App theme: Material 3 light + dark | ✅ | Added theme composable, dark-mode toggle, and Quasar palette variables with auto dark boot |
| 7.9 | Auth guard in GoRouter redirect | ✅ | Added router beforeEach guard for protected routes and auth-page redirect when logged in |
| 7.10 | App runs on: web, Windows, Android (confirm all three) | ⏳ | |

### Phase 8 — Flutter Tracking Screens
**Goal**: Users can search anime/manga, add to list, update progress from the app.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 8.1 | Discover/search screen (calls GET /media/search) | ⏳ | |
| 8.2 | Media detail screen (full info page) | ⏳ | |
| 8.3 | Add to list bottom sheet | ⏳ | |
| 8.4 | My list screen (tabbed by status) | ⏳ | |
| 8.5 | Progress update widget (episode counter, chapter counter) | ⏳ | |
| 8.6 | Score widget | ⏳ | |
| 8.7 | Airing calendar screen | ⏳ | |
| 8.8 | Import list screen (AniList/MAL OAuth) | ⏳ | |
| 8.9 | Custom list creation + management | ⏳ | |
| 8.10 | Widget tests for all new screens | ⏳ | |

### Phase 9 — Social Features — Backend
**Goal**: Friend activity feed, recommendations, and discussion endpoints live.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 9.1 | GET /api/v1/social/feed (group activity feed) | ⏳ | |
| 9.2 | POST /api/v1/social/recommend | ⏳ | |
| 9.3 | GET /api/v1/social/recommendations/inbox | ⏳ | |
| 9.4 | PATCH /api/v1/social/recommendations/{id}/acknowledge | ⏳ | |
| 9.5 | POST /api/v1/social/discussions | ⏳ | |
| 9.6 | GET /api/v1/social/discussions/{media_id} | ⏳ | |
| 9.7 | POST /api/v1/social/discussions/{id}/replies | ⏳ | |
| 9.8 | GET /api/v1/users/{username}/profile (public profile) | ⏳ | |

### Phase 10 — Watch Party
**Goal**: Create watch party, RSVP, share stream link.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 10.1 | POST /api/v1/watchparty | ⏳ | |
| 10.2 | GET /api/v1/watchparty (upcoming in group) | ⏳ | |
| 10.3 | POST /api/v1/watchparty/{id}/rsvp | ⏳ | |
| 10.4 | Watch party list screen (Flutter) | ⏳ | |
| 10.5 | Create watch party screen (Flutter) | ⏳ | |
| 10.6 | Watch party detail + RSVP screen (Flutter) | ⏳ | |

### Phase 11 — Notifications
**Goal**: New episode/chapter alerts and group activity push via Apprise.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 11.1 | Apprise client configured | ⏳ | |
| 11.2 | New episode notification Celery task | ⏳ | |
| 11.3 | New chapter notification Celery task | ⏳ | |
| 11.4 | Watch party reminder Celery task | ⏳ | |
| 11.5 | GET /api/v1/notifications | ⏳ | |
| 11.6 | PATCH /api/v1/notifications/read | ⏳ | |
| 11.7 | Notification preferences: GET + PATCH /api/v1/notifications/preferences | ⏳ | |
| 11.8 | Notification bell screen (Flutter) | ⏳ | |
| 11.9 | Notification preferences screen (Flutter) | ⏳ | |

### Phase 12 — Polish, Testing & Deploy
**Goal**: Full test suite, Docker prod deploy, all platforms verified.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 12.1 | Backend test coverage ≥ 80% | ⏳ | |
| 12.2 | Flutter widget test coverage for all screens | ⏳ | |
| 12.3 | Security audit (run /audit-security) | ⏳ | |
| 12.4 | Performance: search < 200ms p95 | ⏳ | |
| 12.5 | Flutter build verified: web, Windows, Android, iOS, Linux | ⏳ | |
| 12.6 | Docker prod compose tested | ⏳ | |
| 12.7 | Nginx config + TLS | ⏳ | |
| 12.8 | README.md with setup instructions | ⏳ | |
| 12.9 | All ADRs written (docs/adr/) | ⏳ | |

---

## Completion Log

> Add a line here every time a sub-phase is completed.

```
# Format: YYYY-MM-DD | Phase X.Y | <one-line description>
# Example:
# 2026-04-20 | Phase 1.1 | Monorepo directory structure created
# 2026-04-22 | Phase 1.2 | Docker Compose dev stack setup with postgres, redis, backend, worker
# 2026-04-22 | Phase 1.3 | Docker Compose prod stack setup
# 2026-04-22 | Phase 1.2 | Docker Compose dev stack setup with postgres, redis, backend, worker
# 2026-04-24 | Phase 2.1 | PostgreSQL extensions implemented
# 2026-04-24 | Phase 2.2 | All enums created
# 2026-04-24 | Phase 2.3 | Media catalogue tables migrated
# 2026-04-24 | Phase 2.4 | User & auth tables migrated
# 2026-04-24 | Phase 2.5 | Group tables migrated
# 2026-04-24 | Phase 2.6 | Tracking tables migrated
# 2026-04-24 | Phase 2.7 | Social tables migrated
# 2026-04-24 | Phase 2.8 | Watch party tables migrated
# 2026-04-24 | Phase 2.9 | Notification tables migrated
# 2026-04-24 | Phase 2.10 | Sync jobs table migrated
# 2026-04-24 | Phase 2.11 | All SQLAlchemy models written
# 2026-04-24 | Phase 2.12 | Repository base classes scaffolded
# 2026-04-24 | Phase 2.13 | GET /health endpoint implemented
# 2026-04-24 | Phase 2.14 | GET /api/v1/status endpoint implemented
# 2026-04-26 | Phase 3.1 | AniList GraphQL client implemented
# 2026-04-26 | Phase 3.2 | MangaDex REST client implemented
# 2026-04-26 | Phase 3.3 | Jikan client implemented
# 2026-04-26 | Phase 3.4 | Seed script: download + import anime-offline-database created
# 2026-04-26 | Phase 3.5 | Celery app + Redis broker configured
# 2026-04-26 | Phase 3.6 | Backfill worker: AniList batch fetch implemented
# 2026-04-26 | Phase 3.7 | MangaDex detail worker implemented
# 2026-04-26 | Phase 3.8 | Weekly refresh cron task implemented
# 2026-04-26 | Phase 3.9 | On-demand fetch mechanism implemented
# 2026-04-26 | Phase 3.10 | Media search endpoint implemented
# 2026-04-26 | Phase 3.11 | Media detail endpoint implemented
# 2026-04-26 | Phase 3.12 | Airing calendar endpoint implemented
# 2026-04-26 | Phase 3.13 | Seed script tested and functional
```
# Format: YYYY-MM-DD | Phase X.Y | <one-line description>
# Example:
# 2026-04-20 | Phase 1.1 | Monorepo directory structure created
# 2026-04-22 | Phase 1.1 | Monorepo directory structure created
# 2026-04-22 | Phase 1.2 | Docker Compose dev stack setup with postgres, redis, backend, worker
# 2026-04-22 | Phase 1.3 | Docker Compose prod stack setup
# 2026-04-22 | Phase 1.2 | Docker Compose dev stack setup with postgres, redis, backend, worker
# 2026-04-24 | Phase 2.1 | PostgreSQL extensions implemented
# 2026-04-24 | Phase 2.2 | All enums created
# 2026-04-24 | Phase 2.3 | Media catalogue tables migrated
# 2026-04-24 | Phase 2.4 | User & auth tables migrated
# 2026-04-24 | Phase 2.5 | Group tables migrated
# 2026-04-24 | Phase 2.6 | Tracking tables migrated
# 2026-04-24 | Phase 2.7 | Social tables migrated
# 2026-04-24 | Phase 2.8 | Watch party tables migrated
# 2026-04-24 | Phase 2.9 | Notification tables migrated
# 2026-04-24 | Phase 2.10 | Sync jobs table migrated
# 2026-04-24 | Phase 2.11 | All SQLAlchemy models written
# 2026-04-24 | Phase 2.12 | Repository base classes scaffolded
# 2026-04-24 | Phase 2.13 | GET /health endpoint implemented
# 2026-04-24 | Phase 2.14 | GET /api/v1/status endpoint implemented
# 2026-04-26 | Phase 3.1 | AniList GraphQL client implemented
# 2026-04-26 | Phase 3.2 | MangaDex REST client implemented
# 2026-04-26 | Phase 3.3 | Jikan client implemented
# 2026-04-26 | Phase 3.4 | Seed script: download + import anime-offline-database created
# 2026-04-26 | Phase 3.5 | Celery app + Redis broker configured
# 2026-04-26 | Phase 3.6 | Backfill worker: AniList batch fetch implemented
# 2026-04-26 | Phase 3.7 | MangaDex detail worker implemented
# 2026-04-26 | Phase 3.8 | Weekly refresh cron task implemented
# 2026-04-26 | Phase 3.9 | On-demand fetch mechanism implemented
# 2026-04-26 | Phase 3.10 | Media search endpoint implemented
# 2026-04-26 | Phase 3.11 | Media detail endpoint implemented
# 2026-04-26 | Phase 3.12 | Airing calendar endpoint implemented
# 2026-04-26 | Phase 3.13 | Seed script tested and functional
# 2026-05-04 | Phase 4.1 | Query builder base class created and implemented
# 2026-05-04 | Phase 4.2 | Fluent filtering methods (where, and_, or_) implemented
# 2026-05-04 | Phase 4.3 | Support for ordering, pagination, and joins added
# 2026-05-04 | Phase 4.5 | Method chaining for all repository operations completed
# 2026-05-04 | Phase 4.6 | Repository query builder tests completed
# 2026-05-04 | Phase 4.7 | Query builder pattern documentation completed
# 2026-05-04 | Phase 5.1 | Phase 5 started: auth register/login/refresh/logout scaffolding implemented
# 2026-05-04 | Phase 5 | User Auth & Groups marked complete
# 2026-05-04 | Phase 6.1 | Implemented GET /api/v1/lists/me with auth, filters, and response envelope
# 2026-05-04 | Phase 6.2 | Implemented POST /api/v1/lists with /entries compatibility alias
# 2026-05-04 | Phase 6.3 | Implemented PATCH /api/v1/lists/{media_id} with /entries compatibility alias
# 2026-05-04 | Phase 6.4 | Implemented DELETE /api/v1/lists/{media_id} with /entries compatibility alias
# 2026-05-04 | Phase 6.5 | Implemented GET /api/v1/lists/me/history endpoint
# 2026-05-04 | Phase 6.6 | Implemented POST /api/v1/sync/import/anilist endpoint
# 2026-05-04 | Phase 6.7 | Implemented POST /api/v1/sync/import/mal endpoint
# 2026-05-04 | Phase 6.8 | Implemented POST /api/v1/lists/custom endpoint
# 2026-05-04 | Phase 6.9 | Implemented PUT /api/v1/lists/custom/{id}/entries endpoint
# 2026-05-04 | Phase 6.10 | Implemented explicit list-entry history auto-log event typing on updates
# 2026-05-04 | Phase 6 | Tracking & Lists marked complete
# 2026-05-04 | Phase 7.1 | Implemented frontend named routes and router setup scaffold
# 2026-05-04 | Phase 7.2 | Implemented adaptive app shell with responsive drawer and bottom tabs
# 2026-05-04 | Phase 7.3 | Implemented Axios auth interceptor with token attach and automatic refresh retry
# 2026-05-04 | Phase 7.4 | Implemented frontend secure token storage wrapper and auth hydration store
# 2026-05-04 | Phase 7.5 | Implemented login screen with auth submission flow
# 2026-05-04 | Phase 7.6 | Implemented register screen with auth submission flow
# 2026-05-04 | Phase 7.7 | Implemented Pinia auth provider/store replacing Riverpod intent for Quasar
# 2026-05-04 | Phase 7.8 | Implemented light/dark theme scaffolding and runtime toggle
# 2026-05-04 | Phase 7.9 | Implemented router auth guard and redirect rules
```

---

## Known Blockers

> List anything that is blocking progress. Remove when resolved.

```
# Format: [OPEN/RESOLVED] Phase X.Y — description
[OPEN] Phase 7.10 — Android build blocked: JAVA_HOME/JDK not configured in environment
```

---

## Agent Instructions for Reading This File

When an AI agent reads this file, it must:
1. Find the `CURRENT_PHASE` and `CURRENT_SUB_PHASE` values
2. Find the corresponding row in the detailed table
3. Only work on that specific sub-phase task
4. After completing the task, update the row status from ⏳ to ✅
5. Set `CURRENT_SUB_PHASE` to the next ⏳ item in the same phase
6. If the entire phase is complete, set all rows to ✅, update `CURRENT_PHASE`, and set `STATUS` to `PHASE_COMPLETE` until the user advances
7. Add a line to the Completion Log
8. Never modify completed (✅) entries

