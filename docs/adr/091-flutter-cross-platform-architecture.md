# ADR 091 — Flutter Cross-Platform Architecture

**Status**: Accepted
**Date**: 2026-06-09

## Context

OtakuHub needs to support **mobile, desktop, web, TV, and tablet** from a single codebase. The current frontend (Vue 3 + Vite + Tailwind + shadcn-vue) covers web and desktop (via Electron) but cannot target TV at all, and mobile (via Capacitor) feels like a web app in a WebView wrapper rather than a native experience.

The requirements are:
1. **Single codebase** for all target platforms — not separate projects per platform
2. **TV support** — Android TV and Fire TV with remote/D-pad navigation
3. **Tablet support** — adaptive layouts with proper split-pane and multi-column
4. **Desktop** — native Windows, macOS, Linux executables
5. **Mobile** — native Android and iOS with platform-appropriate UX
6. **Web** — full web support via Flutter for Web

## Options Considered

### Option A: Vue 3 + Vite + Tailwind + Capacitor (current)
- **Pros**: Existing codebase, Vue code is written
- **Cons**: No TV support, WebView mobile feels non-native, Electron desktop is ~150MB, Capacitor mobile lacks native transitions

### Option B: Vue 3 + separate Android TV app
- **Pros**: Keeps Vue for web/desktop
- **Cons**: Two codebases to maintain, TV app is standalone Kotlin/Java

### Option C: Flutter
- **Pros**: True single codebase for all targets, native performance on mobile/desktop, Material 3 adaptive layouts, Focus widget for TV D-pad, growing ecosystem
- **Cons**: Complete frontend rewrite, new language (Dart), fewer web-specific APIs than Vue

### Option D: React Native + React Native TV + RN Desktop
- **Pros**: JavaScript ecosystem
- **Cons**: Three separate projects with different APIs, fragmented maintenance

## Decision

**Adopt Flutter as the primary frontend framework**.

The Vue 3 code in `frontend/` is **kept as reference** — not deleted. It represents the design patterns, UX decisions, and API integration patterns that the Flutter app should replicate. All new frontend work targets Flutter.

### Project Structure
```
otakuhub/
├── frontend/                ← Vue 3 reference code (kept as-is, not removed or moved)
│   ├── src/                 ← Vue components, stores, composables
│   ├── ...                  ← All existing files remain
│   └── flutter/             ← NEW: Flutter project (the active frontend)
│       ├── lib/
│       ├── test/
│       ├── pubspec.yaml
│       └── ...
├── backend/                 ← Unchanged (FastAPI)
├── docs/
│   ├── flutter-architecture.md   ← NEW: Flutter architecture doc
│   └── ...
└── ...
```

### Why Flutter Over Alternatives

| Factor | Flutter | Vue + Capacitor | React Native |
|--------|---------|----------------|--------------|
| TV (Android TV, Fire TV) | ✅ Built-in Focus widget | ❌ Not possible | ⚠️ Separate project |
| Mobile native feel | ✅ Native ARM | ❌ WebView | ✅ JavaScript bridge |
| Desktop native | ✅ Windows/Mac/Linux | ❌ Electron only | ⚠️ RN Windows (separate) |
| Web | ✅ Flutter for Web | ✅ Native Vue | ⚠️ RN Web (separate) |
| Single codebase | ✅ Yes | ❌ No TV | ❌ 3 projects |
| Performance | ✅ Skia/Impeller render | ⚠️ DOM/Electron | ⚠️ JS Bridge |
| State management | ✅ Riverpod | ✅ Pinia | ❌ Boilerplate-heavy |
| Material 3 | ✅ Native | ⚠️ shadcn-vue | ❌ Third-party |

## Consequences

**Good**:
- True single codebase for all 5+ target platforms
- Native performance on mobile and desktop
- TV support via same APK with Focus widget + D-pad navigation
- Material 3 theming with full custom ColorScheme (aniwaves dark palette)
- Riverpod provides clean async state management similar to Pinia patterns
- Flutter's LayoutBuilder + breakpoints provide the same responsive pattern as Tailwind

**Bad**:
- Complete frontend rewrite from Vue 3 to Dart/Flutter
- Team must learn Dart and Riverpod (if not already familiar)
- Vue reference code (`frontend/`) becomes read-only — no dual-maintenance
- Flutter for Web is not as SEO-friendly as SSR Vue (not a concern — private app)

**Neutral**:
- `frontend/` directory now contains two projects: `frontend/` (Vue reference) and `frontend/flutter/` (active Flutter)
- Backend API stays identical — no backend changes needed
- All existing Pinia stores, composables, and Vue components serve as design reference only
- CI/CD needs updating to build Flutter on each platform

## Migration Strategy

### Phase F1 — Flutter Foundation
- `flutter create` in `frontend/flutter/`
- GoRouter + ShellRoute + auth guard
- Dio client with auth interceptor
- Riverpod + flutter_secure_storage
- Dark Material 3 theme (aniwaves palette)
- Web + Windows + Android builds verified

### Phase F2 — Auth & Setup
- Login screen, Register screen, Setup bootstrap screen
- Auth provider (login, register, refresh, logout)
- Auth guard redirect logic
- Token persistence with flutter_secure_storage

### Phase F3 — Discover & Media Detail
- Search, trending, new releases tabs
- Media detail with hero, episodes, info, related tabs
- media_card, hero_banner, episode_item, related_carousel

### Phase F4 — Tracking & Lists
- My List with status tabs (watching, completed, paused, dropped, plan)
- Progress/score update widgets
- Airing calendar
- Import from AniList/MAL

### Phase F5 — Social Features
- Activity feed (group + personal)
- Recommendations (inbox + sent)
- Discussions (threads + replies)

### Phase F6 — Watch Party
- Party list (upcoming + past)
- Create party with form
- RSVP and detail view

### Phase F7 — Notifications
- Inbox (all + unread)
- Preferences (content + channels)

### Phase F8 — Profile
- Profile overview, edit profile, account & security

### Phase F9 — TV Optimization
- Focus widget integration across all screens
- TV-optimized layouts for hero, cards, lists
- Remote control D-pad navigation testing

### Phase F10 — Polish & Cross-Platform QA
- Full test coverage
- Build verification on all targets
- Performance profiling (especially web)
- Visual QA against aniwaves.ru design reference
