---
name: flutter-riverpod
description: Create a correctly structured Riverpod 2 provider + notifier for a new feature. Handles async state, error, and loading.
---

# Riverpod Provider Creation

## Decision Tree

| Use case | Provider type |
|----------|--------------|
| Read data, no mutations | `@riverpod Future<T> myData(ref)` |
| Read list, can refresh | `@riverpod class MyNotifier extends _$MyNotifier { Future<List<T>> build() }` |
| Mutable state + actions | `@riverpod class MyNotifier extends _$MyNotifier { ... }` with methods |
| Sync derived state | `@riverpod T myValue(ref)` (no async) |
| Parameterized (by ID) | `@riverpod Future<T> detail(ref, String id)` |

## Template: AsyncNotifier with mutations

```dart
part '$filename.g.dart';

@riverpod
class TrackingListNotifier extends _$TrackingListNotifier {
  @override
  Future<List<ListEntryModel>> build() async {
    return ref.watch(listRepositoryProvider).getUserList();
  }

  Future<void> updateProgress({
    required String mediaId,
    required int progress,
  }) async {
    // Optimistic update
    final current = await future;
    state = AsyncData(
      current.map((e) => e.mediaId == mediaId
          ? e.copyWith(progress: progress)
          : e).toList(),
    );
    // Persist
    try {
      await ref.read(listRepositoryProvider).updateProgress(
        mediaId: mediaId, progress: progress,
      );
    } catch (e, st) {
      state = AsyncError(e, st);
      ref.invalidateSelf(); // reload from server
    }
  }
}
```

## After Creating Provider
```bash
dart run build_runner build --delete-conflicting-outputs
dart analyze lib/features/
```
The `.g.dart` file must be generated before the provider is usable.
