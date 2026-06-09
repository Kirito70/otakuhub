# ADR 084 — Real AniList/MAL List Import

**Status**: Proposed
**Date**: 2026-06-08

## Context

The `import_user_list_task` in `sync_tasks.py` is currently a **skeleton**:

```python
# TODO: Implement real AniList/MAL list import
job.status = "completed"
job.processed_items = 0
job.completed_at = datetime.now(UTC)
```

It creates a `sync_jobs` row, marks it completed immediately, and imports nothing. The frontend `ImportListPage.vue` polls for status and shows a completion card, but no actual data flows.

There are two approaches:

**A. OAuth import** — User connects their AniList/MAL account via OAuth in OtakuHub, we store the token in `external_auth`, then fetch their list server-to-server in a Celery task.

**B. Username-based import** — User provides their AniList/MAL username (no OAuth), we fetch publicly available list data from AniList GraphQL or MAL API. AniList supports this for public lists; MAL requires the list to be public.

For a **private friend-group app** (5–20 users), approach B is simpler and avoids OAuth complexity. However, approach A is more reliable (works for private lists, gives access to all data including scores/notes).

## Decision

### 1. Implement both approaches: username-first, OAuth fallback

**Phase 1 (immediate)**: Username-based public list import via AniList GraphQL API.

- AniList allows querying any user's public anime/manga list via GraphQL:
  ```graphql
  query ($username: String) {
    MediaListCollection(userName: $username, type: ANIME) {
      lists {
        entries {
          mediaId
          status
          score
          progress
          repeat
          startedAt { year month day }
          completedAt { year month day }
        }
      }
    }
  }
  ```
- No authentication required for public lists
- Import result: upsert into `user_list_entries` with correct status mapping
- Status mapping: `CURRENT → watching`, `COMPLETED → completed`, `PAUSED → paused`, `DROPPED → dropped`, `PLANNING → plan_to_watch`
- Progress mapping: `progress` → episodes watched, `mediaId` → resolved via `media_external_ids.anilist_id`
- Score mapping: AniList uses 0–100 (100-point scale), OtakuHub uses 0.0–10.0 — divide by 10

**Phase 2 (future)**: OAuth-based import for private lists and MAL.

- Store AniList access/refresh tokens in `external_auth`
- Use token to authenticate GraphQL requests for private list data
- MAL OAuth flow for MAL list import
- Phase 2 is scoped out of this ADR — will be ADR 085

### 2. Celery task implementation

Replace the skeleton `import_user_list_task` in `sync_tasks.py`:

```python
@celery_app.task(bind=True, name="sync.import_user_list", max_retries=3)
def import_user_list_task(self, user_id: UUID, provider: str, username: str) -> dict[str, Any]:
```

**Behavior:**
1. Create `sync_jobs` row with `status='running'`, `job_type='user_import_anilist'` or `'user_import_mal'`
2. Call `AniListListFetcher.fetch_user_list(username)` for AniList
3. For each entry in the response:
   - Resolve `mediaId` → `media_entries.id` via `media_external_ids.anilist_id`
   - Upsert into `user_list_entries` using `(user_id, media_id)` conflict key
   - If conflict: update status, progress, score; do NOT overwrite notes or custom data
   - If no conflict: insert new entry
4. For each inserted/updated entry, create a `list_entry_history` row with `event_type='added'` (for insert) or `event_type='status_changed'`/`'progress_updated'` (for update)
5. Track: `processed_items` = number of entries processed, `failed_items` = number of entries where media_id could not be resolved (unknown anime)
6. Set terminal status: `completed` if all succeeded, `partial` if some failed, `failed` if unrecoverable

### 3. New external client: AniList list fetcher

Location: `backend/src/app/external/anilist_list_client.py`

```python
class AniListListFetcher:
    """Fetches a user's anime/manga list from AniList GraphQL API.

    Uses the same rate limiter as `AnilistClient` (80 req/min).
    """

    def __init__(self, rate_limiter: RateLimiter | None = None):
        self.rate_limiter = rate_limiter or RateLimiter(
            max_requests=80, time_window=60.0
        )

    async def fetch_user_list(
        self, username: str, media_type: str = "ANIME"
    ) -> list[AniListListEntry]:
        """Fetch a user's public anime/manga list."""

    async def fetch_user_list_by_token(
        self, access_token: str, media_type: str = "ANIME"
    ) -> list[AniListListEntry]:
        """Fetch a user's private list using OAuth token."""
```

### 4. AniListListEntry schema

```python
class AniListListEntry(BaseModel):
    anilist_media_id: int
    status: str                    # CURRENT, COMPLETED, PAUSED, DROPPED, PLANNING, REPEATING
    score: float | None            # 0–100 scale
    progress: int = 0
    repeat_count: int = 0
    started_at: dict | None        # { year, month, day }
    completed_at: dict | None      # { year, month, day }
```

### 5. Status mapping logic (service layer)

Location: `services/import_service.py` (new)

```python
ANILIST_STATUS_MAP = {
    "CURRENT": WatchStatus.WATCHING,
    "COMPLETED": WatchStatus.COMPLETED,
    "PAUSED": WatchStatus.PAUSED,
    "DROPPED": WatchStatus.DROPPED,
    "PLANNING": WatchStatus.PLAN_TO_WATCH,
    "REPEATING": WatchStatus.REWATCHING,
}

# For manga/manhwa:
ANILIST_STATUS_MAP_MANGA = {
    "CURRENT": WatchStatus.READING,
    "COMPLETED": WatchStatus.COMPLETED,
    "PAUSED": WatchStatus.PAUSED,
    "DROPPED": WatchStatus.DROPPED,
    "PLANNING": WatchStatus.PLAN_TO_READ,
    "REPEATING": WatchStatus.REREADING,
}
```

### 6. Database: `list_entry_history` for imports

Each imported entry creates a history row:

```python
# event_type = "imported"
# old_status = None
# new_status = mapped watch status
# old_progress = 0
# new_progress = imported progress
```

This makes imported entries distinguishable from manually-added ones in the activity feed.

### 7. User feedback improvements

The existing ImportListPage frontend already polls and displays status. After the real implementation:

- **Running**: Shows "Importing {N} anime entries from AniList..."
- **Completed**: Shows "Imported {N} entries" with breakdown
- **Partial**: Shows "Imported {N} entries, {M} skipped (anime not in database)"
- **Failed**: Shows error message with retry button

### 8. Testing contract

- `AniListListFetcher.test.py`: mock GraphQL response, verify parsing, handle empty list, handle unknown user error
- `user_import_task.test.py`: mock fetcher, verify upsert, verify history rows, verify status mapping, verify conflict handling (re-import updates existing)
- `ImportListPage.test.ts`: already has 21 tests — add test for real data flow (mock import response, verify status polling shows correct counts)

## Consequences

**Good**:
- Users can finally import their existing anime lists from AniList
- Username-only flow is simple: no OAuth setup, no tokens to store
- Public list import covers 95% of use cases for a private friend-group app
- Re-import is idempotent (upsert with conflict key)

**Bad**:
- Only works for public AniList lists initially (MAL and private lists need OAuth)
- AniList GraphQL rate limit (90 req/min) shared with metadata backfill — import uses the same 80 req/min token bucket
- Media matching depends on `media_external_ids.anilist_id` being populated (requires prior seed/backfill)

**Neutral**:
- MAL import (Phase 2) will need the Jikan API or MAL OAuth — significantly more complex
- OAuth flow adds a redirect-based auth dance on the frontend
