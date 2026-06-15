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
| Discover | `features/discover/` | MediaItem, SearchResult |
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
| `core/theme/app_theme.dart` | Material 3 dark theme (aniwaves palette) |
| `core/theme/app_colors.dart` | Semantic color constants |
| `core/router/app_router.dart` | GoRouter config with routes + guards |
| `core/router/route_names.dart` | String constants for all route names |
| `core/widgets/adaptive_scaffold.dart` | Desktop/mobile/TV adaptive shell |
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
  → If true and route is /auth/* → redirect to /discover

Token Refresh:
  → Dio interceptor catches 401
  → AuthNotifier.refreshToken() → POST /api/v1/auth/refresh
  → On success: retry original request with new token
  → On failure: logout, redirect to login
```

### Navigation Structure
```
GoRouter
├── ShellRoute (AdaptiveScaffold)
│   ├── /discover           → DiscoverScreen
│   ├── /media/:id          → MediaDetailScreen
│   ├── /search             → SearchResultsScreen
│   ├── /list               → MyListScreen
│   ├── /calendar           → AiringCalendarScreen
│   ├── /feed               → FeedScreen
│   ├── /recommendations    → RecommendationsScreen
│   ├── /discussions        → DiscussionScreen
│   ├── /discussions/:id    → DiscussionDetailScreen
│   ├── /watchparty         → WatchPartyListScreen
│   ├── /notifications      → NotificationsScreen
│   ├── /notifications/preferences → PreferencesScreen
│   └── /profile            → ProfileScreen
├── /auth/login             → LoginScreen (no shell)
├── /auth/register          → RegisterScreen (no shell)
└── /setup                  → SetupScreen (no shell)
```

### AdaptiveScaffold Behavior
| Width | Type | Nav Style | Grid Cols |
|-------|------|-----------|-----------|
| < 600 | Phone | Bottom NavigationBar | 2 columns |
| 600–1024 | Tablet | NavigationRail | 3 columns |
| > 1024 | Desktop | Persistent NavigationDrawer | 4–5 columns |
| TV | TV | Focus-based NavigationRail | 5–6 large cards |

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

## Design System

### Dark Theme (aniwaves.ru-inspired)
| Token | Hex | Usage |
|-------|-----|-------|
| `bgPrimary` | `#0A0A0A` | Scaffold background |
| `bgSecondary` | `#111111` | Card/section background |
| `bgElevated` | `#1A1A1A` | Sheet/dialog background |
| `accentPrimary` | `#A855F7` | Purple accent (buttons, links, selection) |
| `accentSecondary` | `#06B6D4` | Cyan accent (badges, tags, SUB label) |
| `textPrimary` | `#FFFFFF` | Primary text |
| `textSecondary` | `#A1A1AA` | Secondary text |
| `textMuted` | `#6B7280` | Disabled/placeholder text |
| `borderDefault` | `#1F2937` | Default borders |
| `borderStrong` | `#374151` | Strong borders |
| `success` | `#22C55E` | Success state |
| `warning` | `#EAB308` | Warning state |
| `destructive` | `#EF4444` | Error/destructive state |

### Typography
| Style | Size/Weight | Usage |
|-------|-------------|-------|
| Display | 36px Bold | Page titles |
| Heading XL | 30px Bold | Section headers |
| Heading LG | 24px Semibold | Card titles |
| Heading MD | 20px Semibold | List item titles |
| Heading SM | 16px Semibold | Subsection headers |
| Body | 14px Normal | Content text |
| Body SM | 13px Normal | Descriptions |
| Label | 12px Medium | Labels, timestamps |
| Caption | 11px Normal | Small metadata |

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
- Auth flow: login → navigate to discover
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
