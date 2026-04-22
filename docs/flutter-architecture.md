# OtakuHub — Flutter Architecture

## Overview
Single Flutter codebase targeting 5 platforms: web, Windows, Android, iOS, Linux.
Feature-first folder structure. Riverpod 2 for state. GoRouter for navigation.

## Project Structure
```
mobile/
├── lib/
│   ├── main.dart
│   ├── app.dart                       ← MaterialApp + GoRouter + ProviderScope
│   ├── core/
│   │   ├── config/
│   │   │   └── app_config.dart        ← env-based config (API base URL, etc.)
│   │   ├── network/
│   │   │   ├── dio_client.dart        ← Dio instance + interceptors
│   │   │   ├── auth_interceptor.dart  ← attach token, refresh on 401
│   │   │   └── retry_interceptor.dart ← exponential backoff on 5xx
│   │   ├── router/
│   │   │   └── app_router.dart        ← GoRouter: all named routes + auth guard
│   │   ├── storage/
│   │   │   └── secure_storage.dart    ← flutter_secure_storage wrapper
│   │   ├── theme/
│   │   │   ├── app_theme.dart         ← Material 3 light + dark theme
│   │   │   └── app_colors.dart        ← semantic color tokens
│   │   └── widgets/
│   │       ├── error_view.dart        ← reusable error + retry widget
│   │       ├── loading_view.dart
│   │       └── adaptive_layout.dart   ← breakpoint helpers
│   └── features/
│       ├── auth/
│       ├── media/                     ← anime/manga search + detail
│       ├── tracking/                  ← user list management
│       ├── social/                    ← friend feed, recommendations, discussions
│       ├── watchparty/
│       ├── notifications/
│       └── profile/
├── test/
│   ├── features/                      ← mirrors lib/features/ structure
│   └── core/
├── integration_test/
│   └── app_test.dart
├── pubspec.yaml
└── analysis_options.yaml
```

## Feature Folder Pattern
Every feature follows this exact structure:
```
features/<feature>/
  data/
    datasources/<feature>_remote_datasource.dart   ← Dio HTTP calls
    repositories/<feature>_repository_impl.dart    ← implements domain repo
  domain/
    models/<feature>_model.dart                    ← Freezed data class
    repositories/<feature>_repository.dart         ← abstract interface
  presentation/
    screens/<feature>_screen.dart                  ← GoRouter target page
    widgets/                                        ← feature-specific widgets
    providers/<feature>_provider.dart              ← @riverpod notifiers
```

## Key Packages
```yaml
dependencies:
  flutter_riverpod: ^2.x
  riverpod_annotation: ^2.x
  go_router: ^14.x
  dio: ^5.x
  freezed_annotation: ^2.x
  json_annotation: ^4.x
  cached_network_image: ^3.x
  flutter_secure_storage: ^9.x
  flutter_adaptive_scaffold: ^0.x
  intl: ^0.x

dev_dependencies:
  riverpod_generator: ^2.x
  freezed: ^2.x
  json_serializable: ^6.x
  build_runner: ^2.x
  flutter_test:
  mocktail: ^1.x
```

## State Management (Riverpod)

### Provider Types
| Situation | Use |
|-----------|-----|
| Read-only async data (no mutations) | `@riverpod Future<T> myData(ref)` |
| Mutable async state | `@riverpod class MyNotifier extends _$MyNotifier` |
| Sync derived state | `@riverpod T myValue(ref)` |
| Parameterized by ID | `@riverpod Future<T> detail(ref, String id)` |
| Auth state (global) | `@Riverpod(keepAlive: true) class AuthNotifier` |

### Provider File Header Pattern
```dart
// Always include the part directive for code generation
part 'tracking_provider.g.dart';

@riverpod
class TrackingListNotifier extends _$TrackingListNotifier {
  @override
  Future<List<ListEntryModel>> build() async {
    // Triggers rebuild when auth state changes
    ref.watch(authStateProvider);
    return ref.read(trackingRepositoryProvider).getUserList();
  }
}
```

### Consuming in Widgets
```dart
// ALWAYS use .when() — never access .value directly
ref.watch(trackingListNotifierProvider).when(
  loading: () => const LoadingView(),
  error: (e, _) => ErrorView(message: e.toString(), onRetry: () =>
      ref.invalidate(trackingListNotifierProvider)),
  data: (list) => TrackingListBody(entries: list),
);
```

## Navigation (GoRouter)

### Route Structure
```dart
final appRouter = GoRouter(
  redirect: (context, state) {
    final isAuthenticated = ref.read(authStateProvider).isAuthenticated;
    final isAuthRoute = state.matchedLocation.startsWith('/auth');
    if (!isAuthenticated && !isAuthRoute) return '/auth/login';
    if (isAuthenticated && isAuthRoute) return '/';
    return null;
  },
  routes: [
    ShellRoute(                          // persistent bottom nav / side nav
      builder: (context, state, child) => AppShell(child: child),
      routes: [
        GoRoute(path: '/', name: 'home', builder: ...),
        GoRoute(path: '/discover', name: 'discover', builder: ...),
        GoRoute(path: '/lists', name: 'lists', builder: ...),
        GoRoute(path: '/social', name: 'social', builder: ...),
      ],
    ),
    GoRoute(
      path: '/media/:mediaId',
      name: 'media-detail',
      builder: (context, state) => MediaDetailScreen(
        mediaId: state.pathParameters['mediaId']!,
      ),
    ),
  ],
);
```

### Navigation Usage
```dart
// Go to a named route
context.goNamed('media-detail', pathParameters: {'mediaId': id});

// Push onto stack (for detail overlays)
context.pushNamed('media-detail', pathParameters: {'mediaId': id});
```

## Responsive Layout

### Breakpoints
| Name | Width | Layout |
|------|-------|--------|
| Mobile | < 600px | Bottom nav bar, full-screen pages |
| Tablet | 600–1200px | Bottom nav, master-detail side panel |
| Desktop | > 1200px | Persistent side nav rail, content area |

### Implementation
```dart
class AppShell extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return AdaptiveScaffold(
      destinations: destinations,
      body: (_) => child,                    // main content
      secondaryBody: (_) => DetailPanel(),   // side panel on tablet+
      smallBody: (_) => child,               // mobile: no side panel
    );
  }
}
```

## HTTP Client (Dio)

### Client Setup
```dart
Dio createDio(String baseUrl, SecureStorage storage) {
  final dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  ));
  dio.interceptors.addAll([
    AuthInterceptor(dio, storage),    // attach + refresh tokens
    RetryInterceptor(dio),            // retry on 5xx
    LogInterceptor(requestBody: kDebugMode, responseBody: kDebugMode),
  ]);
  return dio;
}
```

### Auth Interceptor
```dart
class AuthInterceptor extends Interceptor {
  @override
  Future<void> onRequest(options, handler) async {
    final token = await _storage.getAccessToken();
    if (token != null) options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, handler) async {
    if (err.response?.statusCode == 401) {
      // Token expired — refresh it
      final newToken = await _refreshAccessToken();
      if (newToken != null) {
        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        return handler.resolve(await _dio.fetch(err.requestOptions));
      }
    }
    handler.next(err);
  }
}
```

## Platform-Specific Notes
| Platform | Notes |
|----------|-------|
| Web | Uses `flutter_web_plugins`, router uses URL hash strategy |
| Windows | Uses `windows_taskbar` for watch party reminders; MSIX packaging |
| Android | Min SDK 21; `flutter_secure_storage` uses Keystore |
| iOS | Min iOS 14; `flutter_secure_storage` uses Keychain |
| Linux | `secret_service` for secure storage; GTK runner |

## Testing
```bash
# Unit + widget tests
flutter test

# Specific feature
flutter test test/features/tracking/

# Integration tests (requires device/emulator)
flutter test integration_test/app_test.dart

# Coverage
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```
