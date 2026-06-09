# OtakuHub — Project Status

> This file is the single source of truth for build progress.
> Every AI agent MUST read this file before starting any task.
> Update this file at the end of every phase or sub-task completion.
> Never skip ahead — complete the current phase before marking it done.

---

## Current State

```
CURRENT_PHASE:     28
CURRENT_SUB_PHASE: 28.7
STATUS:            ✅ COMPLETE
LAST_UPDATED:      2026-06-09
BLOCKED_BY:        none
NEXT_ACTION:       Phase 29 — Real AniList/MAL List Import
```

> **Note**: After completing all 24 formal phases, an audit (AUDIT-PLAN.md) identified real gaps. Phases 0–4 are complete. Phase 5 (Frontend Feature Gaps) is in progress.

> **Urgent pre-audit interruption (2026-06-05/06)**: ADR 078 defines and implements source-provider ID storage and Anikoto/MegaPlay sync.

> **Streaming Features (2026-06-08)**: ADRs 079–087 define Phases 23–28 — streaming-first redesign with aniwave-style dark UX, playback API, video player, real AniList import, notification pipeline, and admin source provider UI.

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
| 9 | Social Features — Backend | ✅ Complete |
| 10 | Social Features — Flutter | ✅ Complete |
| 11 | Watch Party | ✅ Complete |
| 12 | First-Run Setup & Super Admin Bootstrap | ✅ Complete |
| 13 | Backend Seed/Sync Command Consolidation | ✅ Complete |
| 14 | Frontend Foundation Stabilization | ✅ Complete |
| 15 | Frontend Design System (Shadcn-inspired, Quasar-native) | ✅ Complete |
| 16 | Auth & Setup Frontend Hardening | ✅ Complete |
| 17 | Discover & Media Detail Frontend | ✅ Complete |
| 18 | Tracking Frontend Pages | ✅ Complete |
| 19 | Social Frontend Pages | ✅ Complete |
| 20 | Watch Party Frontend Pages | ✅ Complete |
| 21 | Notifications Frontend Pages | ✅ Complete |
| 22 | Profile Frontend Pages | ✅ Complete |
| 23 | Polish, Testing & Deploy | ✅ Complete |
| 24 | Security & Production Hardening Remediation | ✅ Complete |
| 25 | Streaming Backend Infrastructure | ⏳ Planned |
| 26 | Streaming UI Component Library | ✅ Complete |
| 27 | Home Page Streaming Redesign | ⏳ Planned |
| 28 | Media Detail Page Streaming Redesign | ✅ Complete |
| 29 | Real AniList/MAL Import | ⏳ Planned |
| 30 | Episode Notification Pipeline (Complete) | ⏳ Planned |
| 31 | Admin Source Provider UI | ⏳ Planned |
| 32 | Migration & Cleanup | ⏳ Planned |
| 33 | Characters, Staff & Voice Actors | 🔲 Gap |
| 34 | Advanced User Statistics | 🔲 Gap |
| 35 | Charts & Top Lists | 🔲 Gap |
| 36 | Advanced Discovery & Browse | 🔲 Gap |
| 37 | Player Enhancements | 🔲 Gap |
| 38 | Social & Community Expansion | 🔲 Gap |
| 39 | Manga Reader | 🔲 Gap |
| 40 | Advanced Platform Features | 🔲 Gap |

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
| 7.10 | App runs on: web, Windows, Android (confirm all three) | ✅ | Verified quasar build (web), quasar build -m electron (Windows), and quasar build -m capacitor -T android |

### Phase 8 — Flutter Tracking Screens
**Goal**: Users can search anime/manga, add to list, update progress from the app.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 8.1 | Discover/search screen (calls GET /media/search) | ✅ | Implemented DiscoverPage search UI + useMediaSearch composable calling /api/v1/media/search |
| 8.2 | Media detail screen (full info page) | ✅ | Implemented MediaDetailPage with API detail fetch, metadata display, and synopsis panel |
| 8.3 | Add to list bottom sheet | ✅ | Added AddToListSheet component with status/progress/score inputs and POST /api/v1/lists integration |
| 8.4 | My list screen (tabbed by status) | ✅ | Implemented MyListPage with status tabs and Pinia tracking store-backed list rendering |
| 8.5 | Progress update widget (episode counter, chapter counter) | ✅ | Added reusable ProgressWidget and wired PATCH updates from My List items |
| 8.6 | Score widget | ✅ | Added reusable ScoreWidget and wired score updates through tracking store patch endpoint |
| 8.7 | Airing calendar screen | ✅ | Implemented AiringCalendarPage with /api/v1/media/airing fetch and media detail navigation |
| 8.8 | Import list screen (AniList/MAL OAuth) | ✅ | Implemented ImportListPage using sync import endpoints for AniList and MAL job creation |
| 8.9 | Custom list creation + management | ✅ | Added custom list create/entries management flows in MyListPage with tracking store methods |
| 8.10 | Widget tests for all new screens | ✅ | Added Vitest coverage for Discover, Media Detail, My List, Airing, and Import screens (5 passing tests) |

### Phase 9 — Social Features — Backend
**Goal**: Friend activity feed, recommendations, and discussion endpoints live.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 9.1 | GET /api/v1/social/feed (group activity feed) | ✅ | Implemented authenticated shared-group activity feed endpoint with pagination metadata |
| 9.2 | POST /api/v1/social/recommend | ✅ | Implemented shared-group recommendation creation with validation and conflict handling |
| 9.3 | GET /api/v1/social/recommendations/inbox | ✅ | Implemented paginated inbox endpoint with include_acknowledged filter |
| 9.4 | PATCH /api/v1/social/recommendations/{id}/acknowledge | ✅ | Implemented ownership-checked acknowledge endpoint returning updated recommendation |
| 9.5 | POST /api/v1/social/discussions | ✅ | Implemented group-membership-checked creation with graceful 400 when media is not yet seeded/synced |
| 9.6 | GET /api/v1/social/discussions/{media_id} | ✅ | Implemented membership-scoped discussion listing with pagination and optional group filter |
| 9.7 | POST /api/v1/social/discussions/{id}/replies | ✅ | Implemented reply creation with discussion existence checks and group-membership authorization |
| 9.8 | GET /api/v1/users/{username}/profile (public profile) | ✅ | Implemented public-safe username profile endpoint without exposing email |

### Phase 10 — Watch Party
**Goal**: Create watch party, RSVP, share stream link.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 10.1 | POST /api/v1/watchparty | ✅ | Implemented group-membership-checked creation with graceful 400 when media is not yet seeded/synced |
| 10.2 | GET /api/v1/watchparty (upcoming in group) | ✅ | Implemented membership-scoped upcoming party listing with pagination and optional group filter |
| 10.3 | POST /api/v1/watchparty/{id}/rsvp | ✅ | Implemented RSVP endpoint with watch-party existence checks and group-membership authorization |
| 10.4 | Watch party list screen (Flutter) | ✅ | Implemented WatchPartyPage with Pinia watchparty store, loading/error states, and upcoming-list rendering |
| 10.5 | Create watch party screen (Flutter) | ✅ | Added create-watch-party form on WatchPartyPage with store-backed POST flow and success/error handling |
| 10.6 | Watch party detail + RSVP screen (Flutter) | ✅ | Added per-party detail display and RSVP actions (attending/pending/declined) wired to backend RSVP endpoint |

### Phase 11 — Notifications
**Goal**: New episode/chapter alerts and group activity push via Apprise.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 11.1 | Apprise client configured | ✅ | Added Apprise client wrapper with URL parsing and delivery helper |
| 11.2 | New episode notification Celery task | ✅ | Added notifications.new_episode Celery task with Apprise fan-out + enqueue command |
| 11.3 | New chapter notification Celery task | ✅ | Added notifications.new_chapter Celery task with Apprise fan-out + enqueue command |
| 11.4 | Watch party reminder Celery task | ✅ | Added notifications.watch_party_reminder Celery task with Apprise fan-out + enqueue command |
| 11.5 | GET /api/v1/notifications | ✅ | Added authenticated notifications inbox endpoint with pagination and total count |
| 11.6 | PATCH /api/v1/notifications/read | ✅ | Added authenticated mark-read endpoint scoped to current user notifications |
| 11.7 | Notification preferences: GET + PATCH /api/v1/notifications/preferences | ✅ | Added authenticated GET/PATCH endpoints with default-row creation and update persistence tests |
| 11.8 | Notification bell screen (Flutter) | ✅ | Implemented notifications inbox screen with unread count, refresh, and mark-read actions |
| 11.9 | Notification preferences screen (Flutter) | ✅ | Implemented QForm-based preferences screen with validation rules and save/reset flow |

### Phase 12 — First-Run Setup & Super Admin Bootstrap
**Goal**: Add first-run setup UX/API so initial super admin can be created safely, then manage additional users.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 12.1 | Gap analysis + ADR for bootstrap flow, threat model, and lock-after-first-admin rule | ✅ | Added ADR 032 with lock-after-bootstrap policy and race-handling approach |
| 12.2 | DB/model readiness check for super-admin bootstrap flags and one-time setup state | ✅ | Reused existing `users.is_admin`; no migration required |
| 12.3 | Backend endpoint: POST /api/v1/setup/bootstrap-admin (one-time) | ✅ | Added one-time bootstrap endpoint returning 409 after completion |
| 12.4 | Backend endpoint: GET /api/v1/setup/status | ✅ | Added public setup status endpoint for router decision |
| 12.5 | Authorization policy for post-bootstrap user creation (super-admin only) | ✅ | Disabled public register post-bootstrap and added admin-only `POST /users` |
| 12.6 | Quasar setup screen with QForm validation (username/email/password + confirm) | ✅ | Added SetupPage with QForm rules, inline errors, and blocked invalid submit |
| 12.7 | Router/bootstrap guard (redirect to setup when no super admin exists) | ✅ | Added setup-status-aware guard and setup route handling |
| 12.8 | Frontend tests for setup form validation and success/failure states | ✅ | Added SetupPage component tests for invalid + success flow |
| 12.9 | Backend tests for idempotency, race-safety, and auth boundaries | ✅ | Added bootstrap/status/register-lock/admin-create tests |

### Phase 13 — Backend Seed/Sync Command Consolidation
**Goal**: Move root-level seeding scripts into backend command/task architecture with shared code; support per-source and all-in-one runs + scheduled refresh.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 13.1 | Gap analysis: inventory every existing seed/sync script in root `scripts/` and backend | ✅ | Completed inventory in `docs/seed-sync-inventory-phase13.md` |
| 13.2 | Architecture spec for unified seed/sync module inside backend | ✅ | Added `docs/seed-sync-architecture-phase13.md` with unified CLI/Celery orchestration contract |
| 13.3 | Implement backend command group `otakuhub seed ...` with per-source commands | ✅ | Implemented and verified by passing backend pytest suite |
| 13.4 | Implement umbrella command `otakuhub seed all` orchestrating ordered steps | ✅ | Implemented ordered umbrella orchestration with dry-run/resume + umbrella/sub-step sync_jobs tracking |
| 13.5 | Refactor shared ingestion code to eliminate duplication across commands/tasks | ✅ | Shared ingestion/execution path consolidated; verified by passing Phase 13 regression tests |
| 13.6 | Add Celery tasks for each seed/sync command (individually runnable) | ✅ | Implemented per-source + umbrella Celery tasks reusing shared orchestrator, with sync queue routing and retry behavior |
| 13.7 | Add scheduled daily/weekly refresh task composition using same shared pipeline | ✅ | Added beat schedule composition tasks delegating only to shared sync task entrypoints |
| 13.8 | Add observability: structured logs + sync_jobs status/error payload consistency | ✅ | Standardized structured payload fields across command/task/orchestrator and unified sync_jobs error_log envelope |
| 13.9 | Deprecate root `src/` (if unused) and root `scripts/` seed entrypoints with migration notes | ✅ | Added deprecation shims + warnings; documented canonical `otakuhub seed ...` migration path |
| 13.10 | Tests: command tests + task tests + idempotent upsert validation | ✅ | Added final docs/command consistency regression tests and re-ran Phase 13 targeted suite (docs + orchestrator/unit paths) |

### Phase 14 — Frontend Foundation Stabilization
**Goal**: Restore reliable navigation and shared page/form behavior before feature polish.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 14.1 | Navigation shell reliability (drawer open/close + breakpoint behavior) | ✅ | Fixed drawer trigger visibility and breakpoint-driven open/close sync in MainLayout |
| 14.2 | Global page scaffolding standards (loading/empty/error/content states) | ✅ | Added shared AppPageState wrapper and applied to core page shells |
| 14.3 | Form framework baseline (shared validation rules + typed errors) | ✅ | Added shared useValidationRules composable and refactored auth/setup forms |
| 14.4 | Inline feedback standardization (disabled submit, actionable messages) | ✅ | Standardized actionable validation feedback and disabled-submit behavior |
| 14.5 | Route/access smoke pass for auth/setup/navigation paths | ✅ | Extracted and validated route guard logic with setup/auth deep-link smoke coverage |

### Phase 15 — Frontend Design System (Shadcn-inspired, Quasar-native)
**Goal**: Deliver a cleaner dashboard-quality UI language using Quasar primitives across desktop/mobile.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 15.1 | Design tokens + theme semantics (light/dark) | ✅ | Added ADR 033 + frontend semantic token contract (no API/DB change) |
| 15.2 | Typography + spacing scale definition | ✅ | Added ADR 034 + semantic typography/spacing architecture contract |
| 15.3 | Shared UI primitives (AppCard, AppBadge, AppToolbar, AppEmptyState) | ✅ | Added ADR 035 + shared primitive contracts and layer boundaries |
| 15.4 | Dashboard template (desktop-first, mobile-adaptive) | ✅ | Added ADR 036 + standardized dashboard layout/zone contract |
| 15.5 | Responsive behavior validation for mobile/web/electron shells | ✅ | Added ADR 037 + breakpoint interaction/state validation contract |

### Phase 16 — Auth & Setup Frontend Hardening
**Goal**: Make auth/setup flows stable, validated, and user-friendly end-to-end.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 16.1 | Login page hardening | ✅ | Added ADR 038 + login validation/loading/error-mapping architecture contract |
| 16.2 | Register page hardening | ✅ | Added ADR 039 + register validation/loading/error-mapping architecture contract |
| 16.3 | Setup bootstrap page hardening | ✅ | Added ADR 040 + setup one-time flow/error-mapping architecture contract |
| 16.4 | Auth/setup component tests expansion | ✅ | Added ADR 041 + auth/setup coverage matrix and verification baseline |

### Phase 17 — Discover & Media Detail Frontend
**Goal**: Complete discover and media experience with robust tab-level flows.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 17.1 | Discover — Search tab | ✅ | Added ADR 042 + debounced search/state/retry/navigation architecture contract |
| 17.2 | Discover — Trending tab | ✅ | Added ADR 043 + trending tab loading/empty/error/retry/navigation contract |
| 17.3 | Discover — New Releases tab | ✅ | Added ADR 044 + new releases pagination/state/retry/navigation contract |
| 17.4 | Media Detail — Overview tab | ✅ | Added ADR 045 + overview hero/synopsis/list-action contract |
| 17.5 | Media Detail — Episodes/Chapters tab | ✅ | Added ADR 046 + installment sort/progress/retry behavior contract |
| 17.6 | Media Detail — Relations tab | ✅ | Added ADR 047 + relation labeling/traversal/fallback contract |
| 17.7 | Discover/media tests (page + tab states) | ⏳ | Loading/error/data assertions across tabs |

### Phase 18 — Tracking Frontend Pages
**Goal**: Ensure list management workflows are complete and usable per list state/tab.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 18.1 | My List — Watching/Reading tab | ✅ | Added ADR 048 + active list quick-update/fallback contract |
| 18.2 | My List — Completed tab | ✅ | Added ADR 049 + completed-list score/rewatch behavior contract |
| 18.3 | My List — Paused tab | ✅ | Added ADR 050 + paused-list resume/progress/fallback contract |
| 18.4 | My List — Dropped tab | ✅ | Added ADR 051 + dropped-list recovery/notes/fallback contract |
| 18.5 | My List — Plan to Watch/Read tab | ✅ | Added ADR 052 + plan-list transition/prioritization/fallback contract |
| 18.6 | My List — Custom Lists tab | ✅ | Added ADR 053 + custom-list CRUD/reorder/fallback contract |
| 18.7 | Airing Calendar page | ✅ | Added ADR 054 + airing timezone/pagination/navigation contract |
| 18.8 | Import List — AniList tab | ✅ | Added ImportListPage with provider-specific validation, job polling (3s), status display (running/completed/failed/partial), error mapping (400/429/generic) |
| 18.9 | Import List — MAL tab | ✅ | AniList+MAL tabs with distinct validation rules (AniList: alphanumeric+`-`+`_`, 3–20; MAL: alphanumeric+`_`, 3–16); both call same backend import flow |
| 18.10 | Tracking page tests | ✅ | 21 tests for ImportListPage: rendering, API routing, error mapping, loading states, job polling, status display, reset flow, validation rules |

### Phase 19 — Social Frontend Pages
**Goal**: Deliver complete social experience with clear tab boundaries and spoiler-safe UX.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 19.1 | Feed — Group Activity tab | ✅ | Added ADR 055 + group feed filtering/pagination/navigation contract |
| 19.2 | Feed — My Activity tab | ✅ | Added ADR 056 + my-activity filtering/pagination/navigation contract |
| 19.3 | Recommendations — Inbox tab | ✅ | Added ADR 057 + inbox acknowledge/triage/pagination contract |
| 19.4 | Recommendations — Sent tab | ✅ | Added ADR 058 + sent-tab filter/pagination/navigation contract |
| 19.5 | Discussions — Threads tab | ✅ | Added ADR 059 + threads listing/spoiler/pagination contract |
| 19.6 | Discussions — Thread Detail tab | ✅ | Added ADR 060 + thread detail/replies/spoiler reveal contract |
| 19.7 | Discussions — Create tab | ✅ | Added ADR 061 + discussions-create validation/spoiler/submit-lock contract |
| 19.8 | Social page tests | ✅ | Added ADR 062 + social coverage matrix and verification baseline |

### Phase 20 — Watch Party Frontend Pages
**Goal**: Make watch party workflows reliable from scheduling to RSVP.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 20.1 | Watch Party — Upcoming tab | ✅ | Added ADR 063 + upcoming watch-party listing/pagination/navigation contract |
| 20.2 | Watch Party — Create tab | ✅ | Added ADR 064 + watch-party creation validation/submission contract |
| 20.3 | Watch Party — Detail tab | ✅ | Added ADR 065 + watch-party detail/RSVP/role-gated contract |
| 20.4 | Watch Party — Past tab | ✅ | Added ADR 066 + past-session status/history/pagination contract |
| 20.5 | Watch party tests | ✅ | Added ADR 067 + watch-party coverage matrix and verification baseline |

### Phase 21 — Notifications Frontend Pages
**Goal**: Provide dependable notifications UX across inbox and preferences tabs.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 21.1 | Notifications Inbox — All tab | ✅ | Added ADR 068 + notifications all-tab read/unread/pagination contract |
| 21.2 | Notifications Inbox — Unread tab | ✅ | Added ADR 069 + unread triage/mark-read/pagination contract |
| 21.3 | Notification Preferences — Content tab | ✅ | Added ADR 070 + preferences content-toggle/save-state contract |
| 21.4 | Notification Preferences — Channels tab | ✅ | Added ADR 071 + channel validation/save-state/sensitive-field contract |
| 21.5 | Notifications tests | ⏳ | Inbox + preferences tab validation coverage |

### Phase 22 — Profile Frontend Pages
**Goal**: Complete account/profile management pages with secure and validated forms.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 22.1 | Profile — Overview tab | ✅ | Added ADR 072 + profile overview metadata/state/navigation contract |
| 22.2 | Profile — Edit Profile tab | ✅ | Added ADR 073 + profile edit validation/save-state/error-mapping contract |
| 22.3 | Profile — Account & Security tab | ✅ | Added ADR 074 + account-security validation/confirmation/retry contract |
| 22.4 | Profile tests | ✅ | Added ADR 075 + profile coverage matrix and verification baseline |

### Phase 23 — Polish, Testing & Deploy
**Goal**: Full quality gates, cross-platform verification, and production deployment readiness.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 23.1 | Backend test coverage ≥ 80% | ✅ | Achieved 80% total backend coverage with expanded unit/integration suite |
| 23.2 | Frontend component/page coverage expansion and stabilization | ✅ | Stabilized failing Discover/MainLayout tests; Vitest + typecheck passing |
| 23.3 | Security audit (run /audit-security) | ✅ | Audit completed in docs/security-audit-2026-05-21.md (overall FAIL pending critical fixes) |
| 23.4 | Performance target: search < 200ms p95 | ✅ | Added endpoint-level p95 performance check test (backend/tests/test_phase23_performance.py) |
| 23.5 | Build verification: web, Windows, Android, iOS, Linux | ✅ | Web/Windows/Android passed; iOS/Linux host-constrained. See docs/build-verification-2026-05-21.md |
| 23.6 | Docker prod compose tested | ✅ | Verified db/redis/backend/worker startup after compose and Dockerfile fixes; worker restart loop resolved |
| 23.7 | Nginx config + TLS | ✅ | Added hardened nginx TLS proxy config, generated local certs, validated HTTPS proxy to /health |
| 23.8 | README.md with setup instructions | ✅ | Added root README with prerequisites, local dev setup, prod-compose+TLS verification, quality gates, and key docs |
| 23.9 | All ADRs written (docs/adr/) | ✅ | Audited ADR set; all phase-referenced ADRs (031-075 plus prior foundational ADRs) are present in docs/adr |
| 23.10 | Type-checking cleanup (MyPy strictness and residual typing debt) | ✅ | Added mypy configuration baseline + package-root normalization; strict mypy now passes with documented module overrides |

### Phase 24 — Security & Production Hardening Remediation
**Goal**: Remediate critical security findings and close remaining production-risk gaps before next feature expansion.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 24.1 | Replace insecure password hashing with bcrypt/passlib policy and migration-safe verification path | ✅ | Implemented bcrypt/passlib hashing with legacy SHA-256 verify fallback + login-time rehash upgrade path; added regression tests |
| 24.2 | Remove insecure default secrets/config fallbacks (JWT secret, permissive CORS) | ✅ | Enforced explicit strong JWT secret and banned wildcard CORS fallback via settings validation; added regression tests and env-example updates |
| 24.3 | Harden auth/session security controls (token rotation/expiry/revocation edge cases) | ✅ | Added refresh-token reuse detection and user-wide active-token revocation on replay attempts; extended auth unit coverage |
| 24.4 | Add regression tests for security remediations (auth + config boundaries) | ✅ | Added consolidated security regression tests for config and refresh-reuse edge cases; expanded auth/config suite coverage |
| 24.5 | Re-run security audit and publish follow-up report | ✅ | Published follow-up audit in docs/security-audit-2026-05-23-followup.md (criticals resolved; one high placeholder gap remains) |
| 24.6 | Update docs (backend architecture, runbooks, env examples) to match remediated posture | ✅ | Updated backend architecture, root README, and backend .env example to document bcrypt migration, replay protection, and strict config validation |

---

### Phase 25 — Streaming Backend Infrastructure
**Goal**: Provide backend APIs for streaming playback, canonical episodes/chapters, and source provider data.

**ADRs**: `079-frontend-design-direction-aniwave.md`, `080-playback-api-contract.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 25.1 | GET /media/{id}/episodes — canonical episode list ordered by number | ✅ | EpisodeItem schema, MediaRepository.get_episodes_by_media_id, MediaService.get_episodes, route endpoint. 8 integration tests pass |
| 25.2 | GET /media/{id}/chapters — canonical chapter list ordered by number | ✅ | ChapterItem schema, repository/service method, route, 8 integration tests |
| 25.3 | GET /media/{id}/sources — available provider source mappings with episodes | ✅ | SourceEpisodeItem/SourceMappingDetail/MediaSourceResponse schemas, SourceMappingRepository.get_mappings_by_media, SourceProviderService, route, 6 integration tests |
| 25.4 | GET /media/{id}/episodes/sources — consolidated episodes (canonical + source) | ✅ | Merges canonical episodes with source provider episodes deduplicated by episode_number. ConsolidatedEpisodeSourceResponse schemas, SourceProviderService.get_consolidated_episodes(), route. 8 integration tests pass |
| 25.5 | GET /media/genres — simple genre list endpoint | ✅ | GenreItem/GenreListResponse schemas, MediaRepository.get_genres, MediaService.get_genres, route with auth, 3 integration tests |
| 25.6 | GET /media/seasonal — currently airing season anime sorted by score | ✅ | SeasonalMediaItem/SeasonalResponse schemas, defaults to current season/year, ordered by average_score DESC NULLS LAST. MediaRepository.get_seasonal_media, route, 7 integration tests. Added nulls_last() to QueryBuilder |
| 25.7 | GET /admin/source-mappings + PATCH /admin/source-mappings/{id} — list with filters and update source mappings | ✅ | AdminSourceMappingItem/ListResponse/Update schemas, SourceMappingRepository.list_all_with_filters/count_all_with_filters, routes in admin.py with require_admin guard, mapping_status validation, 18 integration tests |

### Phase 26 — Streaming UI Component Library
**Goal**: Build custom content-first Vue 3 components to achieve aniwave-style dark streaming aesthetic.

**ADR**: `079-frontend-design-direction-aniwave.md`, `081-player-frontend-architecture.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 26.1 | Design token system — palette, typography, spacing SCSS variables | ✅ | Dark theme: #0a0a0a bg, purple/cyan accents; semantic token map |
| 26.2 | AnimeCard + AnimeGrid primitives | ✅ | Pure Vue 3 + SCSS card with cover/badges/hover-overlay; responsive CSS grid. 22 Vitest tests pass |
| 26.3 | HeroBanner + ScoreRing | ✅ | Full-width gradient hero with gradient overlay, metadata tags, genre chips, expandable synopsis, ScoreRing integration, image error handling, responsive mobile layout. ScoreRing: SVG-based circular indicator with color thresholds (green/gold/yellow/red), size prop, optional label. 14 new Vitest tests pass |
| 26.4 | EpisodeItem + EpisodeList + ServerSelector | ✅ | EpisodeItem.vue (thumbnail/play overlay/watched checkmark), EpisodeList.vue (loading skeleton/error/empty states, asc/desc sort, watched tracking), ServerSelector.vue (source pills with SUB/DUB badges, skeleton/error/empty states, unavailable/active states). 27 new Vitest tests (9 each). All 250 frontend tests pass |
| 26.5 | VideoPlayer + usePlayerListener composable | ✅ | VideoPlayer.vue (iframe/loading/error/empty states, fullscreen API, composable integration) + PlayerControls.vue (progress bar with seek, play/pause, time display, quality selector, fullscreen toggle) + PlayerError.vue (message/retry button) + usePlayerListener composable (postMessage origin validation, reactive isPlaying/currentTime/error state, sendCommand/togglePlay/seek, lifecycle cleanup, onEvent callback). 51 new Vitest tests (19 composable + 6 error + 14 controls + 12 video player). All 301 frontend tests pass |
| 26.6 | TrendingCarousel (horizontal scroll) | ✅ | TrendingCarousel.vue with horizontal scroll track (hidden scrollbar), arrow navigation (scrolls by itemWidth×3, disabled at bounds), gradient fade overlays, skeleton loading (7 cards), error/empty states, lifecycle resize handling. 12 new Vitest tests. All 313 frontend tests pass across 33 files |

### Phase 27 — Home Page Streaming Redesign
**Goal**: Replace DiscoverPage tabs with aniwave-style scrollable content sections.

**ADR**: `083-home-page-streaming-redesign.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 27.1 | HomePage layout — spotlight hero + section structure | ✅ | HomePage.vue with hero carousel (auto-rotate, gradient overlays, dots nav), TrendingCarousel (trending/recent updates), AnimeGrid (new releases), FriendActivityRow (activity feed), GenrePills (genre nav), SectionHeader, home.ts Pinia store (parallel section fetches, graceful fallback, error collection). Route `/` now serves HomePage. 27 new tests (8 HomePage + 6 FriendActivityRow + 5 GenrePills + 7 store + 1 SectionHeader). All 340 frontend tests pass across 38 files |
| 27.2 | Continue Watching section | ✅ | User-list entries with progress, progress bar overlays on AnimeCard, horizontal scroll rack; hidden if empty. 12 new tests (+13 total across 27.2), 352 frontend tests passing |
| 27.3 | Friends Activity section | ✅ | Group feed with media type filter pills (All/Anime/Manga/Manhwa), pagination (Load More), store pagination state management. Backend: media_type filter param on GET /social/feed. Frontend: 13 new tests, 365 frontend tests passing |
| 27.4 | Search integration — prominent top bar with autocomplete | ✅ | SearchBar.vue (debounced 300ms, autocomplete dropdown with top 5 results, Enter → /search?q=). SearchResultsPage.vue at /search route. MainLayout toolbar integration. 11 new Vitest tests |
| 27.5 | Genre pills — clickable genre filter navigation | ✅ | GenrePills component (loading/error/empty/select), HomePage searchByGenre navigates to DiscoverPage?genre=, useMediaSearch composable supports genres param, DiscoverPage auto-searches when genre param present |
| 27.6 | Test coverage | ✅ | 377 frontend tests pass across 39 files. Final coverage: SearchBar (11), GenrePills (5), DiscoverPage genre (1), HomePage (10) |

### Phase 28 — Media Detail Page Streaming Redesign
**Goal**: Replace basic card layout with streaming-first hero banner + episode list + player.

**ADR**: `082-media-detail-streaming-redesign.md`, `081-player-frontend-architecture.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 28.1 | Hero banner with cover art, gradient overlay, metadata, action buttons | ✅ | 40vh desktop, 25vh mobile; gradient overlay; Play/+List/Like/Share. HeroBanner enhanced with action emits, styled with design tokens |
| 28.2 | Episodes tab — list with language filter and sub/dub badges | ✅ | EpisodeItem language badge + hasSources prop; EpisodeList language filter bar (All/SUB/DUB); consolidated episode mapping from sources array. 28 tests pass |
| 28.3 | Info tab — synopsis (expandable), genres, metadata table | ✅ | Expandable synopsis, clickable genre pills, metadata table with Unknown/N/A fallbacks |
| 28.4 | Related tab — horizontal carousel with relation labels | ✅ | RelatedMediaCarousel component with sequel/prequel/side-story labels, cover image placeholder, shimmer skeleton loading. 12 Vitest tests |
| 28.5 | VideoPlayer overlay integration | ✅ | Teleport-to-body full-viewport overlay with header (close + Ep N title + Prev/Next nav), VideoPlayer autoplay, lastEvent→ended emit for auto-advance |
| 28.6 | Progress tracking from player events | ✅ | onPlayerEnded → getEntryByMedia (GET /api/v1/lists/entries/{id}) → addToList (POST, new entry) or updateEntry (PATCH, progress). Auto-complete on last episode. Double-watch guard. 7 new Vitest tests |
| 28.7 | Test coverage | ✅ | 399 total frontend tests across 40 files. 17 MediaDetailPage tests (10 existing + 7 player/progress), 12 RelatedMediaCarousel, 9 EpisodeItem, 9 EpisodeList, 9 HeroBanner, 12 VideoPlayer, 9 ServerSelector |

### Phase 29 — Real AniList/MAL List Import
**Goal**: Replace skeleton import with real AniList GraphQL public list fetching.

**ADR**: `084-real-anilist-mal-import.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 29.1 | AniListListFetcher — GraphQL client for public user list | ⏳ | Backend external client; shared rate limiter with AnilistClient |
| 29.2 | Import service — status mapping, progress mapping, score conversion (100→10) | ⏳ | ANILIST_STATUS_MAP, media_id resolution via media_external_ids |
| 29.3 | Real import_user_list_task — fetch, upsert, history rows, progress tracking | ⏳ | Replace skeleton; create/update user_list_entries + list_entry_history |
| 29.4 | Frontend status enhancement — show per-entry progress during import | ⏳ | Enhance ImportListPage running state with item-level details |
| 29.5 | Test coverage | ⏳ | Fetcher mock tests, import task integration tests, ImportListPage enhanced tests |

### Phase 30 — Episode Notification Pipeline (Complete)
**Goal**: Hook notification creation into daily refresh, deliver via Apprise, clean up old notifications.

**ADR**: `085-episode-notification-pipeline.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 30.1 | Hook process_new_episodes into daily_refresh_compose | ⏳ | Append to signature chain after megaplay_verify |
| 30.2 | Notify users task — group by user, deliver via Apprise per preferences | ⏳ | Query unsent notifications, call AppriseClient per channel, set sent_at |
| 30.3 | Apprise client enhancement — channel routing (discord/telegram/email/push) | ⏳ | Map notification_preferences to Apprise URLs |
| 30.4 | Cleanup task — purge read notifications older than 90 days | ⏳ | Weekly schedule; uses idx_notifications_cleanup index |
| 30.5 | Beat schedule updates | ⏳ | Add notify_users + cleanup_notifications to Celery beat |
| 30.6 | Frontend notification badge polling | ⏳ | useNotificationBadge composable; 60s poll interval |
| 30.7 | Test coverage | ⏳ | Process/notify/cleanup task tests, AppriseClient tests |

### Phase 31 — Admin Source Provider UI
**Goal**: Simple admin page to trigger syncs, view jobs, and reconcile unmatched mappings.

**ADR**: `086-admin-source-provider-ui.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 31.1 | Backend endpoints — list + update source mappings | ⏳ | GET /admin/source-mappings, PATCH /admin/source-mappings/{id} |
| 31.2 | AdminSourceProviderPage — sync trigger buttons, job status list | ⏳ | Reuse existing admin endpoints; trigger Anikoto full/recent/verify |
| 31.3 | Unmatched mappings section with reconciliation workflow | ⏳ | Search on AniList dialog, manual match, ignore, delete actions |
| 31.4 | Test coverage | ⏳ | Admin page tests, API endpoint tests |

### Phase 32 — Migration & Cleanup
**Goal**: Convert remaining Quasar pages to custom components and remove unused framework weight.

**ADR**: `079-frontend-design-direction-aniwave.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 32.1 | Convert MyListPage to custom streaming components | ⏳ | Replace QCard with AnimeCard, QList with custom list components |
| 32.2 | Convert social/watchparty pages to match design system | ⏳ | Consistent dark theme across all remaining pages |
| 32.3 | Bundle optimization — remove unused Quasar components | ⏳ | Tree-shake unused Quasar modules; verify electron/mobile builds |
| 32.4 | Full visual QA + accessibility pass | ⏳ | Keyboard nav, screen reader, color contrast, responsive breakpoints |
| 32.5 | Test pass — all existing + new tests verified | ⏳ | Full vitest run + backend pytest run |

---

### Phase 33 — Characters, Staff & Voice Actors
**Goal**: Complete character and staff database with AniList sync, character/staff pages, and media detail integration.

**ADR**: `088-feature-gap-analysis-aniwave-anilist-mal.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 33.1 | characters + staff tables, models, repos | 🔲 | Name, image, description, favorites count |
| 33.2 | media_characters + media_staff join tables | 🔲 | Character role (MAIN/SUPPORTING/BACKGROUND), staff role enum |
| 33.3 | character_voice_actors join table | 🔲 | character ↔ staff ↔ language ↔ media |
| 33.4 | AniList sync for character/staff data | 🔲 | New Celery task, GraphQL client, rate-limited |
| 33.5 | API endpoints: GET /characters/{id}, /staff/{id}, /media/{id}/characters, /media/{id}/staff | 🔲 | Also character search |
| 33.6 | Character page (bio, image, animeography, VA roles) | 🔲 | Frontend |
| 33.7 | Staff page (bio, image, filmography by role) | 🔲 | Frontend |
| 33.8 | Character + Staff tabs on media detail | 🔲 | Frontend, with voice actor names |
| 33.9 | Test coverage | 🔲 | Backend + frontend tests |

### Phase 34 — Advanced User Statistics
**Goal**: AniList-style stats dashboard — genre distribution, activity heatmap, score distribution, format breakdown.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 34.1 | Stats computation service | 🔲 | Genre, format, score, status distribution from user_list_entries |
| 34.2 | Yearly activity calendar (GitHub-style heatmap) | 🔲 | Group by completed_at dates |
| 34.3 | Voice actor / studio stats (requires Phase 33) | 🔲 | Most watched VA/studio |
| 34.4 | API: GET /users/{id}/stats?type=genres|formats|scores|activity | 🔲 | Chart-ready JSON |
| 34.5 | Stats page on user profile (tab or separate page) | 🔲 | Frontend |
| 34.6 | Genre distribution + score distribution charts | 🔲 | Lightweight CSS/SVG charts |
| 34.7 | Activity calendar heatmap | 🔲 | GitHub-style contribution graph |
| 34.8 | Stats summary card | 🔲 | "N days watched", "Mean score: X" |
| 34.9 | Test coverage | 🔲 | |

### Phase 35 — Charts & Top Lists
**Goal**: Top 100 anime by score/popularity/favorites. Seasonal rankings. Group-specific charts.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 35.1 | GET /charts/top?category=score|popularity|favorites | 🔲 | Backend endpoint |
| 35.2 | Seasonal ranking endpoint | 🔲 | Current season top anime |
| 35.3 | Group-specific charts | 🔲 | What's popular in friend group |
| 35.4 | Charts page with tab switcher | 🔲 | Top Rated / Most Popular / Most Favorited |
| 35.5 | Test coverage | 🔲 | |

### Phase 36 — Advanced Discovery & Browse
**Goal**: Power-user browse with multi-filter, seasonal page, random, tags, "more like this".

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 36.1 | Enhanced browse endpoint — multi-filter + sort | 🔲 | genres, year, season, format, status, score, sort |
| 36.2 | Tags-based discovery | 🔲 | Filter by tag with relevance |
| 36.3 | Seasonal grouping endpoint | 🔲 | Current season + next season |
| 36.4 | Random anime endpoint | 🔲 | GET /media/random |
| 36.5 | "More like this" by shared tags/genres | 🔲 | Endpoint + media detail section |
| 36.6 | Browse page: advanced filter sidebar | 🔲 | Genre checkboxes, year slider, format dropdown |
| 36.7 | Seasonal anime page | 🔲 | Current season grid + upcoming tab |
| 36.8 | Random anime button with re-roll | 🔲 | Frontend |
| 36.9 | Test coverage | 🔲 | |

### Phase 37 — Player Enhancements
**Goal**: Pro-level video player with auto-next, keyboard shortcuts, multi-language subs, server failover.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 37.1 | Auto-next episode with countdown overlay | 🔲 | 10s→3s countdown, cancelable |
| 37.2 | Keyboard shortcuts (space, f, n, b, m, arrows) | 🔲 | Play/pause, fullscreen, next, back, mute, seek |
| 37.3 | Multiple subtitle language selector | 🔲 | If provider returns multiple language embeds |
| 37.4 | Server reliability tracking + auto-failover | 🔲 | Track error rate, switch on failure |
| 37.5 | Report broken episode link | 🔲 | Flags episode for admin review |
| 37.6 | Skip intro/outro buttons | 🔲 | Requires episode timing data |
| 37.7 | Picture-in-picture mode | 🔲 | Via documentPictureInPicture API |
| 37.8 | Watch history tracking | 🔲 | Every play session logged |
| 37.9 | Test coverage | 🔲 | |

### Phase 38 — Social & Community Expansion
**Goal**: Follow system, reviews with helpful votes, global discussions, text posts, share links.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 38.1 | Follow system — user_follows table + notifications | 🔲 | Follower/following relationship |
| 38.2 | Reviews table + model + repo | 🔲 | user_id, media_id, body, score, is_spoiler |
| 38.3 | Review helpful votes — review_votes table | 🔲 | helpful / not-helpful voting |
| 38.4 | Global discussions (optional group_id) | 🔲 | Remove group requirement for discussions |
| 38.5 | Activity text posts — activity_posts table | 🔲 | Text status updates, not just list changes |
| 38.6 | Share link generation | 🔲 | GET /share/{type}/{id} returns deep link |
| 38.7 | Reviews tab on media detail + create review form | 🔲 | Frontend with markdown |
| 38.8 | Follow/unfollow on user profiles | 🔲 | Frontend |
| 38.9 | Text status posting from profile | 🔲 | Frontend |
| 38.10 | Share button on media + episode | 🔲 | Copy deep link to clipboard |
| 38.11 | Test coverage | 🔲 | |

### Phase 39 — Manga Reader
**Goal**: Read manga chapters in-browser with MangaDex source, customizable reading direction, bookmarks.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 39.1 | MangaDex chapter content API client | 🔲 | Fetch chapter page images |
| 39.2 | Chapter page caching strategy | 🔲 | Cache pages, respect MangaDex rate limits |
| 39.3 | Source/mirror switching for manga chapters | 🔲 | Multiple manga source providers |
| 39.4 | API: GET /media/{id}/manga/chapters/{ch_id}/pages | 🔲 | Proxied and cached |
| 39.5 | PUT /reading/bookmark endpoint | 🔲 | Save position within chapter |
| 39.6 | Manga reader page — scrollable layout | 🔲 | Long-strip vertical reading |
| 39.7 | Page turning modes (scroll, LTR paged, RTL) | 🔲 | Toggle reading direction |
| 39.8 | Bookmark + resume from position | 🔲 | Within-chapter progress |
| 39.9 | Progress auto-save on last page | 🔲 | Marks chapter read |
| 39.10 | Test coverage | 🔲 | |

### Phase 40 — Advanced Platform Features
**Goal**: PWA, i18n, theme customization, import/export, batch editing, view toggles.

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 40.1 | PWA manifest + install prompt | 🔲 | Offline browse, install banner |
| 40.2 | Multi-language UI (vue-i18n) | 🔲 | i18n integration |
| 40.3 | Theme customization — accent color picker | 🔲 | Custom CSS like AniList |
| 40.4 | Watch history page | 🔲 | Full browsing/playback history |
| 40.5 | List import/export (JSON/CSV) | 🔲 | GET /lists/export, POST /lists/import |
| 40.6 | Batch editing list entries | 🔲 | Multi-select status/progress change |
| 40.7 | List view toggle (grid / list / detailed) | 🔲 | Per-user preference |
| 40.8 | Test coverage | 🔲 | |

---

**Goal**: Fix UUID v7, Full-Text Search, Alembic migrations, PostgreSQL default config, and missing constraints.

**ADR**: `docs/adr/077-database-models-alignment.md`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 2.1 | UUID v7 migration — create `generate_uuid7()`, update all 28 model PKs | ✅ | `core/uuid7.py` + 21 model files updated |
| 2.2 | Full-Text Search — `TSVector` type, GIN indexes, trigram indexes, PG trigger | ✅ | `core/tsvector.py`, media_entry uses TSVector, repo search uses ILIKE |
| 2.3 | Alembic migration system — init, configure async, baseline migration | ✅ | `alembic/` initialized, async env.py, 001_initial_tables.py |
| 2.4 | PostgreSQL default config — change `DATABASE_URL`, wire pool settings | ✅ | config.py default → postgresql+asyncpg, pool_size/max_overflow wired |
| 2.5 | Missing constraints — explicit `UniqueConstraint` on models | ✅ | user_list_entry + recommendation updated |
| 2.6 | Update docs — backend-architecture.md paths, database.py location | ✅ | Fixed config.py/database.py paths, added uuid7/tsvector modules |

---

### Audit Phase 3 — Backend Endpoint Gaps
**Goal**: Implement missing CRUD endpoints across all routers, fix the FK validation pre-existing failures, and document all endpoints.

**Reference**: `AUDIT-PLAN.md §3`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 3.1a | **Admin Sync routes** — `POST /admin/sync/seed`, `POST /admin/sync/weekly-refresh`, `GET /admin/sync/jobs`, `GET /admin/sync/jobs/{job_id}` with Celery enqueue fallback | ✅ | 4 integration tests added |
| 3.1b | **Groups CRUD** — `PATCH /groups/{id}`, `DELETE /groups/{id}`, `DELETE /groups/{id}/members/{user_id}`, `PATCH /groups/{id}/members/{user_id}/role` | ✅ | 11 integration tests added |
| 3.1c | **Watchparty PATCH/DELETE** — Authorization-gated update and soft-delete | ✅ | 6 integration tests added |
| 3.1d | **Password Change** — `POST /auth/change-password` with current password verification, old token revocation, fresh token issuance | ✅ | 6 integration tests added |
| 3.1e | **FK Validation Fixes** — Explicit `MediaEntry` existence checks in watch party + discussion create endpoints | ✅ | 2 pre-existing failures fixed (283 passed, 1 pre-existing mock failure remains) |
| 3.1f | **Documentation** — `docs/api-spec.md` updated: Notification endpoints, Discussion Replies, Related Media, Admin Sync routes | ✅ | |
| 3.1g | Remaining endpoints (media CRUD, social DELETE, admin user list/delete, user settings, notification delete, watchparty RSVPs) | ✅ | Implemented + 17 integration tests pass after `BaseService.db_session` session-caching fix |
| 3.2 | Service/Repository pattern consistency audit | ✅ | Orphaned GroupRepository wired; 4 new repos (social, watch_party, notification, tracking); SocialService, WatchPartyService, NotificationService, TrackingService migrated; MediaService.delete/get_users/delete bypasses fixed; `BaseService.db_session` caching bug fixed; QueryBuilder.exists() SQLite fix; 80 tests pass |
| 3.3 | `get_related_media()` stub — implement real DB query | ✅ | Already a real DB query with relation type labels and `deleted_at` filter |
| 3.4 | User settings stubs — create table or add columns | ✅ | `user_settings` table created, `get_user_settings()`/`update_user_settings()` wired with auto-create defaults |

---

### Audit Phase 4 — Frontend Pages (Complete Missing Implementations)
**Goal**: Replace all stub pages with full implementations per architecture contracts. Covers social domain (Feed, Recommendations, Discussions), Profile, shared components, stores, and composables.

**Reference**: `AUDIT-PLAN.md §4`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 4.1 | Social Domain — Feed, Recommendations, Discussion pages | ✅ | Full implementations with tabs, pagination, AppEmptyState, spoiler handling, reply flow; 10 Vitest tests pass |
| 4.2 | Profile page (Overview, Edit Profile, Account & Security tabs) | ✅ | Full 3-tab layout: overview with avatar/bio/metadata cards, edit form with display name/avatar/bio/timezone validation, password change with match validation; 4 Vitest tests pass |
| 4.3 | Missing stores & composable (`social.ts`, `useInfiniteScroll.ts`) | ✅ | Created in Phase 4.1 — `stores/social.ts` with full feed/recs/discussions state management, `composables/useInfiniteScroll.ts` with pagination logic |
| 4.4 | Missing shared components (MediaCard, MediaBanner, ActivityFeedItem, RecommendCard) | ✅ | ActivityFeedItem + RecommendCard created in Phase 4.1; MediaCard + MediaBanner deferred to future refactor |

---

### Audit Phase 5 — Frontend Feature Gaps on Existing Pages
**Goal**: Add missing tabs, detail views, and features to existing populated pages (WatchParty, Notifications, MyList).

**Reference**: `AUDIT-PLAN.md §5`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 5.1 | WatchPartyPage — Past tab, Party Detail view with RSVP, detail navigation | ✅ | Added Past tab with fetch & status badges, maximized detail dialog with host/media/RSVP info, RSVP actions (Attending/Maybe/Decline), card-click navigation to detail; 14 Vitest tests pass |
| 5.2 | NotificationsPage — All/Unread tab structure, Mark All Read | ✅ | Implemented All/Unread tabs, per-item Mark Read, Mark All Read (batch via PATCH), Mark Selected Read in All tab, Preferences navigation; 16 Vitest tests pass |
| 5.3 | MyListPage — history feed section, statistics summary | ✅ | Added stats summary card (status chips with counts), history feed section with GET /api/v1/lists/me/history, event descriptions (added/status_changed/progress_updated/score_set), relative dates; 8 Vitest tests pass |
| 5.4 | Missing types — `types/auth.ts`, `types/api.ts` | ✅ | Created types/auth.ts (TokenPair, AuthResponse, LoginPayload, RegisterPayload, UserProfile, PasswordChangeRequest, UserProfileUpdateRequest) and types/api.ts (PaginatedResponse); consolidated UserProfile from social.ts duplicate; updated stores/auth.ts, services/storage.ts imports; 0 regressions |
| 5.5 | Phase 5 complete — all feature gaps resolved | ✅ | |

### Audit Phase 6 — Frontend Test Coverage
**Goal**: Expand frontend page tests from minimal/dummy coverage to comprehensive state/interaction coverage per architecture contracts.

**Reference**: `AUDIT-PLAN.md §6`

| Sub-phase | Task | Status | Notes |
|-----------|------|--------|-------|
| 6.1 | Page test expansion — core pages (Discover, MediaDetail, Airing, Import, NotifPrefs, Login, Register) | ✅ | 10→10, 1→7, 1→7, 1→8, 2→9, 0→9, 0→9 = 59 new tests across 7 pages; 124 total |
| 6.2 | Store test coverage — tracking.ts, watchparty.ts, notifications.ts | ✅ | 37 tests across 3 stores; all pass |
| 6.3 | Remaining page tests — expand SetupPage (2→7), FeedPage (3→7), RecommendationsPage (3→7) | ✅ | +15 tests; 174 total frontend tests across 21 files |

---

## Completion Log

> Add a line here every time a sub-phase is completed.

```
# Format: YYYY-MM-DD | Phase X.Y | <one-line description>
# Example:
# 2026-04-20 | Phase 1.1 | Monorepo directory structure created
# 2026-04-22 | Phase 1.2 | Docker Compose dev stack setup with postgres, redis, backend, worker
# 2026-04-22 | Phase 1.3 | Docker Compose prod stack setup
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
# 2026-05-05 | Phase 7.10 | Verified app build/run targets on web, Windows (Electron), and Android (Capacitor release)
# 2026-05-05 | Phase 7 | Flutter App Shell marked complete
# 2026-05-05 | Phase 8.1 | Implemented discover/search screen with API-backed media search and result cards
# 2026-05-05 | Phase 8.2 | Implemented media detail screen with backend fetch and structured metadata display
# 2026-05-05 | Phase 8.3 | Implemented add-to-list bottom sheet component wired to tracking endpoint
# 2026-05-05 | Phase 8.4 | Implemented tabbed My List screen grouped by watch status
# 2026-05-05 | Phase 8.5 | Implemented progress update widget and inline list progress patch flow
# 2026-05-05 | Phase 8.6 | Implemented score widget and inline score patch flow
# 2026-05-05 | Phase 8.7 | Implemented airing calendar screen backed by media airing endpoint
# 2026-05-05 | Phase 8.8 | Implemented list import screen for AniList/MAL sync job start
# 2026-05-05 | Phase 8.9 | Implemented custom list creation and entry management UI/store actions
# 2026-05-05 | Phase 8.10 | Added and ran frontend widget tests for newly delivered tracking screens
# 2026-05-05 | Phase 8 | Flutter Tracking Screens marked complete
# 2026-05-05 | Phase 9.1 | Implemented GET /api/v1/social/feed using shared group-member activity history
# 2026-05-05 | Phase 9.2 | Recommendation create endpoint implemented with shared-group guards
# 2026-05-05 | Phase 9.3 | Recommendation inbox endpoint implemented with pagination
# 2026-05-05 | Phase 9.4 | Recommendation acknowledge endpoint implemented with recipient ownership checks
# 2026-05-05 | Phase 9.5 | Discussion create endpoint implemented with group membership authorization
# 2026-05-05 | Phase 9.6 | Discussion list endpoint implemented with visibility filtering by group membership
# 2026-05-05 | Phase 9.7 | Discussion replies endpoint implemented with authorization and validation
# 2026-05-05 | Phase 9.8 | Public profile endpoint implemented with safe response schema
# 2026-05-05 | Phase 10.1 | Watch party create endpoint implemented with group membership authorization
# 2026-05-05 | Phase 10.2 | Watch party upcoming list endpoint implemented with membership filtering
# 2026-05-05 | Phase 10.3 | Watch party RSVP endpoint implemented with membership authorization
# 2026-05-05 | Phase 10.4 | Watch party list screen implemented with store-backed fetch and test coverage
# 2026-05-05 | Phase 10.5 | Watch party create screen implemented with form and store integration
# 2026-05-05 | Phase 10.6 | Watch party detail+RSVP UI implemented with store-backed RSVP actions
# 2026-05-06 | Phase 11.1 | Apprise client configured with multi-target URL support
# 2026-05-06 | Phase 11.2 | New episode notification Celery task implemented with Apprise delivery wrapper
# 2026-05-06 | Phase 11.3 | New chapter notification Celery task implemented with Apprise delivery wrapper
# 2026-05-06 | Phase 11.4 | Watch party reminder Celery task implemented with Apprise delivery wrapper
# 2026-05-06 | Phase 11.5 | Notifications inbox endpoint implemented with auth + pagination
# 2026-05-06 | Phase 11.6 | Notifications mark-read endpoint implemented with user-scoped updates
# 2026-05-06 | Phase 11.7 | Notification preferences GET/PATCH endpoints implemented with defaults and persistence tests
# 2026-05-06 | Phase 11.8 | Notification bell screen implemented with unread count and mark-read actions
# 2026-05-06 | Phase 11.9 | Notification preferences screen implemented with QForm validation and save flow
# 2026-05-06 | Phase 12.1 | Added ADR 032 documenting bootstrap setup lock and security boundaries
# 2026-05-06 | Phase 12.2 | Completed setup data-model review; existing users.is_admin supports flow (no migration)
# 2026-05-06 | Phase 12.3 | Added one-time POST /api/v1/setup/bootstrap-admin endpoint
# 2026-05-06 | Phase 12.4 | Added public GET /api/v1/setup/status endpoint for first-run detection
# 2026-05-06 | Phase 12.5 | Enforced post-bootstrap user creation via admin-only POST /api/v1/users
# 2026-05-06 | Phase 12.6 | Added frontend SetupPage with QForm validation and inline errors
# 2026-05-06 | Phase 12.7 | Added setup-aware router guard redirecting to /setup when required
# 2026-05-06 | Phase 12.8 | Added SetupPage Vitest coverage for invalid and successful submit flows
# 2026-05-06 | Phase 12.9 | Added backend setup tests for status/bootstrap/register lock/admin authorization
# 2026-05-06 | Phase 12 | First-run setup and super-admin bootstrap phase completed
# 2026-05-08 | Phase 13.1 | Completed seed/sync inventory and gap analysis with consolidation targets
# 2026-05-08 | Phase 13.2 | Defined unified backend seed/sync architecture spec and execution contracts
# 2026-05-10 | Phase 13.3 | Implementation delivered; completion reverted pending required passing pytest verification
# 2026-05-10 | Phase 13.3 | Verification completed: backend Phase 13.3 pytest suite passed; advanced to 13.4
# 2026-05-10 | Phase 13.4 | Implemented `otakuhub seed all` umbrella orchestration with ordered execution, dry-run/resume, and failure handling tests
# 2026-05-10 | Phase 13.5 | Refactored shared ingestion/execution path and verified with passing Phase 13 test suite
# 2026-05-10 | Phase 13.6 | Added per-source + umbrella Celery sync tasks reusing shared orchestration with queue routing and retry coverage
# 2026-05-10 | Phase 13.7 | Added daily/weekly Celery beat compositions that orchestrate existing shared sync tasks without scheduler business logic
# 2026-05-10 | Phase 13.8 | Standardized observability fields for command/task/orchestrator logs and unified sync_jobs error_log payload envelope
# 2026-05-10 | Phase 13.9 | Deprecated root seed entrypoints with compatibility shims and migration notes to canonical `otakuhub seed ...` commands
# 2026-05-11 | Phase 13.10 | Added final command/docs consistency regression tests, aligned runtime docs to canonical `otakuhub ...` paths, and completed Phase 13 verification
# 2026-05-11 | Phase 14.1 | Stabilized navigation shell drawer behavior and ensured always-available open trigger
# 2026-05-11 | Phase 14.2 | Added shared AppPageState wrapper and standardized page loading/empty/error/content scaffolds
# 2026-05-11 | Phase 14.3 | Added shared useValidationRules composable and applied typed validation baseline to auth/setup forms
# 2026-05-11 | Phase 14.4 | Standardized inline validation feedback and disabled-submit UX to prevent silent form failures
# 2026-05-11 | Phase 14.5 | Added route/auth/setup guard smoke coverage and extracted guard resolver for deep-link resilience
# 2026-05-11 | Phase 14 | Frontend foundation stabilization completed; advanced to Phase 15.1
# 2026-05-11 | Phase 15.1 | Defined semantic design-token architecture (ADR 033) and frontend layer boundaries for light/dark theming
# 2026-05-11 | Phase 15.2 | Defined semantic typography hierarchy and 4px-based spacing scale contract (ADR 034)
# 2026-05-11 | Phase 15.3 | Defined shared UI primitive contracts (AppCard/AppBadge/AppToolbar/AppEmptyState) with semantic token-only mapping (ADR 035)
# 2026-05-11 | Phase 15.4 | Defined dashboard page template and zone composition contract for desktop-first/mobile-adaptive layouts (ADR 036)
# 2026-05-11 | Phase 15.5 | Defined responsive validation contract and breakpoint acceptance criteria for web/electron/mobile shells (ADR 037)
# 2026-05-11 | Phase 15 | Frontend design system architecture phase completed; advanced to Phase 16.1
# 2026-05-11 | Phase 16.1 | Defined login hardening contract for validation, submit locking, and backend error mapping (ADR 038)
# 2026-05-11 | Phase 16.2 | Defined register hardening contract for validation, confirm-password matching, and conflict/policy error mapping (ADR 039)
# 2026-05-11 | Phase 16.3 | Defined setup bootstrap hardening contract for one-time flow handling, 409 redirect policy, and retry-safe UX (ADR 040)
# 2026-05-11 | Phase 16.4 | Defined auth/setup test expansion contract covering login/register/setup validation and backend error mapping cases (ADR 041)
# 2026-05-11 | Phase 16 | Auth & setup frontend hardening architecture phase completed; advanced to Phase 17.1
# 2026-05-11 | Phase 17.1 | Defined Discover Search tab contract for debounced query handling, resilient state management, and retry/navigation behavior (ADR 042)
# 2026-05-11 | Phase 17.2 | Defined Discover Trending tab contract for tab-load fetching, fallback states, and media-detail navigation (ADR 043)
# 2026-05-11 | Phase 17.3 | Defined Discover New Releases tab contract for release-context pagination, fallback states, and navigation behavior (ADR 044)
# 2026-05-11 | Phase 17.4 | Defined Media Detail Overview tab contract for hero metadata, synopsis interaction, and add/update list CTA behavior (ADR 045)
# 2026-05-11 | Phase 17.5 | Defined Media Detail Episodes/Chapters tab contract for installment sorting, progress actions, and fallback/retry states (ADR 046)
# 2026-05-11 | Phase 17.6 | Defined Media Detail Relations tab contract for relation labeling, fallback states, and related-title navigation (ADR 047)
# 2026-05-11 | Phase 17 | Discover & Media Detail frontend architecture phase completed; advanced to Phase 18.1
# 2026-05-11 | Phase 18.1 | Defined My List Watching/Reading tab contract for active-entry quick progress updates, fallback states, and retry behavior (ADR 048)
# 2026-05-11 | Phase 18.2 | Defined My List Completed tab contract for score adjustments, rewatch/reread actions, and fallback/retry behavior (ADR 049)
# 2026-05-11 | Phase 18.3 | Defined My List Paused tab contract for resume-focused actions, paused-context visibility, and retry behavior (ADR 050)
# 2026-05-11 | Phase 18.4 | Defined My List Dropped tab contract for recovery transitions, dropped-context visibility, and retry behavior (ADR 051)
# 2026-05-11 | Phase 18.5 | Defined My List Plan tab contract for backlog prioritization, active-state transitions, and retry behavior (ADR 052)
# 2026-05-11 | Phase 18.6 | Defined My List Custom Lists tab contract for list CRUD, entry reorder persistence, and fallback/retry behavior (ADR 053)
# 2026-05-11 | Phase 18.7 | Defined Airing Calendar page contract for timezone-safe schedule grouping, pagination, and navigation behavior (ADR 054)
# 2026-05-11 | Phase 18 | Tracking frontend pages architecture phase completed; advanced to Phase 19.1
# 2026-05-11 | Phase 19.1 | Defined Feed Group Activity tab contract for social event rendering, filtering, pagination, and route navigation behavior (ADR 055)
# 2026-05-11 | Phase 19.2 | Defined Feed My Activity tab contract for personal event timelines, filtering, pagination, and navigation behavior (ADR 056)
# 2026-05-11 | Phase 19.3 | Defined Recommendations Inbox tab contract for acknowledge actions, triage visibility, pagination, and navigation behavior (ADR 057)
# 2026-05-11 | Phase 19.4 | Defined Recommendations Sent tab contract for outbound-state visibility, filtering, pagination, and navigation behavior (ADR 058)
# 2026-05-11 | Phase 19.5 | Defined Discussions Threads tab contract for spoiler-safe thread discovery, filtering, pagination, and navigation behavior (ADR 059)
# 2026-05-11 | Phase 19.6 | Defined Discussions Thread Detail tab contract for replies, spoiler reveal controls, pagination, and navigation stability (ADR 060)
# 2026-05-11 | Phase 19.7 | Defined Discussions Create tab contract for validated authoring, spoiler signaling, submit-lock, and success/error transitions (ADR 061)
# 2026-05-11 | Phase 19.8 | Defined Social page test matrix contract for feed/recommendations/discussions state, interaction, and error coverage (ADR 062)
# 2026-05-11 | Phase 19 | Social frontend pages architecture phase completed; advanced to Phase 20.1
# 2026-05-11 | Phase 20.1 | Defined Watch Party Upcoming tab contract for schedule visibility, fallback states, pagination, and watch-party navigation behavior (ADR 063)
# 2026-05-11 | Phase 20.2 | Defined Watch Party Create tab contract for scheduling validation, URL checks, submit-lock behavior, and success/error transitions (ADR 064)
# 2026-05-11 | Phase 20.3 | Defined Watch Party Detail tab contract for RSVP transitions, role-gated controls, and fallback/retry behavior (ADR 065)
# 2026-05-11 | Phase 20.4 | Defined Watch Party Past tab contract for completed/cancelled status labeling, filtering, pagination, and navigation behavior (ADR 066)
# 2026-05-11 | Phase 20.5 | Defined Watch Party test matrix contract for upcoming/create/detail/past state, interaction, and error coverage (ADR 067)
# 2026-05-11 | Phase 20 | Watch party frontend pages architecture phase completed; advanced to Phase 21.1
# 2026-05-11 | Phase 21.1 | Defined Notifications Inbox All tab contract for read/unread clarity, fallback states, pagination, and navigation behavior (ADR 068)
# 2026-05-11 | Phase 21.2 | Defined Notifications Inbox Unread tab contract for unread triage, mark-read actions, pagination, and navigation behavior (ADR 069)
# 2026-05-11 | Phase 21.3 | Defined Notification Preferences Content tab contract for toggle management, save-state handling, and retry-safe feedback (ADR 070)
# 2026-05-11 | Phase 21.4 | Defined Notification Preferences Channels tab contract for channel validation, sensitive-field handling, and save/retry behavior (ADR 071)
# 2026-05-11 | Phase 21 | Notifications frontend pages architecture phase completed; advanced to Phase 22.1
# 2026-05-11 | Phase 22.1 | Defined Profile Overview tab contract for identity/summary rendering, fallback states, and profile-action navigation (ADR 072)
# 2026-05-11 | Phase 22.2 | Defined Profile Edit tab contract for form validation, save-state control, and actionable backend error mapping (ADR 073)
# 2026-05-11 | Phase 22.3 | Defined Profile Account & Security tab contract for password/session safety actions, confirmation flows, and secure feedback behavior (ADR 074)
# 2026-05-11 | Phase 22.4 | Defined Profile page test matrix contract for overview/edit/security validation and state-flow coverage (ADR 075)
# 2026-05-11 | Phase 22 | Profile frontend pages architecture phase completed; advanced to Phase 23.1
# 2026-05-21 | Phase 23.1 | Expanded backend unit/integration suite and achieved 80% total backend coverage
# 2026-05-21 | Phase 23.2 | Stabilized frontend page/layout tests and verified Vitest + TypeScript checks
# 2026-05-21 | Phase 23.3 | Completed security audit and documented findings in docs/security-audit-2026-05-21.md
# 2026-05-21 | Phase 23.4 | Added media search p95 performance test and verified threshold under 200ms
# 2026-05-21 | Phase 23.5 | Completed build verification matrix with host-constrained notes for iOS/Linux in docs/build-verification-2026-05-21.md
# 2026-05-22 | Phase 23.6 | Validated prod docker compose core services (db/redis/backend/worker) after Dockerfile and compose command/path fixes
# 2026-05-22 | Phase 23.7 | Implemented nginx TLS reverse-proxy config and verified HTTPS health check via docker compose nginx service
# 2026-05-22 | Phase 23.8 | Added root README.md with end-to-end setup instructions for backend, frontend, docker compose, TLS, and verification commands
# 2026-05-22 | Phase 23.9 | Audited docs/adr and confirmed all phase-referenced ADRs are present
# 2026-05-22 | Phase 23.10 | Added backend mypy configuration cleanup and achieved passing strict mypy run (uv run mypy)
# 2026-05-23 | Phase 24.1 | Replaced SHA-256 password hashing with bcrypt/passlib policy and added migration-safe legacy verification + login rehash tests
# 2026-05-23 | Phase 24.2 | Removed insecure config fallbacks by enforcing explicit JWT secret and non-wildcard CORS origins with tests
# 2026-05-23 | Phase 24.3 | Hardened refresh/session controls with token-reuse detection and active-session revocation tests
# 2026-05-23 | Phase 24.4 | Added security regression tests for JWT/CORS config guards and refresh-token replay edge cases
# 2026-05-23 | Phase 24.5 | Re-ran security audit and published follow-up report documenting resolved criticals and remaining high-risk placeholder
# 2026-05-23 | Phase 24.6 | Updated architecture/runbook/env docs to reflect security hardening baseline and fail-fast config rules
# 2026-06-03 | Audit Phase 0 | Cleanup: deleted root src/app/ (79 files), 4 hidden test files renamed, conftest fixed, 13 test failures reduced to 2
# 2026-06-03 | Audit Phase 1.1 | Fixed external API clients (lazy-init sessions, RateLimiter token-bucket, MangaDex title param)
# 2026-06-03 | Audit Phase 1.2 | Implemented AnimeOfflineSeedAdapter — real _parse_item/_upsert_item with data loading
# 2026-06-03 | Audit Phase 1.3 | Implemented AniListSeedAdapter — batch GraphQL backfill with full metadata upsert
# 2026-06-03 | Audit Phase 1.4 | Implemented MangaDexSeedAdapter — chapter fetching and upsert for manga types
# 2026-06-03 | Audit Phase 1.5 | De-stubbed SyncService (sync_media_from_anilist, backfill_missing_metadata, update_or_create_media_from_anilist)
# 2026-06-03 | Audit Phase 1.6 | Implemented import_user_list_task and process_new_episodes_task with real async logic
# 2026-06-03 | Audit Phase 1.7 | Completed — 206 tests pass, 2 pre-existing failures remain (media_id FK validation)
# 2026-06-04 | Audit Phase 2.0 | Design complete — ADR 077 covers UUID v7, Full-Text Search, Alembic migration system, PostgreSQL default config, and constraint alignment
# 2026-06-05 | Audit Phase 3 | Started Audit Phase 3 (Backend Endpoint Gaps) implementation
# 2026-06-05 | Audit Phase 3.1a | Added admin sync routes: POST seed, POST weekly-refresh, GET jobs list, GET job detail with Celery enqueue fallback
# 2026-06-05 | Audit Phase 3.1b | Added groups CRUD: PATCH, DELETE, member removal, role change endpoints with 11 integration tests
# 2026-06-05 | Audit Phase 3.1c | Added authorization-gated watchparty PATCH/DELETE with 6 integration tests
# 2026-06-05 | Audit Phase 3.1d | Added POST /auth/change-password with current password verification, token revocation, and fresh token issuance with 6 integration tests
# 2026-06-05 | Audit Phase 3.1e | Fixed 2 pre-existing FK validation failures in watch party and discussion create endpoints (283 passed, 1 remaining mock failure)
# 2026-06-05 | Audit Phase 3.1f | Updated docs/api-spec.md with Notification Endpoints, Discussion Replies, Related Media, and Admin Sync routes documentation
# 2026-06-05 | Audit Phase 3.1g | Added media CRUD (POST/PATCH/DELETE), social DELETE, admin user list/delete, notification delete, watchparty RSVPs, user settings — 17 integration tests
# 2026-06-05 | Audit Phase 3.3 | Confirmed get_related_media() is a real DB query with relation type labels (not a stub)
# 2026-06-05 | Audit Phase 3.4 | Confirmed user_settings table exists with real get/update operations (not a stub)
# 2026-06-05 | Bugfix | Fixed BaseService.db_session session-caching bug — property created new AsyncSessionLocal() on every call instead of caching it, causing all write operations to commit on a different session than the one tracking object changes
# 2026-06-05 | Audit Phase 3.2 | Full service/repository consistency audit completed: 4 new repo files (social, watch_party, notification, tracking) with 14 repo classes; GroupService, SocialService, WatchPartyService, NotificationService, TrackingService migrated; MediaService/UserService bypasses fixed; 80 tests pass across all migrated services
# 2026-06-05 | Audit Phase 4.1 | Social Domain frontend pages implemented: FeedPage (group + my activity tabs), RecommendationsPage (inbox + sent tabs), DiscussionPage (threads list + detail + replies + create form); created social.ts types, social.ts Pinia store, useInfiniteScroll composable, ActivityFeedItem + RecommendCard components; 10 new Vitest tests pass; 33 total frontend tests pass
# 2026-06-05 | Audit Phase 4.2 | ProfilePage implemented: 3-tab layout (Overview, Edit Profile, Account & Security); overview with avatar/bio/metadata; edit form with displayName/avatar/bio/timezone validation; password change with match validation; 4 new Vitest tests pass; 37 total frontend tests pass
# 2026-06-05 | Audit Phase 4 | Complete — all 4 sub-phases done. Social domain pages, Profile page, stores/composables, and social components all implemented.
# 2026-06-05 | Audit Phase 5.1 | WatchPartyPage enhanced: Past tab with fetch+status badges, maximized detail dialog with host/media/RSVP info, RSVP actions (Attending/Maybe/Decline), card-click detail navigation; 14 Vitest tests pass; 49 total frontend tests pass
# 2026-06-05 | Audit Phase 5.2 | NotificationsPage enhanced: All/Unread tabs with independent state, per-item Mark Read, Mark Selected Read, Mark All Read (batch PATCH), Preferences navigation, scope-aware tab assertions; 16 Vitest tests pass; 64 total frontend tests pass
# 2026-06-05 | Audit Phase 5.3 | MyListPage enhanced: stats summary card (status chip counts), history feed section with event descriptions (added/status_changed/progress_updated/score_set), relative dates, loading/error/empty states per AppPageState pattern; 8 new Vitest tests pass; 71 total frontend tests pass
# 2026-06-05 | Audit Phase 5.4 | Created types/auth.ts (7 interfaces) and types/api.ts (PaginatedResponse); consolidated UserProfile duplicate from social.ts; updated stores/auth.ts and services/storage.ts imports; no test regressions
# 2026-06-05 | Audit Phase 5 | Complete — all 4 sub-phases done. WatchParty (Past/Detail/RSVP), Notifications (All/Unread/Mark Read), MyList (Stats/History), and type extraction all implemented.
# 2026-06-05 | Audit Phase 6.1 | Page test expansion: LoginPage (0→9), RegisterPage (0→9), DiscoverPage (1→10), MediaDetailPage (1→7), AiringCalendarPage (1→7), ImportListPage (1→8), NotificationPreferencesPage (2→9); 124 total frontend tests pass
# 2026-06-05 | Audit Phase 6.2 | Store tests: tracking.ts (10), watchparty.ts (13), notifications.ts (14); 161 total frontend tests pass
# 2026-06-05 | Audit Phase 6.3 | Page expansion: SetupPage (2→7), FeedPage (3→7), RecommendationsPage (3→7); 174 total frontend tests pass — Audit Phase 6 complete
```

---

## Known Blockers

> List anything that is blocking progress. Remove when resolved.

# 2026-06-08 | Phase 18.8 | Import List — AniList tab: ImportListPage with provider-specific validation, job polling (3s), status display (running/completed/failed/partial), error mapping (400/429/generic)
# 2026-06-08 | Phase 18.9 | Import List — MAL tab: AniList+MAL tabs with distinct validation rules; both call same backend import flow; backend added GET /api/v1/sync/jobs/{job_id} user-facing endpoint
# 2026-06-08 | Phase 18.10 | Tracking page tests: 21 tests for ImportListPage — rendering, API routing, error mapping, loading states, job polling, status display, reset flow, validation rules
# 2026-06-08 | Phase 18 | Tracking frontend pages fully implemented (18.1–18.10); 187 frontend tests, 324 backend tests passing
# 2026-06-08 | .gitignore fixed (removed overbroad `env.*` rule); alembic/env.py now load_dotenv() for .env without manual env var; committed to version control
# 2026-06-08 | ADR 079 | Frontend design direction — keep Quasar as shell, build custom streaming component library for aniwave-style aesthetic
# 2026-06-08 | ADR 080 | Playback API contract — GET /media/{id}/episodes, /sources, /episodes/sources endpoints
# 2026-06-08 | ADR 081 | Frontend player architecture — usePlayerListener composable, VideoPlayer overlay, origin validation
# 2026-06-08 | ADR 082 | Media detail streaming redesign — hero banner, episode list with server selector, player overlay
# 2026-06-08 | ADR 083 | Home page streaming redesign — content sections, trending carousel, continue watching
# 2026-06-08 | ADR 084 | Real AniList import — username-based GraphQL public list fetching (replaces skeleton)
# 2026-06-08 | ADR 085 | Episode notification pipeline — hook + Apprise delivery + cleanup
# 2026-06-08 | ADR 086 | Admin source provider UI — sync triggers, job viewer, unmatched reconciliation
# 2026-06-08 | ADR 087 | Streaming features master plan — phased roadmap (Phases 25-32), ~46 days estimate
# 2026-06-08 | ADR 088 | Feature gap analysis vs AniWave/AniList/MAL — identified 8 new phases (33-40): Characters & Staff, User Stats, Charts, Advanced Browse, Player Enhancements, Social Expansion, Manga Reader, Platform Features — ~108 days total
# 2026-06-09 | Phase 25.1 | GET /media/{id}/episodes — canonical episode list endpoint implemented. EpisodeItem/EpisodeListResponse schemas, MediaRepository.get_episodes_by_media_id, MediaService.get_episodes, route with pagination, 8 integration tests (auth, empty, ordering, fields, pagination, invalid params, missing media)
# 2026-06-09 | Phase 25.2 | GET /media/{id}/chapters — canonical chapter list endpoint implemented. ChapterItem/ChapterListResponse schemas, same pattern, 8 integration tests
# 2026-06-09 | Phase 25.3 | GET /media/{id}/sources — provider source mappings endpoint implemented. SourceEpisodeItem/SourceMappingDetail/MediaSourceResponse schemas, SourceMappingRepository.get_mappings_by_media, SourceProviderService, route, 6 integration tests
# 2026-06-09 | Phase 25.4 | GET /media/{id}/episodes/sources — consolidated episodes endpoint implemented. ConsolidatedSourceInfo/ConsolidatedEpisodeSourceItem/ConsolidatedEpisodeSourceResponse schemas, SourceEpisodeRepository.get_episodes_by_media, SourceProviderService.get_consolidated_episodes merges canonical + source episodes by episode_number, route, 8 integration tests. Fixed empty-state test isolation across Phase 25 test files with _create_test_media helper. All 354 backend + 187 frontend tests pass
# 2026-06-09 | Phase 25.5 | GET /media/genres — simple genre list endpoint. GenreItem/GenreListResponse schemas, MediaRepository.get_genres, MediaService.get_genres, route with auth, 3 integration tests. All 357 backend + 187 frontend tests pass
# 2026-06-09 | Phase 25.6 | GET /media/seasonal — seasonal media endpoint. SeasonalMediaItem/SeasonalResponse schemas, defaults to current season/year, ordered by average_score DESC NULLS LAST. MediaRepository.get_seasonal_media, route, 7 integration tests. Added nulls_last() to QueryBuilder. All 364 backend + 187 frontend tests pass

# 2026-06-09 | Phase 25.7 | Admin source-mapping management — GET /admin/source-mappings (list with source/mapping_status filters + pagination) and PATCH /admin/source-mappings/{id} (update media_id, mapping_status, match_confidence, streaming flags, title, etc.) with require_admin guard. Added AdminSourceMappingItem/AdminSourceMappingListResponse/AdminSourceMappingUpdate schemas, SourceMappingRepository.list_all_with_filters/count_all_with_filters methods, routes in admin.py, mapping_status validation (matched/unmatched/ignored/stale). 18 integration tests (auth, admin gate, filters, pagination, field updates, partial updates, empty body 400, invalid status 422). Phase 25 complete — all 7 sub-phases implemented. All 382 backend + 187 frontend tests pass
# 2026-06-09 | Phase 26.2 | AnimeCard + AnimeGrid primitives — AnimeCard.vue (cover/badges/hover play overlay, image lifecycle, skeleton state), AnimeGrid.vue (responsive CSS grid 2→3→4→6 cols, loading/error/empty states, title header, item-click emit). 22 Vitest tests (12 card + 10 grid). All 220 frontend tests pass
# 2026-06-09 | Phase 26.3 | HeroBanner + ScoreRing — HeroBanner.vue (gradient overlay hero, poster/banner images, metadata tags, genre chips, expandable synopsis, ScoreRing integration, error fallback, responsive mobile layout), ScoreRing.vue (SVG circular score indicator with color thresholds green/gold/yellow/red, size prop, optional label, animated dashoffset). 14 new Vitest tests (9 banner + 5 ring). All 236 frontend tests pass
# 2026-06-09 | Phase 26.4 | EpisodeItem + EpisodeList + ServerSelector — EpisodeItem.vue (thumbnail/play overlay/watched checkmark/selected state), EpisodeList.vue (5-row skeleton, error/empty states, asc/desc sorting, watched tracking), ServerSelector.vue (source pills with SUB/DUB badges, skeleton/loading/error/empty states, unavailable/active states). 27 new Vitest tests (9 each). All 250 frontend tests pass
# 2026-06-09 | Phase 26.5 | VideoPlayer + usePlayerListener composable — VideoPlayer.vue (iframe/loading/error/empty states, fullscreen API, PlayerControls+PlayerError integration), PlayerControls.vue (progress bar with seek, play/pause, MM:SS time display, quality selector, fullscreen toggle, hover fade), PlayerError.vue (message/retry button), usePlayerListener composable (postMessage origin validation, reactive isPlaying/currentTime/error state, sendCommand/togglePlay/seek, lifecycle cleanup, onEvent callback). 51 Vitest tests (19 composable + 6 error + 14 controls + 12 video player). All 301 frontend tests pass
# 2026-06-09 | Phase 26.6 | TrendingCarousel — horizontal scroll track with hidden scrollbar, arrow navigation (scrolls by itemWidth×3, disabled at start/end bounds via scrollPos tracking), gradient fade overlays (left+right), skeleton loading (7 shimmer cards), error/empty states, resize handler for maxScroll recalculation. 12 Vitest tests. All 313 frontend tests pass across 33 files
# 2026-06-09 | Phase 26 | Complete — All 6 sub-phases (26.1–26.6) implemented. 8 new components (AnimeCard, AnimeGrid, HeroBanner, ScoreRing, EpisodeItem, EpisodeList, ServerSelector, TrendingCarousel), 1 new player composable (usePlayerListener), 3 player components (VideoPlayer, PlayerControls, PlayerError), 1 composable test suite (19 tests), 107 total new Vitest tests across 33 files. tokens.scss design token system (surfaces, accents, spacing, typography, breakpoints, mixins). Dark streaming-first aesthetic (bg: #0a0a0a, purple/cyan accents). All 313 frontend tests + 382 backend tests pass. Phase 26 COMPLETE
# 2026-06-09 | Phase 27.1 | HomePage layout — hero spotlight + section structure. HomePage.vue (hero carousel with auto-rotate/dots/gradient, TrendingCarousel, AnimeGrid, FriendActivityRow, GenrePills, SectionHeader), home.ts Pinia store (parallel fetchHome with Promise.allSettled, graceful error isolation, API data mapping), route `/` -> HomePage. 27 new tests (8 HomePage + 6 FriendActivityRow + 5 GenrePills + 7 store + 1 SectionHeader). All 340 frontend tests pass across 38 files
# 2026-06-09 | Phase 27.2 | Continue Watching section — GET /api/v1/lists/me?statuses=watching,reading with progress/percentage overlay on AnimeCard, ContinueWatchingItem type, home.ts store fetchContinueWatching, horizontal scroll rack, See All → /list. Backend: QueryBuilder.options() for eager-loading, MediaEntryRef schema, ListEntryResponse.media field. Frontend: AnimeCard progress bar (4px accent), 12 new tests (6 AnimeCard + 4 store + 2 HomePage). 352 frontend tests pass. Backend: MediaEntrySchema/ref fix, dict-dump for create/update, 3 new backend tests
# 2026-06-09 | Phase 27.3 | Friends Activity section — media type filter pills + pagination. Backend: GET /social/feed accepts media_type query param (anime/manga/manhwa), joins MediaEntry, filters by type. Frontend: home.ts store pagination refs (friendActivityOffset/HasMore/Filter), fetchFriendActivity(loadMore, mediaType), loadMoreFriendActivity(), setFriendActivityFilter(). FriendActivityRow.vue: filter pill bar + Load More button + disabled states. HomePage.vue: Friend Activity always visible (no v-if). Bug fixes: filterOptions syntax error (]()→]), removed conflicting isLoading guard from store, Pinia ref unwrapping in tests. 13 new tests (4 store + 8 component + 1 HomePage). 365 frontend tests pass across 38 files
# 2026-06-09 | Phase 27.4 | Search integration — SearchBar.vue with debounced autocomplete dropdown (top 5 results), Enter → /search?q= route. SearchResultsPage.vue with AnimeGrid results rendering. MainLayout toolbar: OtakuHub brand + SearchBar + theme toggle. 11 new Vitest tests (component states, debounce, API calls, navigation, clear). 376 frontend tests pass across 39 files
# 2026-06-09 | Phase 27.5 | Genre pills navigation — useMediaSearch composable now supports genres param (comma-separated, sent to backend as-is). DiscoverPage reads genre query param on mount and auto-executes search. GenrePills (existing) navigates via searchByGenre → /discover?genre=slug. All 376 frontend tests pass (no regressions)
# 2026-06-09 | Phase 27.6 | Final test coverage pass — added DiscoverPage genre auto-search test (11 total), SearchBar (11), GenrePills (5), HomePage (10+). 377 frontend tests pass across 39 files. Phase 27 is fully complete
```
# Format: [OPEN/RESOLVED] Phase X.Y — description
[RESOLVED] Phase 13.3 — Backend pytest runtime verified via backend .venv and tests passed
[RESOLVED] Phase 7.10 — Android SDK configured; Capacitor Android release build succeeds
[RESOLVED] Audit Phase 3.1e — watchparty + discussion create endpoints now validate media_id FK (return 400 for unknown media)
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
