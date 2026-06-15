---
paths:
  - "frontend/flutter/**"
---
# Frontend Rules (Flutter / Dart / Riverpod)

## Project Paths
The active Flutter frontend lives at `frontend/flutter/`.
The reference Vue frontend lives at `frontend/` but is NOT actively developed.

## Flutter State Pattern (Riverpod)
```dart
// lib/features/tracking/providers/list_provider.dart
final userListProvider = FutureProvider<List<ListEntry>>((ref) async {
  final api = ref.read(apiClientProvider);
  final response = await api.get('/api/v1/lists/me');
  return (response.data as List).map((j) => ListEntry.fromJson(j)).toList();
});

// For mutable state with methods
final trackingNotifierProvider =
    NotifierProvider<TrackingNotifier, TrackingState>(TrackingNotifier.new);

class TrackingNotifier extends Notifier<TrackingState> {
  @override
  TrackingState build() => TrackingState();

  Future<void> updateProgress(String mediaId, int progress) async {
    state = state.copyWith(isLoading: true);
    try {
      final api = ref.read(apiClientProvider);
      await api.patch('/api/v1/lists/$mediaId', data: {'progress': progress});
      ref.invalidate(userListProvider);
      state = state.copyWith(isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}
```

## Screen Pattern
```dart
class DiscoverScreen extends ConsumerWidget {
  const DiscoverScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final trending = ref.watch(trendingProvider);
    return Scaffold(
      body: trending.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => AppEmptyState(
          message: 'Failed to load',
          actionLabel: 'Retry',
          onAction: () => ref.invalidate(trendingProvider),
        ),
        data: (items) => ListView(
          children: items.map((item) => MediaCard(item: item)).toList(),
        ),
      ),
    );
  }
}
```

## Responsive Layout
```dart
LayoutBuilder(
  builder: (context, constraints) {
    final width = constraints.maxWidth;
    if (width < 600) {
      return _MobileLayout(child: child);
    } else if (width < 1024) {
      return _TabletLayout(child: child);
    } else {
      return _DesktopLayout(child: child);
    }
  },
)
```

## API Calls — Always Via Dio
```dart
// CORRECT — use the configured Dio instance from provider
final api = ref.read(apiClientProvider);
final response = await api.get('/api/v1/media/search');

// WRONG — never use `http` package or create raw Dio instances
import 'package:http/http.dart' as http; // DON'T
```

## TV Support
- Wrap all interactive elements in `Focus()` widget
- Use `FocusNode` + `onFocusChange` for visual feedback
- Add `semanticLabel` to all interactive elements
- Test navigation via keyboard arrows / D-pad

## Never
- Never call AniList, MangaDex, or Jikan directly from frontend code
- Never use `flutter_secure_storage` on web (use `shared_preferences` fallback)
- Never use `GoRouter.go()` with raw paths — use named routes from route_names.dart
- Never use bare `Image.network` without error handling — use `CachedNetworkImage`
- Never modify Vue reference code in `frontend/` for Flutter features
