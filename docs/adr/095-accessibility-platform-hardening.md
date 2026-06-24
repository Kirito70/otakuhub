# ADR 095 — F11.13 Accessibility + Platform Hardening

**Status**: Accepted  
**Date**: 2026-06-23  
**Depends on**: ADR 094 (design system, tokens, component library)  

## Context

ADR 094's build order (Section 16) specifies "Platform-specific hardening (TV D-pad, desktop keyboard shortcuts, web PWA)" as the final sub-phase of Phase F11. The preceding 11 sub-phases (F11.1–F11.11) delivered the full design system, component library, and all redesigned screens across 8 features.  

F11.13 is a quality and accessibility pass that makes the app usable by more people on more platforms:

1. **Reduce motion** — Users who set "Reduce motion" in their OS accessibility settings should not see unnecessary animations.
2. **Screen reader support** — All interactive elements must have `Semantics` labels. Compound cards use `MergeSemantics`. Decorative elements use `ExcludeSemantics`.
3. **TV D-pad** — The `FocusableWidget` infrastructure (from F9) must wrap interactive elements across all remaining features, not just the 3 widgets it currently covers.
4. **Desktop keyboard shortcuts** — Beyond `Ctrl+K` for search, add `Escape` to close overlays, `Enter`/`Space` for primary actions, and arrow navigation for grids.
5. **Web PWA** — The default Flutter web manifest uses placeholder colors and description. Fix it.

## Decision

### 1. Reduce Motion — Centralized Animation Token System

**Create** `AnimationTokens` as a `ThemeExtension<AnimationTokens>` with `Duration` fields enumerated by use case:

```dart
class AnimationTokens extends ThemeExtension<AnimationTokens> {
  final Duration fast;      // 100ms — press feedback, focus borders
  final Duration normal;    // 200ms — standard transitions
  final Duration slow;      // 400ms — page transitions, hero animations
  final Duration shimmer;   // 1600ms — skeleton shimmer period
  final Duration toast;     // 300ms — toast slide/fade
}
```

**Create a helper** `withReducedMotion(BuildContext context)` that returns `Duration.zero` when `MediaQuery.disableAnimations(context)` is true.

**Pattern**: Every hardcoded `Duration(milliseconds: N)` in `lib/core/widgets/` and `lib/features/` must be replaced with `AnimationTokens` lookups. Skeleton shimmer uses `AnimationPeriod(period: tokens.shimmer)` only when animations enabled, else shows static skeleton.

**Files to change**: All animation durations in `focusable_widget.dart`, `app_button.dart`, `app_chip.dart`, `app_toast.dart`, `progress_control.dart`, `quick_action_sheet.dart`, `skeletons.dart`, `search_overlay.dart`, `home_screen.dart`, `notification_card.dart`.

### 2. Semantics Audit — Labels, MergeSemantics, ExcludeSemantics

**All interactive elements** must have `semanticLabel`:
- `FocusableWidget` and `FocusableTile` already accept `semanticLabel` — pass it from every call site
- `AppButton` should accept and forward `semanticLabel`
- `AppChip` should accept and forward `semanticLabel`
- `PosterCard` / `MediaCard` should use `MergeSemantics` wrapping image + title + subtitle for screen-reader efficiency
- `NavigationRail` destinations and `BottomNavigationBar` items must have labels
- Filter chips, tab bars, discussion list tiles, notification cards, watch party cards, profile tiles — all need labels

**Decorative elements** use `ExcludeSemantics(child: ...)`:
- Background images, banner gradients, spacer icons, purely visual decorations

**Forms (Login, Register, Setup, Edit Profile)**:
- Each `TextFormField` must have `semanticLabel` on its `InputDecoration`
- Validation error messages need `Semantics(liveRegion: true, child: errorText)`

### 3. TV D-pad — Extend FocusableWidget Coverage

Currently only 3 feature widgets use `FocusableWidget`/`FocusableTile`:
- `media_card.dart` (discover)
- `score_widget.dart` (tracking)
- `progress_widget.dart` (tracking)

**Add FocusableWidget wrapper to**:
- All discussion list tiles (`social/screens/discussion_list_screen.dart`)
- Discussion reply tiles (`social/screens/discussion_detail_screen.dart`)
- Recommendation cards (`social/screens/recommendations_screen.dart`)
- Feed items (`social/screens/feed_screen.dart`)
- Notification cards (`notifications/screens/notifications_screen.dart`)
- Watch party cards (`watchparty/screens/watch_party_screen.dart`)
- Profile settings tiles (`profile/`)
- All `AppButton` instances (already handled via `AppButton` → use `FocusableWidget` internally when on TV)
- Calendar grid items (`tracking/screens/airing_calendar_screen.dart`)
- Episode/chapter list items (`media_detail/widgets/episodes_tab.dart`)
- Related media carousel items (`media_detail/widgets/related_carousel.dart`)

**Add FocusTraversalGroup** with `OrderedTraversalPolicy` for logical D-pad flow on:
- Navigation rail destinations
- Tab bars
- Grid layouts (calendar, related media)

### 4. Desktop Keyboard Shortcuts

Current: Only `Ctrl+K` / `Meta+K` for search (in `AdaptiveScaffold`).

**Add a global `Shortcuts` widget** in `OtakuHubApp` wrapping the `MaterialApp`:

| Shortcut | Action | Scope |
|----------|--------|-------|
| `Escape` | Close overlay / bottom sheet / dialog | Global |
| `Ctrl+,` | Open settings/profile | Global |
| `Ctrl+1`–`Ctrl+5` | Navigate to nav destinations (Home, List, Feed, Alerts, Profile) | Global |
| `Enter` / `Space` | Activate focused item | Widget level (via `FocusableWidget` already) |
| `Arrow keys` | Navigate grid/list items | `FocusTraversalGroup` |

Implementation: Use `CallbackShortcuts` in the app's root alongside `Focus`.

### 5. Web PWA — Manifest + Theme Color

**Update `web/manifest.json`**:
```json
{
  "name": "OtakuHub",
  "short_name": "OtakuHub",
  "description": "Anime, manga, and manhwa tracking for you and your friends.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0A0A0A",
  "theme_color": "#A855F7",
  "icons": [ ... ]  // keep existing icon references
}
```

**Update `web/index.html`**:
- Add `<meta name="theme-color" content="#0A0A0A">`
- Add apple splash screen meta tags

## Consequences

**Good**:
- Screen reader users can navigate the full app.
- Reduce-motion users get a static, comfortable experience.
- TV users (Android TV, Fire TV) get full D-pad navigation.
- Desktop power users get keyboard-driven workflows.
- Web users get a proper PWA install prompt with branded colors.

**Bad**:
- ~70+ widgets need semantics labels added — careful to avoid test breakage.
- FocusableWidget wrapping in list items may slightly increase widget tree depth.
- Global keyboard shortcuts could conflict with browser defaults on web (mitigated: avoid `Ctrl+S`, `Ctrl+P`, etc.)

**Neutral**:
- No backend changes needed (pure frontend).
- No database schema changes.
- No new dependencies — all work uses Flutter's built-in `Focus`, `Semantics`, and `Shortcuts` APIs.

## Implementation Order

1. **Animation tokens + reduce motion** (smallest surface area, touches core widgets)
2. **Semantics audit** (largest change, touches every feature but per-widget scoped)
3. **TV D-pad extension** (wraps existing widgets, very low risk)
4. **Desktop shortcuts** (additive — won't break existing)
5. **Web PWA** (standalone file edits)
