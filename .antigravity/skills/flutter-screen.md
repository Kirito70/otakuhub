---
name: flutter-screen
description: Scaffold a complete Flutter feature screen with Riverpod provider, responsive layout, loading/error/data states, and widget test.
---

# Flutter Screen Scaffold

## Steps

1. **Read context**: Read `docs/flutter-architecture.md` and the relevant feature spec.

2. **Create domain model** in `lib/features/$NAME/domain/models/`:
   - Freezed `@freezed` class
   - `fromJson` / `toJson`
   - `.fixture()` factory for tests

3. **Create Riverpod provider** in `lib/features/$NAME/presentation/providers/`:
   - Use `@riverpod` annotation
   - `AsyncNotifier` for mutable state, `FutureProvider` for read-only
   - Run: `dart run build_runner build --delete-conflicting-outputs`

4. **Create screen** in `lib/features/$NAME/presentation/screens/`:
   - `ConsumerWidget`
   - `ref.watch(provider).when(data:, loading:, error:)`
   - `AdaptiveScaffold` for responsive layout
   - Mobile: bottom nav. Tablet: side panel. Desktop: persistent nav.

5. **Register route** in `lib/core/router/app_router.dart`:
   - Named route
   - Auth guard if needed

6. **Create widget test** in `test/features/$NAME/`:
   - Test: loading state renders CircularProgressIndicator
   - Test: data state renders key widgets
   - Test: error state renders ErrorView with retry button

7. **Verify**:
   ```bash
   dart analyze lib/features/$NAME/
   flutter test test/features/$NAME/
   ```
   Zero errors required before reporting done.
