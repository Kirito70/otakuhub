# OtakuHub — Project Status

> This file is the single source of truth for build progress.
> Every AI agent MUST read this file before starting any task.
> Update this file at the end of every phase or sub-task completion.
> Never skip ahead — complete the current phase before marking it done.

---

## Current State

```
CURRENT_PHASE:     2
CURRENT_SUB_PHASE: 2.14
STATUS:            PHASE_COMPLETE
LAST_UPDATED:      2026-04-24
BLOCKED_BY:        none
NEXT_ACTION:       Begin Phase 3: Anime Metadata Pipeline
LAST_UPDATED:      (set this when you update)
BLOCKED_BY:        none
NEXT_ACTION:       Set up monorepo structure and Docker Compose dev environment
```

---

## Phase Overview

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation & Infrastructure | 🔄 In progress |
| 2 | Database & Backend Core | ⏳ Not started |
| 3 | Anime Metadata Pipeline | ⏳ Not started |
| 4 | User Auth & Groups | ⏳ Not started |
| 5 | Tracking & Lists | ⏳ Not started |
| 6 | Flutter App Shell | ⏳ Not started |
| 7 | Flutter Tracking Screens | ⏳ Not started |
| 8 | Social Features — Backend | ⏳ Not started |
| 9 | Social Features — Flutter | ⏳ Not started |
| 10 | Watch Party | ⏳ Not started |
| 11 | Notifications | ⏳ Not started |
| 12 | Polish, Testing & Deploy | ⏳ Not started |

---

## Detailed Phase Tracking

### Phase 1 — Foundation & Infrastructure
**Goal**: Monorepo skeleton, Docker environment, CI skeleton, all tools reading agent config.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 1.1 | Monorepo directory structure created | ⏳ | backend/, mobile/, infra/, scripts/, docs/ |
| 1.2 | Docker Compose dev stack (postgres, redis, backend, worker) | ⏳ | |
| 1.3 | Docker Compose prod stack | ⏳ | |
| 1.4 | FastAPI app skeleton (main.py, core/, routers/) | ✅ | |
| 1.5 | Alembic configured, initial empty migration | ✅ | |
| 1.6 | Flutter project init, pubspec.yaml with all deps | ✅ | |
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
| 3.1 | AniList GraphQL client (with rate limiter) | ⏳ | |
| 3.2 | MangaDex REST client (with rate limiter) | ⏳ | |
| 3.3 | Jikan client (supplement) | ⏳ | |
| 3.4 | Seed script: download + import anime-offline-database | ⏳ | |
| 3.5 | Celery app + Redis broker configured | ⏳ | |
| 3.6 | Backfill worker: AniList batch fetch (50 IDs/query) | ⏳ | |
| 3.7 | MangaDex detail worker (chapters, cover art) | ⏳ | |
| 3.8 | Weekly refresh cron task | ⏳ | |
| 3.9 | On-demand fetch (search miss handler) | ⏳ | |
| 3.10 | Media search endpoint: GET /api/v1/media/search | ⏳ | |
| 3.11 | Media detail endpoint: GET /api/v1/media/{id} | ⏳ | |
| 3.12 | Airing calendar endpoint: GET /api/v1/media/airing | ⏳ | |
| 3.13 | Seed script tested, 29k entries confirmed in DB | ⏳ | |

### Phase 4 — User Auth & Groups
**Goal**: Register, login, JWT refresh, group creation and invite system working end-to-end.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 4.1 | POST /api/v1/auth/register | ⏳ | |
| 4.2 | POST /api/v1/auth/login | ⏳ | |
| 4.3 | POST /api/v1/auth/refresh | ⏳ | |
| 4.4 | POST /api/v1/auth/logout | ⏳ | |
| 4.5 | GET /api/v1/users/me | ⏳ | |
| 4.6 | PATCH /api/v1/users/me | ⏳ | |
| 4.7 | POST /api/v1/groups | ⏳ | |
| 4.8 | GET /api/v1/groups/{id} | ⏳ | |
| 4.9 | POST /api/v1/groups/join/{invite_code} | ⏳ | |
| 4.10 | GET /api/v1/groups/{id}/members | ⏳ | |
| 4.11 | Auth tests (happy path, wrong password, expired token) | ⏳ | |

### Phase 5 — Tracking & Lists
**Goal**: Full list CRUD — add, update progress, score, remove, custom lists.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 5.1 | GET /api/v1/lists/me (user's full list) | ⏳ | |
| 5.2 | POST /api/v1/lists (add to list) | ⏳ | |
| 5.3 | PATCH /api/v1/lists/{media_id} (update status/progress/score) | ⏳ | |
| 5.4 | DELETE /api/v1/lists/{media_id} (soft delete) | ⏳ | |
| 5.5 | GET /api/v1/lists/me/history (activity history) | ⏳ | |
| 5.6 | POST /api/v1/sync/import/anilist (user list import) | ⏳ | |
| 5.7 | POST /api/v1/sync/import/mal | ⏳ | |
| 5.8 | POST /api/v1/lists/custom (create custom list) | ⏳ | |
| 5.9 | PUT /api/v1/lists/custom/{id}/entries | ⏳ | |
| 5.10 | List entry history auto-logged on every update | ⏳ | |

### Phase 6 — Flutter App Shell
**Goal**: Flutter app navigates correctly on all 5 platforms, auth flow works, Dio talks to backend.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 6.1 | GoRouter setup: all named routes defined | ⏳ | |
| 6.2 | AdaptiveScaffold shell: bottom nav (mobile), side nav (desktop) | ⏳ | |
| 6.3 | Dio client + auth interceptor (token attach + refresh on 401) | ⏳ | |
| 6.4 | flutter_secure_storage wrapper | ⏳ | |
| 6.5 | Auth feature: login screen | ⏳ | |
| 6.6 | Auth feature: register screen | ⏳ | |
| 6.7 | Auth Riverpod provider (AuthNotifier) | ⏳ | |
| 6.8 | App theme: Material 3 light + dark | ⏳ | |
| 6.9 | Auth guard in GoRouter redirect | ⏳ | |
| 6.10 | App runs on: web, Windows, Android (confirm all three) | ⏳ | |

### Phase 7 — Flutter Tracking Screens
**Goal**: Users can search anime/manga, add to list, update progress from the app.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 7.1 | Discover/search screen (calls GET /media/search) | ⏳ | |
| 7.2 | Media detail screen (full info page) | ⏳ | |
| 7.3 | Add to list bottom sheet | ⏳ | |
| 7.4 | My list screen (tabbed by status) | ⏳ | |
| 7.5 | Progress update widget (episode counter, chapter counter) | ⏳ | |
| 7.6 | Score widget | ⏳ | |
| 7.7 | Airing calendar screen | ⏳ | |
| 7.8 | Import list screen (AniList/MAL OAuth) | ⏳ | |
| 7.9 | Custom list creation + management | ⏳ | |
| 7.10 | Widget tests for all new screens | ⏳ | |

### Phase 8 — Social Features — Backend
**Goal**: Friend activity feed, recommendations, and discussion endpoints live.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 8.1 | GET /api/v1/social/feed (group activity feed) | ⏳ | |
| 8.2 | POST /api/v1/social/recommend | ⏳ | |
| 8.3 | GET /api/v1/social/recommendations/inbox | ⏳ | |
| 8.4 | PATCH /api/v1/social/recommendations/{id}/acknowledge | ⏳ | |
| 8.5 | POST /api/v1/social/discussions | ⏳ | |
| 8.6 | GET /api/v1/social/discussions/{media_id} | ⏳ | |
| 8.7 | POST /api/v1/social/discussions/{id}/replies | ⏳ | |
| 8.8 | GET /api/v1/users/{username}/profile (public profile) | ⏳ | |

### Phase 9 — Social Features — Flutter
**Goal**: Friends can see each other's activity, recommend titles, discuss in-app.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 9.1 | Group activity feed screen | ⏳ | |
| 9.2 | Friend profile screen | ⏳ | |
| 9.3 | Recommend to friend bottom sheet | ⏳ | |
| 9.4 | Recommendations inbox screen | ⏳ | |
| 9.5 | Discussion thread screen (per anime) | ⏳ | |
| 9.6 | Discussion reply UI | ⏳ | |
| 9.7 | Group management screen (invite link, member list) | ⏳ | |

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
```
# Format: YYYY-MM-DD | Phase X.Y | <one-line description>
# Example:
# 2026-04-20 | Phase 1.1 | Monorepo directory structure created
# 2026-04-22 | Phase 1.1 | Monorepo directory structure created
# 2026-04-22 | Phase 1.2 | Docker Compose dev stack setup with postgres, redis, backend, worker
# 2026-04-22 | Phase 1.3 | Docker Compose prod stack setup
# 2026-04-22 | Phase 1.2 | Docker Compose dev stack setup with postgres, redis, backend, worker
```

---

## Known Blockers

> List anything that is blocking progress. Remove when resolved.

```
# Format: [OPEN/RESOLVED] Phase X.Y — description
# (none currently)
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
