---
paths:
  - "mobile/**"
---
# Flutter Rules (Dart / Flutter)

## Feature Structure
```
mobile/lib/features/<feature>/
  data/
    datasources/   ← API calls (Dio), local cache
    repositories/  ← implements domain repository interface
  domain/
    models/        ← Freezed data classes
    repositories/  ← abstract interfaces
  presentation/
    screens/       ← full-page screens (GoRouter targets)
    widgets/       ← reusable widgets for this feature
    providers/     ← Riverpod providers + notifiers
```

## State Management (Riverpod)
- Use `@riverpod` annotation with `riverpod_generator` — run `build_runner` after changes
- `AsyncNotifier` for mutable async state (lists, detail pages)
- `FutureProvider` for simple read-only async data
- `Provider` for synchronous derived state
- Always handle `.when(data:, loading:, error:)` in widgets
- Invalidate providers on logout: `ref.invalidateAll()` pattern

## Dio HTTP Client
- Base URL from environment config (`AppConfig.apiBaseUrl`)
- Auth interceptor: attach Bearer token, refresh on 401
- Retry interceptor: 3 retries with exponential backoff for 5xx
- All API responses deserialize into typed Freezed models

## Navigation (GoRouter)
- All routes defined in `lib/core/router/app_router.dart`
- Named routes only: `context.goNamed('anime-detail', pathParameters: {'id': id})`
- Auth guard: `redirect` callback checks auth state provider
- ShellRoute for bottom navigation structure

## Responsive Layout
- `AdaptiveScaffold` (from `flutter_adaptive_scaffold`) for web/desktop/mobile
- Mobile (<600px): bottom nav bar + full-screen detail pages
- Tablet (600–1200px): master-detail with side panel
- Desktop (>1200px): persistent side nav + content area
- Never hardcode pixel widths — use `MediaQuery` or `LayoutBuilder`

## Performance
- `ListView.builder` for all variable-length lists — never `Column` + `map`
- `CachedNetworkImage` for all remote images with placeholder + error widget
- `const` constructors wherever possible
- Dispose controllers, animations, and stream subscriptions in `dispose()`
