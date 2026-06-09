# ADR 086 — Admin Source Provider UI

**Status**: Proposed
**Date**: 2026-06-08

## Context

The admin backend has full Celery task support for Anikoto sync (full/recent catalog, detail refresh, MegaPlay availability verification) but **no frontend UI** to:
- Trigger sync jobs
- View job status and results
- Browse source mappings and their match status
- Manually reconcile unmatched mappings
- View per-media source availability

Currently the admin must use `curl` or direct Celery task calls. For a private friend-group app, a simple admin panel is sufficient — no need for a full dashboard system.

## Decision

### 1. Admin page: `AdminSourceProviderPage.vue`

Location: `frontend/src/pages/admin/AdminSourceProviderPage.vue`

Simple single-page admin panel with sections:

```
┌─────────────────────────────────────────────────────┐
│  Admin — Source Provider Sync                        │
│                                                      │
│  ┌─ Sync Controls ────────────────────────────────┐  │
│  │  [Trigger Full Anikoto Sync]  [pages: 20 ▾]   │  │
│  │  [Trigger Recent Refresh]    [pages: 5 ▾]     │  │
│  │  [MegaPlay Verify]                             │  │
│  │  Status: Last full sync: never                 │  │
│  │          Last recent: 2026-06-07 01:30 UTC     │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Recent Sync Jobs ─────────────────────────────┐  │
│  │  Job ID | Type | Status | Items | Date          │  │
│  │  ─────────────────────────────────────          │  │
│  │  abc123 | full   | ✅ completed | 42  | 06-07  │  │
│  │  def456 | recent | ✅ completed | 12  | 06-08  │  │
│  │  ghi789 | verify | 🔄 running   | —   | 06-08  │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Unmatched Mappings ───────────────────────────┐  │
│  │  Source Title     | Provider  | Confidence      │  │
│  │  ─────────────────────────────────────          │  │
│  │  "Some Anime"     | anikoto   | 0% — unmatched  │  │
│  │  [Search on AniList] [Ignore] [Remove]          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2. API endpoints needed

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/admin/sync/providers/anikoto/full` | Existing |
| `POST` | `/admin/sync/providers/anikoto/recent` | Existing |
| `POST` | `/admin/sync/providers/megaplay/verify` | Existing |
| `GET` | `/admin/sync/jobs` | Existing |
| `GET` | `/admin/sync/jobs/{job_id}` | Existing |
| `GET` | `/admin/source-mappings` | **New** — list all source mappings with filters |
| `GET` | `/admin/source-mappings/unmatched` | **New** — list unmatched mappings only |
| `PATCH` | `/admin/source-mappings/{id}` | **New** — manually set media_id, status, confidence |

### 3. New endpoint: List source mappings

```typescript
// GET /admin/source-mappings?source=anikoto&status=unmatched&limit=50&offset=0
interface AdminSourceMappingResponse {
  id: string
  media_id: string | null
  media_title: string | null          // joined from media_entries for matched
  source: string
  source_media_id: string
  source_title: string | null
  mapping_status: string
  match_confidence: number
  has_sub: boolean
  has_dub: boolean
  episode_count: number | null
  last_seen_at: string
  created_at: string
}
```

### 4. New endpoint: Update source mapping

```typescript
// PATCH /admin/source-mappings/{id}
interface AdminUpdateMappingRequest {
  media_id?: string | null      // Set to match to a media entry
  mapping_status?: string       // "matched", "unmatched", "ignored"
  match_confidence?: number     // 0.00–100.00
}

// Response: updated AdminSourceMappingResponse
```

### 5. Layer boundaries

**Router** (new: `routes/admin_source.py` or extend `routes/admin.py`)
- New GET/PATCH endpoints under `/admin/source-mappings`
- Require admin auth

**Service** (extend: `services/sync_service.py`)
- `list_source_mappings(filters)` — delegate to SourceMappingRepository
- `update_source_mapping(id, payload)` — update media_id, status, confidence
- `get_unmatched_mappings()` — filter by `mapping_status='unmatched'`

**Repository** (extend: `repositories/source_provider_repository.py`)
- Add `list_mappings(filters)` with pagination and status filtering
- Already has `upsert` method, add explicit `update` method

### 6. Source mapping reconciliation workflow

When a mapping is unmatched (confidence = 0, no media_id):

1. Admin sees the mapping in the "Unmatched Mappings" section
2. Admin clicks "Search on AniList" → opens a search dialog that queries `GET /media/search?q={title}`
3. Admin selects the correct media entry from search results
4. Admin clicks "Match" → `PATCH /admin/source-mappings/{id}` with `media_id` set
5. Mapping status updated to `matched`, confidence set to `100.00`
6. Sync task will re-fetch and update episodes for this media next time it runs

### 7. Testing contract

- `AdminSourceProviderPage.test.ts`: rendering, sync job status display, trigger buttons disabled states, unmatched mapping list, search dialog for reconciliation
- `admin_list_source_mappings.test.py`: filter by source/status, pagination, verify joined media_title
- `admin_update_source_mapping.test.py`: verify media_id update, status change, confidence change, 404 for unknown mapping

## Consequences

**Good**:
- Admin can see and fix unmatched mappings without SQL queries
- Simple reconciliation workflow keeps the sync pipeline accurate over time
- Reuses existing admin/auth infrastructure

**Bad**:
- Adds frontend admin surface area (new page, new route, new component)
- Manual reconciliation required for mismatched titles — but this is infrequent

**Neutral**:
- No new backend models needed — all data already exists
- The admin page can be expanded later with more sync controls
