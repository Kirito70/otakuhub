# ADR 094 — Flutter Frontend Redesign: Modern Anime Tracking UI

**Status**: Proposed
**Date**: 2026-06-18

## Context

The current Flutter frontend uses a default Material 3 visual style — functional but dated.
The user describes it as "not modern, not well-looking." A comprehensive UX audit of the 3 core
screens (Discover, Media Detail, My List) reveals the following issues:

### Discover Screen (`discover_screen.dart`)
- Plain `Scaffold` + `AppBar` with no visual branding or personality
- Search triggered via a **dialog popup** — dated UX pattern; should be inline in the AppBar
- `TabBar` + `TabBarView` for Search/Trending/New Releases — functionally fine but visually boring
- All 3 tabs use **identical grid layout** — no visual distinction between search results (dense),
  trending (hero cards), and new releases (compact with release date badges)
- Duplicate boilerplate — each tab has the same loading/error/data pattern repeated 3 times

### Media Card (`media_card.dart`)
- Boxy, flat design — no shadows, no depth, no hover/scale effects on desktop
- Fixed aspect ratio (0.65) is boxy, not modern poster-like (~0.7 is standard)
- Title font at 12px is too small for readability
- Minimal metadata — only score + short type badge; no progress indicator, no airing status pill
- No visual hierarchy — card feels flat, no clear focal point
- No cover-image gradient overlay — modern cards overlay title text on the cover bottom

### Media Detail Screen (`media_detail_screen.dart`)
- Hero section is cramped at 280px height with a small 80×120 cover thumbnail
- No backdrop blur or glassmorphism — content is flat against a dark background
- Tab structure has only Episodes/Info/Related — no Streaming Sources or Recommendations tab
- Info tab is a plain key-value list — looks like a database dump with zero visual engagement
- Synopsis has no expand/collapse — long blocks of text overwhelm the layout
- Episodes tab is a basic ListView — no "continue watching" CTA, no airing-countdown badges
- Related carousel is functional but visually flat — no gradient overlays on relation cards

### My List Screen (`my_list_screen.dart`)
- Uses `ListView` instead of `GridView` — entries are dense rows, not visual cards
- Stats bar is plain `Chip` widgets — no visual emphasis, no score distribution graph
- 6 scrollable `TabBar` tabs — too many! Watching/Reading should be the primary filter
- Bottom history section is awkwardly docked — feels like an afterthought, not integrated
- Cover thumbnails are 52×72 — too small to be visually meaningful
- No quick-action buttons — no "increment progress" or "mark next episode" FAB

### Cross-Cutting Issues
- **No micro-animations**: No hero page transitions, no staggered list animations, no card hover effects
- **No glassmorphism**: Dark theme with flat `bgSecondary` cards looks dated; modern UIs use
  `BackdropFilter` blur for depth
- **No consistent card system**: Media card, relation card, and list tile all look different
  despite displaying the same data type (media item)
- **No empty/error state illustrations**: Using plain icons + text feels unpolished
- **Colors are fine** but the application lacks depth — shadows, gradients, blur, and spacing

## Design Principles

1. **Content-first**: Cover art and titles dominate; chrome (AppBar, tabs) recedes into the background
2. **Depth through glassmorphism**: Semi-transparent panels with backdrop blur create hierarchy
3. **Micro-interactions**: Every tappable item has a visual response — scale, glow, or fade
4. **Consistent card system**: One `MediaCard` widget reused across Discover, List, Detail, and Search
5. **Responsive by default**: All layouts use `LayoutBuilder` breakpoints — same widgets scale
6. **TV-safe**: Focus widgets, semantic labels, larger hit targets on every interactive element

## Decision

### 1. New Shared Widget Library (`lib/core/widgets/`)

Create a reusable component layer that all features consume:

```
lib/core/widgets/
├── media_card.dart          ← Single MediaCard used everywhere (Discover, List, Search, Relations)
├── media_card_grid.dart     ← Responsive grid wrapper with loading/empty/error states
├── hero_banner.dart         ← Full-bleed hero with blur, gradient overlay, offset cover
├── glass_panel.dart         ← Reusable BackdropFilter glass container
├── score_ring.dart          ← Circular score indicator with color thresholds
├── status_pill.dart         ← Airing/status badge (RELEASING green, FINISHED gray, etc.)
├── progress_bar.dart        ← Thin progress overlay for cards and list items
├── section_header.dart      ← "Trending" / "New Releases" header with optional "See All"
├── app_loading.dart         ← Shimmer/skeleton loading state
├── app_empty_state.dart     ← Illustrated empty state (upgrade from plain icon+text)
└── app_error_state.dart     ← Error state with retry button
```

#### MediaCard Contract
```
┌──────────────────────┐
│      Cover Image     │  ← 0.7 aspect ratio, rounded 12px corners
│                      │
│  ┌────────────────┐  │
│  │ Score ● Title   │  │  ← Gradient overlay at bottom (transparent→black 60%)
│  └────────────────┘  │
├──────────────────────┤
│  Status Pill  Type   │  ← Optional bottom metadata row (compact variant)
│  Progress Bar        │  ← Optional (shown when user has progress)
└──────────────────────┘
```

**States**:
- **Loading**: Shimmer placeholder matching card dimensions
- **Error**: Broken-image icon overlay on cover
- **Empty**: N/A (card is never shown without data)
- **Data**: Full card with cover, score, title, type badge, status pill

**Responsive**:
- Mobile (<600): 2 columns, card width fills grid
- Tablet (600–1024): 3 columns, slightly larger cards
- Desktop (>1024): 4–5 columns
- TV: 5–6 columns at 1.15× scale, Focus border on highlighted card

**Interactions**:
- Tap → navigate to `/media/:id`
- Desktop hover: scale(1.03) + subtle glow shadow
- TV: Focus border (2px accentPrimary)
- Long press (mobile): context menu (add to list, share, mark as watched)

#### GlassPanel Contract
```dart
class GlassPanel extends StatelessWidget {
  final Widget child;
  final double borderRadius;
  final double blurStrength; // default 10
  final Color tint;          // default Colors.black.withValues(alpha: 0.4)
  final EdgeInsets padding;
}
```
A reusable `ClipRRect` + `BackdropFilter` (ImageFilter.blur) + `Container` with semi-transparent
background. Used on hero banner overlays, stat cards, and floating action panels.

#### ScoreRing Contract
```dart
class ScoreRing extends StatelessWidget {
  final double? score;        // 0.0–10.0, null → "—"
  final double size;          // default 36
  final double strokeWidth;   // default 3
}
```
Circular progress indicator using `CustomPainter`. Color thresholds:
- ≥ 7.5: green (#22C55E)
- ≥ 6.0: gold (#EAB308)
- ≥ 4.0: orange (#F97316)
- < 4.0: red (#EF4444)
- null: muted gray

#### StatusPill Contract
```dart
class StatusPill extends StatelessWidget {
  final String status;        // 'releasing', 'finished', 'not_yet_released', etc.
  final bool compact;         // default false (shorter for cards)
}
```
Color map:
- `releasing`: green border, "Airing" text
- `finished`: gray, "Finished"
- `not_yet_released`: amber, "Upcoming"
- `cancelled`: red, "Cancelled"
- `hiatus`: orange, "Hiatus"

### 2. Discover Screen Redesign

```
┌──────────────────────────────────────┐
│ AppBar: [OtakuHub logo] [🔍 search]  │  ← Inline search field (no dialog)
│                                       │
│ ┌── Trending Hero ──────────────────┐ │
│ │  ┌──────┐  ┌──────┐  ┌──────┐   │ │  ← Horizontal scrollable hero cards
│ │  │Ep 12 │  │Ep 24 │  │Ep 8  │   │ │
│ │  │Solo  │  │Frier │  │Dand  │   │ │  ← Full-bleed covers with glass overlay
│ │  │Lv.2  │  │en    │  │adan  │   │ │
│ │  └──────┘  └──────┘  └──────┘   │ │
│ └──────────────────────────────────┘ │
│                                       │
│ [Trending] [New Releases] [Search] → │  ← Tab bar or segmented control
│                                       │
│ ┌── Content Grid ───────────────────┐ │
│ │  ┌───┐ ┌───┐ ┌───┐ ┌───┐       │ │
│ │  │ C │ │ C │ │ C │ │ C │       │ │  ← MediaCard grid
│ │  │ a │ │ a │ │ a │ │ a │       │ │
│ │  │ r │ │ r │ │ r │ │ r │       │ │
│ │  │ d │ │ d │ │ d │ │ d │       │ │
│ │  └───┘ └───┘ └───┘ └───┘       │ │
│ │  ┌───┐ ┌───┐ ┌───┐            │ │
│ │  │ C │ │ C │ │ C │            │ │
│ │  │ a │ │ a │ │ a │            │ │
│ │  │ r │ │ r │ │ r │            │ │
│ │  │ d │ │ d │ │ d │            │ │
│ │  └───┘ └───┘ └───┘            │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Structure**:
- **Top section**: AppBar with inline search field (auto-focus on navigate to search tab)
- **Hero strip**: Horizontal scrollable hero cards (top 10 trending, full-bleed covers with glass overlay)
- **Tab/segment row**: Trend / New / Search — visually distinct content per tab
- **Content grid**: MediaCard grid with responsive column count

**Tab-specific behavior**:
- **Trending tab**: Cards with trending-rank badge, sorted by popularity
- **New Releases tab**: Cards with "NEW" badge on recently added, date labels
- **Search tab**: Cards with search-highlighted titles, no badges, infinite scroll

**States**:
- **Loading**: Shimmer grid (8 skeleton cards)
- **Empty**: "No results found" illustration with search tips
- **Error**: Retry-friendly error with error details

### 3. Media Detail Screen Redesign

```
┌──────────────────────────────────────┐
│ ← Back           [Share] [⇅ List]    │  ← Transparent AppBar over hero
│ ┌── Full-Bleed Hero ───────────────┐ │
│ │  ┌────────┐ ┌──────────────────┐ │ │
│ │  │        │ │ Title (Romaji)   │ │ │  ← Cover image offset to left
│ │  │ Cover  │ │ Title (English)  │ │ │
│ │  │ 160×   │ │                  │ │ │  ← GlassPanel overlay for text
│ │  │ 228    │ │ ⭐ 8.5  ●  TV    │ │ │
│ │  │        │ │ 🔵 Airing        │ │ │
│ │  │        │ │ ┌─Add to List─┐  │ │ │  ← Floating CTA button
│ │  └────────┘ └──────────────────┘ │ │
│ └──────────────────────────────────┘ │
│                                       │
│ [Overview] [Episodes] [Related] [Src] │  ← Sticky tab bar
│                                       │
│ ┌── Tab Content ────────────────────┐ │
│ │  Overview tab:                    │ │
│ │  ┌─ Synopsis (expandable) ─────┐ │ │
│ │  │  Long synopsis text...      │ │ │
│ │  │  [Show More ▾]              │ │ │
│ │  └──────────────────────────────┘ │ │
│ │  ┌─ Info Grid ──────────────────┐ │ │
│ │  │  Type: Anime  |  Ep: 24     │ │ │
│ │  │  Season: Spr |  Duration:   │ │ │
│ │  │  2024        |  24m/ep      │ │ │
│ │  └──────────────────────────────┘ │ │
│ │  Genres: [Action] [Fantasy] ...   │ │
│ │  ┌─ Stats ──────────────────────┐ │ │
│ │  │  📊 Score Dist  |  📈 Rank  │ │ │
│ │  │  👥 Popularity  |  📅 Started│ │ │
│ │  └──────────────────────────────┘ │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Hero section** (replaces current cramped banner):
- Full-bleed backdrop image (banner_image) with `BackdropFilter` blur and gradient overlay
- Cover image: 160w × 228h, offset to left, with subtle shadow/elevation
- Info panel: GlassPanel overlay containing title, score ring, format badge, status pill
- Floating CTA: "Add to List" / "Continue Watching" / "Mark Episode 5" — changes based on user tracking state

**Tabs**:
1. **Overview**: Synopsis (expandable), info grid, genres, stats section
2. **Episodes**: Episode list (same as current but with airing countdown badges, watch-status indicators)
3. **Related**: Horizontal scroll of MediaCards (not custom relation cards — reuse MediaCard)
4. **Sources**: Streaming provider links (new — shows available source mappings)

**States**:
- **Loading**: Hero shimmer + tab content skeleton
- **Error**: Error state with retry
- **Data**: Full hero + tabs
- **No tracking data**: Show "Add to List" CTA prominently

### 4. My List Screen Redesign

```
┌──────────────────────────────────────┐
│ My List              [🔍 filter/sort] │  ← AppBar with filter button
│                                       │
│ ┌─ Stats Bar ───────────────────────┐ │
│ │  Watching: 12  |  Completed: 45  │ │  ← GlassPanel with stat chips
│ │  Paused: 3     |  Dropped: 2     │ │
│ │  Plan: 18      |  Total: 80      │ │
│ └────────────────────────────────────┘ │
│                                       │
│ [Watching] [Completed] [All] [Pl→]    │  ← Compact tab bar (3 primary + dropdown for rest)
│                                       │
│ ┌── Content Grid ───────────────────┐ │
│ │  ┌───┐ ┌───┐ ┌───┐ ┌───┐       │ │  ← MediaCard with progress overlay
│ │  │ C │ │ C │ │ C │ │ C │       │ │
│ │  │ a │ │ a │ │ a │ │ a │       │ │  ← Each card shows:
│ │  │ r │ │ r │ │ r │ │ r │       │ │      - cover image
│ │  │ d │ │ d │ │ d │ │ d │       │ │      - title
│ │  │ 📊│ │ 📊│ │ 📊│ │ 📊│       │ │      - progress bar (ep 12/24)
│ │  └───┘ └───┘ └───┘ └───┘       │ │      - score badge
│ └──────────────────────────────────┘ │
│                                       │
│                    [➕ Add from search]│  ← FAB to add media to list
└──────────────────────────────────────┘
```

**Key changes from current**:
- **Grid of MediaCards** replaces dense `ListView` — same `MediaCard` as Discover, with `progress` overlay
- **Stats bar** is a single `GlassPanel` row, not scattered `Chip` widgets
- **Tabs reduced** from 6 to 4 visible (Watching, Completed, All, dropdown for Paused/Dropped/Plan)
- **FAB** opens a search-and-add flow rather than being hidden in a menu
- **Quick actions**: Tap a card → bottom sheet with "Mark Next Episode", "Update Score", "Change Status"

**States**:
- **Loading**: 6 skeleton cards
- **Empty per tab**: "Nothing in this list yet" with illustration + "Browse Discover" CTA
- **Empty all**: "Your list is empty" onboarding illustration
- **Error**: Retry-friendly error

### 5. Animation & Transition Contracts

| Animation | When | Implementation |
|-----------|------|----------------|
| Hero transition | Tap MediaCard → Detail page | `Hero` widget on cover image |
| Staggered list | Grid/List first appears | `StaggeredGridAnimation` wrapper |
| Card hover scale | Desktop mouse enter | `MouseRegion` + `AnimationController` scale(1.03) |
| Glass shimmer | Loading states | `ShimmerLoading` (gradient sweep) |
| Tab slide | Tab change | `TabBarView` animation (keep current) |
| Score ring fill | Score appears | `TweenAnimationBuilder` on ring |
| FAB scale | Scroll down | Scaling/fab visibility based on scroll offset |

### 6. Responsive Breakpoint Summary

| Breakpoint | Nav | Discover cols | List cols | Card size | Hero height |
|------------|-----|--------------|-----------|-----------|-------------|
| < 600 (phone) | BottomNav | 2 | 2 | compact | 280px |
| 600–1024 (tablet) | Rail | 3 | 3 | normal | 340px |
| > 1024 (desktop) | Drawer | 4–5 | 4–5 | large | 400px |
| TV (any width) | Rail | 5–6 | 5–6 | 1.15× scale | 450px |

## Consequences

**Good**:
- Single `MediaCard` widget eliminates 3 separate card implementations (discover, relations, list)
- Glassmorphism and micro-animations create a premium, modern feel without heavy assets
- All screens share the same component library, reducing future feature development time
- Responsive by design — no per-platform screen implementations needed
- TV gets Focus-based navigation for free since all interactive elements are standardized

**Bad**:
- Significant refactoring of existing screens — need to replace current widgets with new ones
- `BackdropFilter` can be expensive on low-end Android devices — need to detect and fall back
- Micro-animations add complexity to widget tests (need `tester.pump()` with durations)

**Neutral**:
- Existing color palette stays unchanged — only the composition and depth layers are new
- Riverpod providers need only minor adjustments (same data, new presentation)
- Route structure unchanged — only screen internals change

## Migration Strategy

The redesign should be implemented in order to avoid breaking existing functionality:

1. **Phase 1 — Shared widgets**: Build `MediaCard`, `GlassPanel`, `ScoreRing`, `StatusPill`, `SectionHeader`,
   shimmer loading, empty/error states. Write widget tests for each. No existing screens are touched.

2. **Phase 2 — Discover refactor**: Replace `discover_screen.dart` internals with new widgets.
   Add hero strip, inline search, section headers. Keep API providers unchanged.

3. **Phase 3 — Media Detail refactor**: Replace `media_detail_screen.dart` internals with hero banner,
   glass info panel, expandable synopsis, reusing MediaCard for related.

4. **Phase 4 — My List refactor**: Replace `my_list_screen.dart` with grid layout, stats bar,
   quick-action bottom sheet. Add FAB.

5. **Phase 5 — Polish**: Add micro-animations, test all transitions, verify TV focus navigation,
   performance test BackdropFilter on low-end Android.

## Files Affected

### New Files (shared widget library)
- `lib/core/widgets/media_card.dart`
- `lib/core/widgets/media_card_grid.dart`
- `lib/core/widgets/hero_banner.dart`
- `lib/core/widgets/glass_panel.dart`
- `lib/core/widgets/score_ring.dart`
- `lib/core/widgets/status_pill.dart`
- `lib/core/widgets/progress_bar.dart`
- `lib/core/widgets/section_header.dart`
- `lib/core/widgets/app_loading.dart` (extends/replaces current)

### Modified Files (screens)
- `lib/features/discover/screens/discover_screen.dart` — full rewrite
- `lib/features/discover/widgets/media_card.dart` — **remove** (replaced by core widget)
- `lib/features/media_detail/screens/media_detail_screen.dart` — hero + tab refactor
- `lib/features/media_detail/widgets/hero_banner.dart` — **remove** (replaced by core widget)
- `lib/features/media_detail/widgets/info_tab.dart` — synopsis expand, info grid layout
- `lib/features/media_detail/widgets/episodes_tab.dart` — airing badges, watch indicators
- `lib/features/media_detail/widgets/related_carousel.dart` — reuse core MediaCard
- `lib/features/tracking/screens/my_list_screen.dart` — full rewrite
- `lib/features/tracking/widgets/progress_widget.dart` — **remove** (replaced by core progress_bar)

### Unchanged
- All providers, models, API layer, routing, auth — no changes needed
- `app_colors.dart` — palette stays the same
- `app_theme.dart` — Material theme stays the same
- `adaptive_scaffold.dart` — nav structure unchanged
