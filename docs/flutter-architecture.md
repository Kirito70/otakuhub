# OtakuHub — Flutter Frontend Architecture

## Overview
Cross-platform Flutter app targeting **mobile (Android/iOS), desktop (Windows/macOS/Linux), web, TV (Android TV/Fire TV), and tablet** from a single Dart codebase.

The Vue 3 code in `frontend/` is kept as reference material — the Flutter app reimplements all features natively.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Framework | Flutter 3.x (stable channel, Dart 3.x) |
| State Management | Riverpod 2.x (providers, notifiers, families) |
| Router | GoRouter with ShellRoute, auth redirect guard |
| HTTP | Dio with auth interceptor (token refresh on 401) |
| Secure Storage | `flutter_secure_storage` (mobile/desktop) |
| Preferences | `shared_preferences` (settings, onboarding flags) |
| Models | `freezed` + `json_serializable` (immutable data classes) |
| Architecture | Feature-first: `lib/features/<name>/` |
| Testing | `flutter_test` + `mocktail` |
| Integration | `integration_test` (cross-platform) |

## Target Platforms

| Platform | Build Command | Notes |
|----------|-------------|-------|
| Android | `flutter build apk` or `flutter build appbundle` | Same APK also runs on Android TV / Fire TV |
| iOS | `flutter build ios` (requires macOS + Xcode) | |
| Web | `flutter build web` | CanvasKit renderer for pixel-perfect |
| Windows | `flutter build windows` | Native Windows executable |
| macOS | `flutter build macos` | Native macOS app |
| Linux | `flutter build linux` | Native Linux app |
| Android TV | Same APK as Android | Focus widgets + D-pad navigation |
| Fire TV | Same APK as Android | Amazon Appstore deploy |

## Feature-First Structure
Every feature is a self-contained module with models, providers, screens, and widgets:

```
lib/features/<name>/
├── models/          ← Data classes (freezed, fromJson/toJson)
├── providers/       ← Riverpod providers (notifiers, futures, families)
├── screens/         ← Full-page ConsumerWidget/ConsumerStatefulWidget
└── widgets/         ← Reusable sub-components (cards, tiles, forms)
```

### Currently Planned Features
| Feature | Directory | Key Models |
|---------|-----------|------------|
| Auth | `features/auth/` | LoginRequest, TokenResponse |
| Home | `features/home/` | HomeData, SpotlightItem, ContentRail |
| Media Detail | `features/media_detail/` | MediaDetail, EpisodeItem, ChapterItem |
| Tracking | `features/tracking/` | ListEntry, CustomList |
| Social | `features/social/` | FeedItem, Recommendation, Discussion |
| Watch Party | `features/watchparty/` | WatchParty, RSVP |
| Notifications | `features/notifications/` | NotificationItem, Preferences |
| Profile | `features/profile/` | UserProfile, UserSettings |

## Core Layers

### Core (`lib/core/`)
Shared infrastructure used by every feature.

| Module | Purpose |
|--------|---------|
| `core/api/api_client.dart` | Dio instance, auth interceptor, base URL config |
| `core/api/api_exceptions.dart` | Typed exceptions (401, 404, 422, 500) |
| `core/auth/auth_provider.dart` | AuthNotifier — login, register, refresh, logout |
| `core/auth/storage_service.dart` | `flutter_secure_storage` wrapper for tokens |
| `core/theme/app_theme.dart` | Material 3 dark theme (AppTokens design system) |
| `core/theme/app_colors.dart` | Semantic color constants (legacy — use AppTokens) |
| `core/theme/app_tokens.dart` | ADR 094 design tokens — ThemeExtension with 41 tokens |
| `core/router/app_router.dart` | GoRouter config with routes + guards |
| `core/router/route_names.dart` | String constants for all route names |
| `core/widgets/adaptive_scaffold.dart` | Desktop/mobile/TV adaptive shell with search header |
| `core/widgets/search_overlay.dart` | Universal search overlay — single search surface |
| `core/widgets/app_empty_state.dart` | Loading / error / empty state widget |
| `core/widgets/app_badge.dart` | Notification badge overlay |

### Auth Flow
```
LoginScreen
  → AuthNotifier.login(username, password)
    → Dio POST /api/v1/auth/login
    → Store access_token + refresh_token in flutter_secure_storage
    → Update auth_provider state (isAuthenticated = true)

GoRouter redirect:
  → Check auth_provider.isAuthenticated
  → If false and route requires auth → redirect to /auth/login
  → If true and route is /auth/* → redirect to /home

Token Refresh:
  → Dio interceptor catches 401
  → AuthNotifier.refreshToken() → POST /api/v1/auth/refresh
  → On success: retry original request with new token
  → On failure: logout, redirect to login
```

### Navigation Structure (ADR 096)
**5 primary nav items**: Home · List · Feed · Alerts · Profile

Search is a **shell-level capability**, not a page — always accessible from the header via `SearchOverlay`.

```
GoRouter
├── ShellRoute (AdaptiveScaffold) — search always in header
│   ├── /home               → HomeScreen (hero + content rails)
│   ├── /list               → ListScreen (sub-tabs: Your List, Discover, Calendar)
│   ├── /feed               → FeedScreen
│   ├── /notifications      → NotificationsScreen
│   ├── /notifications/preferences → PreferencesScreen
│   ├── /profile            → ProfileScreen
│   └── /media/:id          → MediaDetailScreen
├── /auth/login             → LoginScreen (no shell)
├── /auth/register          → RegisterScreen (no shell)
└── /setup                  → SetupScreen (no shell)
```

**Removed routes** (ADR 096): `/search` (SearchResultsScreen eliminated, `/discover` → `/home` redirect), `/discover` (DiscoverScreen replaced by HomeScreen), `/calendar` (moved to List sub-tab), `/watchparty` (moved from primary nav to Profile sub-page, route kept for direct access), `/recommendations` (merged into Feed), `/discussions/:id` (merged into Feed).

**Deep links**: `otakuhub://media/{id}`, `otakuhub://party/{id}`, `otakuhub://group/join/{code}`.

### AdaptiveScaffold Behavior (ADR 096)
| Width | Type | Nav Style | Search | Grid Cols |
|-------|------|-----------|--------|-----------|
| < 600 | Phone | Bottom NavigationBar (5 items) | Search icon in AppBar → opens SearchOverlay (slide-up) | 2 columns |
| 600–1024 | Tablet | NavigationRail (collapsed) | Persistent search bar in header | 3 columns |
| > 1024 | Desktop | NavigationRail (extended) | Persistent search bar in header. Ctrl+K/Cmd+K keyboard shortcut opens search from anywhere. | 4–5 columns |
| TV | TV | Focus-based NavigationRail | Search icon in rail → opens SearchOverlay | 5–6 large cards |

## State Management (Riverpod)

### Provider Types
```dart
// Simple state
final counterProvider = StateProvider<int>((ref) => 0);

// Computed / derived
final doubleCounterProvider = Provider<int>((ref) {
  return ref.watch(counterProvider) * 2;
});

// Async data fetching
final mediaDetailProvider = FutureProvider.family<MediaDetail, String>((ref, id) async {
  final api = ref.read(apiClientProvider);
  final response = await api.get('/api/v1/media/$id');
  return MediaDetail.fromJson(response.data);
});

// Notifier (complex state + methods)
final authProvider = NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);
```

### Auth Provider Pattern
```dart
@freezed
class AuthState with _$AuthState {
  const factory AuthState({
    @Default(false) bool isAuthenticated,
    @Default(false) bool isLoading,
    String? error,
    User? user,
  }) = _AuthState;
}

class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    _checkExistingToken();
    return AuthState();
  }

  Future<void> login(String username, String password) async { ... }
  Future<void> register(...) async { ... }
  Future<bool> refreshToken() async { ... }
  Future<void> logout() async { ... }
}
```

## HTTP Client (Dio)

### Interceptor Chain
1. **AuthInterceptor**: Attach `Authorization: Bearer <token>` to every request
2. **RetryInterceptor**: Catch 401, attempt token refresh, retry request
3. **LogInterceptor**: Log request/response for debugging (disabled in prod)

### API Endpoint Constants
```dart
class ApiEndpoints {
  static const baseUrl = 'http://localhost:8000';
  static const auth = '/api/v1/auth';
  static const media = '/api/v1/media';
  static const lists = '/api/v1/lists';
  static const social = '/api/v1/social';
  static const watchParty = '/api/v1/watchparty';
  static const notifications = '/api/v1/notifications';
  static const sync = '/api/v1/sync';
  static const admin = '/api/v1/admin';
  static const setup = '/api/v1/setup';
  static const users = '/api/v1/users';
}
```

## Search Architecture (ADR 096)

Search is a **shell-level capability**, not a page. There is exactly one search surface: `SearchOverlay`. No separate search route, no search tab inside any screen.

### Search Flow
```
User taps search (icon or bar)
  ↓
SearchOverlay opens (slide-up on mobile, slide-down on desktop/tablet)
  ↓
┌─ Empty state (no query) ──────────────────────┐
│  • Recent searches (from shared_preferences)  │
│  • Trending searches (from GET /search/suggest)│
│  • Quick genre chips                           │
└────────────────────────────────────────────────┘
  ↓ User types
┌─ Typing state (300ms debounce) ───────────────┐
│  • Loading: skeleton cards (3 per group)       │
│  • Results: grouped by media type              │
│    Anime (12)   Manga (5)   Manhwa (3)         │
│  • "View all N results" per type               │
└────────────────────────────────────────────────┘
  ↓
┌─ Result tap ───────────────────────────────────┐
│  → Dismiss overlay                             │
│  → GoRouter.push /media/{id}                   │
└────────────────────────────────────────────────┘
```

### SearchOverlay States
| State | UX |
|-------|----|
| **Initial (no query)** | Recent searches + trending suggestions + genre chips |
| **Loading** | 3 skeleton cards per group (Shimmer) |
| **Results** | Grouped by media type with count badges, 2-col grid per group on mobile |
| **Empty (no results)** | "No titles match '{query}'" + clear button + genre chip suggestions |
| **Error** | Inline retry with friendly message |

### Keyboard Integration
| Shortcut | Action |
|----------|--------|
| `Ctrl+K` / `Cmd+K` | Open search overlay from anywhere |
| `Escape` | Close overlay |
| `↑` / `↓` | Navigate result groups |
| `Enter` | Select focused result |
| `Tab` | Move between result groups |

### Search Provider Architecture
```dart
// Core search provider — single source of truth
final searchOverlayProvider = NotifierProvider<SearchOverlayNotifier, SearchOverlayState>(
  SearchOverlayNotifier.new,
);

// Debounced query provider
final searchDebounceProvider = StateProvider<String>((ref) => '');

// API call (debounced, cancellable)
final searchResultsProvider = FutureProvider.family<SearchResults, String>(
  (ref, query) async {
    final api = ref.read(apiClientProvider);
    final response = await api.get('/api/v1/media/search', queryParams: {'q': query});
    return SearchResults.fromJson(response.data);
  },
);

// Recent searches (persisted)
final recentSearchesProvider = StateNotifierProvider<RecentSearchesNotifier, List<String>>(
  (ref) => RecentSearchesNotifier(ref.read(storageServiceProvider)),
);
```

## Design System

> **Full spec**: `docs/adr/094-flutter-frontend-redesign-modern-anime-tracking.md` (Sections 2–4)
> **Tokens implementation**: `lib/core/theme/app_tokens.dart` (41-token `ThemeExtension`)

### Token Categories
| Category | Description | Source |
|----------|-------------|--------|
| **Surfaces** (6) | App background, cards, inputs, modals, hover, borders | `AppTokens.bgBase` through `borderStrong` |
| **Text** (4) | Primary, secondary, tertiary, on-accent | `AppTokens.textPrimary` through `textOnAccent` |
| **Accents** (11) | Violet brand, coral, mint, sky, amber, rose, green | `AppTokens.accentPrimary` through `accentGreen` |
| **Spacing** (8) | 4pt scale: 4→72 | `AppTokens.spaceXs` through `space4xl` |
| **Radius** (5) | sm(10) md(14) lg(20) xl(28) pill(999) | `AppTokens.radiusSm` through `radiusPill` |
| **Elevation** (3) | Card, raised, modal shadow levels | `AppTokens.elevation1` through `elevation3` |

### Typography (ADR 094)
| Style | Font | Size/Line | Weight | Usage |
|-------|------|-----------|--------|-------|
| displayXL | Space Grotesk | 40/46 | 700 | Hero spotlight title (desktop) |
| displayL | Space Grotesk | 30/36 | 700 | Hero title (mobile), stat numbers |
| headlineL | Space Grotesk | 24/30 | 600 | Screen titles |
| titleL | Plus Jakarta | 20/26 | 600 | Section headers |
| titleM | Plus Jakarta | 17/22 | 600 | Card titles, dialog titles |
| bodyL | Plus Jakarta | 15/22 | 400 | Primary body, synopsis |
| bodyM | Plus Jakarta | 14/20 | 400 | Secondary text, metadata |
| label | Plus Jakarta | 13/16 | 600 | Buttons, tabs, chips |
| caption | Plus Jakarta | 12/16 | 400 | Timestamps, footnotes |
| micro | Plus Jakarta | 11/14 | 600 | Badges, status pills |

### TV-Specific Design
- Cards render at 1.15× scale for readability at distance
- Focus borders (2px accentPrimary) around focused elements
- Navigation uses `NavigationRail` (always visible for TV)
- Snackbars replaced with persistent toast at top of screen
- All interactive elements need `semanticLabel` for accessibility

## Testing Strategy

### Unit Tests (`test/`)
- Model serialization tests (fromJson/toJson round-trip)
- Provider logic tests (mocked API)
- Utility function tests

### Widget Tests (`test/features/<name>/`)
- Screen state tests: loading → data / loading → error → retry
- Form validation: empty submit, invalid input, submission
- Navigation: correct route on action

### Integration Tests (`integration_test/`)
- Auth flow: login → navigate to home
- Tracking flow: add to list → update progress → verify change

### Test File Naming
```
test/features/auth/
├── login_screen_test.dart
├── auth_provider_test.dart
└── auth_repository_test.dart
```

## Build Verification

Every platform build must pass before marking a phase complete:
```bash
flutter analyze           # No errors
flutter test              # All tests pass
flutter build web         # Web build succeeds
flutter build apk         # Android build succeeds
flutter build windows     # Windows build succeeds (on Windows host)
flutter build macos       # macOS build succeeds (on macOS host)
flutter build linux       # Linux build succeeds (on Linux host)
```

## Relationship to Vue Reference Code

The `frontend/` directory contains the original Vue 3 implementation (currently in transition from Quasar to Vite + Tailwind + shadcn-vue). This code is **reference-only** — do not modify it for Flutter development.

### What to Reference
- **UX patterns**: How pages are structured, what data is shown, navigation flow
- **API integration**: How Pinia stores call API endpoints (same endpoints in Flutter)
- **Error/loading states**: How the app handles loading, empty, error states
- **Form validation**: What fields exist and what rules they have

### What NOT to Reference
- **UI components**: Flutter uses Material 3, not HTML/CSS
- **State management**: Riverpod replaces Pinia (conceptually similar)
- **Styling**: Flutter uses Widget tree, not Tailwind classes
- **Router syntax**: GoRouter replaces vue-router
