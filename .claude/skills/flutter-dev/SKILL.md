---
name: flutter-dev
description: Build a Flutter feature for OtakuHub: Dart models, Riverpod providers, GoRouter pages, Firestore/API integration, and Widget tests.
---

# Flutter Feature Development Skill

## Tech Stack Summary
- **Framework**: Flutter 3.x (stable channel, Dart 3.x)
- **State**: Riverpod 2.x (providers, notifiers, families, autodispose)
- **Router**: GoRouter with ShellRoute for adaptive scaffold, auth redirect guard
- **HTTP**: Dio with auth interceptor (token attach + 401 refresh)
- **Storage**: `flutter_secure_storage` for tokens, `shared_preferences` for settings
- **Backend**: FastAPI REST API at configured base URL
- **Desktop**: Flutter Desktop (Windows, macOS, Linux via `flutter build windows/macos/linux`)
- **Mobile**: Flutter Mobile (Android, iOS via `flutter build apk/ios`)
- **Web**: Flutter for Web (`flutter build web`)
- **TV**: Android TV / Fire TV (same APK, Focus widget + remote D-pad support)
- **Tests**: `flutter_test` + `mocktail` + `integration_test`

## Project Structure (frontend/flutter/)
```
flutter/
├── lib/
│   ├── main.dart                   ← App entry, ProviderScope, MaterialApp.router
│   ├── app.dart                    ← App widget with theme, router, providers
│   ├── core/
│   │   ├── api/
│   │   │   ├── api_client.dart     ← Dio singleton with interceptors
│   │   │   ├── api_exceptions.dart ← Typed exceptions (401, 404, 422, 500)
│   │   │   └── api_endpoints.dart  ← Base URL + path constants
│   │   ├── auth/
│   │   │   ├── auth_provider.dart  ← AuthNotifier Riverpod provider
│   │   │   ├── auth_repository.dart
│   │   │   └── storage_service.dart ← flutter_secure_storage wrapper
│   │   ├── theme/
│   │   │   ├── app_theme.dart      ← Material 3 light + dark with custom ColorScheme
│   │   │   └── app_colors.dart     ← OtakuHub design tokens (aniwaves dark palette)
│   │   ├── router/
│   │   │   ├── app_router.dart     ← GoRouter config + ShellRoute + auth guard
│   │   │   └── route_names.dart    ← Named route string constants
│   │   └── widgets/
│   │       ├── adaptive_scaffold.dart  ← Desktop sidebar + mobile bottom nav
│   │       ├── app_empty_state.dart    ← Empty / error / loading state widget
│   │       └── app_badge.dart          ← Notification badge
│   ├── features/
│   │   ├── auth/
│   │   │   ├── models/
│   │   │   │   ├── login_request.dart
│   │   │   │   └── token_response.dart
│   │   │   ├── providers/
│   │   │   │   └── auth_provider.dart
│   │   │   ├── screens/
│   │   │   │   ├── login_screen.dart
│   │   │   │   └── register_screen.dart
│   │   │   └── widgets/
│   │   │       └── auth_form.dart
│   │   ├── discover/
│   │   │   ├── models/
│   │   │   │   └── media_item.dart
│   │   │   ├── providers/
│   │   │   │   ├── search_provider.dart
│   │   │   │   └── trending_provider.dart
│   │   │   ├── screens/
│   │   │   │   ├── discover_screen.dart
│   │   │   │   └── search_results_screen.dart
│   │   │   └── widgets/
│   │   │       ├── media_card.dart
│   │   │       ├── trending_carousel.dart
│   │   │       └── genre_pills.dart
│   │   ├── media_detail/
│   │   │   ├── models/
│   │   │   │   ├── media_detail.dart
│   │   │   │   └── episode.dart
│   │   │   ├── providers/
│   │   │   │   ├── media_detail_provider.dart
│   │   │   │   └── episodes_provider.dart
│   │   │   ├── screens/
│   │   │   │   └── media_detail_screen.dart
│   │   │   └── widgets/
│   │   │       ├── hero_banner.dart
│   │   │       ├── info_tab.dart
│   │   │       ├── episodes_tab.dart
│   │   │       └── related_carousel.dart
│   │   ├── tracking/
│   │   │   ├── models/
│   │   │   │   └── list_entry.dart
│   │   │   ├── providers/
│   │   │   │   └── list_provider.dart
│   │   │   ├── screens/
│   │   │   │   ├── my_list_screen.dart
│   │   │   │   └── airing_calendar_screen.dart
│   │   │   └── widgets/
│   │   │       ├── list_tile.dart
│   │   │       ├── progress_widget.dart
│   │   │       └── score_widget.dart
│   │   ├── social/
│   │   │   ├── models/
│   │   │   │   ├── feed_item.dart
│   │   │   │   ├── recommendation.dart
│   │   │   │   └── discussion.dart
│   │   │   ├── providers/
│   │   │   │   ├── feed_provider.dart
│   │   │   │   ├── recommendations_provider.dart
│   │   │   │   └── discussions_provider.dart
│   │   │   ├── screens/
│   │   │   │   ├── feed_screen.dart
│   │   │   │   ├── recommendations_screen.dart
│   │   │   │   └── discussion_screen.dart
│   │   │   └── widgets/
│   │   │       ├── activity_row.dart
│   │   │       └── rec_card.dart
│   │   ├── watchparty/
│   │   │   ├── models/
│   │   │   │   └── watch_party.dart
│   │   │   ├── providers/
│   │   │   │   └── watch_party_provider.dart
│   │   │   ├── screens/
│   │   │   │   ├── watch_party_list_screen.dart
│   │   │   │   └── create_party_screen.dart
│   │   │   └── widgets/
│   │   │       └── party_card.dart
│   │   ├── notifications/
│   │   │   ├── models/
│   │   │   │   └── notification_item.dart
│   │   │   ├── providers/
│   │   │   │   ├── inbox_provider.dart
│   │   │   │   └── preferences_provider.dart
│   │   │   ├── screens/
│   │   │   │   ├── notifications_screen.dart
│   │   │   │   └── preferences_screen.dart
│   │   │   └── widgets/
│   │   │       └── notification_tile.dart
│   │   └── profile/
│   │       ├── models/
│   │       │   └── user_profile.dart
│   │       ├── providers/
│   │       │   └── profile_provider.dart
│   │       ├── screens/
│   │       │   ├── profile_screen.dart
│   │       │   └── edit_profile_screen.dart
│   │       └── widgets/
│   │           └── profile_header.dart
│   └── tv/                       ← TV-specific layouts (Focus widgets, remote nav)
│       ├── tv_media_card.dart
│       ├── tv_hero_banner.dart
│       └── tv_adaptive_scaffold.dart
├── test/
│   ├── core/
│   │   └── api/
│   │       └── api_client_test.dart
│   ├── features/
│   │   ├── auth/
│   │   │   └── login_screen_test.dart
│   │   ├── discover/
│   │   │   └── discover_screen_test.dart
│   │   ├── media_detail/
│   │   └── ...
│   └── widget_test.dart
├── integration_test/
│   └── app_test.dart
├── pubspec.yaml
├── analysis_options.yaml         ← strict Dart analysis
└── build.yaml
```

## Execution Order
Always build in this sequence:

### Step 1 — Models (`lib/features/<name>/models/`)
- Create Dart model classes with `freezed` for immutability + JSON serialization
- Or hand-written `fromJson`/`toJson` for simple models
- Backend API response structure determines model fields
- Nullable `int?`, `String?` for fields that may not be present
- Map backend snake_case to Dart camelCase in `fromJson`

```dart
// Example: MediaItem model
import 'package:freezed_annotation/freezed_annotation.dart';
part 'media_item.freezed.dart';
part 'media_item.g.dart';

@freezed
class MediaItem with _$MediaItem {
  const factory MediaItem({
    required String id,
    required String titleRomaji,
    String? titleEnglish,
    required String mediaType,
    @Default('not_yet_released') String status,
    String? coverImageLarge,
    double? averageScore,
  }) = _MediaItem;

  factory MediaItem.fromJson(Map<String, dynamic> json) =>
      _$MediaItemFromJson(json);
}
```

### Step 2 — Providers (`lib/features/<name>/providers/`)
Riverpod providers with notifier pattern:

```dart
// Example: Discover providers
final searchQueryProvider = StateProvider<String>((ref) => '');

final searchResultsProvider = FutureProvider<List<MediaItem>>((ref) async {
  final query = ref.watch(searchQueryProvider);
  if (query.isEmpty) return [];
  final api = ref.read(apiClientProvider);
  final response = await api.get('/api/v1/media/search', queryParameters: {'q': query});
  return (response.data['results'] as List)
      .map((json) => MediaItem.fromJson(json))
      .toList();
});
```

### Step 3 — Screens (`lib/features/<name>/screens/`)
- Use ConsumerWidget or ConsumerStatefulWidget
- Always handle: loading → error → empty → content states
- Use `ref.watch()` for providers, `ref.read()` for actions
- Responsive: `LayoutBuilder` + breakpoints for tablet/desktop/mobile

```dart
class DiscoverScreen extends ConsumerWidget {
  const DiscoverScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final searchResults = ref.watch(searchResultsProvider);
    return searchResults.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, stack) => AppEmptyState(
        icon: Icons.error_outline,
        message: 'Failed to load',
        actionLabel: 'Retry',
        onAction: () => ref.invalidate(searchResultsProvider),
      ),
      data: (items) => items.isEmpty
          ? const AppEmptyState(message: 'No results found')
          : GridView.builder(
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: context.isMobile ? 2 : (context.isTablet ? 3 : 5),
                childAspectRatio: 0.7,
              ),
              itemBuilder: (context, index) => MediaCard(item: items[index]),
              itemCount: items.length,
            ),
    );
  }
}
```

### Step 4 — Router (`lib/core/router/app_router.dart`)
```dart
final appRouterProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authProvider);
  return GoRouter(
    initialLocation: '/discover',
    redirect: (context, state) {
      final isLoggedIn = auth.isAuthenticated;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');
      if (!isLoggedIn && !isAuthRoute) return '/auth/login';
      if (isLoggedIn && isAuthRoute) return '/discover';
      return null;
    },
    routes: [
      ShellRoute(
        builder: (context, state, child) => AdaptiveScaffold(child: child),
        routes: [
          GoRoute(path: '/discover', ...),
          GoRoute(path: '/media/:id', ...),
          GoRoute(path: '/list', ...),
        ],
      ),
      GoRoute(path: '/auth/login', ...),
      GoRoute(path: '/auth/register', ...),
    ],
  );
});
```

### Step 5 — Widget Tests (`test/features/<name>/`)
- Use `ProviderScope.overrides` to inject mock providers
- Use `mocktail` for Dio/mock API responses
- Test: loading state renders skeleton, error state shows retry, data state renders list
- Use `pumpWidget` + `pumpAndSettle` for async operations

```dart
testWidgets('shows loading then data', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [searchResultsProvider.overrideWith(...)],
      child: const MaterialApp(home: DiscoverScreen()),
    ),
  );
  expect(find.byType(CircularProgressIndicator), findsOneWidget);
  await tester.pumpAndSettle();
  expect(find.text('Solo Leveling'), findsOneWidget);
});
```

## Adaptive Layout Pattern

### Breakpoints
| Width | Target | Layout |
|-------|--------|--------|
| < 600px | Mobile phone | Bottom navigation bar, single column |
| 600–1024px | Tablet | Side navigation rail, 2–3 column grids |
| > 1024px | Desktop | Persistent side drawer, 4–5 column grids |
| TV | TV (large) | Focus-based navigation, large card grids, D-pad remote |

### AdaptiveScaffold usage
```dart
class AdaptiveScaffold extends StatelessWidget {
  final Widget child;
  const AdaptiveScaffold({required this.child, super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        if (width < 600) {
          return _MobileScaffold(child: child);
        } else if (width < 1024) {
          return _TabletScaffold(child: child);
        } else {
          return _DesktopScaffold(child: child);
        }
      },
    );
  }
}
```

## Dio Client Pattern

```dart
// lib/core/api/api_client.dart
final apiClientProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: AppConstants.apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));

  dio.interceptors.add(AuthInterceptor(ref));
  dio.interceptors.add(LogInterceptor(responseBody: true));
  return dio;
});

class AuthInterceptor extends Interceptor {
  final Ref ref;
  AuthInterceptor(this.ref);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = ref.read(storageServiceProvider).getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Attempt token refresh
      final success = await ref.read(authProvider.notifier).refreshToken();
      if (success) {
        // Retry original request
        final token = await ref.read(storageServiceProvider).getAccessToken();
        err.requestOptions.headers['Authorization'] = 'Bearer $token';
        final response = await Dio(BaseOptions()).fetch(err.requestOptions);
        handler.resolve(response);
        return;
      }
      // Refresh failed → logout
      ref.read(authProvider.notifier).logout();
    }
    handler.next(err);
  }
}
```

## Theme Pattern (aniwaves dark palette)

```dart
// lib/core/theme/app_theme.dart
class AppTheme {
  static ThemeData dark() {
    const colorScheme = ColorScheme.dark(
      primary: Color(0xFFA855F7),       // Purple accent
      secondary: Color(0xFF06B6D4),     // Cyan accent
      surface: Color(0xFF111111),       // Card bg
      background: Color(0xFF0A0A0A),    // Page bg
      error: Color(0xFFEF4444),         // Destructive
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: const Color(0xFF0A0A0A),
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF0A0A0A),
        elevation: 0,
      ),
      cardTheme: CardTheme(
        color: const Color(0xFF111111),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: const BorderSide(color: Color(0xFF1F2937)),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: const Color(0xFF0A0A0A),
        indicatorColor: const Color(0xFFA855F7).withValues(alpha: 0.2),
      ),
    );
  }
}
```

## TV Support Pattern
TV (Android TV / Fire TV) uses the same APK with focus-based navigation:

```dart
// Use Focus widget for D-pad navigation
Focus(
  focusNode: focusNode,
  onFocusChange: (hasFocus) {
    setState(() => _isFocused = hasFocus);
  },
  child: AnimatedContainer(
    duration: const Duration(milliseconds: 200),
    transform: _isFocused ? Matrix4.identity()..scale(1.05) : Matrix4.identity(),
    child: MediaCard(item: item),
  ),
)
```

## Build & Test Commands
```bash
# Development
flutter devices                  # List connected devices
flutter run                      # Auto-select device
flutter run -d chrome            # Web
flutter run -d windows           # Desktop
flutter run -d android           # Mobile

# Platform builds
flutter build web                # Web → build/web/
flutter build apk                # Android → build/app/outputs/
flutter build appbundle          # Android Play Store
flutter build ios                # iOS (requires macOS + Xcode)
flutter build windows            # Windows desktop
flutter build macos              # macOS desktop
flutter build linux              # Linux desktop

# Testing
flutter test                     # Run all widget/unit tests
flutter test test/features/auth/ # Run specific test directory
flutter test --coverage          # With coverage report

# Analysis
dart analyze                    # Static analysis (strict)
dart format .                   # Format all Dart code

# Code generation (freezed, json_serializable)
dart run build_runner build
dart run build_runner watch     # Watch mode during dev
```

## Important Notes
- **No Vue, Quasar, or React code in Flutter** — this is a pure Dart/Flutter app
- **Vue reference code** lives in `frontend/` (parent directory) — reference for UX patterns only, NOT to be ported as-is
- **Backend API is shared** — all endpoints from FastAPI are consumed identically regardless of frontend framework
- **Dio is the HTTP client** — never use `http` package directly
- **Riverpod for state** — never use Provider, BLoC, or GetX
- **`freezed` for models** — use the build_runner codegen for all data classes
- **Material 3 with custom dark theme** — OtakuHub is a dark-only app (aniwaves.ru aesthetic)
- **TV needs special Focus widget considerations** — test with remote D-pad emulation
- **Current frontend (`frontend/`) is Vue 3** — kept as reference for design patterns
