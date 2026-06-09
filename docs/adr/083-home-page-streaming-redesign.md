# ADR 083 — Home Page: Streaming-First Redesign

**Status**: Proposed
**Date**: 2026-06-08

## Context

The current `DiscoverPage.vue` has tabs (Search / Trending / New Releases) but feels like a generic catalog browser. An aniwave-style home page puts **content discovery first**: large featured items, horizontal carousels, trending grid, and recently updated episodes — all immediately visible without clicking tabs.

Since OtakuHub is a private friend-group app (not a public streaming site), the home page should also integrate **group-aware content** — what friends are watching, recent group activity related to anime, and watch party invitations.

## Decision

### 1. New page layout: `HomePage.vue` (replaces DiscoverPage)

```
┌─────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────┐   │
│  │         Spotlight / Hero Carousel             │   │
│  │   [Featured Anime] with gradient overlay      │   │
│  │   Title | Score | Type | "Watch Now" button   │   │
│  │   ◀ ● ● ○ ● ▶                               │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Section: Continue Watching ───────────────────┐  │
│  │  [Card] [Card] [Card]  → See all               │  │
│  │  (Horizontal scroll, max 10 items)              │  │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Section: Trending Now ────────────────────────┐  │
│  │  [Card] [Card] [Card] [Card] [Card] [Card]     │  │
│  │  (6-column responsive grid)                     │  │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Section: Recently Updated ────────────────────┐  │
│  │  [Card] [Card] [Card] [Card] [Card] [Card]     │  │
│  │  (6-column grid with "New Episode" badge)      │  │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Section: New Releases ────────────────────────┐  │
│  │  [Card] [Card] [Card] [Card]                   │  │
│  │  (4-column grid for brand-new anime)            │  │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Section: Friends Watching ────────────────────┐  │
│  │  (Group-aware — shows what friends added/      │  │
│  │   watched recently, if group feature enabled)   │  │
│  │  "Sakura started watching Jujutsu Kaisen"       │  │
│  │  "Kirito completed Attack on Titan S4"          │  │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Section: Popular Genres ──────────────────────┐  │
│  │  [Action] [Romance] [Fantasy] [Slice of Life]  │  │
│  │  [Sci-Fi] [Comedy] [Horror] [Mecha]            │  │
│  │  (Pill buttons, click → search by genre)        │  │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 2. Sections and data sources

| Section | Data Source | Caching | Fallback |
|---------|-------------|---------|----------|
| **Hero Spotlight** | Backend: trending/popular anime endpoint, top 5 | Session (refresh on page load) | Empty state hidden |
| **Continue Watching** | Backend: user list with in-progress statuses | Persisted per user | Hidden if none |
| **Trending Now** | `GET /media/trending?limit=24` | 5 min cache | "No trending data" |
| **Recently Updated** | Anikoto recent catalog + canonical episodes | 15 min (provider-limited) | Show from canonical episodes |
| **New Releases** | `GET /media/popular?limit=12` with season filtering | 5 min | "No new releases" |
| **Friends Watching** | Group activity feed, filtered to media events | Real-time | Hidden for single-user or no groups |
| **Popular Genres** | Static list from DB genres table | Static | "No genres" |

### 3. Component: `AnimeCard.vue`

The core primitive for all grid/carousel display:

```vue
<template>
  <div class="anime-card" @click="navigate">
    <!-- Cover image -->
    <div class="card-cover">
      <img :src="coverImage || '/placeholder.jpg'" :alt="title" loading="lazy" />
      <!-- Overlay badges -->
      <div class="card-badges">
        <span class="badge-type">{{ mediaType }}</span>
        <span v-if="episodeCount" class="badge-episodes">{{ episodeCount }} eps</span>
      </div>
      <!-- Hover action -->
      <div class="card-hover-overlay">
        <button class="btn-play-hover">▶ Watch Now</button>
      </div>
    </div>
    <!-- Title and metadata -->
    <div class="card-info">
      <h3 class="card-title">{{ title }}</h3>
      <div class="card-meta">
        <ScoreRing :score="score" :size="20" />
        <span class="card-year">{{ year }}</span>
        <span v-if="isNew" class="badge-new">NEW</span>
      </div>
    </div>
  </div>
</template>
```

**States:**
- **Loading**: Skeleton placeholder (animated gray rectangle matching card aspect ratio)
- **Error**: Image fallback (gradient placeholder with title text overlay)
- **Empty**: N/A (card only renders with data)
- **Hover**: Play button overlay with gradient fade
- **Badges**: Type badge (ANIME/MANGA), episode count, NEW indicator

### 4. Component: `TrendingCarousel.vue`

Horizontal scrollable row of `AnimeCard` components:

```vue
<template>
  <section class="trending-section">
    <div class="section-header">
      <h2>{{ title }}</h2>
      <button v-if="hasMore" class="btn-see-all">See All →</button>
    </div>
    <div class="carousel-track" ref="trackRef" @wheel.prevent="onWheelScroll">
      <AnimeCard v-for="item in items" :key="item.id" v-bind="item" />
    </div>
  </section>
</template>
```

- Horizontal scroll via CSS `overflow-x: auto` + `scroll-snap-type: x mandatory`
- Mouse wheel scrolls horizontally (shift equivalent)
- Touch/swipe on mobile
- "See All" navigates to a full grid page with filters

### 5. State contract (Pinia)

```typescript
// stores/home.ts
export const useHomeStore = defineStore('home', () => {
  const spotlight = ref<MediaItem[]>([])
  const trending = ref<MediaItem[]>([])
  const recentUpdates = ref<MediaItem[]>([])
  const newReleases = ref<MediaItem[]>([])
  const continueWatching = ref<ListEntryItem[]>([])
  const friendActivity = ref<FeedActivityItem[]>([])
  const genres = ref<Genre[]>([])

  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchedAt = ref<number>(0)

  async function fetchHome() {
    // Parallel fetch all sections
    const [trendingRes, popularRes, listRes, activityRes, genresRes] = await Promise.all([
      api.get('/media/trending?limit=24'),
      api.get('/media/popular?limit=12'),
      api.get('/media/search?status=releasing&limit=20'), // recent updates proxy
      api.get('/social/feed?limit=10&event_type=media'),
      api.get('/media/genres'),
    ])
    // ... assign to refs
  }

  return {
    spotlight, trending, recentUpdates, newReleases,
    continueWatching, friendActivity, genres,
    isLoading, error, fetchHome
  }
})
```

### 6. Search integration

Search remains accessible from the top navigation bar (not a tab). `AppToolbar` has a prominent search `QInput` with:
- Debounced query (300ms)
- Autocomplete dropdown with top 5 results (AnimeCard mini)
- Enter → navigate to full search results page
- Clear button

### 7. API changes needed

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /media/genres` | New | Returns all genres — simple list |
| `GET /media/seasonal` | New | Returns currently airing season's anime sorted by score — fills "New Releases" |
| `GET /media/recent-updates` | New | Recently updated episodes from sourced catalog (Anikoto-backed) |

### 8. Testing contract

- `HomePage.test.ts`: loading/error/success states, all sections render, empty section hidden
- `AnimeCard.test.ts`: cover display, badges, hover overlay, click navigation, skeleton loading, error fallback
- `TrendingCarousel.test.ts`: horizontal scroll, see-all navigation, wheel event, section header
- `ContinueWatching.test.ts`: progress indicators, empty state hidden, click navigates to media detail + episode resume
- `FriendActivityRow.test.ts`: avatar display, activity text, click navigates, empty state hidden
- `GenrePills.test.ts`: rendering, click navigates to search filtered by genre

## Consequences

**Good**:
- Content-first design matches aniwave aesthetic — users see trending anime immediately
- Continue Watching and Friends sections add group-aware personalization
- Search always accessible from top bar, not hidden in a tab
- Sections degrade gracefully when data is unavailable

**Bad**:
- Home page makes 6+ parallel API calls on first load
- Horizontal carousels may have accessibility issues (keyboard navigation, screen readers)
- Continue Watching requires tracking data to be useful (new users see nothing)

**Neutral**:
- Existing `DiscoverPage.vue` can be repurposed as a search-results page
- Tab-based navigation (Search/Trending/NewReleases) is replaced by scroll-based sections
