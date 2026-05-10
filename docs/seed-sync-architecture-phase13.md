# Phase 13.2 — Unified Backend Seed/Sync Architecture Spec

**Date**: 2026-05-08  
**Status**: Proposed (implementation target for Phase 13.3+)

## Context

Phase 13.1 confirmed current seed/sync execution is split across:
- root script (`scripts/seed_database.py`),
- backend CLI wrappers,
- placeholder Celery tasks,
- partially implemented service methods.

This creates duplicate ownership, weak observability consistency, and non-unified async execution.

## Decision Summary

Adopt a **single backend-owned orchestration module** that is reused by both:
1. CLI commands (`otakuhub seed ...`) and
2. Celery tasks (`sync.*`).

No root-level seed logic remains canonical after consolidation.

---

## Target Module Layout

Create a backend package dedicated to seed/sync orchestration:

```
backend/src/app/sync/
├── orchestrator.py         # shared orchestration entrypoints
├── job_runner.py           # sync_jobs lifecycle helpers
├── types.py                # typed payload/result/error models
├── sources/
│   ├── anime_offline.py    # seed source adapter
│   ├── anilist.py          # metadata backfill adapter
│   ├── mangadex.py         # chapters/detail adapter
│   └── jikan.py            # supplemental adapter
└── upsert/
    ├── media.py            # media_entries/media_external_ids upsert rules
    ├── relations.py        # tags/genres/studios/related entities
    └── tracking_import.py  # user list import upsert logic (read-only external)
```

> Note: exact filenames can vary, but one shared module must be reused by CLI + Celery.

---

## Canonical Job Types

Use the values already documented in `docs/sync-pipeline.md`:

- `seed`
- `backfill_anilist`
- `mangadex_detail`
- `weekly_refresh`
- `user_import_anilist`
- `user_import_mal`

No ad-hoc aliases in persisted `sync_jobs.job_type`.

---

## CLI Contract (Phase 13.3/13.4)

Replace `seed run` root-script execution path with backend-native commands:

- `otakuhub seed anime-offline [--batch-size N] [--dry-run]`
- `otakuhub seed anilist [--limit N] [--only-unsynced]`
- `otakuhub seed mangadex [--limit N]`
- `otakuhub seed jikan [--limit N]`
- `otakuhub seed all [--dry-run] [--resume-job-id <uuid>]`

### Execution rules
- Commands call orchestrator functions directly (no `exec` of root scripts).
- Command output includes processed/failed counts and terminal status.
- `seed all` executes ordered pipeline stages and supports safe resume behavior.

---

## Celery Contract (Phase 13.6/13.7)

Each Celery task must call the same orchestrator methods used by CLI.

Required task names (or close equivalents preserving queue contracts):
- `sync.seed_database`
- `sync.backfill_anilist`
- `sync.mangadex_detail`
- `sync.weekly_refresh`
- `sync.import_user_list`

### Queueing
- Sync tasks routed to `sync` queue.
- Notifications remain separate in `notifications` queue.

### Scheduling
- Beat schedule should invoke orchestration-backed tasks only.
- No duplicate “special-case” logic in scheduler layer.

---

## `sync_jobs` Lifecycle & Observability Rules

Centralize in `job_runner.py` helpers so all command/task paths are consistent:

1. `start_job(...)` → creates `sync_jobs` row with `status='running'`.
2. `progress(...)` → updates `processed_items`, `failed_items` at batch boundaries.
3. `finish_completed(...)` → terminal `completed` + `completed_at`.
4. `finish_partial(...)` → terminal `partial` + structured error payload.
5. `finish_failed(...)` → terminal `failed` + structured error payload.

### Error payload format
Persist JSON text in `error_log`:

```json
[
  {
    "item": "<external-or-local-id>",
    "source": "anilist|mangadex|jikan|anime_offline|mal",
    "error": "<message>"
  }
]
```

---

## Upsert / Idempotency Strategy

All stages must be rerunnable safely:
- Use `anilist_id` as canonical cross-reference conflict key where available.
- Never duplicate `media_external_ids` rows for same external identifier.
- Metadata updates must set `media_entries.metadata_synced_at` on success.
- User import remains read-only external integration (no write-back to providers).

---

## Layer Boundaries (for this feature)

### Router
- Creates/import triggers only (already present in `/sync/import/...`).
- No external API calls or long-running sync logic.

### Service
- Coordinates orchestration invocation and high-level business constraints.
- May validate user permissions and invoke Celery enqueue paths.

### Repository / DB access
- Upsert/retrieval helpers are used by orchestration modules.
- QueryBuilder usage for read paths; direct writes for create/update/soft-delete patterns.

### Worker
- Owns rate-limited external API calls, retries, batching, and job progress persistence.

### Frontend state shape impact
- No immediate frontend schema changes for Phase 13.2.
- Existing sync job responses should remain backward compatible (`job_id`, `status`, `job_type`).

---

## Security & Reliability Considerations

- No secret/token values may be written into `error_log`.
- External API failures should be sanitized before persistence.
- Keep user-import operations scoped to authenticated user context.
- Avoid loading full 29k+ media records into memory; process in bounded batches.

---

## Migration/Deprecation Plan

1. Introduce new sync package and orchestrator entrypoints.
2. Rewire `commands/seed.py` to backend-native orchestration.
3. Rewire `workers/sync_tasks.py` to same orchestrator.
4. Deprecate root `scripts/seed_database.py` with migration note.
5. Keep temporary compatibility shim only if CI/dev workflow still references old path.

---

## Verification Plan (maps to 13.10)

- Command tests:
  - per-source command execution
  - `seed all` ordering
  - dry-run behavior
- Task tests:
  - each sync task invokes orchestrator
  - terminal status (`completed`, `partial`, `failed`) correctness
- Idempotency tests:
  - repeated seed/backfill runs do not duplicate rows
  - `media_external_ids` uniqueness maintained

---

## 13.2 Exit Criteria Check

- [x] Unified architecture defined for backend seed/sync ownership
- [x] CLI + Celery reuse contract documented
- [x] `sync_jobs` lifecycle and error format standardized
- [x] Layer boundaries and security implications captured
- [x] Clear implementation path for 13.3+ documented
