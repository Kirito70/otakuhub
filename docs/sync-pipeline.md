# OtakuHub — Sync Pipeline Architecture

## Overview
The sync pipeline populates and maintains the local anime/manga database
by pulling from three external sources: anime-offline-database (seed),
AniList GraphQL (primary metadata), and MangaDex REST (manga detail).

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
```

## Rate Limits Reference

| API | Limit | Our target | Strategy |
|-----|-------|-----------|----------|
| AniList GraphQL | 90 req/min | 80 req/min | Redis token bucket; batch 50 IDs/query |
| MangaDex REST | ~5 req/s global | 4 req/s | asyncio.sleep(0.25) between calls |
| MAL API v2 | ~1 req/s (unofficial) | 0.8 req/s | Sleep 1.25s between calls |
| Jikan v4 | 60 req/min | 50 req/min | Token bucket |

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

# direct seed script path (non-celery)
uv run otakuhub seed run
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
    # Every Sunday at 02:00 UTC
    "weekly-refresh": {
        "task": "workers.sync_tasks.weekly_refresh",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
    },
    # Every 6 hours — keep airing schedule current
    "refresh-airing": {
        "task": "workers.sync_tasks.refresh_airing_schedule",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    # Daily at 03:00 — clean old read notifications
    "cleanup-notifications": {
        "task": "workers.cleanup_tasks.purge_old_notifications",
        "schedule": crontab(hour=3, minute=0),
    },
    # Daily at 03:30 — revoke expired refresh tokens
    "cleanup-tokens": {
        "task": "workers.cleanup_tasks.purge_expired_tokens",
        "schedule": crontab(hour=3, minute=30),
    },
}
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
