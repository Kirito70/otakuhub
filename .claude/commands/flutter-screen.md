# Scaffold a New Flutter Feature Screen

Given a feature name and description, generate the full feature scaffold.

## Files to Create

### 1. Domain Model — `lib/features/$NAME/domain/models/$NAME_model.dart`
Freezed immutable data class with all relevant fields.
Include a `.fixture()` factory for tests.

```dart
@freezed
class AnimeModel with _$AnimeModel {
  const factory AnimeModel({
    required String id,
    required AnimeTitle title,
    required String mediaType,
    // ... fields
  }) = _AnimeModel;

  factory AnimeModel.fromJson(Map<String, dynamic> json) => _$AnimeModelFromJson(json);
  
  // Test fixture
  factory AnimeModel.fixture() => const AnimeModel(
    id: 'test-id',
    title: AnimeTitle(romaji: 'Test Anime', english: 'Test Anime', native: 'テスト'),
    mediaType: 'anime',
  );
}
```

### 2. Repository Interface — `lib/features/$NAME/domain/repositories/$NAME_repository.dart`
Abstract class defining what data operations this feature needs.

### 3. Remote Datasource — `lib/features/$NAME/data/datasources/$NAME_remote_datasource.dart`
Dio-based implementation. All methods return typed models or throw typed exceptions.

### 4. Repository Implementation — `lib/features/$NAME/data/repositories/$NAME_repository_impl.dart`
Implements domain interface, calls datasource, maps errors.

### 5. Riverpod Provider — `lib/features/$NAME/presentation/providers/$NAME_provider.dart`
```dart
@riverpod
class $NameNotifier extends _$$NameNotifier {
  @override
  Future<$NameModel> build(String id) async {
    return ref.watch(${name}RepositoryProvider).getById(id);
  }
}
```

### 6. Screen — `lib/features/$NAME/presentation/screens/$NAME_screen.dart`
- `ConsumerWidget`
- Responsive: works on mobile, tablet, desktop
- Handles: loading spinner, error view with retry, success content
- Uses named GoRouter route

### 7. Widget Test — `test/features/$NAME/presentation/screens/$NAME_screen_test.dart`
Tests: renders loading state, renders data state, renders error state.

## After Generating All Files
```bash
dart run build_runner build --delete-conflicting-outputs
dart analyze
flutter test test/features/$NAME/
```
Report any issues found.
