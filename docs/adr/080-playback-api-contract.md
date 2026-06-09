# ADR 080 — Playback API & Episode Resolution Contract

**Status**: Proposed
**Date**: 2026-06-08

## Context

OtakuHub has source provider data (Anikoto catalog, MegaPlay embed URLs) stored in `media_source_mappings` and `media_source_episodes`, but there is **no user-facing API** for the frontend to discover available sources, episodes, or embed URLs for a given media title. The frontend currently has:

- `GET /api/v1/media/{media_id}` — returns basic media metadata (no sources)
- `GET /api/v1/media/{media_id}/relations` — returns related media
- `GET /api/v1/media/{media_id}/episodes` — **does not exist**
- `GET /api/v1/media/{media_id}/chapters` — **does not exist**

To build a streaming playback UI, the frontend needs endpoints that return:
1. Which streaming sources/mirrors are available for a media title
2. Which episodes exist from each source (with embed URLs)
3. The canonical episode list (from our `episodes` table)
4. Episode playback resolution (return a safe embed URL for a specific episode)

## Decision

### 1. New endpoints

All under `/api/v1/media/`:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/media/{media_id}/episodes` | Canonical episode list (from `episodes` table, ordered by number) |
| `GET` | `/media/{media_id}/chapters` | Canonical chapter list (from `chapters` table, ordered by number) |
| `GET` | `/media/{media_id}/sources` | Available provider source mappings (Anikoto, MegaPlay) |
| `GET` | `/media/{media_id}/episodes/sources` | All episodes from all providers, grouped or flat, with embed URLs |

### 2. Response schemas

#### `GET /api/v1/media/{media_id}/episodes`

```typescript
interface EpisodeResponse {
  id: string                    // UUID
  episode_number: number
  title: string | null
  air_date: string | null       // ISO datetime
  duration_minutes: number | null
  thumbnail_url: string | null
}
```

#### `GET /api/v1/media/{media_id}/sources`

```typescript
interface SourceResponse {
  id: string                    // mapping UUID
  source: string                // "anikoto", "megaplay", etc.
  source_title: string | null
  mapping_status: string        // "matched", "unmatched", etc.
  match_confidence: number
  is_streaming_enabled: boolean
  has_sub: boolean
  has_dub: boolean
  episode_count: number | null
  episode_list: SourceEpisodeItem[]
}

interface SourceEpisodeItem {
  id: string                    // episode UUID
  episode_number: number
  title: string | null
  language: string              // "sub" | "dub"
  embed_url: string | null      // safe MegaPlay embed URL, never raw media
  is_available: boolean
}
```

#### `GET /api/v1/media/{media_id}/episodes/sources` (consolidated)

```typescript
interface ConsolidatedEpisodeSource {
  episode_number: number
  canonical_title: string | null    // title from episodes table
  canonical_air_date: string | null
  sources: {
    source: string
    language: string
    embed_url: string | null
    is_available: boolean
  }[]
}
```

### 3. Auth requirements

All four endpoints require JWT auth (`Depends(get_current_user)`). This is consistent with the existing media endpoints.

### 4. Rate limiting

- Standard media endpoint rate limit applies (no external API calls — reads from DB only)
- No rate limit concerns — all data is pre-synced by the background Celery pipeline

### 5. Embed URL safety

`embed_url` is always an **HTML page embed URL** (`https://megaplay.buzz/stream/s-2/{id}/sub`), never a raw media segment URL (`.m3u8`, `.mp4`, etc.). The backend `MegaPlayEmbedResolver.safe_embed_url()` validator is applied before storage.

### 6. Layer Boundary Spec

**Router** (`routes/media.py`)
- Add four new GET routes under existing `/api/v1/media/` prefix
- Validate `media_id` UUID format, return 404 if media not found
- Delegate to `MediaService` for canonincal episodes/chapters
- Delegate to new `SourceProviderService` for source/episode data

**Service** (new: `services/source_provider_service.py`)
- `get_sources_for_media(media_id)` → query `SourceMappingRepository` + `SourceEpisodeRepository`, group results
- `get_consolidated_episodes(media_id)` → merge episodes table with source episodes, deduplicate by number, prefer highest-confidence source
- `get_episodes_for_media(media_id)` → canonical episodes from episodes repo

**Repository** (existing: `repositories/source_provider_repository.py`)
- Already has `SourceMappingRepository.list_by_source()` and `SourceEpisodeRepository.list_for_mapping()`
- Add: `get_mappings_by_media(media_id)` — find all non-deleted mappings for a media entry

## Consequences

**Good**:
- Frontend has everything needed to build an episode selector + player
- Consolidated endpoint avoids N+1 queries from frontend
- No breaking changes to existing APIs
- Background sync makes this a read-only fast path

**Bad**:
- Adds surface area to the media router
- Consolidated episode merging logic is moderately complex (matching source episodes to canonical episodes by number)

**Neutral**:
- Existing `SourceEpisodeUpsert` schema remains unchanged
- Metadata sync jobs continue to populate source tables independently
