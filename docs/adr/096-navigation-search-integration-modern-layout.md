# ADR 096 — Navigation & Search Integration: Modern Anime Site Layout

**Status**: Accepted
**Date**: 2026-06-23
**Supersedes**: Section 6.2 (Search/Discover), Section 6.4 (My List), Section 5 (IA) and Section 4.14 (NavigationScaffold) of ADR 094
**Depends on**: ADR 094 (Design System, Component Library)

## Context

ADR 094 v3 (2026-06-19) specified a modern redesign of the Flutter frontend. However, during implementation it became clear that the information architecture — inherited from the earlier tabbed-discover-and-separate-search-page model — does not match how modern anime sites actually work.

**Four search surfaces currently coexist:**

| Surface | Where | Problem |
|---------|-------|---------|
| Search tab inside `DiscoverScreen` | `features/discover/screens/discover_screen.dart` | Search is buried as one of three tabs below Trending/NewReleases |
| `SearchResultsScreen` at `/search` | Separate GoRouter route | Requires navigation away from current context |
| `SearchOverlay` modal | `core/widgets/search_overlay.dart` | Works well but underused — only triggered via header tap |
| `_SearchHeaderBar` in scaffold | `adaptive_scaffold.dart` | Only on desktop/tablet; mobile has an AppBar stub |

**This fragmentation creates four concrete problems:**

1. **UX confusion** — Users don't know which search surface to use. The overlay, the tab, and the separate page all behave differently. Modern anime sites (Crunchyroll, Aniwave, AniList) have exactly ONE search surface: a persistent search bar in the shell header.

2. **State duplication** — Search query, results, and selection state are split across `discover_providers.dart`, `search_provider.dart`, and the overlay's local state. The same API (`GET /api/v1/media/search`) is called from three different places.

3. **Navigation fragility** — The `/search` route is a standalone page within the `AdaptiveScaffold` ShellRoute, which means the nav bar stays visible, but the user has "navigated" to search as if it's a destination. This conflicts with the principle that nav destinations (Home, List, Feed, Alerts, Profile) are modes, not pages.

4. **Mobile friction** — On mobile (<600px), tapping the AppBar search text opens the overlay, but the overlay is a full-screen route push (slide from right), which feels like navigating away. The `DiscoverScreen` still shows a Search tab, creating a cycle.

**Additionally, the navigation label and landing page are misaligned:**

- ADR 094 v3 specified the nav as **Home · List · Feed · Alerts · Profile** with `HomeScreen` (hero + content rails) as the landing page.
- The actual implementation shows **Discover** as the nav label and `DiscoverScreen` (tabbed Search/Trending/NewReleases) as the landing page.
- `HomeScreen` exists at `features/discover/screens/home_screen.dart` but is unreachable from navigation.

**The core design principle we're correcting:** Search is a **capability of the shell**, not a destination. Modern anime sites treat search the way macOS treats Spotlight — always one keystroke (or tap) away, with results overlaid on the current context, never a page you "go to."

## Decision

### 1. Eliminate the separate search page

- **Remove** the `/search` route from `app_router.dart`.
- **Remove** the `SearchResultsScreen` widget.
- **Remove** the Search tab from `DiscoverScreen`.
- **Remove** `discover_screen.dart` entirely (replaced by `home_screen.dart`).

### 2. Make search a shell-level concern

- **One search surface**: `SearchOverlay` becomes the **single** search interface for all platforms.
- **Desktop/tablet (>=600px)**: The `_SearchHeaderBar` always visible in the `AdaptiveScaffold` header. Typing or focusing it opens `SearchOverlay` in compact mode (slide-down dialog, max 800px wide, 75vh tall).
- **Mobile (<600px)**: The AppBar shows a search icon button. Tapping opens `SearchOverlay` in full-screen mode (slide-up from bottom, not slide-right — feels like a sheet, not navigation).
- **Keyboard**: `Ctrl+K` / `Cmd+K` opens the overlay from anywhere. `Escape` closes it.
- **The overlay is the only search surface**: No separate results page. The overlay shows:
  - **Empty state** (no query): Recent searches, trending searches, quick genre chips
  - **Typing**: Debounced results grouped by media type (Anime/Manga/Manhwa) with count badges
  - **Result tap**: Dismisses overlay, navigates to `/media/:id`
  - **"View all"**: Expand the overlay to full-screen grid for that media type
  - **Error/empty states**: Handled within the overlay

### 3. Rename and restructure navigation

| Nav Item | Label | Route | Screen | Notes |
|----------|-------|-------|--------|-------|
| 1 | Home | `/home` | `HomeScreen` | Hero spotlight + content rails |
| 2 | List | `/list` | `MyListScreen` | Unified: Your List + Discover sub-tab (browse) + Calendar sub-tab |
| 3 | Feed | `/feed` | `FeedScreen` | Activity + Recommendations + Discussions |
| 4 | Alerts | `/notifications` | `NotificationsScreen` | Notification inbox |
| 5 | Profile | `/profile` | `ProfileScreen` | Profile + Watch Party + Settings |

- **"Discover" is gone as a nav label.** Browsing new content happens via the **Discover sub-tab** inside the List page (which contains a genre/format/season browse grid).
- **"My List" is renamed to "List"** — shorter, cleaner, matching Crunchyroll/AniList convention.
- **Watch Party** moves from a primary nav item into Profile (as a sub-page), since it's an occasional-action feature, not a daily destination. On desktop, it stays in the nav rail as an optional item.
- **Home is the landing page** — always the first thing users see after login.

### 4. Restructure the List page

The List page (`/list`) has three sub-tabs:

1. **Your List** — Status-tabbed tracking library (Watching, Completed, Paused, Dropped, Plan). Inline progress/score. Same as current `MyListScreen`.
2. **Discover** — Browse mode: genre chips, season selector, format filter. Results in a responsive poster grid. This is where the "browse" functionality of the old `DiscoverScreen` goes (minus search).
3. **Calendar** — Airing calendar (same as current `AiringCalendarScreen`).

A shared filter bar sits above the sub-tabs with 8 filter types (status, type, genre, format, year, season, score, sort).

### 5. Home screen as the true landing

`HomeScreen` becomes the primary landing (route `/home`):

- **Spotlight hero**: Full-width auto-cycling banner with gradient overlay, title, synopsis, CTA buttons
- **Content rails** (horizontal scroll with PosterCards):
  - "Jump Back In" — continue watching (status=watching, ordered by recent progress)
  - "From Your Friends" — friend recommendations with FriendAvatar overlay
  - "Trending Now" — trending in your group
  - "New Releases" — recently released episodes/chapters
  - "Popular This Season" — seasonal top-rated
- **Skeleton state**: Hero block + 3 rail skeletons
- **Pull to refresh**

### 6. SearchOverlay redesign

The existing `SearchOverlay` at `core/widgets/search_overlay.dart` is expanded:

**Before (current)**: Full-screen PageRouteBuilder on mobile, dialog on desktop. Has grouped results, but also has an alternative full results page (`/search`).

**After**: The overlay is the **terminal search experience**.

- **Mobile (<600px)**: Full-screen, but presented as a bottom sheet (slide-up, not slide-right) to feel like temporary context, not navigation.
- **Desktop/tablet (>=600px)**: Slide-down dialog centered in viewport, max 800px × 75vh, with scrim.
- **States**:
  - **Recent**: Show last 5 searches from memory (shared_preferences) + "Trending searches" from backend
  - **Typing**: Debounced (300ms) — grouped results with "View all N results" per media type
  - **Loading**: Skeleton cards (3 per group)
  - **Empty (no results)**: "No titles match '{query}'" with clear button and genre chip suggestions
  - **Error**: Inline retry with friendly message
- **Navigation**: Tapping a result → dismiss overlay → push `/media/:id`. "View all" → dismiss overlay → push to `/list?discover&type=anime&q=query`.
- **Keyboard**: Arrow keys navigate results, Enter selects, Escape closes.

### 7. Shell layout changes

**Mobile (<600px)**:
```
┌─────────────────────────────────┐
│ AppBar: [icon] Search… [bell]   │  ← search icon opens overlay
├─────────────────────────────────┤
│                                 │
│         Page Content            │
│                                 │
├─────────────────────────────────┤
│  Home │ List │ Feed │ Alerts │ Profile │  ← 5 tabs, bottom nav
└─────────────────────────────────┘
```

**Desktop/Tablet (>=600px)**:
```
┌──────────────────────────────────────────────────┐
│  Header: [logo]  [🔍 Search anime, manga…] [bell] │  ← search always visible
├──────────┬───────────────────────────────────────┤
│          │                                       │
│  Home    │                                       │
│  List    │          Page Content                  │
│  Feed    │                                       │
│  Alerts  │                                       │
│  Profile │                                       │
│          │                                       │
└──────────┴───────────────────────────────────────┘
```

### 8. Backend alignment

**No new backend endpoints are required** for this change. Existing endpoints suffice:

| Existing Endpoint | Used By |
|-------------------|---------|
| `GET /api/v1/media/search` | SearchOverlay (query + type filter) |
| `GET /api/v1/home` | HomeScreen (composite payload) |
| `GET /api/v1/lists/me` | List > Your List sub-tab |
| `GET /api/v1/media/browse` | List > Discover sub-tab (genre/season/format filtering) |
| `GET /api/v1/media/airing` | List > Calendar sub-tab |
| `GET /api/v1/social/feed` | Feed screen |
| `GET /api/v1/notifications` | Alerts screen |

The `GET /api/v1/media/search` endpoint may benefit from a `trending_searches` or `suggestions` sub-resource for the overlay's empty-state trending chips, but this is additive and non-blocking.

### 9. Screen disposition summary

| Current Screen | Action | Notes |
|----------------|--------|-------|
| `discover_screen.dart` | **Remove** | Replaced by `HomeScreen` as landing |
| `search_results_screen.dart` | **Remove** | `/search` route eliminated |
| `home_screen.dart` | **Keep + promote** | Becomes landing page at `/home` |
| `my_list_screen.dart` | **Keep + rename route** | Renamed nav label to "List" |
| `discover` feature directory | **Restructure** | Remove Search tab from providers; rename to `home` |
| `search_overlay.dart` | **Expand** | Becomes the single search surface |
| `adaptive_scaffold.dart` | **Modify** | Search always in header; nav items change |
| `app_router.dart` | **Modify** | Remove `/search` route; add `/home` route |
| `route_names.dart` | **Modify** | Remove `searchResults`; add `home` |
| `watch_party_screen.dart` | **Move** | Removed from primary nav; accessible from Profile |

## Consequences

**Good**:
- **Single search surface** — eliminates confusion between overlay/tab/page. One provider, one API call pattern, one UX.
- **Matches modern anime sites** — persistent search in header, content as landing, minimal chrome.
- **Cleaner navigation** — 5 primary items with clear labels (Home, List, Feed, Alerts, Profile). No "Discover" ambiguity.
- **Less code** — removes `SearchResultsScreen`, `discover_screen.dart`, the Search tab, and the `/search` route.
- **Better mobile UX** — search via bottom sheet (temporary) instead of page push (navigation).

**Bad**:
- **Breaking change** — removes the `/search` route. Any deep links or bookmarks to `/search?q=...` will 404.
- **`HomeScreen` needs feature parity** — the current `HomeScreen` (genre rails + spotlight) must be expanded to include all the content rails from Section 6.1 of ADR 094 (continue watching, friend recs, etc.).
- **`SearchOverlay` needs expansion** — must handle recent searches, trending suggestions, and "view all" expansion that the separate page used to handle.
- **Migration effort** — tests, providers, and existing Discover feature code need updating.

**Neutral**:
- No database schema changes.
- No new backend endpoints (though search suggestions are a possible future addition).
- The Vue reference frontend is unaffected — this is Flutter-only.
- The `discover` feature directory in `lib/features/` can be renamed to `home/` (with git mv for history preservation).

## Implementation Order

1. **ADR acceptance** — get consensus on nav structure and search approach.
2. **AdaptiveScaffold refactor** — update nav items, ensure search header is persistent across all breakpoints.
3. **SearchOverlay expansion** — add recent searches, trending suggestions, "view all" expansion.
4. **HomeScreen promotion** — expand content rails, set as `/home` landing, move from discover feature.
5. **Router cleanup** — remove `/search`, add `/home`, update route names.
6. **DiscoverScreen removal** — remove the old tabbed screen, the Search tab, and `SearchResultsScreen`.
7. **List page restructure** — add Discover sub-tab with browse grid, Calendar as sub-tab, shared filter bar.
8. **Watch Party relocation** — move from primary nav to Profile sub-page.
9. **Test sweep** — update all affected widget tests for new nav, removed routes, changed screen behavior.
