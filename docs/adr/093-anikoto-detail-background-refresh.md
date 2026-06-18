# ADR 093 — Anikoto Detail Refresh Background Job

**Status**: Proposed
**Date**: 2026-06-18

## Context

The Anikoto full-catalog sync (`seed anikoto-full`) fetches the provider's list of
recent anime series, then for each series optionally fetches detail (episode list,
embed URLs, multilingual titles, etc.) via `/series/{id}`.  The Anikoto API enforces
a rate limit of **60 requests per 60-second window** (observed via
`X-RateLimit-Limit: 60`).  With 100 series per catalog page, fetching details for
all of them synchronously during the catalog sync is **slow** — at 55 req/60s,
100 detail calls take ~2 minutes per page, and the full catalog runs many pages.

Worse, the rate limiter adaptation bug (now fixed in ADR 093 implementation)
was permanently reducing the effective rate to as low as 2 req/120s, making
detail refresh effectively stall.

## Decision

**Separate the concerns:**

1. **Catalog sync** (`seed anikoto-full`) stores list-level data only — series
   IDs, titles, basic metadata, episode *counts*, and any embed URLs already
   present in the list response.  **No per-series `/series/{id}` calls during
   catalog sync.**

2. **Detail refresh** runs as a **Celery background task** that:
   - Picks `media_source_mappings` where `details_synced_at IS NULL`
     or `details_synced_at` is older than a configurable TTL (default 24 h).
   - Fetches `/series/{id}` for each, respecting a **dedicated, generous
     rate limiter** (e.g., 50 req/60s).
   - Updates `source_payload`, `source_titles`, `source_episodes`, and
     `details_synced_at` in batches.
   - Runs on a **periodic Celery Beat schedule** (e.g., every 6 hours).

This way the catalog sync completes in seconds per page, and the detail
fetch runs at a steady pace in the background without blocking anything.

## Detailed Design

### New Celery Task: `refresh_provider_details`

```
@celery_app.task(bind=True, max_retries=None, acks_late=True, rate_limit="60/m")
def refresh_provider_details(self, source: str = "anikoto", batch_size: int = 50) -> dict:
    """Fetch /series/{id} details for mappings where details are missing or stale."""
```

**Query** (per batch):

```sql
SELECT m.id, m.source_media_id
FROM media_source_mappings m
WHERE m.source = :source
  AND m.deleted_at IS NULL
  AND (m.details_synced_at IS NULL OR m.details_synced_at < :stale_cutoff)
  AND m.mapping_status IN ('matched', 'unmatched')
ORDER BY m.details_synced_at NULLS FIRST, m.last_seen_at DESC
LIMIT :batch_size
```

**Processing loop** (per mapping):
1. Call `client.get_series(source_media_id)` with the **dedicated** rate limiter.
2. Extract episodes via `_extract_detail()` / `_extract_episodes()`.
3. Upsert the mapping's `source_payload`, `source_titles`, `details_synced_at`.
4. Bulk-upsert episodes via `SourceEpisodeRepository.bulk_upsert_episodes()`.
5. Commit batch.

**Rate limiting**:
- A **separate** `AnikotoClient` instance is created per task invocation,
  with `rate_max=50`, `rate_window=60.0`, `min_requests=10`.
- This is independent of the catalog-sync client, so both can run concurrently
  without competing for tokens.
- Server-cap adaptation from `X-RateLimit-*` headers auto-restores after the
  window reset (as fixed in the RateLimiter refactor).

### Schedule (Celery Beat)

```python
# In celery_app.py
app.conf.beat_schedule = {
    "refresh-anikoto-details": {
        "task": "src.app.workers.sync_tasks.refresh_provider_details",
        "schedule": crontab(minute="*/30"),  # every 30 minutes while stale items exist
        "kwargs": {"source": "anikoto", "batch_size": 50},
    },
}
```

The 30-minute interval is deliberately short — the `LIMIT 50` controls how many
detail calls are made per run, so each run takes ~1 minute at 50 req/60s.
When no stale mappings remain, the query returns 0 rows and the task exits
quickly.

### New / Changed Files

| File | Change |
|------|--------|
| `workers/sync_tasks.py` | Add `refresh_provider_details` task |
| `workers/celery_app.py` | Add `beat_schedule` entry |
| `sync/sources/anikoto.py` | Add `threshold_seconds` param to control detail skip during catalog sync |
| `external/anikoto_client.py` | No change (reuses existing rate-limited client) |

### Default: Skip Details During Catalog Sync

The `AnikotoSourceAdapter` already has a `refresh_details` flag.  We change
the **default** for `seed anikoto-full` to `--no-refresh-details` so the
catalog sync is fast by default:

```python
# In the CLI command definition
refresh_details: bool = typer.Option(False, "--refresh-details", ...)
```

Users can still pass `--refresh-details` if they want the old inline behaviour
for debugging or small runs.

## Consequences

**Good**:
- Catalog sync completes in **seconds** per page instead of minutes.
- Detail fetch runs at a steady, rate-limit-friendly pace in the background.
- Rate limiter is **dedicated** to the detail task — no competition with catalog sync.
- If a detail fetch fails (timeout, 429), only that single item is retried next run.
- Users can see fresh catalog data immediately; details arrive asynchronously.

**Bad**:
- Detail data is not available *immediately* after catalog sync — there is a
  delay of up to 30 min for the first batch.
- Additional Celery task to monitor and maintain.

**Neutral**:
- The worker queue needs capacity for the periodic task.
- Old detail payloads are retained in `source_payload` JSONB until refreshed.
