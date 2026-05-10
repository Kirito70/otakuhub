# Phase 13.1 — Seed/Sync Inventory & Gap Analysis

**Date**: 2026-05-08  
**Scope**: Inventory existing seed/sync scripts and backend entrypoints before consolidation.

## Current Entry Points (Observed)

### Root-level scripts
- `scripts/seed_database.py`
  - Async placeholder script that downloads a JSON manifest and prints placeholder import logs.
  - Not integrated with repository/service-layer upsert rules.
  - Not suitable as canonical production seed pipeline.

### Backend CLI commands
- `backend/src/app/commands/seed.py`
  - `otakuhub seed run`
  - Uses `exec()` to run `scripts/seed_database.py` dynamically.
  - Couples backend command path to root script and bypasses structured service/task orchestration.

- `backend/src/app/commands/celery.py`
  - `otakuhub celery seed --batch-size <n>` → enqueues `sync.seed_database`
  - `otakuhub celery weekly-refresh` → enqueues `sync.weekly_refresh`
  - Notification commands exist and are unrelated to Phase 13 scope.

### Worker tasks
- `backend/src/app/workers/sync_tasks.py`
  - `sync.seed_database` (currently simulated placeholder result)
  - `sync.backfill_anilist_batch` (mixed async/sync misuse; placeholder logic)
  - `sync.weekly_refresh` (placeholder)
  - `sync.import_user_list` (placeholder)
  - `sync.process_new_episodes` (placeholder)

### Service layer
- `backend/src/app/services/sync_service.py`
  - Has `create_sync_job`, `update_sync_job`, `complete_sync_job`, and query helpers.
  - External sync methods (`sync_media_from_anilist`, `backfill_missing_metadata`, `update_or_create_media_from_anilist`) are placeholders / incomplete.

### API layer
- `backend/src/app/routes/sync.py`
  - User import endpoints create `sync_jobs` rows (`user_import_anilist`, `user_import_mal`).
  - Router enqueues/records intent but pipeline execution contracts are not fully consolidated.

### Existing architecture docs
- `docs/sync-pipeline.md`
  - Defines canonical pipeline stages, job-type naming, rate-limit strategy, and sync job audit expectations.
  - Current implementation does not yet fully satisfy these contracts.

## Duplication & Ownership Gaps

1. **Dual seed ownership**
   - Root script and backend CLI both represent seed entrypoints.
   - Backend command currently shells into root script instead of owning seed pipeline.

2. **Placeholder-heavy execution path**
   - Worker tasks and service methods return mocked/simulated behavior in several paths.

3. **Inconsistent async boundaries**
   - Celery tasks currently call async-oriented services/clients without robust async execution wrappers.

4. **No canonical shared orchestration module**
   - Missing single pipeline module for reusable source adapters (anime-offline, AniList, MangaDex, Jikan).

5. **Partial `sync_jobs` lifecycle coverage**
   - Job creation exists, but terminal state and structured error consistency are not guaranteed across all tasks.

## Missing Coverage vs Phase 13 Goals

- Missing per-source CLI commands under one backend-owned interface.
- Missing `seed all` orchestrator with ordered execution and optional resume/dry-run controls.
- Missing one shared ingestion/upsert layer used by both CLI and Celery.
- Missing source-specific Celery task parity and scheduler composition via same shared code.
- Missing test coverage validating idempotent re-runs and command/task parity.

## Proposed Consolidation Targets (for Phase 13.2+)

1. Introduce a backend-native sync orchestration package (single source of truth).
2. Rework CLI:
   - `otakuhub seed anime-offline`
   - `otakuhub seed anilist`
   - `otakuhub seed mangadex`
   - `otakuhub seed jikan`
   - `otakuhub seed all`
3. Rework Celery tasks to call same orchestration functions.
4. Standardize `sync_jobs` updates:
   - running → completed/partial/failed
   - structured JSON error payloads
5. Deprecate root script path with migration note + optional compatibility shim.
6. Add command tests + worker tests for parity and idempotency checks.

## 13.1 Exit Criteria Check

- [x] Inventory of root `scripts/` seed/sync files
- [x] Inventory of backend command entrypoints
- [x] Inventory of sync workers/services/routes
- [x] Duplication and ownership gaps documented
- [x] Forward plan for 13.2+ captured
