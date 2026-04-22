---
applyTo: "mobile/**"
---
# Flutter-Specific Copilot Instructions

State: `@riverpod` annotation + `riverpod_generator`. Run `build_runner` after changes.
Navigation: `GoRouter` named routes in `lib/core/router/app_router.dart`.
HTTP: `Dio` with auth interceptor. All responses typed as Freezed models.
Structure: `lib/features/<feature>/data/domain/presentation/`.
Responsive: `AdaptiveScaffold` from `flutter_adaptive_scaffold`.
Lists: always `ListView.builder` or `SliverList` — never `Column` + `map` for long lists.
Images: always `CachedNetworkImage` with placeholder.
Every `AsyncValue` widget: always handle `.when(data:, loading:, error:)`.
