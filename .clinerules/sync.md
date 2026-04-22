---
paths:
  - "backend/workers/**"
  - "backend/external/**"
  - "scripts/**"
---
# Sync Pipeline Rules

## Celery Task Requirements
- Every task: `bind=True`, `max_retries=3`, `acks_late=True`
- `autoretry_for` must include at minimum: `httpx.TimeoutException`, `httpx.HTTPStatusError`
- Tasks must be idempotent — safe to run twice on the same data
- Use `ON CONFLICT DO NOTHING` or `ON CONFLICT DO UPDATE` for all DB inserts
- Never hard-fail a whole batch because of one bad entry — wrap per-item logic in try/except

## Rate Limiting
- AniList: max 80 req/min (token bucket in Redis, key `anilist:rate_limit`)
- MangaDex: max 4 req/s (asyncio.sleep(0.25) between calls)
- MAL: max 0.8 req/s (asyncio.sleep(1.25))
- Always respect `Retry-After` header on 429 responses

## External API Client Rules
- All clients in `backend/external/` — never in workers or routers directly
- Clients return typed Pydantic models — never raw dicts to callers
- Clients raise typed exceptions: `AniListRateLimitError`, `MangaDexError`, etc.
- Log every external API call at DEBUG level with URL and response code

## Sync Job Logging
- Create a `sync_jobs` row at the start of every batch job
- Update `processed_items` and `failed_items` as the job runs
- Set `status = 'completed'` or `status = 'failed'` on exit
- On failure: append to `error_log` JSON array with the failed ID + error message
