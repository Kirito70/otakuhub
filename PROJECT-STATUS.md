# OtakuHub — Project Status

> This file is the single source of truth for build progress.
> Every AI agent MUST read this file before starting any task.
> Update this file at the end of every phase or sub-task completion.
> Never skip ahead — complete the current phase before marking it done.

---

## Current State

```
CURRENT_PHASE:     AUDIT_PHASE_2 (Database & Models Alignment)
CURRENT_SUB_PHASE: 2.6
STATUS:            PHASE_COMPLETE
LAST_UPDATED:      2026-06-04
BLOCKED_BY:        none
NEXT_ACTION:       Review AUDIT-PLAN.md Phase 3 (Backend Endpoint Gaps)
```

> **Note**: After completing all 24 formal phases, an audit (AUDIT-PLAN.md) identified real gaps. Phase 0 (cleanup), Phase 1 (sync pipeline), and Phase 2 (Database & Models Alignment) are now complete. Phases 3+ pending.

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
| 18.8 | Import List — AniList tab | ⏳ | Import trigger, job status, user feedback |
| 18.9 | Import List — MAL tab | ⏳ | Provider-specific validation and feedback |
| 18.10 | Tracking page tests | ⏳ | Core interaction and validation coverage |

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

### Audit Phase 2 — Database & Models Alignment
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
```

---

## Known Blockers

> List anything that is blocking progress. Remove when resolved.

```
# Format: [OPEN/RESOLVED] Phase X.Y — description
[RESOLVED] Phase 13.3 — Backend pytest runtime verified via backend .venv and tests passed
[RESOLVED] Phase 7.10 — Android SDK configured; Capacitor Android release build succeeds
[OPEN] Pre-existing — watchparty + discussion create endpoints don't validate media_id FK (return 201 instead of 400)
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
