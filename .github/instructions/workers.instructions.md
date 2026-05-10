---
applyTo: "backend/workers/**"
---
# Sync Worker Copilot Instructions

Celery tasks must: use `bind=True`, `max_retries=3`, `acks_late=True`.
Include `autoretry_for=(httpx.TimeoutException, httpx.HTTPStatusError)`.
All tasks must be idempotent — safe to run twice without corrupting data.
Respect rate limits: AniList 80 req/min, MangaDex 4 req/s.
Per-item exceptions must not abort the whole batch — catch inside the loop.
Log to sync_jobs table: create row on start, update counts during, set final status on exit.
