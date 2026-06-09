# ADR 079 — Frontend Design Direction: Streaming-First UX

**Status**: Proposed
**Date**: 2026-06-08

## Context

OtakuHub's current frontend uses Quasar 2.x (Vue 3), which ships with Material Design components by default. While functional, the visual result feels like a productivity tool, not a media/streaming platform. The user has expressed dissatisfaction with the current design and requested something "like aniwave" — a dark-themed, content-first streaming experience.

**Aniwave-style design characteristics:**
- Very dark backgrounds (`#0a0a0a`, `#111`, `#1a1a2e`) with neon/cyan/purple accents
- Content-first: large cover images, minimal UI chrome around them
- Card-based grid layout for browse/discover
- Clean episode list with sub/dub indicators and server mirrors
- Prominent search bar, trending/popular/new-releases sections on home
- No login wall on browse — content is immediately visible
- Fast, lightweight feel
- Cinematic, immersive detail pages with hero banners

**The question**: Can Quasar deliver this look, or should we switch frameworks?

## Assessment

### Quasar's Position
| For Quasar | Against Quasar |
|-----------|---------------|
| 187 existing tests, 24 Vue files already built | Material Design aesthetic baked into every component |
| Auth, routing, Pinia stores, axios interceptors done | QForm/QInput/QBtn patterns are form-oriented, not content-oriented |
| Cross-platform: Web/Electron/Capacitor from one codebase | Heavy bundle (~300KB+ for core Quasar) |
| Dark mode built-in with `$q.dark.set(true)` | Material ripple effects, elevation shadows, primary/secondary color system fight dark streaming look |
| Responsive layout via QLayout/QDrawer/QFooter | QCard/QList/QItem are productivity-widget shaped |
| Quasar CLI manages Vite/TS/Babel/electron config | Every Quasar component needs heavy SCSS overrides to look "non-Material" |

### Verdict

Quasar can be **kept as an application shell** (layout, routing, auth guard, dark mode toggle) while building a **custom component layer** for all content/streaming surfaces. This avoids rewriting the entire frontend while achieving the desired aesthetic.

The migration pattern:
1. Keep Quasar for: `QLayout`, `QDrawer`, `QFooter`, `QPage`, `QBtn` (minimal), `QInput` (search only), `QDark` mode, `QCircularProgress` (score rings)
2. Build custom for: `AnimeCard`, `HeroBanner`, `EpisodeList`, `VideoPlayer`, `MediaGrid`, `ServerSelector`, `TrendingCarousel`
3. Override via SCSS: dark palette, remove Material shadows, flatten elevations, custom scrollbars

## Decision

### 1. Keep Quasar as the application shell only

Do **not** throw away Quasar entirely. The existing auth, routing, Pinia, axios, and test infrastructure are valuable. Instead, use Quasar for:

- **Layout framework**: `QLayout` + `QDrawer` + `QFooter` for responsive shell
- **Routing**: `vue-router` (already Quasar-configured)
- **State**: Pinia stores (unchanged)
- **Theming**: `$q.dark.set(true)`, custom brand SCSS variables
- **Minimal UI components**: `QBtn` (just for basic actions), `QInput` (search), `QCircularProgress` (score rings)
- **Build tooling**: Quasar CLI for Vite/TypeScript/Electron/Capacitor

### 2. Build a custom streaming component library

All media-display and playback components are **pure Vue 3 + SCSS** — no Quasar wrapper:

```
frontend/src/
├── components/
│   ├── anime/
│   │   ├── AnimeCard.vue           ← pure custom, no QCard
│   │   ├── AnimeGrid.vue           ← responsive CSS grid
│   │   ├── HeroBanner.vue          ← full-width hero with gradient overlay
│   │   ├── EpisodeItem.vue         ← episode row with sub/dub badges
│   │   ├── EpisodeList.vue         ← scrollable episode grid/list
│   │   ├── ServerSelector.vue      ← mirror server picker
│   │   ├── TrendingCarousel.vue    ← horizontal scroll of anime cards
│   │   └── ScoreRing.vue           ← circular score indicator (CSS only)
│   ├── player/
│   │   ├── VideoPlayer.vue         ← iframe embed wrapper
│   │   ├── PlayerControls.vue      ← play/pause/next-episode overlay
│   │   └── PlayerError.vue         ← fallback states
```

### 3. Visual contract (aniwave-inspired palette)

```scss
// Core surface colors
$bg-primary:   #0a0a0a;   // main background
$bg-secondary: #111111;   // card surfaces
$bg-elevated:  #1a1a1a;   // hover/dropdown
$bg-overlay:   rgba(0, 0, 0, 0.7);

// Content hierarchy
$text-primary:   #ffffff;
$text-secondary: #a0a0a0;
$text-muted:     #606060;

// Accent palette
$accent-primary:   #7c3aed;  // purple
$accent-secondary: #06b6d4;  // cyan
$accent-glow:      #a855f7;  // bright purple glow
$accent-warm:      #f59e0b;  // amber for ratings

// Status colors
$status-green:  #22c55e;
$status-red:    #ef4444;
$status-blue:   #3b82f6;
```

### 4. Migration approach (incremental)

Each new page/sub-phase builds using the custom component library. Existing Quasar-based pages (DiscoverPage, MediaDetailPage, etc.) are converted page-by-page as they are reimplemented for the streaming experience. The old Quasar page and its replacement exist side-by-side during transition.

**Phased migration:**
1. Build custom component library (tracking, typography, palette)
2. Build new HomePage (replaces DiscoverPage) using custom components
3. Build new MediaDetailPage with episodes tab + player
4. Convert MyListPage to custom components
5. Convert remaining social/watchparty pages
6. Strip unused Quasar components from final bundle

## Consequences

**Good**:
- No rewrite of auth/routing/state/test infrastructure
- Achieves the dark cinematic streaming aesthetic on every platform (web, electron, mobile)
- Dual-approach lets us ship features immediately while gradually migrating
- Custom components are lighter and faster than Quasar equivalents for content display
- All existing 187 tests remain valid during migration

**Bad**:
- Two visual systems coexist during migration (possible inconsistency in early releases)
- Some Quasar components will still need SCSS overrides for the interactive shell areas
- Developers must be clear about which components use Quasar vs. custom patterns

**Neutral**:
- Quasar's build chain (Vite + TypeScript + electron + capacitor) remains intact
- The custom component library can eventually replace Quasar entirely if desired
- Full migration could be abandoned at any point — Quasar-shell approach works as a steady state
