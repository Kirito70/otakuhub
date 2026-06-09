# ADR 089 — Phase 26: Streaming UI Component Library

**Status**: Proposed
**Date**: 2026-06-09

## Context

Phase 26 builds the custom streaming-first Vue 3 + SCSS component library defined in ADR 079. These components replace Material Design Quasar equivalents for all media-display and playback surfaces.

The library must serve two immediate consumers:
- **Phase 27** — Home Page streaming redesign (HeroBanner, TrendingCarousel, AnimeCard, AnimeGrid)
- **Phase 28** — Media Detail + Player pages (EpisodeList, ServerSelector, VideoPlayer, ScoreRing)

## Decision

### 1. File organization

All custom streaming components live under `frontend/src/components/` with no Quasar dependency:

```
frontend/src/
├── css/
│   ├── tokens.scss              ← Design tokens (Phase 26.1)
│   ├── app.scss                 ← Global styles, imports tokens
│   └── quasar.variables.scss    ← Unchanged (Quasar shell only)
├── components/
│   ├── anime/
│   │   ├── AnimeCard.vue        ← Core media card primitive (26.2)
│   │   ├── AnimeGrid.vue        ← Responsive CSS grid wrapper (26.2)
│   │   ├── HeroBanner.vue       ← Full-width hero with gradient (26.3)
│   │   ├── ScoreRing.vue        ← CSS circular score (26.3)
│   │   ├── EpisodeItem.vue      ← Single episode row (26.4)
│   │   ├── EpisodeList.vue      ← Scrollable episode grid (26.4)
│   │   ├── ServerSelector.vue   ← Language/server mirror picker (26.4)
│   │   └── TrendingCarousel.vue ← Horizontal scroll of cards (26.6)
│   └── player/
│       ├── VideoPlayer.vue      ← Iframe embed overlay (26.5)
│       ├── PlayerControls.vue   ← Play/pause/next overlay (26.5)
│       └── PlayerError.vue      ← Fallback/error states (26.5)
├── composables/
│   ├── usePlayerListener.ts     ← postMessage handler (26.5)
│   └── useTheme.ts              ← Already exists
```

### 2. Design token system (`tokens.scss`)

Defines all visual properties in one file imported by all components and `app.scss`.

**Surfaces:**
```scss
$bg-primary:   #0a0a0a;
$bg-secondary: #111111;
$bg-elevated:  #1a1a1a;
$bg-hover:     #222222;
$bg-overlay:   rgba(0, 0, 0, 0.75);
```

**Text:**
```scss
$text-primary:   #ffffff;
$text-secondary: #a0a0a0;
$text-muted:     #606060;
```

**Accents:**
```scss
$accent-primary:   #7c3aed;  // purple
$accent-secondary: #06b6d4;  // cyan
$accent-glow:      #a855f7;  // bright purple
$accent-warm:      #f59e0b;  // amber/ratings
```

**Utility:**
```scss
$radius-sm:   4px;
$radius-md:   8px;
$radius-lg:   12px;
$radius-xl:   16px;
$transition:  200ms ease;
```

### 3. Component contracts

#### AnimeCard (26.2)
- **Props**: `id`, `title`, `coverImage`, `mediaType`, `format`, `episodeCount`, `score`, `year`, `isNew`, `status`
- **States**: loading (skeleton), error (gradient fallback), hover (play overlay), normal
- **Slots**: `badges` (for custom badge injection), `actions` (for overlay actions)
- **Emits**: `click`
- **Responsive**: aspect-ratio 3:4 via CSS `aspect-ratio`

#### AnimeGrid (26.2)
- **Props**: `items` (array), `loading`, `error`, `columns` (default responsive: 2/3/4/6)
- **States**: loading (skeleton grid), empty (AppEmptyState), error (AppEmptyState retry)
- **Slots**: none
- **Emits**: `item-click`, `retry`
- **Responsive**: CSS grid with `grid-template-columns: repeat(auto-fill, minmax(...))`

#### HeroBanner (26.3)
- **Props**: `item` (MediaItem with coverImage, title, score, mediaType, synopsis), `loading`
- **States**: loading (gradient skeleton), empty (hidden), normal
- **Slots**: `actions` (buttons overlay)
- **Emits**: `play`, `details`

#### ScoreRing (26.3)
- **Props**: `score` (number, 0-10), `size` (px, default 36), `strokeWidth` (default 3)
- **States**: zero score (gray ring with "-"), normal
- **Slots**: none
- **Color scale**: <4 = red, 4-6 = amber, 6-8 = green, 8+ = cyan

#### EpisodeList (26.4)
- **Props**: `episodes` (EpisodeItem[]), `loading`, `error`, `currentEpisode`, `watchingProgress`
- **States**: loading (skeleton rows), empty (AppEmptyState), error (AppEmptyState retry), has-data
- **Emits**: `play-episode`, `retry`
- **Responsive**: single-column list, episode numbers visible

#### ServerSelector (26.4)
- **Props**: `servers` (array of {id, name, is_available}), `selectedServer`, `language`, `hasDub`
- **States**: single server (no selector shown), multiple servers, all servers offline
- **Emits**: `server-change`, `lang-change`

#### VideoPlayer (26.5)
- **Props**: `embedUrl`, `episodeNumber`, `title`, `language`, `visible`, `episodes` (prev/next context)
- **States**: loading (spinner), playing (iframe), error (PlayerError), no-url (unavailable)
- **Emits**: `close`, `next-episode`, `previous-episode`, `progress`

#### TrendingCarousel (26.6)
- **Props**: `title` (section header), `items`, `loading`, `hasMore`, `seeAllLink`
- **States**: loading (skeleton cards), empty (hidden), has-data
- **Slots**: `header-actions`
- **Emits**: `item-click`, `see-all`
- **Scroll**: CSS `overflow-x: auto`, `scroll-snap-type: x mandatory`, mouse wheel horizontal

### 4. Composable contracts

#### usePlayerListener (26.5)
- Accepts `allowedOrigins: string[]`
- Exposes `isPlaying`, `currentTime`, `duration`, `percent`, `error` refs
- Lifecycle: `attach(iframeWindow)`, `detach()`
- Callbacks: `onProgress`, `onComplete`, `onError`
- Origin validation: rejects messages from untrusted origins
- Debounce: progress events at most 1 per 30s

### 5. Token import strategy

`tokens.scss` is imported in two ways:
1. **`app.scss`** — `@use 'tokens' as *` — for global styles
2. **Each component** — `@use 'src/css/tokens' as *` — for self-contained components

No component imports `quasar.variables.scss` (that's for the Quasar shell only).

### 6. TypeScript types

New types are needed:
```typescript
// types/media.ts — expanded
export interface MediaItem {
  id: string
  title: string
  coverImage: string | null
  mediaType: string
  format: string | null
  score: number | null
  year: number | null
  episodeCount: number | null
  status: string | null
}

// types/anime.ts — new, for streaming components
export interface EpisodeItem {
  episodeNumber: number
  title: string | null
  airDate: string | null
  thumbnail: string | null
  sources: SourceOption[]
  isWatched: boolean
}

export interface SourceOption {
  source: string
  language: 'sub' | 'dub'
  embedUrl: string | null
  isAvailable: boolean
}

export interface ServerOption {
  id: string
  name: string
  isAvailable: boolean
}
```

## Consequences

**Good**:
- Clean separation: streaming components are pure Vue 3 + SCSS with no Quasar dependency
- Design tokens in one file ensure visual consistency
- Components are self-contained and testable
- ADR 079/081/083 contracts are realized in concrete code

**Bad**:
- 26.5 (VideoPlayer) depends on backend Phase 25 data and MegaPlay embed URLs
- Components require test files for each (20+ new test files across Phase 26)

**Neutral**:
- Components will be consumed in Phase 27 (HomePage) and Phase 28 (MediaDetailPage + Player)
- Existing Quasar-based pages continue working until migrated
