# ADR 078 — Source Provider ID Registry and Anime Playback Sync

**Status**: Proposed
**Date**: 2026-06-05

## Context

OtakuHub currently ingests anime and manga metadata through the Phase 3/13 sync pipeline:

1. `AnimeOfflineSeedAdapter` loads anime-offline-database and inserts base rows into `media_entries` plus a 1:1 `media_external_ids` row.
2. `AniListSeedAdapter` backfills canonical metadata by selecting `media_external_ids.anilist_id` and updating `media_entries`, genres, studios, tags, relations, and airing data.
3. `MangaDexSeedAdapter` enriches manga/manhwa titles when `media_external_ids.mangadex_id` exists.
4. `JikanSeedAdapter` supplements MAL-side metadata during weekly refresh.
5. Celery daily refresh currently chains AniList unsynced backfill and MangaDex detail; weekly refresh chains anime-offline seed, AniList refresh, MangaDex detail, and Jikan refresh.

`media_external_ids` is a static, one-row-per-media cross-reference table for canonical metadata identifiers. It already has columns such as `anilist_id`, `mal_id`, `mangadex_id`, `anidb_id`, and `kitsu_id`. This works for stable metadata providers, but it does not scale to playback/source providers because:

- each provider can have its own series ID, episode IDs, language variants, availability status, and freshness timestamps;
- adding one column per future source would require repeated table changes;
- playback availability is not the same concern as canonical metadata identity;
- some providers expose episode-level IDs, not just series-level IDs.

The urgent new source is MegaPlay/Anikoto:

- MegaPlay API docs state that catalog discovery should use Anikoto, base URL `https://anikotoapi.site`.
- Anikoto endpoints documented on 2026-06-05:
  - `GET /recent-anime?page=1&per_page=20`
  - `GET /series/{id}`
- Anikoto returns recent anime, series details, and episode rows containing `episode_embed_id` / embed URL hints.
- MegaPlay playback docs expose embed URL patterns using Anikoto/legacy HiAnime episode IDs, MAL IDs, or AniList IDs.
- Anikoto rate limit: 60 requests per IP every 120 seconds; backend-only usage is explicitly recommended.

Security/compliance note: MegaPlay/Anikoto positions itself as a hosted playback/embed service. OtakuHub may store provider catalog IDs and availability metadata for future integrations, but implementation must not scrape protected raw media URLs or bypass embed restrictions. Frontend must never call Anikoto/MegaPlay directly. Any production playback resolver must be separately reviewed for provider terms, copyright posture, domain allow-listing, and event-origin validation.

## Project Status check

To check status of the project and know about its phase always refer to PROJECT-STATUS.md file at root of the project and once phase or sub phase is completed always update the project status.

Current project state on 2026-06-05: Audit Phase 6 is complete. This ADR creates an urgent pre-audit feature design before moving to the next audit phase.

## Decision

### 1. Keep `media_external_ids` canonical and add source-provider registry tables

Do **not** add an unbounded set of playback columns to `media_external_ids`.

Instead, introduce a normalized provider registry:

1. `media_source_mappings` — one row per media title per external source/provider.
2. `media_source_episodes` — one row per provider episode/language variant, optionally linked to our canonical `episodes` row.

`media_external_ids` remains the canonical cross-reference table for metadata providers where AniList ID remains the primary matching key. New stable metadata columns can still be added there when a provider is globally useful, but playback/source availability belongs in the new source registry.

### 2. Source naming

Use explicit source names:

| Source | Meaning |
|--------|---------|
| `anime-offline` | Seed metadata source |
| `anilist` | Canonical metadata source |
| `mangadex` | Manga/chapter metadata source |
| `jikan` | MAL supplement source |
| `anikoto` | Catalog/series/episode ID source for MegaPlay-compatible anime playback |
| `megaplay` | Playback/embed provider that consumes Anikoto/MAL/AniList IDs |

Anikoto and MegaPlay are deliberately separate because Anikoto is the catalog API while MegaPlay is the embed/playback host.

### 3. Matching strategy for Anikoto catalog sync

Anikoto list rows may not always include AniList/MAL IDs. The matching strategy is ordered:

1. If Anikoto detail includes AniList ID, match `media_external_ids.anilist_id`.
2. Else if it includes MAL ID, match `media_external_ids.mal_id`.
3. Else match normalized title + media type + year using conservative fuzzy rules; mark confidence in `media_source_mappings.match_confidence`.
4. If confidence is below threshold, create an unmapped `media_source_mappings` row with `media_id = NULL` and `mapping_status = 'unmatched'`; do **not** create duplicate `media_entries` unless a canonical AniList search confirms it.

AniList remains canonical; Anikoto should never replace AniList metadata when both exist. Anikoto can fill playback availability and provider-specific episode IDs.

### 4. Sync jobs

Add two provider sync paths:

1. `anikoto_full_catalog`
   - One-time/admin-triggered backfill.
   - Pages through `/recent-anime` or equivalent catalog pages until exhausted.
   - For each series ID, calls `/series/{id}` to capture detail and episodes.
   - Upserts into `media_source_mappings` and `media_source_episodes`.

2. `anikoto_recent_refresh`
   - Daily job.
   - Pages only recent anime, bounded by configured page count / last seen timestamp.
   - Refreshes details for recently changed series.
   - Updates `last_seen_at`, `details_synced_at`, episode availability, and stale/missing flags.

Hook `anikoto_recent_refresh` into `sync.daily_refresh_compose` after canonical AniList/MangaDex jobs. Weekly refresh may also enqueue a broader Anikoto refresh if provider rate limits allow.

### 5. API client and service boundaries

- `external/anikoto_client.py` owns HTTP calls, rate limiting, response parsing, timeouts, and 429/403 handling.
- `external/megaplay_client.py` owns safe MegaPlay embed path/url construction from Anikoto `episode_embed_id` values.
- `sync/sources/anikoto.py` owns paging, detail retrieval, and transforming source payloads into source mapping DTOs.
- repository layer owns source mapping/episode upserts.
- service layer owns matching policy, confidence thresholds, and orchestration between `media_external_ids`, `media_entries`, and source tables.
- Celery worker owns scheduling, retries, and `sync_jobs` progress.
- routers only enqueue admin jobs and expose status; they never call Anikoto/MegaPlay synchronously.

### 6. Playback boundary for future work

For this phase, store IDs and availability only. Do not expose public playback endpoints yet.

Future playback should be a separate ADR/API contract, but if enabled it must:

- resolve by our `media_id` + episode number + language;
- choose a provider from `media_source_episodes`;
- return an embeddable provider URL only for configured/approved domains;
- never proxy raw media segments or bypass provider embed controls;
- validate `postMessage` events by origin (`https://megaplay.buzz`) before watch-progress updates.

### 7. Layer Boundary Spec

**Router owns**
- Admin-only enqueue endpoints for full/recent Anikoto sync jobs.
- Request validation for bounded `per_page`, `max_pages`, `refresh_details`, and `dry_run` inputs.
- Auth/authorization via existing admin dependencies.
- Returning typed job enqueue/status responses.
- Never performs external HTTP calls or DB upserts inline.

**Service owns**
- Provider matching policy: AniList ID → MAL ID → conservative normalized-title/year match → unmatched row.
- Match confidence thresholds and status transitions (`matched`, `unmatched`, `ignored`, `stale`).
- Orchestration between `media_external_ids`, `media_entries`, `media_source_mappings`, and `media_source_episodes`.
- Sync job lifecycle updates, including terminal status and structured errors.
- Does not own raw HTTP details or frontend presentation.

**Repository owns**
- QueryBuilder-backed reads for source mappings/episodes.
- Idempotent upserts using `(source, source_media_id)` and `(source, source_episode_id, language)` conflict keys.
- Soft-delete/stale filtering for source mappings and episodes.
- No matching business rules beyond applying provided fields.

**Worker/external owns**
- `external/anikoto_client.py`: HTTP client, base URL, rate limiter, pagination/detail request helpers, 429/403/timeout handling.
- `sync/sources/anikoto.py`: full/recent run modes, paging loop, detail-fetch loop, DTO normalization.
- `external/megaplay_client.py`: builds `/stream/s-2/{episode_embed_id}/{language}` paths and validates stored embed paths against `megaplay.buzz` only.
- Celery tasks: retries, queue routing, daily composition integration, and progress checkpoints.

**Flutter/Quasar state shape**
- No user-facing playback state is introduced in this ADR.
- Future admin UI may track:
  - `sourceMappings.items: SourceMapping[]`
  - `sourceMappings.filters: { source?: string; mappingStatus?: string; mediaId?: string }`
  - `sourceMappings.isLoading: boolean`
  - `sourceMappings.error: string | null`
  - `sourceMappings.actionState: Record<string, 'idle' | 'loading' | 'success' | 'error'>`
- Future playback UI state must be defined by a separate playback ADR before implementation.

## Consequences

**Good**:
- Future-proof source/provider ID storage without repeated `media_external_ids` migrations.
- Supports both series-level and episode-level provider IDs.
- Keeps AniList as canonical cross-reference and avoids provider-specific metadata overwriting canonical data.
- Allows Anikoto/MegaPlay sync to be backend-only and rate-limited.
- Makes unmatched provider titles visible for manual reconciliation instead of creating duplicates.

**Bad**:
- Adds schema and repository complexity compared with simply adding `anikoto_id` and `megaplay_id` columns.
- Requires matching logic and confidence tracking for provider rows without AniList/MAL IDs.
- Requires compliance review before any playback UI/API is shipped.

**Neutral**:
- `media_external_ids` remains 1:1 with `media_entries`; provider mapping tables are 0:N.
- Daily refresh grows by one external API dependency and must respect Anikoto's 60 requests / 120 seconds limit.
