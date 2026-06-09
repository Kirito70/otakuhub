# ADR 082 — Media Detail Page: Streaming-First Redesign

**Status**: Proposed
**Date**: 2026-06-08

## Context

The current `MediaDetailPage.vue` is a basic card layout: cover image left, metadata right, synopsis below, and an "Add to List" button. It has no episode list, no play button, and no source provider awareness. Compare with aniwave-style detail pages which feature:

- Full-width hero banner with gradient overlay
- Large cover image as part of the hero
- Prominent "Play" / "Watch Now" CTA
- Episode grid with sub/dub badges and air dates
- Related media carousel at bottom
- Quick-access to add to list / change status

The media detail page is the single most important page for a streaming platform — it's where users discover episodes, start watching, and manage their progress.

## Decision

### 1. New page layout: `MediaDetailPage.vue` (rewritten)

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │           Hero Banner (gradient overlay)      │   │
│  │  ┌────┐  Title (romaji / english / native)    │   │
│  │  │    │  Type • Format • Status • Score       │   │
│  │  │cover│  ┌───┐ ┌───┐ ┌───┐ ┌───┐           │   │
│  │  │    │  │Play│ │+List│ │Like│ │Share│        │   │
│  │  └────┘  └───┘ └───┘ └───┘ └───┘           │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Tab bar: Episodes | Info | Related           │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Episodes Tab (default, active)               │   │
│  │                                               │   │
│  │  Server Selector: [Anikoto#1] [Anikoto#2]    │   │
│  │  Language: [SUB] [DUB]                       │   │
│  │                                               │   │
│  │  ┌────────────────────────────────────────┐  │   │
│  │  │  1 │ Title of Episode 1  │ SUB │ Air   │  │   │
│  │  │  2 │ Title of Episode 2  │ SUB │ Air   │  │   │
│  │  │  3 │ Title of Episode 3  │ SUB│ No date│  │   │
│  │  │ ...                                       │  │
│  │  └────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Info Tab                                      │   │
│  │  Synopsis (expandable)                         │   │
│  │  Genres, Studios, Tags                         │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Related Tab                                   │   │
│  │  [Sequel Card] [Prequel Card] [Side Story]    │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 2. Hero banner component

`components/anime/HeroBanner.vue`

- Full-width, 40vh tall on desktop, 25vh on mobile
- Background: `banner_image` from media entry (if null, use cover_image_large blurred)
- Gradient overlay: `linear-gradient(to top, #0a0a0a 0%, transparent 60%, rgba(10,10,10,0.8) 100%)`
- Cover art: left-aligned, 200×300px, with subtle box-shadow glow
- Title: white, stacked (romaji primary, english secondary, native tertiary in muted)
- Metadata row: Type badge, Format badge, Status badge, Score ring
- Action buttons row: Play (primary, large), Add to List (secondary), Like/Bookmark (icon)
- Score ring: custom CSS circular indicator, color-coded by value (green > 7, yellow > 5, red < 5)

### 3. Episode list component

`components/anime/EpisodeList.vue`

- Server selector bar at top (language toggle + available server mirrors)
- Episodes fetch from `GET /api/v1/media/{id}/episodes/sources` (ADR 080)
- Each episode row shows: number, title, language badge (SUB/DUB), air date, play button
- Play button disabled if `is_available === false` with tooltip
- Current progress indicator: episodes before user progress shown as "watched" (dimmed + check icon)
- Responsive: grid on desktop (6 cols), list on mobile (1 col)
- Infinite scroll or "Load More" for large episode counts (500+ for long-running series)
- Filter: show all / only sub / only dub / only available

### 4. Info tab

`components/anime/MediaInfo.vue`

- Synopsis: expandable text (show more / show less)
- Fallback: "No synopsis available" when null
- Genre tags: pill-shaped, clickable → search by genre
- Studio list with main studio highlighted
- Tags: truncated with expand, clickable
- Metadata table: Country, Season, Duration, Episode count, Source

### 5. Related media tab

`components/anime/RelatedMediaCarousel.vue`

- Horizontal scrollable row of `AnimeCard` components
- Relation label overlaid on each card (Sequel, Prequel, Side Story)
- Click → navigate to related media detail
- Empty state: "No related media" with `AppEmptyState`

### 6. State contract

```typescript
// state managed by a dedicated composable
interface MediaDetailState {
  media: MediaDetail | null
  episodes: ConsolidatedEpisodeSource[]   // from ADR 080 endpoint
  sources: SourceResponse[]               // from ADR 080 endpoint
  isLoading: boolean
  isEpisodesLoading: boolean
  error: string | null
  activeTab: 'episodes' | 'info' | 'related'
  selectedLanguage: 'sub' | 'dub'
  selectedServer: string                  // source name
  userProgress: number                    // episodes watched from list entry
}
```

### 7. Data flow

```
Page mount
  → fetch media detail (existing endpoint)
  → fetch sources (GET /media/{id}/sources)
  → fetch consolidated episodes (GET /media/{id}/episodes/sources) — parallel
  → fetch user list entry (GET /lists/entry/{media_id}) for progress
  → render hero + episode list

User clicks "Play" on episode N
  → VideoPlayer overlay opens with embed URL for selected language/server
  → usePlayerListener attaches to iframe
  → On complete: PATCH /lists/entries/{entry_id} progress = N
  → Close player → episode N marked as watched in list

User switches language (SUB ↔ DUB)
  → Reload embed URL with new language parameter
  → Re-attach usePlayerListener to new iframe

User switches server
  → Reload embed URL from different source mapping
  → Re-attach usePlayerListener
```

### 8. API changes needed

| Endpoint | Status | Dependency |
|----------|--------|------------|
| `GET /media/{id}/episodes` | New (ADR 080) | Backend service |
| `GET /media/{id}/episodes/sources` | New (ADR 080) | Backend service + source repo |
| `GET /lists/entry/{media_id}` | Existing | Already returns user tracking state |
| `PATCH /lists/entries/{entry_id}` | Existing | Already updates progress |

### 9. Testing contract

- `MediaDetailPage.test.ts`: loading/error/success states, tab switching, play button visibility, episode list rendering
- `HeroBanner.test.ts`: cover/banner display, score ring color, action buttons, responsive breakpoints
- `EpisodeList.test.ts`: loading/empty/error/success states, language filter, server selector, play button disabled states, progress indicators
- `MediaInfo.test.ts`: synopsis expand, genre pills, studio display, metadata table
- `RelatedMediaCarousel.test.ts`: cards rendering, relation labels, navigation, empty state

## Consequences

**Good**:
- Single page handles all media consumption: discover, browse episodes, play, track progress
- Leverages all existing backend data (episodes, sources, user list)
- Progressive: works with no source providers (just shows canonical episodes), enhanced with sources

**Bad**:
- Large page with many sub-components — must carefully split state to avoid over-fetching
- Hero banner with large images may be slow on mobile
- Consolidated episode endpoint may return large payloads for 500+ episode series

**Neutral**:
- The existing `MediaDetailPage.vue` is small (69 lines) — rewriting is low risk
- Old page is replaced entirely, no backward compat needed for internal app
