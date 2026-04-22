---
name: flutter-dev
description: Build a Flutter feature screen, Riverpod provider, and widget test. Follows feature-first folder structure with adaptive responsive layout.
---

# Flutter Development Skill

## Before Starting
```bash
cd mobile
flutter pub get
dart analyze                   # note baseline issues — don't add new ones
```

## Folder Creation Checklist
For feature named `<feature>`:
```
lib/features/<feature>/
  data/
    datasources/<feature>_remote_datasource.dart
    repositories/<feature>_repository_impl.dart
  domain/
    models/<feature>_model.dart
    repositories/<feature>_repository.dart
  presentation/
    screens/<feature>_screen.dart
    widgets/                       (create if needed)
    providers/<feature>_provider.dart
test/features/<feature>/
  presentation/screens/<feature>_screen_test.dart
  presentation/providers/<feature>_provider_test.dart
```

## Model (Freezed)
```dart
import 'package:freezed_annotation/freezed_annotation.dart';
part '<feature>_model.freezed.dart';
part '<feature>_model.g.dart';

@freezed
class <Feature>Model with _$<Feature>Model {
  const factory <Feature>Model({
    required String id,
    required String title,
    // all fields with required/optional
  }) = _<Feature>Model;

  factory <Feature>Model.fromJson(Map<String, dynamic> json) =>
      _$<Feature>ModelFromJson(json);

  // Always include a fixture for tests
  factory <Feature>Model.fixture() => const <Feature>Model(
    id: 'fixture-id',
    title: 'Test Title',
  );
}
```

## Provider (@riverpod)
```dart
part '<feature>_provider.g.dart';

@riverpod
class <Feature>Notifier extends _$<Feature>Notifier {
  @override
  Future<List<<Feature>Model>> build() async {
    return ref.watch(<feature>RepositoryProvider).getList();
  }
}
```

## Screen (ConsumerWidget)
```dart
class <Feature>Screen extends ConsumerWidget {
  const <Feature>Screen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncState = ref.watch(<feature>NotifierProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('<Feature>')),
      body: asyncState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error: $e'),
              ElevatedButton(
                onPressed: () => ref.invalidate(<feature>NotifierProvider),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
        data: (items) => _<Feature>Body(items: items),
      ),
    );
  }
}
```

## After Writing All Files
```bash
# Generate Freezed + Riverpod code
dart run build_runner build --delete-conflicting-outputs

# Verify
dart analyze lib/features/<feature>/
flutter test test/features/<feature>/

# Test on web
flutter run -d web-server --web-port 8080
```
Zero analyzer warnings allowed before marking work done.
