---
name: sync-pipeline
description: Build or extend a Celery worker for the AniList/MangaDex data sync pipeline. Covers seed, backfill, weekly refresh, and user list import tasks.
---

# Sync Pipeline Skill

## Pipeline Overview
```
anime-offline-database JSON
        ↓  (seed worker — one-time)
media_entries + media_external_ids (bare metadata)
        ↓  (backfill worker — Celery batch tasks)
Full AniList metadata: titles, synopsis, genres, studios, tags, cover images
        ↓  (manga detail worker — for manga/manhwa only)
MangaDex chapter data, cover art
        ↓  (weekly cron — every Sunday 02:00 UTC)
Diff new entries + refresh 'releasing' status titles
        ↓  (on-demand — user search miss)
Live AniList search → upsert into DB
```

## Celery Worker Pattern
```python
# backend/workers/sync_tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(httpx.TimeoutException, httpx.HTTPStatusError),
    acks_late=True,           # acknowledge only after success (no-loss on restart)
)
async def backfill_anilist_batch(self, anilist_ids: list[int]) -> dict[str, int]:
    """Fetch full metadata for a batch of up to 50 AniList IDs."""
    logger.info(f"Backfilling {len(anilist_ids)} entries, task {self.request.id}")
    try:
        async with get_db_session() as db:
            results = await anilist_client.fetch_media_batch(anilist_ids)
            count = 0
            for item in results:
                await media_repository.upsert_from_anilist(db, item)
                count += 1
            await db.commit()
        return {"processed": count, "task_id": self.request.id}
    except AniListRateLimitError as e:
        raise self.retry(countdown=int(e.retry_after) + 5)
```

## AniList Batch GraphQL Query
Fetch 50 IDs in one request — key to staying within the 90 req/min limit:
```python
BATCH_QUERY = """
query BatchMedia($ids: [Int], $page: Int) {
  Page(page: $page, perPage: 50) {
    media(id_in: $ids) {
      id
      title { romaji english native }
      type format status
      description(asHtml: false)
      coverImage { large medium }
      bannerImage
      episodes chapters volumes
      duration
      averageScore popularity trending
      startDate { year month day }
      endDate { year month day }
      season seasonYear
      countryOfOrigin isAdult
      genres
      tags { name rank isMediaSpoiler isAdult }
      studios(isMain: true) { nodes { id name } }
      relations { edges {
        relationType(version: 2)
        node { id }
      }}
      nextAiringEpisode { episode airingAt }
      airingSchedule(notYetAired: true, perPage: 25) {
        nodes { episode airingAt }
      }
    }
  }
}
"""
```

## Rate Limiter (Redis token bucket)
```python
class AniListRateLimiter:
    """Enforces 80 req/min — 10% buffer under AniList's 90 req/min limit."""
    KEY = "anilist:rate_limit"
    LIMIT = 80
    WINDOW = 60  # seconds

    async def acquire(self, redis: Redis) -> None:
        count = await redis.incr(self.KEY)
        if count == 1:
            await redis.expire(self.KEY, self.WINDOW)
        if count > self.LIMIT:
            ttl = await redis.ttl(self.KEY)
            logger.warning(f"AniList rate limit hit, sleeping {ttl}s")
            await asyncio.sleep(ttl + 0.5)
```

## Seed Script Entry Point
```bash
# One-time seed at initial deployment
python -m scripts.seed_anime_db

# Trigger full AniList backfill (runs as background Celery tasks)
python -m scripts.trigger_backfill

# Weekly refresh (also scheduled via Celery Beat)
python -m scripts.weekly_refresh --dry-run
```

## Celery Beat Schedule (`backend/core/celery_config.py`)
```python
beat_schedule = {
    "weekly-refresh": {
        "task": "workers.sync_tasks.weekly_refresh",
        "schedule": crontab(hour=2, minute=0, day_of_week="sunday"),
    },
    "cleanup-old-notifications": {
        "task": "workers.cleanup_tasks.purge_read_notifications",
        "schedule": crontab(hour=3, minute=0),  # daily
    },
    "refresh-airing-episodes": {
        "task": "workers.sync_tasks.refresh_airing_schedule",
        "schedule": crontab(hour="*/6"),   # every 6 hours
    },
}
```

## Error Handling Rules
1. AniList 429 → read `Retry-After` header → `self.retry(countdown=retry_after)`
2. MangaDex 429 → backoff 30 seconds
3. Any 5xx → retry up to 3 times with exponential backoff (60, 120, 240 seconds)
4. Network timeout → retry immediately once, then exponential
5. A single failed entry must NEVER abort the whole batch — use try/except per item
6. After max retries → log to `sync_jobs` table with `status='failed'` + error details
7. Send Apprise alert for any task that exhausts retries
