# ADR 094 — Flutter Frontend Redesign: Modern Anime Tracking UI

**Status**: Proposed
**Date**: 2026-06-19
**Supersedes**: Original ADR 094 (2026-06-18)

## Context

The current Flutter UI (Discover, Media Detail, My List screens) was built as a functional
first pass. It lacks a cohesive design system, uses one-off styling, and doesn't feel like a
premium anime tracking app. This ADR provides the complete visual and interaction specification
for a redesigned Flutter app, covering design tokens, component library, screen-by-screen design,
new API endpoints, and build order.

**Aesthetic north star**: cinematic, dark, poster-forward, and quietly alive — the energy of a
premium streaming app, but structured around a small group of friends, not a faceless public
catalogue. The artwork is the hero; the chrome recedes. This is an original design — do not
replicate any existing site's exact layout, logo, or component shapes.

## Decision

Adopt the complete design system below as the single source of truth for all Flutter UI work.
Every screen must be built from shared components — never one-off styling.

---

## 1. Design Principles

- **Content is the interface.** Cover art and banners carry the visual weight. UI chrome is
  dark, minimal, and gets out of the way. Never put a solid color block where artwork could be.
- **Dark-first, always.** This is a binge-at-night app. The dark theme is the primary theme.
  A light theme is optional and secondary.
- **Calm, not flashy.** Motion is purposeful — things ease in, lift on hover, cross-fade. No
  bouncing, no spinning, no gratuitous parallax. Restraint reads as premium.
- **The group is present.** Friends' faces, activity, and recommendations are woven throughout.
- **One tap to the thing.** The most common action on any screen is always reachable in a single
  tap, never buried in a menu.
- **Every state is designed.** Loading, empty, error, and offline states are first-class —
  never a bare spinner or a blank screen.
- **Touch and pointer both.** Hover states enhance; they're never required to reach functionality.

---

## 2. Design Tokens

Implement as a central `AppTokens` / `ThemeExtension<AppTokens>`. Never hardcode a hex value
in a widget — always reference a token.

### 2.1 Color — Dark Theme (primary)

**Surfaces** (layered depth — darker = further back):

| Token | Hex | Use |
|-------|-----|-----|
| `bg.base` | `#0B0B12` | App background (near-black, faint violet-blue tint) |
| `bg.surface` | `#14141F` | Cards, list rows |
| `bg.surfaceAlt` | `#1A1A28` | Inputs, secondary cards |
| `bg.elevated` | `#1F1F30` | Modals, bottom sheets, menus |
| `bg.hover` | `#26263A` | Hover/pressed surface tint |
| `border.subtle` | `#262636` | Hairline dividers, card borders (1px) |
| `border.strong` | `#3A3A52` | Focused inputs, emphasized edges |

**Text:**

| Token | Hex | Use |
|-------|-----|-----|
| `text.primary` | `#F4F4F8` | Titles, primary content |
| `text.secondary` | `#A6A6BD` | Subtitles, metadata |
| `text.tertiary` | `#6E6E85` | Hints, timestamps, disabled-ish |
| `text.onAccent` | `#0B0B12` | Text sitting on a bright accent fill |

**Brand & accents:**

| Token | Hex | Use |
|-------|-----|-----|
| `accent.primary` | `#7C5CFC` | Brand violet — primary buttons, active nav, links |
| `accent.primaryHover` | `#8E72FF` | Hover state |
| `accent.primaryPressed` | `#6A48E0` | Pressed state |
| `accent.primarySubtle` | `#7C5CFC` @ 14% alpha | Tinted backgrounds |
| `accent.coral` | `#FF6E8A` | Highlights, "new", live dots, secondary CTA |
| `accent.mint` | `#2FD9A8` | Progress, "watching", success |
| `accent.sky` | `#5AB0FF` | Info, "plan to watch", links in body |
| `accent.amber` | `#FFB454` | Warnings, "paused", airing-soon |
| `accent.rose` | `#FF5C6C` | Errors, "dropped", destructive |

**Brand gradient** (FAB, hero CTA, logo accent): `linear-gradient(135°, #7C5CFC → #FF6E8A)`.

**Watch-status color map:**

| Status | Color |
|--------|-------|
| watching | mint `#2FD9A8` |
| rewatching | cyan `#3FD0D9` |
| completed | accent.primary `#7C5CFC` |
| plan to watch / read | sky `#5AB0FF` |
| paused / on hold | amber `#FFB454` |
| dropped | rose `#FF5C6C` |

**Score color scale:**

| Range | Color |
|-------|-------|
| 8.5–10 | mint |
| 7.0–8.4 | green `#7FD957` |
| 5.5–6.9 | amber |
| < 5.5 | rose |
| unrated | text.tertiary |

### 2.2 Color — Light Theme

Same token names, remapped: `bg.base #F7F7FB`, `bg.surface #FFFFFF`, `bg.elevated #FFFFFF`,
`border.subtle #E6E6EF`, `text.primary #15151F`, `text.secondary #5A5A70`. Accents unchanged
but use pressed variants for text-on-light contrast. Dark remains the recommended default.

### 2.3 Typography

Three families via `google_fonts`:
- **Space Grotesk** — hero titles, big numbers, section headers with personality.
- **Plus Jakarta Sans** — everything else. Clean, geometric, excellent at small sizes.
- **Noto Sans JP** — Japanese/Korean/Chinese original titles (auto-fallback).

Two weights: 400 (regular) and 600 (semibold). Display may use 700.

| Style | Font | Size/Line | Weight | Use |
|-------|------|-----------|--------|-----|
| displayXL | Space Grotesk | 40/46 | 700 | Hero spotlight title (desktop) |
| displayL | Space Grotesk | 30/36 | 700 | Hero title (mobile), big stat numbers |
| headlineL | Space Grotesk | 24/30 | 600 | Screen titles |
| titleL | Plus Jakarta | 20/26 | 600 | Section headers |
| titleM | Plus Jakarta | 17/22 | 600 | Card titles, dialog titles |
| bodyL | Plus Jakarta | 15/22 | 400 | Primary body, synopsis |
| bodyM | Plus Jakarta | 14/20 | 400 | Secondary text, metadata |
| label | Plus Jakarta | 13/16 | 600 | Buttons, tabs, chips |
| caption | Plus Jakarta | 12/16 | 400 | Timestamps, footnotes |
| micro | Plus Jakarta | 11/14 | 600 | Badges, status pills, counters |

Always sentence case. Never ALL CAPS except a single-letter rank/badge.

### 2.4 Spacing, Radius, Layout

**Spacing scale** (4pt base): 4, 8, 12, 16, 20, 24, 32, 40, 56, 72. `space.md = 16` as default gutter.
Screen edge padding: 16 (mobile), 24 (tablet), 40 (desktop).

**Radius**: sm 10, md 14, lg 20, xl 28, pill 999. Cards use lg (20). Poster cards md (14).
Buttons pill for primary CTAs, md for secondary. Bottom sheets xl top corners only.

**Elevation** (dark UI = surface lightening + soft shadow):
- e0: flat (base)
- e1: cards — surface `bg.surface` + shadow `0 2 8 rgba(0,0,0,0.35)`
- e2: raised/hover — surface `bg.elevated` + shadow `0 8 24 rgba(0,0,0,0.45)`
- e3: modals/sheets — surface `bg.elevated` + shadow `0 16 48 rgba(0,0,0,0.55)`

**Breakpoints**: compact < 600 (phone), medium 600–1024 (tablet), expanded > 1024 (desktop).

### 2.5 Imagery & Posters

- Poster aspect ratio: always 2:3 (standard anime cover).
- Banner aspect ratio: 16:9 desktop, 3:2 mobile hero crop.
- All remote images via `cached_network_image` with shimmer skeleton placeholder and error fallback.
- Poster corner radius md (14), clipped, subtle 1px `border.subtle` inside edge.
- Lazy-load offscreen images. Decode at display size.

---

## 3. Motion & Interaction

- Durations: instant 90ms, fast 160ms, base 240ms, slow 360ms.
- Curves: `Curves.easeOutCubic` (default), `easeOutQuart` (entrances), `easeInCubic` (exits).
- Use `flutter_animate` package for declarative entrances.
- Honor `MediaQuery.disableAnimations` / reduce-motion: cut durations to instant and drop slides.

| Interaction | Spec |
|-------------|------|
| Poster card hover (pointer) | scale 1.0→1.04, shadow e1→e2, reveal title+score overlay, fast |
| Poster card press (touch) | scale 1.0→0.97, instant, release springs back |
| Page transition | shared-axis horizontal (push) / fade-through (tab switch), base |
| Bottom sheet | slide up + scrim fade, base, `easeOutQuart` |
| List item entrance | staggered fade + 12px slide-up, 40ms stagger, first paint only |
| Progress +1 tap | number rolls up (AnimatedSwitcher), mint ring pulses once, fast |
| Skeleton shimmer | 1.2s loop, diagonal sweep, `bg.surfaceAlt` → `bg.hover` |
| Tab indicator | slides under active tab, fast, `accent.primary` |
| Pull to refresh | custom indicator: small spinning ring in `accent.primary` |

---

## 4. Component Library

Build each as a reusable widget in `lib/core/widgets/`. Screens compose these only.

### 4.1 PosterCard
2:3 cached image, radius md, 1px inner border. Resting: image + ScoreChip (top-right) + thin
status rail (bottom, 3px). Hover: dark gradient scrim + title + format/year + quick-action button.
Long-press: opens QuickActionSheet. Sizes: sm (w104), md (w140), lg (w168).

### 4.2 ScoreChip
Pill, bg = score color @ 16% alpha, text = score color, micro weight. Shows ★ 8.7.

### 4.3 StatusPill
Pill colored by watch-status map. Label = status name. Optional leading 6px dot.

### 4.4 ProgressControl
Inline stepper: – Ep 5 / 12 +. +/– are circular 32px tap targets. Center tappable → number-pad sheet.
Thin progress bar under it (mint fill) when max is known. On +: optimistic update, number rolls.

### 4.5 SectionHeader
`titleL` left, optional "See all →" text button right (`accent.primary`). Optional leading accent bar.

### 4.6 ContentRail
Horizontal scrolling row of PosterCards with SectionHeader. Snap-to-card on touch; arrow buttons on
hover. Edge fade-out gradient. First card left-aligned; trailing peek of next card.

### 4.7 QuickActionSheet
Bottom sheet triggered by long-press on PosterCard or + on detail. Header: mini poster + title.
Then: status selector (segmented, colored), ProgressControl, ScoreWidget (10 half-stars),
"Recommend to a friend" row, "Add to custom list" row. Saves on dismiss (debounced) with toast.

### 4.8 FriendAvatar
Circular avatar with 2px ring. Ring = `accent.mint` if active in last 5 min. Fallback: initials
on deterministic color from brand ramp. Stackable (AvatarStack) with +N overflow.

### 4.9 AppButton
- primary: pill, gradient or solid `accent.primary`, `text.onAccent`, label weight, 44px tall.
- secondary: pill, `bg.surfaceAlt`, `text.primary`, 1px `border.subtle`.
- ghost: text only, `accent.primary`.
- destructive: solid `accent.rose`.
All: press scale 0.98, disabled at 38% opacity, loading shows inline ring.

### 4.10 AppChip / FilterChip
Pill, `bg.surfaceAlt`, selected = `accent.primarySubtle` bg + `accent.primary` text + 1px border.

### 4.11 EmptyState
Centered: large outline icon (`text.tertiary`), `titleM` line, `bodyM` subtitle, optional primary action.

### 4.12 Skeletons
PosterCardSkeleton, RailSkeleton, ListRowSkeleton, DetailSkeleton, FeedItemSkeleton.
Each mirrors the real component's dimensions exactly. Shimmer per 3.x.

### 4.13 Toast / Snackbar
Bottom-floating, `bg.elevated`, radius lg, e3. Leading status icon. Optional "Undo" action (`accent.primary`).
Auto-dismiss 4s.

### 4.14 NavigationScaffold
- Compact: bottom nav bar (5 items: Home, Search, My List, Feed, You). Floating, `bg.elevated`,
  radius xl, 12px above bottom edge with blur backdrop. Active: icon + label + `accent.primary`;
  inactive: icon only, `text.tertiary`.
- Medium: NavigationRail, collapsed (icons), left edge.
- Expanded: extended NavigationRail (icons + labels) + top bar with search and avatar.
  Notification bell with coral count badge top-right (medium/expanded) or on "You" badge (compact).

---

## 5. Information Architecture & Navigation

Primary destinations (bottom nav / rail):
- **Home** — personalized landing (spotlight, continue, friend activity, recommendations, trending).
- **Search / Discover** — search + browse by genre/season/format.
- **My List** — tracking library (tabbed by status).
- **Feed** — social hub: friend activity, recommendations inbox, discussions.
- **You** — profile, stats, watch parties, notifications, settings, group management.

Secondary (pushed routes): Media Detail, Friend Profile, Discussion Thread, Watch Party Detail,
Airing Calendar, Import, Custom List Detail, Group Management, Settings sub-pages.

Deep links: `otakuhub://media/{id}`, `otakuhub://party/{id}`, `otakuhub://group/join/{code}`.

---

## 6. Screen-by-Screen Design

See full specification in the canonical design-system document (`DESIGN-SYS.md` in docs/).

### 6.1 Home
Spotlight hero (full-width banner), "Jump back in" rail (continue watching), "From your friends"
rail (recommendations with FriendAvatar), "Your group is watching" rail, "Airing soon" rail,
"Trending in your group" rail. Pull-to-refresh. Skeleton: hero block + 3 rail skeletons.

### 6.2 Search / Discover
Search bar pinned top. Browse mode: filter chips + genre/season/top-rated rails. Search mode:
responsive poster grid. Sticky filter/sort bar. Empty: "No titles match — try fewer filters".

### 6.3 Media Detail
Full-width banner with floating poster. Title, meta row, primary action bar (sticky-ish).
Synopsis, genre chips. "In your group" strip (social differentiator — AvatarStack + ratings).
Details grid. Episodes/Chapters list, relations rail, recommendations rail, discussion preview.

### 6.4 My List
Tabs: Watching · Reading · Completed · Plan · Paused · Dropped. View toggle (grid/list).
Inline ProgressControl. Sort/filter bar. Header summary stats. Swipe actions (mobile). Empty: CTA to Search.

### 6.5 Feed
Sub-tabs: Activity, Recommendations, Discussions. Reverse-chron activity list with FriendAvatar.
Recommendations inbox. Discussion threads list with FAB to start a thread. Group selector.

### 6.6 Discussion Thread
Chat-style bubbles (yours right-aligned, others left with FriendAvatar). Spoiler blur overlay.
Composer pinned bottom. Threaded replies indent one level.

### 6.7 Friend Profile
Header card, stat row (big-number cards: watching/completed/mean score/days watched),
taste snapshot (genre chips, favorites rail), recent activity, optional compatibility flourish.

### 6.8–6.12
Watch Party, Airing Calendar, Notifications, You/Profile, Settings — see full spec.

---

## 7. States, Accessibility, Edge Cases

- **Loading**: always skeletons matching layout; never a centered spinner.
- **Empty**: every list/grid/tab has a tailored EmptyState with CTA.
- **Error**: inline error card with Retry button; friendly copy, never raw exceptions.
- **Offline**: cached data with "Offline — showing saved data" banner.
- **Accessibility**: ≥44×44 tap targets, semantic labels, text scales to 130%, ≥4.5:1 contrast,
  reduce-motion honored, full keyboard/focus support on web/desktop.
- **Localization-ready**: all strings via l10n ARB; never concatenate sentences.

---

## 8. New / Adjusted API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/home` | Composite home payload (spotlight, continue watching, friend recs, group watching, airing soon, trending) |
| `GET /api/v1/lists/me/continue` | Continue-watching feed (status=watching, ordered by recent progress) |
| `GET /api/v1/media/{id}/group-context` | Social strip on detail (group stats, members' states) |
| `GET /api/v1/media/browse` | Discover browse rails (by=genre, season, top, trending with cursor) |
| `GET /api/v1/users/{username}/stats` | Profile stat cards (watching, completed, mean score, top genres) |
| `GET /api/v1/users/{username}/compatibility` | Taste-match flourish (%, shared titles, score correlation) |
| `GET /api/v1/social/feed` (extended) | Group consecutive events, cursor pagination |
| `POST/GET /api/v1/media/{id}/source-preference` | User's pinned "where to watch" source |
| Field additions | `banner_image`, `format`, `season_year`, `average_score`, `user_entry` on summaries; `avatar_url` + `display_name` on feed items; `airing_at` on airing endpoints |

If any conflict with `docs/api-spec.md`, prefer extending existing endpoints and update both
`docs/api-spec.md` and `docs/database-schema.md` accordingly.

---

## 9. Flutter Implementation Notes

- **Theming**: `AppTheme.dark()` with `ThemeData(useMaterial3: true, ...)` + custom
  `ColorScheme.fromSeed` overridden by tokens + `ThemeExtension<AppTokens>` + `TextTheme` from
  `google_fonts`.
- **Packages**: `google_fonts`, `cached_network_image`, `shimmer`, `flutter_animate`, `go_router`,
  `flutter_riverpod`, `visibility_detector`, `flutter_staggered_grid_view`, `intl`.
- **Responsiveness**: one `Responsive` helper → `isCompact/isMedium/isExpanded`; `LayoutBuilder`.
- **Performance**: `const` everywhere; `ListView.builder/SliverList`; `cacheExtent` tuned;
  decode images at target size; debounce search; paginate with cursors.
- **Composition rule**: screens assembled from Section 4 components only. If a screen needs a
  new visual, add it to the component library first.
- **Definition of done per screen**: all 4 states (loading/empty/error/data), responsive at all
  3 breakpoints, reduce-motion respected, semantic labels, `dart analyze` clean, widget test for
  loading + error + data.

---

## 10. Build Order

1. **Tokens** + `AppTheme.dark()` + `ThemeExtension<AppTokens>` + typography.
2. **Core components** (order): PosterCard, ScoreChip, StatusPill, ProgressControl, SectionHeader,
   ContentRail, FriendAvatar/AvatarStack, AppButton, AppChip, EmptyState, Skeletons, Toast,
   QuickActionSheet, NavigationScaffold.
3. **Redesign screens** (order): Home → Media Detail → My List → Search/Discover → Feed →
   Discussion → Profile → Watch Party → Airing Calendar → Notifications → Settings/Group.
4. **Add Section 8 endpoints** as each screen needs them (Home first → endpoint 8.1).
5. **Light theme** last (optional).
6. **Full accessibility + reduce-motion pass**.

Update `PROJECT-STATUS.md` as each component and screen is completed.

---

## Consequences

**Good**:
- Cohesive, premium visual identity across all platforms.
- Shared component library means consistent UX and faster feature development.
- Design tokens prevent hardcoded values and enable future light theme.
- New composite API endpoints reduce round-trips (Home = 1 call instead of 4+).
- Social differentiator ("In your group" strip) leverages the core value prop.
- All states designed — no blank screens or raw spinners.

**Bad**:
- Significant upfront investment (~10–14 screens, 14 components, 9 new endpoints).
- Requires design token discipline from every developer.
- New API endpoints need backend work alongside Flutter work.
- Must maintain backwards compatibility with existing routes during migration.

**Neutral**:
- Dark theme is the primary design; light theme is deferred.
- 5-phase migration strategy from original ADR 094 folded into the 10-part build order.
- The Vue reference code is not affected — this is Flutter-only.
