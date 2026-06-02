# OtakuHub — Complete Audit & Implementation Plan

> Generated: 2026-06-02  
> Source files audited: 418 tracked in `checkfiles.csv`  
> This document organizes EVERY missing feature, stub, dead code, and gap discovered during the full codebase audit.

---

## Phase 0: Immediate Cleanup

### 0.1 Delete Dead Code
**Root `src/app/` directory** (79 files): Old version superseded by `backend/src/app/`. Creates shadow-import risk when Python's `sys.path` resolves to project root first.  
**Action**: Delete `src/app/` entire tree after confirming nothing depends on it.

| File | Why dead |
|------|----------|
| `src/app/` (all 79 files) | No `pyproject.toml`, no Docker, no tests. `backend/pyproject.toml` is the only entry point |
| `backend/src/app/routers/_deprecated_auth.py` | Uses wrong import paths, not registered in any `__init__.py` |
| `backend/src/app/repositories/_deprecated_refresh_token_repository.py` | Broken imports, wrong constructor signature, auth service bypasses it |
| `backend/tests/debug_path.py` | Debugging aid, not a real test — prints sys.path |
| `gql/` directory | Unused GraphQL library — AniList client uses the `gql` PyPI package, not this local stub |

### 0.2 Rename Hidden Integration Tests
4 test files lack `test_` prefix, so they are NOT auto-discovered by `pytest`.

| Current name | Rename to | Tests |
|---|---|---|
| `backend/tests/phase9_social.py` | `backend/tests/test_phase9_social.py` | 15 tests (excellent) |
| `backend/tests/phase10_watchparty.py` | `backend/tests/test_phase10_watchparty.py` | 8 tests (good) |
| `backend/tests/phase11_notifications.py` | `backend/tests/test_phase11_notifications.py` | 9 tests (good) |
| `backend/tests/phase12_setup.py` | `backend/tests/test_phase12_setup.py` | 5 tests (good) |

### 0.3 Fix conftest.py JWT Secret
**Problem**: `backend/tests/conftest.py` uses `JWT_SECRET=test-suite-jwt-secret-value-change-me` which contains "test" and "secret" — both rejected by `Settings` validation.  
**Fix**: Use a secure random value like `JWT_SECRET=abbaf01d-e5e3-49c9-8ef1-677155e45d4f`.  
**Also missing**: No `db_session` or `auth_headers` fixtures despite what `backend-architecture.md` specifies.

---

## Phase 1: Sync Pipeline — Real Data Ingestion

**Current state**: All 4 source adapters are **stubs**. Framework works but no real data is ever ingested. SyncJobs show "completed" with dummy counts.

### 1.1 Anime Offline Database Adapter
**File**: `backend/src/app/sync/sources/anime_offline.py`  
**Status**: `_parse_item` returns `{"index": i}`, `_upsert_item` does nothing.  
**Work needed**:
- [ ] Download/embed `anime-offline-database.json` (or fetch at runtime)
- [ ] Implement `_parse_item` to parse anime entries (title, type, format, status, dates, etc.)
- [ ] Implement `_upsert_item` to insert/update `media_entries` + `media_external_ids`
- [ ] Handle batch processing with `context.batch_size`

### 1.2 AniList Adapter
**File**: `backend/src/app/sync/sources/anilist.py`  
**Status**: Identical stub.  
**Work needed**:
- [ ] Query `AniListClient` (real GraphQL client exists) for trending/popular media
- [ ] Implement `_parse_item` to extract fields from AniList GraphQL response
- [ ] Implement `_upsert_item` to backfill metadata for existing entries
- [ ] Handle rate limiting via the (currently no-op) `RateLimiter`
- [ ] Handle `context.only_unsynced` flag

### 1.3 MangaDex Adapter
**File**: `backend/src/app/sync/sources/mangadex.py`  
**Status**: Identical stub.  
**Work needed**:
- [ ] Query `MangaDexClient` (real REST client exists) for manga/manhwa
- [ ] Implement `_parse_item` to extract fields from MangaDex API response
- [ ] Implement `_upsert_item` for manga entries + chapters
- [ ] Handle rate limiting

### 1.4 Jikan Adapter
**File**: `backend/src/app/sync/sources/jikan.py`  
**Status**: Identical stub.  
**Work needed**:
- [ ] Query `JikanClient` (real REST client exists) for supplementary MAL data
- [ ] Implement `_parse_item` and `_upsert_item`

### 1.5 External API Client Fixes
- [ ] **AniListClient**: Cache the schema fetch (`fetch_schema_from_transport=True` fetches on every instantiation)
- [ ] **JikanClient** / **MangaDexClient**: Fix context manager pattern — services don't use `async with`, causing `AttributeError` when `self.session is None`
- [ ] **MangaDexClient.get_manga_list()**: Does not pass the `title` parameter to the API — bug
- [ ] **RateLimiter**: Implement actual token-bucket or sliding-window rate limiting

### 1.6 SyncService Un-stub
**File**: `backend/src/app/services/sync_service.py`  
- [ ] Implement `sync_media_from_anilist()` — currently stub/commented out
- [ ] Implement `backfill_missing_metadata()` — returns `True` but does nothing
- [ ] Implement `update_or_create_media_from_anilist()` — currently would crash

### 1.7 Worker Task Fixes
- [ ] `sync.import_user_list` task: returns hardcoded dict, no import logic
- [ ] `sync.process_new_episodes` task: returns hardcoded dict, no processing logic
- [ ] Trigger notification tasks with real data (nothing calls `send_new_episode_notifications_task.delay()`)

---

## Phase 2: Database & Models Alignment

### 2.1 UUID v7 Migration
**Problem**: All models use `default_factory=uuid4()` (random UUIDs) instead of `uuid7()` (time-ordered).  
**Files affected**: All 31 model files in `backend/src/app/models/`.  
**Work needed**:
- [ ] Change `uuid4()` to `uuid7()` in all model files
- [ ] Verify PostgreSQL has `pg_uuidv7` extension
- [ ] Create Alembic migration for any existing data

### 2.2 Full-Text Search Setup
**Problem**: `MediaEntry.title_search` is defined as `str` (plain text), not `TSVECTOR`. No GIN index. No trigger function. PostgreSQL `to_tsvector()` calls in `search_media()` will fail.  
**Files affected**:
- `backend/src/app/models/media_entry.py`
- `backend/src/app/repositories/media_repository.py`  
**Work needed**:
- [ ] Change `title_search` column type to `TSVECTOR`
- [ ] Create trigger function `update_media_title_search()`
- [ ] Create GIN index on `title_search`
- [ ] Create `pg_trgm` and `unaccent` extensions
- [ ] Create trigram indexes on `title_romaji`, `title_english`

### 2.3 Alembic Migration System
**Problem**: No migrations — uses `SQLModel.metadata.create_all()` for schema management.  
**Work needed**:
- [ ] Initialize Alembic in `backend/`
- [ ] Create initial migration capturing all current models
- [ ] Create migration for full-text search setup
- [ ] Write migration for UUID v7 change
- [ ] Document migration workflow

### 2.4 SQLite → PostgreSQL Compatibility
**Problem**: Default DB is `sqlite+aiosqlite:///:memory:` but models use PostgreSQL-only features (`TSVECTOR`, `varchar_pattern_ops`).  
**Fix**: Change default in `config.py` or ensure Docker Compose is always used for development.

### 2.5 Missing Unique Constraint
**Problem**: `user_list_entries` has a unique index on `(user_id, media_id)` but no DB-level `UNIQUE` constraint in the model.  
**Fix**: Add `UniqueConstraint` to `UserListEntry` model.

---

## Phase 3: Backend Endpoint Gaps

### 3.1 Missing CRUD Endpoints

| Router | Missing Endpoints | Priority |
|--------|-------------------|----------|
| **auth** | `PATCH /auth/me` (password change), `DELETE /auth/me` (delete account) | Medium |
| **media** | `POST /media` (admin create), `PATCH /media/{id}`, `DELETE /media/{id}` | Low |
| **media** | `GET /media/airing` — currently returns `{"items": [], "total": 0}` (stub) | High |
| **groups** | `PATCH /groups/{id}`, `DELETE /groups/{id}`, `GET /groups` (list all) | Medium |
| **groups** | `DELETE /groups/{id}/members/{user_id}` (remove member) | Medium |
| **groups** | Admin role change endpoint | Low |
| **social** | `GET /social/recommendations/sent` (sent recommendations) | High |
| **social** | `GET /social/discussions/{id}/replies` (list replies) | Medium |
| **social** | `DELETE /social/recommendations/{id}` | Low |
| **social** | `DELETE /social/discussions/{id}` | Low |
| **watchparty** | `GET /watchparty/{id}` (single party detail) | High |
| **watchparty** | `PATCH /watchparty/{id}`, `DELETE /watchparty/{id}` | Medium |
| **watchparty** | `GET /watchparty/past` (past parties) | Medium |
| **watchparty** | `GET /watchparty/{id}/rsvps` (list RSVPs) | Low |
| **notifications** | `POST /notifications/mark-all-read` | Medium |
| **notifications** | `DELETE /notifications/{id}` | Low |
| **users** | `GET /users/` (admin list), `DELETE /users/{id}` | Low |
| **sync** | Actually trigger Celery tasks from sync routes | High |

### 3.2 Service/Repository Pattern Inconsistency
**Problem**: Some services use repositories (`media_service`, `user_service`), others use direct `select(Model)` calls (`tracking_service`, `social_service`, `auth_service`, `group_service`).  
**Work needed**:
- [ ] Audit every service to use the repository pattern consistently
- [ ] Either use `GroupRepository`/`GroupMemberRepository` (currently orphaned) from `group_service`, or remove the orphaned repos

### 3.3 `get_related_media()` Stub
**File**: `backend/src/app/services/media_service.py`  
**Status**: Always returns `[]`.  
**Work needed**:
- [ ] Implement real DB query using `related_media` table
- [ ] Include relation type labels

### 3.4 User Settings Stubs
**File**: `backend/src/app/services/user_service.py`  
**Status**: `get_user_settings()` returns defaults, `update_user_settings()` is no-op. No settings table in DB.  
**Work needed**:
- [ ] Create `user_settings` table or add settings columns to `user` table
- [ ] Implement real get/update

---

## Phase 4: Frontend Pages — Complete Missing Implementations

### 4.1 Social Domain (3 pages — currently STUBS)

#### FeedPage.vue
**Current**: Just renders "Feed" text.  
**Required** (per architecture contract Phases 19.1-19.2):
- [ ] Tab navigation: Group Activity | My Activity
- [ ] Group Activity tab: fetch `GET /social/feed`, display activity cards (actor + action + media + timestamp)
- [ ] My Activity tab: fetch personal activity, same card format
- [ ] Pagination for both tabs
- [ ] `AppEmptyState` for empty/error/loading
- [ ] Tests: loading, empty, error, retry, pagination, navigation

#### RecommendationsPage.vue
**Current**: Just renders "Recommendations" text.  
**Required** (per architecture contract Phases 19.3-19.4):
- [ ] Tab navigation: Inbox | Sent
- [ ] Inbox tab: fetch `GET /social/recommendations/inbox`, display sender + media + message + acknowledge button
- [ ] Sent tab: fetch sent recommendations (needs `GET /social/recommendations/sent` endpoint)
- [ ] Acknowledge action via `PATCH /social/recommendations/{id}/acknowledge`
- [ ] Pagination, filters for acknowledged state
- [ ] Tests: full state coverage

#### DiscussionPage.vue
**Current**: Just renders "Discussion" text.  
**Required** (per architecture contract Phases 19.5-19.7):
- [ ] Tab navigation: Threads | Create | (Thread Detail on selection)
- [ ] Threads tab: fetch discussions, display title + body preview + author + spoiler label
- [ ] Thread Detail view: show thread + replies with pagination
- [ ] Create tab: form with title, body, spoiler toggle, media selector
- [ ] Spoiler reveal controls
- [ ] Tests: full state coverage, form validation, reply flow

### 4.2 ProfilePage.vue (currently STUB)
**Current**: Just renders "Profile" text.  
**Required** (per architecture contract Phases 22.1-22.4):
- [ ] Overview tab: avatar, display name, bio, timezone, summary stats
- [ ] Edit Profile tab: form for display name, avatar URL, bio, timezone
- [ ] Account & Security tab: password change, session management

### 4.3 Missing Stores & Composable
- [ ] Create `stores/social.ts` — feed, recommendations, discussions state
- [ ] Create `composables/useInfiniteScroll.ts` — for paginated lists

### 4.4 Missing Components
- [ ] `components/media/MediaCard.vue` — reusable card (currently built inline in DiscoverPage)
- [ ] `components/media/MediaBanner.vue` — hero banner for media detail
- [ ] `components/social/ActivityFeedItem.vue` — feed entry card
- [ ] `components/social/RecommendCard.vue` — recommendation card

---

## Phase 5: Frontend — Feature Gaps on Existing Pages

### 5.1 WatchPartyPage Enhancements
**Current**: Has create form + list. Missing detail view and past tab.  
- [ ] Add Past tab (`GET /watchparty/past`)
- [ ] Add Party Detail view with RSVP list
- [ ] Add detail navigation from upcoming list cards

### 5.2 NotificationsPage Enhancements
**Current**: Single inbox view, no tab separation.  
- [ ] Add All / Unread tab structure
- [ ] Add "Mark All Read" button (needs backend endpoint)

### 5.3 MyListPage Enhancements
**Current**: Working with inline custom list management.  
- [ ] Add `GET /lists/me/history` feed section
- [ ] Add statistics summary (total, completed, watching counts)

### 5.4 Missing Types
- [ ] Create `types/auth.ts` — UserProfile, LoginRequest, RegisterRequest (currently inline in store)
- [ ] Create `types/api.ts` — PaginatedResponse<T>, ErrorResponse
- [ ] Create `types/social.ts` — FeedItem, Recommendation, Discussion

---

## Phase 6: Frontend Test Coverage (Critical Gap)

**Current state**: 7 of 12 frontend test files are DUMMY (single text assertion). The architecture contracts (Phases 16-22) specify detailed test requirements that are NOT met.

### 6.1 Page Test Rewrites
Every page test should cover:
- Loading state (spinner/skeleton visible)
- Empty state (AppEmptyState rendered)
- Error state (error message + retry visible)
- Success state (data rendered correctly)
- Form validation (empty submit shows errors, invalid input blocked)
- Interaction (navigation, action triggers)

| Page | Current tests | Required coverage |
|------|--------------|-------------------|
| LoginPage | NONE | 5+ tests |
| RegisterPage | NONE | 6+ tests |
| SetupPage | 2 tests (decent) | Expand to 5+ |
| DiscoverPage | 1 dummy | Rewrite for search behavior |
| MediaDetailPage | 1 dummy | Rewrite for detail + add-to-list |
| MyListPage | 1 dummy | Rewrite for tab switching, CRUD |
| AiringCalendarPage | 1 dummy | Rewrite for airing display |
| ImportListPage | 1 dummy | Rewrite for import flow |
| WatchPartyPage | 2 tests (decent) | Expand |
| NotificationsPage | 1 dummy | Rewrite |
| NotificationPreferencesPage | 2 tests (good) | Expand |
| FeedPage | NONE | 4+ tests |
| RecommendationsPage | NONE | 4+ tests |
| DiscussionPage | NONE | 5+ tests |
| ProfilePage | NONE | 4+ tests |

### 6.2 Store Test Coverage
- [ ] Add tests for `tracking.ts` store
- [ ] Add tests for `watchparty.ts` store
- [ ] Add tests for `notifications.ts` store

---

## Phase 7: Infrastructure & DevOps Gaps

### 7.1 Rate Limiter
**File**: `backend/src/app/core/rate_limiter.py`  
**Status**: No-op (`await asyncio.sleep(0)`).  
**Work needed**:
- [ ] Implement token-bucket rate limiter for external API calls
- [ ] Track per-API rate limits (AniList: 90 req/min, Jikan: 60 req/min, MangaDex: 5 req/s)

### 7.2 Blocking Call in Async Context
**File**: `backend/src/app/external/apprise_client.py`  
**Problem**: `send_notification()` is synchronous (`def` not `async def`) but called from async Celery tasks.  
**Fix**:
- [ ] Run in executor: `await asyncio.get_event_loop().run_in_executor(None, self.send_notification, ...)`
- [ ] Or rewrite as async using `aiohttp` or `asyncio.to_thread()`

### 7.3 Default Config
**File**: `backend/src/app/config.py`  
**Issues**:
- [ ] Default `database_url = "sqlite+aiosqlite:///:memory:"` is incompatible with PostgreSQL features
- [ ] External API credentials have dummy defaults (`"dummy-anilist-id"`)

### 7.4 Docker & Deployment
- [x] Docker Compose for development exists
- [x] Docker Compose for production exists
- [ ] Add health check endpoints (only root + health exist)
- [ ] Configure Alembic migration in deployment pipeline
- [ ] Celery worker needs proper configuration for production

---

## Summary: All Known Gaps by Category

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| **Sync pipeline** | 4 adapters are stubs | External client context manager bugs | Rate limiter no-op | Schema fetch caching |
| **Database** | TSVECTOR fail on PG | UUID v7 migration | Alembic setup | Unique constraint |
| **Backend endpoints** | airing stub, sent recs, party detail | 5+ missing endpoints | 8+ missing endpoints | 5+ missing endpoints |
| **Social frontend** | 3 pages are stubs | Profile stub | Missing stores, types | Missing components |
| **Frontend tests** | 7 dummy tests | 8 pages untested | Store tests missing | N/A |
| **Infrastructure** | SQLite default vs PG features | Dead code cleanup | Hidden integration tests | conftest JWT secret |

**Total estimated effort**: 6-8 weeks for a single full-stack developer working focused.
