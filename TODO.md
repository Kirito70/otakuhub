# Phase 1.5 & 1.6 — Sync Pipeline Real Data Ingestion

## Phase 1.5 — De-stub SyncService
- [x] `sync_media_from_anilist()` — Call `AniListSeedAdapter().run()` with proper `SeedExecutionContext`
- [x] `backfill_missing_metadata()` — Use adapters based on media type/external IDs
- [x] `update_or_create_media_from_anilist()` — Real upsert logic with _parse_item helper
- [x] Test: sync_media_from_anilist happy path + failure
- [x] Test: backfill_missing_metadata with anilist/mangadex adapters + not found
- [x] Test: update_or_create_media_from_anilist create + update paths

## Phase 1.6 — Implement Worker Tasks
- [x] `import_user_list_task()` — Create sync_job, add proper framework + logging
- [x] `process_new_episodes_task()` — Query recent episodes/chapters, notification skeleton
- [x] Test: import_user_list_task creates sync_job and returns correct shape
- [x] Test: process_new_episodes_task returns counts and correct shape
