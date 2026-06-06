# OtakuHub — Sync Pipeline Architecture

## Overview
The sync pipeline populates and maintains the local anime/manga database
by pulling from canonical metadata sources: anime-offline-database (seed),
AniList GraphQL (primary metadata), MangaDex REST (manga detail), and Jikan.

ADR 078 adds a second class of sources: **provider/source mappings** for systems
that expose catalog IDs and episode IDs used by future playback integrations.
The first provider-source integration is Anikoto/MegaPlay. Anikoto provides the
catalog and episode IDs; MegaPlay consumes those IDs for approved embeds. These
IDs are stored in `media_source_mappings` and `media_source_episodes`, not in
`media_external_ids`.

## Pipeline Stages

```
┌──────────────────────────────────────────────────────────┐
│  Stage 1: SEED (one-time, ~30 seconds)                   │
│  Source: anime-offline-database GitHub Release JSON      │
│  Output: 29,000+ rows in media_entries + external_ids   │
└─────────────────────────┬────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Stage 2: ANILIST BACKFILL (background, ~7 min)          │
│  Source: AniList GraphQL API (50 IDs per query)          │
│  Output: Full metadata — titles, synopsis, covers,       │
│          genres, studios, tags, episode count            │
└─────────────────────────┬────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Stage 3: MANGADEX DETAIL (background, manga only)       │
│  Source: MangaDex REST API v5                            │
│  Output: Chapter list, chapter release dates, cover art  │
└─────────────────────────┬────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Stage 4: WEEKLY REFRESH (cron, every Sunday 02:00 UTC)  │
│  Source: anime-offline-database + AniList                │
│  Output: New entries added; 'releasing' entries updated  │
└─────────────────────────┬────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  Stage 5: ON-DEMAND (triggered by search miss)           │
│  Source: AniList GraphQL live search                     │
│  Output: Missing title upserted into DB + served         │
└──────────────────────────────────────────────────────────┘

  Plus (user-triggered):
┌──────────────────────────────────────────────────────────┐
│  Stage 6: USER LIST IMPORT                               │
│  Source: AniList OAuth / MAL API v2 (user's own list)    │
│  Output: user_list_entries populated from external list  │
└──────────────────────────────────────────────────────────┘

  Plus (provider-source mapping):
┌──────────────────────────────────────────────────────────┐
│  Stage 7: ANIKOTO / MEGAPLAY SOURCE IDS                  │
│  Source: Anikoto API (catalog + series + episode IDs)     │
│  Output: media_source_mappings + media_source_episodes    │
│          for future approved MegaPlay/provider playback   │
└──────────────────────────────────────────────────────────┘
```

## Rate Limits Reference

| API | Limit | Our target | Strategy |
|-----|-------|-----------|----------|
| AniList GraphQL | 90 req/min | 80 req/min | Redis token bucket; batch 50 IDs/query |
| MangaDex REST | ~5 req/s global | 4 req/s | asyncio.sleep(0.25) between calls |
| MAL API v2 | ~1 req/s (unofficial) | 0.8 req/s | Sleep 1.25s between calls |
| Jikan v4 | 60 req/min | 50 req/min | Token bucket |
| Anikoto API | 60 req / 120 sec / IP | 45 req / 120 sec | Backend-only client; bounded recent refresh; retry 429 using headers/backoff; dynamic adaptation via X-RateLimit-* headers; 403 treated as retryable (transient ban) |

## AniList Batch Math
- 29,000 entries ÷ 50 IDs/query = 580 queries needed
- At 80 queries/min: 580 ÷ 80 = 7.25 minutes
- Full backfill completes in ~8 minutes safely

## Celery Configuration

### Runtime Commands (uv)

Use backend CLI wrappers so workers/jobs are runnable the same way in local/dev CI:

```bash
# from backend/
uv run otakuhub celery worker --loglevel info --queue sync
uv run otakuhub celery beat --loglevel info

# enqueue jobs
uv run otakuhub celery seed --batch-size 50
uv run otakuhub celery weekly-refresh

# direct seed command paths (non-celery)
uv run otakuhub seed anime-offline
uv run otakuhub seed all
```

### Workers
```
celery -A backend.workers.celery_app worker \
    --concurrency=4 \
    --queues=sync,notifications,default \
    --loglevel=info
```

### Queues
| Queue | Purpose | Concurrency |
|-------|---------|------------|
| `sync` | AniList/MangaDex backfill tasks | 2 (rate limit friendly) |
| `notifications` | Apprise delivery | 4 |
| `default` | General background tasks | 4 |

### Beat Schedule
```python
beat_schedule = {
    # Every day at 01:00 UTC: AniList unsynced + MangaDex incremental
    "sync-daily-refresh-compose": {
        "task": "sync.daily_refresh_compose",
        "schedule": crontab(hour=1, minute=0),
    },
    # Every Sunday at 02:00 UTC: full canonical refresh composition
    "sync-weekly-refresh-compose": {
        "task": "sync.weekly_refresh_compose",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
    },
}

# ADR 078 extension: daily composition should enqueue Anikoto recent refresh
# after canonical metadata refresh, subject to ANIKOTO_SYNC_ENABLED=true.
# Full Anikoto catalog sync is admin-triggered/manual, not an every-day full scan.

# Notification/cleanup schedules remain under their own task namespace.

```

## Sync Service Implementation Contract (must-follow)

When implementing/expanding `sync_service.py` and worker tasks, use these fixed rules:

1. **Job audit row first**
   - Create `sync_jobs` row at task start with `status='running'`.
   - Always store `job_type`, `total_items`, and `started_at`.

2. **Progress updates in-loop**
   - Update `processed_items` and `failed_items` at batch boundaries.
   - Never keep progress only in memory.

3. **Terminal status is mandatory**
   - `completed` when all items succeeded,
   - `partial` when some failed,
   - `failed` for unrecoverable task-level failure.
   - Set `completed_at` for all terminal states.

4. **Error log format**
   - Persist machine-readable JSON in `sync_jobs.error_log`:
   - `[{"item": <id>, "source": "anilist|mangadex|mal", "error": "..."}]`

5. **Idempotent upserts only**
   - Seed/backfill jobs must be rerunnable without creating duplicates.
   - Use external IDs (especially `anilist_id`) as conflict keys where applicable.

6. **Rate-limit in worker layer, not router layer**
   - Router only enqueues jobs.
   - Worker task enforces external API pacing/retries.

7. **No user progress write-back to external providers**
   - Import from AniList/MAL is read-only external access.
   - Canonical tracking stays in OtakuHub DB.

8. **Freshness updates for metadata jobs**
   - Any successful metadata update must set `media_entries.metadata_synced_at = NOW()`.

## Recommended Job Types (canonical names)

Keep `sync_jobs.job_type` values consistent:

- `seed`
- `backfill_anilist`
- `mangadex_detail`
- `weekly_refresh`
- `user_import_anilist`
- `user_import_mal`
- `anikoto_full_catalog`
- `anikoto_recent_refresh`

## Upsert Strategy

### media_entries (seed)
```sql
INSERT INTO media_entries (id, title_romaji, media_type, ...)
VALUES (uuid_generate_v7(), $1, $2, ...)
ON CONFLICT (id) DO NOTHING
```

### media_entries (backfill update)
```sql
INSERT INTO media_entries (...) VALUES (...)
ON CONFLICT (id) DO UPDATE SET
    title_english = EXCLUDED.title_english,
    synopsis = EXCLUDED.synopsis,
    cover_image_large = EXCLUDED.cover_image_large,
    episode_count = EXCLUDED.episode_count,
    status = EXCLUDED.status,
    metadata_synced_at = NOW()
WHERE media_entries.metadata_synced_at IS NULL
   OR media_entries.updated_at < NOW() - INTERVAL '7 days'
```

### media_external_ids
```sql
INSERT INTO media_external_ids (media_id, anilist_id, mal_id, ...)
VALUES ($1, $2, $3, ...)
ON CONFLICT (anilist_id) DO UPDATE SET
    mal_id = COALESCE(EXCLUDED.mal_id, media_external_ids.mal_id),
    mangadex_id = COALESCE(EXCLUDED.mangadex_id, media_external_ids.mangadex_id)
```

### media_source_mappings / media_source_episodes (ADR 078)

Provider-source sync stores source IDs separately from canonical metadata IDs:

```sql
-- series/catalog-level upsert
INSERT INTO media_source_mappings (media_id, source, source_media_id, source_title, mapping_status, match_confidence, ...)
VALUES ($media_id, 'anikoto', $anikoto_series_id, $title, $status, $confidence, ...)
ON CONFLICT (source, source_media_id) DO UPDATE SET
    media_id = COALESCE(EXCLUDED.media_id, media_source_mappings.media_id),
    source_title = EXCLUDED.source_title,
    mapping_status = EXCLUDED.mapping_status,
    match_confidence = EXCLUDED.match_confidence,
    last_seen_at = NOW(),
    details_synced_at = EXCLUDED.details_synced_at,
    updated_at = NOW();

-- episode-level upsert
INSERT INTO media_source_episodes (mapping_id, media_id, source, source_episode_id, episode_number, language, embed_path, ...)
VALUES ($mapping_id, $media_id, 'anikoto', $episode_embed_id, $episode_number, $language, $embed_path, ...)
ON CONFLICT (source, source_episode_id, language) DO UPDATE SET
    mapping_id = EXCLUDED.mapping_id,
    media_id = COALESCE(EXCLUDED.media_id, media_source_episodes.media_id),
    episode_number = EXCLUDED.episode_number,
    embed_path = EXCLUDED.embed_path,
    is_available = TRUE,
    last_seen_at = NOW(),
    updated_at = NOW();
```

Matching order for Anikoto/MegaPlay source rows:

1. AniList ID → `media_external_ids.anilist_id`
2. MAL ID → `media_external_ids.mal_id`
3. Conservative title/year/type match → `mapping_status='matched'` only above threshold
4. Otherwise store as `mapping_status='unmatched'` with `media_id=NULL`

Do not create duplicate `media_entries` from Anikoto-only data unless a canonical AniList lookup confirms the media.

## Anikoto/MegaPlay Provider Sync Contract (ADR 078)

### External APIs

- Catalog API base URL: `https://anikotoapi.site`
- Recent anime: `GET /recent-anime?page={page}&per_page={per_page}`
- Series details: `GET /series/{id}`
- Playback/embed host: `https://megaplay.buzz`
- MegaPlay embed path from Anikoto episode ID: `/stream/s-2/{episode_embed_id}/{language}`

### Implementation boundaries

- `external/anikoto_client.py`: HTTP client, server-side only, timeout/backoff/rate limit handling. Reads `X-RateLimit-*` headers for dynamic bucket tuning; treats 403 as retryable with exponential backoff (the API docs note 403 can be a transient ban from aggressive traffic).
- `sync/sources/anikoto.py`: source adapter for full catalog and recent refresh modes. Catches `AnikotoRateLimitError` in the page loop with `Retry-After` sleep; after `detail_retry_cutoff` consecutive 429s on detail fetches, degrades gracefully to list-level data only for remaining items.
- `external/megaplay_client.py`: safe MegaPlay embed URL builder (`safe_embed_url`) and path builder (`safe_embed_path` legacy). Validates MegaPlay host, allowed path prefixes, and blocks raw media segment markers (.m3u8, .mp4, /hls/, etc.).
- source mapping repository: upserts `media_source_mappings` and `media_source_episodes` with full provider payloads (`source_payload` JSONB), structured multilingual titles (`source_titles` JSONB), and streaming options (`embed_url`, `embed_urls` JSONB).
- sync service: matching policy, confidence thresholds, source_payload archival, multilingual title extraction, and progress reporting.
- Celery: schedules/retries jobs and updates `sync_jobs`.
- frontend: no direct Anikoto/MegaPlay calls.

### Daily refresh composition

`sync.daily_refresh_compose` should become:

1. `backfill_anilist_task.s(only_unsynced=True)`
2. `mangadex_detail_task.s()`
3. `anikoto_recent_refresh_task.s()` when `ANIKOTO_SYNC_ENABLED=true`

### Full catalog sync

Full Anikoto sync should be admin-triggered via API/CLI because it can require many `/series/{id}` calls. It must:

- create a `sync_jobs` row with `job_type='anikoto_full_catalog'`;
- page through recent/catalog listing with bounded `per_page`;
- call detail endpoint per new/changed series with rate-limited concurrency (`max_detail_concurrency`, default 3);
- persist full detail payloads as `source_payload` JSONB, structured titles as `source_titles` JSONB, and streaming options as `embed_url`/`embed_urls`;
- set `details_synced_at` on both mapping and episode rows;
- persist progress after each page/batch;
- mark stale source mappings not seen in the latest full sync;
- end with `completed`, `partial`, or `failed`.

### Compliance / security rules

- Store provider IDs and safe embed paths only; never scrape or persist raw media segment URLs.
- Do not bypass provider embed restrictions.
- Do not expose playback endpoints until a separate playback ADR/API contract is accepted.
- Any future player event listener must validate `event.origin === 'https://megaplay.buzz'` before trusting watch-progress events.

## Monitoring

### sync_jobs Table
Every pipeline run creates a row in `sync_jobs`:
- `job_type`: seed | backfill_anilist | mangadex_detail | weekly_refresh | user_import
- `status`: running → completed | failed | partial
- `processed_items` / `total_items` / `failed_items`
- `error_log`: JSON array of failed item IDs + error messages

### Health Check Endpoint
`GET /api/v1/admin/sync/status` (admin auth required):
```json
{
  "last_seed": "2025-11-01T00:00:00Z",
  "last_weekly_refresh": "2026-04-13T02:00:00Z",
  "unsynced_entries": 142,
  "total_media_entries": 29847,
  "last_airing_refresh": "2026-04-19T12:00:00Z",
  "celery_workers": 2,
  "queue_depths": { "sync": 0, "notifications": 0, "default": 0 }
}
```

## User List Import Flow

```
1. User clicks "Import from AniList"
2. Flutter redirects to AniList OAuth (opens browser)
3. User approves → AniList redirects to our callback URL with code
4. POST /api/v1/sync/import/anilist { code, redirect_uri }
5. Backend exchanges code for access token
6. Backend fetches user's full MediaList via AniList GraphQL
7. For each entry:
   a. Look up anilist_id in media_external_ids → get our media_id
   b. If not found → trigger on-demand fetch → create media entry
   c. Upsert into user_list_entries with status, progress, score, dates
   d. Do NOT overwrite local notes or custom list membership
8. Return { imported: N, created: N, skipped: N }
```

## Error Recovery

If a backfill batch fails after max retries:
1. The failed AniList IDs are logged to `sync_jobs.error_log`
2. Entry `metadata_synced_at` remains NULL
3. Admin can re-trigger: `POST /api/v1/admin/sync/retry-failed`
4. Weekly refresh will also naturally pick up entries with NULL `metadata_synced_at`
