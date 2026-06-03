# ADR 076 — Sync Pipeline: Real Data Ingestion

**Status**: Proposed
**Date**: 2026-06-03

## Context

All four source adapters in the sync pipeline are **stubs**:

| Adapter | `_parse_item` | `_upsert_item` |
|---------|--------------|----------------|
| `AnimeOfflineSeedAdapter` | Returns `{"index": i}` | Does nothing |
| `AniListSeedAdapter` | Returns `{"index": i}` | Does nothing |
| `MangaDexSeedAdapter` | Returns `{"index": i}` | Does nothing |
| `JikanSeedAdapter` | Returns `{"index": i}` | Does nothing |

The orchestration framework (orchestrator, factory, job_runner, ingestion loop, observability) is fully built and tested. Tasks route through `run_seed_source()` → `SeedOrchestrator.run_source()` → `adapter.run()`, which calls `run_ingestion()` with a `_parse_item`/`_upsert_item` pair. The ingestion loop already:
- Creates `sync_jobs` rows
- Per-item retry with `IngestionRetryPolicy`
- Progress reporting via `job_runner`
- Terminal status (`completed`/`partial`/`failed`)
- Error logging

**What blocks real data ingestion:**
1. Adapter `_parse_item` / `_upsert_item` implementations are stubs
2. `AniListClient` fetches GraphQL schema on every instantiation (`fetch_schema_from_transport=True`)
3. `MangaDexClient` and `JikanClient` require `async with` context manager but adapters call them directly → `AttributeError: self.session is None`
4. `MangaDexClient.get_manga_list()` ignores the `title` parameter
5. `RateLimiter.acquire()` is a no-op (`await asyncio.sleep(0)`)
6. `SyncService` methods (`sync_media_from_anilist`, `backfill_missing_metadata`, `update_or_create_media_from_anilist`) are stubs
7. Worker tasks `import_user_list_task` and `process_new_episodes_task` return hardcoded dicts

## Decision

### 1. Fix External API Clients First (no adapter work before clients work)

All external client bugs must be resolved before adapters are implemented — adapters depend on clients returning real data.

#### 1a. AniListClient — Cache schema fetch

Change `fetch_schema_from_transport=True` to `False` and provide a static `schema.graphql` file. The AniList schema changes rarely; fetching it on every client instantiation wastes 1-2 seconds per call.

**Alternatively**, lazy-init: only fetch the schema on first `execute_async()` call and cache it on the instance.

**Decision**: Lazy-init via `@cached_property` on `self.client`, constructing the `Client` only when first needed.

#### 1b. MangaDexClient / JikanClient — Remove context manager requirement

**Problem**: Both clients use `async def __aenter__` / `__aexit__` to manage the `aiohttp.ClientSession`. The adapter factory and orchestrator use `AniListSeedAdapter()` directly (no context manager). When an adapter calls `self.client.get_manga_details(...)`, the session is `None` and the client raises `Exception("Client not initialized. Use async with context manager.")`.

**Decision**: Change both clients to use `lazy_session` pattern:

```python
@property
def session(self) -> aiohttp.ClientSession:
    if self._session is None or self._session.closed:
        self._session = aiohttp.ClientSession()
    return self._session
```

Keep `__aenter__`/`__aexit__` for explicit context manager usage (backward compat), but make direct calls work by auto-creating the session.

#### 1c. MangaDexClient.get_manga_list() — Pass `title` parameter

**Current**: `get_manga_list(self, title: str, ...)` — `title` parameter is accepted but not passed to the API call.

**Fix**: Add `?title={title}` to the endpoint. The MangaDex v5 API supports `GET /manga?title={title}`.

#### 1d. RateLimiter — Implement token-bucket

**Decision**: Implement a simple in-memory sliding-window rate limiter:

```python
class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: float = 60.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self._timestamps: list[float] = []

    async def acquire(self):
        now = time.monotonic()
        # Remove timestamps outside the window
        self._timestamps = [t for t in self._timestamps if now - t < self.time_window]
        if len(self._timestamps) >= self.max_requests:
            # Sleep until oldest request expires
            sleep_for = self._timestamps[0] + self.time_window - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
        self._timestamps.append(time.monotonic())
```

This is per-instance. For production with multiple worker processes, this would need Redis (future concern). For the initial implementation with single-worker Celery concurrency on the `sync` queue, per-instance is sufficient.

### 2. Implement Adapter `_parse_item` / `_upsert_item`

#### 2a. AnimeOfflineSeedAdapter (Stage 1: Seed)

**Source**: `anime-offline-database.json` — a static JSON file listing ~29k anime entries with MAL/AniList/Kitsu cross-references.

**`_parse_item` contract**:
- Input: `item_index: int` (index into the pre-loaded JSON array)
- Access the JSON via a class-level or instance-level `self._data` loaded from file in `__init__`
- Output: `dict` with fields matching `media_entries` + `media_external_ids`:
  ```python
  {
      "title_romaji": str,
      "title_english": str | None,
      "title_native": str | None,
      "media_type": "anime",  # always anime for this source
      "format": str | None,   # TV, MOVIE, OVA, etc.
      "status": str,           # FINISHED, RELEASING, etc.
      "synopsis": str | None,
      "episode_count": int | None,
      "cover_image": str | None,
      "anilist_id": int | None,
      "mal_id": int | None,
      "anidb_id": int | None,
      "kitsu_id": int | None,
  }
  ```

**`_upsert_item` contract**:
- Input: parsed dict from `_parse_item`
- `INSERT INTO media_entries ... ON CONFLICT (id) DO NOTHING` — seed entries with metadata_synced_at = NULL
- After `media_entries` insert, `INSERT INTO media_external_ids ... ON CONFLICT (anilist_id) DO NOTHING`
- Use `session.execute()` with raw SQL or SQLAlchemy core for bulk efficiency (but row-by-row is acceptable for 29k items in a batch)

**Data loading**: In `__init__`, load from a well-known path:
1. Check `ANIME_OFFLINE_DATABASE_PATH` env var
2. Fallback: `backend/data/anime-offline-database.json`
3. If not found, download from `https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json`

The `item_count` for `run_ingestion` should be `len(data["data"])` (the full array).

#### 2b. AniListSeedAdapter (Stage 2: Backfill)

**Source**: AniList GraphQL API via `AniListClient`.

**`_parse_item` contract**:
- Input: `item_index: int` (unused — the adapter fetches from AniList directly using `self._batch_buffer`)
- Instead of using the index-based `parse_item` pattern, the adapter batches: fetch 50 AniList IDs from `media_external_ids WHERE metadata_synced_at IS NULL`, buffer them, then `_parse_item` returns one entry from the buffer.

**Revised approach**: The `parse_item`/`upsert_item` loop in `run_ingestion` is item-count-based. For AniList backfill, override at the adapter level:

```python
class AniListSeedAdapter:
    def __init__(self, client: AniListClient | None = None):
        self.client = client or AniListClient()
        self._buffer: list[dict] = []

    async def run(self, context: SeedExecutionContext) -> SeedRunResult: ...
```

The adapter's `run()` method fetches pages of AniList data, processes each batch, and updates progress. This bypasses the index-based `run_ingestion` loop — use the `run_ingestion` function only when the adapter has an item count to iterate over.

**For the initial implementation**, implement `_parse_item` to take an AniList API response dict and return a normalized dict:

```python
async def _parse_item(raw: dict) -> dict:
    return {
        "anilist_id": raw["id"],
        "title_romaji": raw.get("title", {}).get("romaji"),
        "title_english": raw.get("title", {}).get("english"),
        "title_native": raw.get("title", {}).get("native"),
        "media_type": raw.get("type", "").lower(),
        "format": raw.get("format"),
        "status": raw.get("status"),
        "synopsis": raw.get("description"),
        "episode_count": raw.get("episodes"),
        "chapter_count": raw.get("chapters"),
        "volume_count": raw.get("volumes"),
        "duration_minutes": raw.get("duration"),
        "average_score": raw.get("averageScore"),
        "popularity": raw.get("popularity"),
        "trending": raw.get("trending"),
        "season": raw.get("season", "").lower() if raw.get("season") else None,
        "season_year": raw.get("seasonYear"),
        "start_date": _parse_date(raw.get("startDate")),
        "end_date": _parse_date(raw.get("endDate")),
        "cover_image_large": raw.get("coverImage", {}).get("large"),
        "cover_image_medium": raw.get("coverImage", {}).get("medium"),
        "banner_image": raw.get("bannerImage"),
        "is_adult": raw.get("isAdult", False),
        "country_of_origin": raw.get("countryOfOrigin"),
        "genres": raw.get("genres", []),
        "tags": raw.get("tags", []),
        "studios": raw.get("studios", {}).get("nodes", []),
        "relations": raw.get("relations", {}).get("edges", []),
    }
```

**`_upsert_item` contract**:
- `INSERT INTO media_external_ids (anilist_id, ...) ON CONFLICT (anilist_id) DO UPDATE SET ...`
- `INSERT INTO media_entries (...) ON CONFLICT (id) DO UPDATE SET ... metadata_synced_at = NOW()`
- Upsert genres: `INSERT INTO genres ... ON CONFLICT DO NOTHING` then `INSERT INTO media_genres ... ON CONFLICT DO NOTHING`
- Upsert tags: same pattern
- Upsert studios: same pattern
- Upsert relations: `INSERT INTO related_media ... ON CONFLICT DO NOTHING`

**Key**: the `id` lookup is: `anilist_id → media_external_ids.media_id → media_entries.id`.

**Query strategy** (for AniList backfill):
1. `SELECT media_external_ids.media_id FROM media_external_ids WHERE anilist_id IS NOT NULL AND metadata_synced_at IS NULL LIMIT 50` (or use the `only_unsynced` flag)
2. Fetch those 50 AniList IDs via the batch GraphQL query
3. For each result, `_parse_item` then `_upsert_item`

#### 2c. MangaDexSeedAdapter (Stage 3: Manga Detail)

**Source**: MangaDex REST API via `MangaDexClient`.

**Purpose**: Fetch chapter lists and cover art for manga-type entries (manga, manhwa, manhua, light_novel, novel).

**`_parse_item` contract**:
- Input: MangaDex manga UUID string
- Fetch chapters: `client.get_chapters(manga_id)` → extract chapter numbers, titles, published dates
- Output:
  ```python
  {
      "mangadex_id": str,
      "media_id": UUID,      # our internal ID, looked up from media_external_ids
      "chapters": [{"chapter_number": float, "title": str | None, "published_at": datetime | None, "mangadex_chapter_id": str}],
      "cover_url": str | None,
  }
  ```

**`_upsert_item` contract**:
- Update `media_external_ids.mangadex_id` if not set
- `INSERT INTO chapters ... ON CONFLICT (media_id, chapter_number) DO UPDATE SET ...`
- Update `media_entries.cover_image_large/medium` if cover URL is available
- Set `metadata_synced_at = NOW()`

**Query strategy**:
- `SELECT media_external_ids.media_id, media_external_ids.mangadex_id FROM media_external_ids WHERE mangadex_id IS NOT NULL` — for manga types
- Or join with `media_entries` to find manga with `metadata_synced_at IS NULL`

#### 2d. JikanSeedAdapter (Stage 4: Supplement)

**Source**: Jikan (MyAnimeList) API v4 via `JikanClient`.

**Purpose**: Supplement missing data for entries that have MAL IDs but limited AniList data.

**`_parse_item` contract**:
- Input: MAL ID (int)
- Fetch details: `client.get_anime_details(mal_id)`
- Output: similar normalized dict to AniList adapter

**`_upsert_item` contract**:
- Same pattern as AniList adapter but only updates fields missing from previous backfill
- Only runs for entries where `metadata_synced_at IS NULL` or where AniList data is incomplete

**Priority**: Low — Jikan supplement is optional. Skip if the AniList backfill already populated all fields.

### 3. De-stub SyncService

Replace stub methods with real implementations that use the sync pipeline:

| Method | Current | Target |
|--------|---------|--------|
| `sync_media_from_anilist()` | No-op | Calls `AniListSeedAdapter.run()` to backfill from AniList |
| `backfill_missing_metadata()` | Returns `True` | Calls the appropriate adapter based on media type |
| `update_or_create_media_from_anilist()` | Returns `MediaEntry(**data)` | Real upsert logic using repositories |

These service methods should be used by the API routes (e.g., on-demand fetch triggered by search miss).

### 4. Implement Worker Tasks

| Task | Current | Target |
|------|---------|--------|
| `import_user_list_task` | Returns hardcoded dict | Fetches user's AniList/MAL list via external_auth tokens, upserts into `user_list_entries` |
| `process_new_episodes_task` | Returns hardcoded dict | Queries `episodes`/`chapters` for recently aired/published entries, calls notification tasks |

### 5. Data Flow Summary

```
┌──────────────────────────────────────────────────────────────────┐
│  seed_database_task (Celery)                                     │
│  → run_seed_source("anime-offline")                              │
│    → AnimeOfflineSeedAdapter.run()                               │
│      → Load anime-offline-database.json                          │
│      → For each entry: _parse_item → _upsert_item                │
│      → INSERT media_entries + media_external_ids                 │
│      → Result: ~29k entries with NULL metadata_synced_at         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│  backfill_anilist_task (Celery)                                  │
│  → run_seed_source("anilist", only_unsynced=True)                 │
│    → AniListSeedAdapter.run()                                    │
│      → SELECT media_external_ids WHERE anilist_id IS NOT NULL    │
│        AND metadata_synced_at IS NULL  (LIMIT 50)                │
│      → Batch fetch from AniList GraphQL                          │
│      → For each: _parse_item → _upsert_item (full metadata)      │
│      → UPDATE metadata_synced_at = NOW()                         │
│      → Repeat until all unsynced entries processed               │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│  mangadex_detail_task (Celery)                                   │
│  → run_seed_source("mangadex", only_unsynced=True)                │
│    → MangaDexSeedAdapter.run()                                   │
│      → SELECT media_external_ids WHERE mangadex_id IS NOT NULL   │
│        AND metadata_synced_at IS NULL  (for manga types)         │
│      → Fetch chapters + cover from MangaDex REST                 │
│      → INSERT chapters, update cover images                      │
└──────────────────────────────────────────────────────────────────┘
```

### 6. Implementation Order

1. **Phase 1.1**: Fix external API clients (AniListClient lazy-init, MangaDexClient/JikanClient lazy_session, MangaDexClient.get_manga_list() title param, RateLimiter token-bucket)
2. **Phase 1.2**: AnimeOfflineSeedAdapter — real _parse_item and _upsert_item (first working data pipeline)
3. **Phase 1.3**: AniListSeedAdapter — real backfill (core metadata enrichment)
4. **Phase 1.4**: MangaDexSeedAdapter — chapter fetching for manga
5. **Phase 1.5**: De-stub SyncService methods
6. **Phase 1.6**: Implement worker tasks (import_user_list, process_new_episodes)
7. **Phase 1.7**: JikanSeedAdapter — MAL supplement (optional, lowest priority)

## Consequences

**Good**:
- Real data flows through the pipeline end-to-end
- Users see actual media entries, covers, and metadata
- Existing orchestrator, job_runner, and observability code remains unchanged
- Each adapter is self-contained and independently testable
- Lazy client init removes the crash path without breaking context manager API
- Rate limiter prevents API bans while being simple enough for single-worker use

**Bad**:
- The `run_ingestion` index-based loop doesn't fit AniList/MangaDex adapters well — they need custom `run()` overrides
- Rate limiter is in-memory per-process, not Redis-backed — multi-worker setups will exceed limits
- No test coverage yet for the real adapter implementations (must add)

**Neutral**:
- The Jikan adapter is lowest priority — MAL data is supplementary and many entries already have AniList data
- The `import_user_list_task` requires OAuth tokens to already be stored in `external_auth` (separate work item)
