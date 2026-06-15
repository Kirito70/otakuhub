# OtakuHub Flutter App

Cross-platform anime/manga/manhwa tracking and social app for friend groups. Runs on **Android, iOS, Web, Windows, macOS, Linux, and Android TV/Fire TV** from a single codebase.

---

## Quick Start

```bash
# 1. Install dependencies
cd frontend/flutter
flutter pub get

# 2. Generate freezed/models code
dart run build_runner build --delete-conflicting-outputs

# 3. Run dev mode (hot reload enabled)
flutter run -d chrome --dart-define=BACKEND_URL=http://localhost:8000

# 4. Run all tests
flutter test

# 5. Build for production
flutter build web
```

---

## Prerequisites

- **Flutter SDK** 3.x (stable channel) — [install guide](https://docs.flutter.dev/get-started/install)
- **Dart** 3.x (bundled with Flutter)
- **A code editor** — VS Code with Flutter + Dart extensions recommended

Verify installation:

```bash
flutter doctor
flutter --version
```

---

## Setup

### 1. Install dependencies

```bash
cd frontend/flutter
flutter pub get
```

### 2. Generate code (freezed models, json_serializable, riverpod_generator)

Run this after every `pub get`, model change, or provider change:

```bash
dart run build_runner build --delete-conflicting-outputs
```

For watch mode (auto-regenerate on file save during development):

```bash
dart run build_runner watch --delete-conflicting-outputs
```

### 3. Configure API endpoint

The app connects to the FastAPI backend. Default is `http://localhost:8000`. To change it:

**Option A — Edit the constant** (quickest for dev):
```dart
// lib/core/api/api_endpoints.dart
static const String baseUrl = 'http://localhost:8000';
```

**Option B — Use `--dart-define` at run/build time** (recommended — no file changes):
```bash
# Web
flutter run --dart-define=BACKEND_URL=https://api.otakuhub.local

# Android / Windows / Linux
flutter run --dart-define=BACKEND_URL=https://api.otakuhub.local

# Build with env
flutter build web --dart-define=BACKEND_URL=https://api.otakuhub.local
```

**Option C — Use a `.env` file at the project root** (for shared team config):
```bash
# frontend/flutter/.env
BACKEND_URL=http://192.168.1.100:8000
API_TIMEOUT=30
```
Then read it via `const String.fromEnvironment('BACKEND_URL')` or a dotenv package.

---

## Commands

### Run in Dev Mode (hot reload / hot restart)

```bash
# Default: web in Chrome
flutter run

# Choose a specific device
flutter run -d chrome          # Web
flutter run -d windows         # Windows desktop
flutter run -d android         # Connected Android device/emulator
flutter run -d macos           # macOS (macOS host only)
flutter run -d linux           # Linux (Linux host only)
flutter run -d ios             # iOS (macOS host only)

# With custom API endpoint
flutter run --dart-define=BACKEND_URL=http://localhost:8000

# List available devices
flutter devices
```

Dev mode features:
- **Hot reload** (`r` in terminal) — update Dart code instantly, preserves state
- **Hot restart** (`R` in terminal) — full restart, resets state
- **Profile mode** (`--profile`) — measure performance (useful for UI jank debugging)
- **Debug mode** (default) — full debug info, slowest
- **Release mode** (`--release`) — optimized, no debug info, for final testing before build

### VS Code Launch Configurations

Add these to `.vscode/launch.json` for one-click run/debug:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter (web - dev)",
      "type": "dart",
      "request": "launch",
      "flutterMode": "debug",
      "args": ["-d", "chrome", "--dart-define=BACKEND_URL=http://localhost:8000"]
    },
    {
      "name": "Flutter (Windows - dev)",
      "type": "dart",
      "request": "launch",
      "flutterMode": "debug",
      "args": ["-d", "windows", "--dart-define=BACKEND_URL=http://localhost:8000"]
    },
    {
      "name": "Flutter (Android - dev)",
      "type": "dart",
      "request": "launch",
      "flutterMode": "debug",
      "args": ["-d", "android", "--dart-define=BACKEND_URL=http://10.0.2.2:8000"]
    },
    {
      "name": "Flutter (web - staging)",
      "type": "dart",
      "request": "launch",
      "flutterMode": "debug",
      "args": ["-d", "chrome", "--dart-define=BACKEND_URL=https://staging.otakuhub.local"]
    },
    {
      "name": "Flutter (web - release)",
      "type": "dart",
      "request": "launch",
      "flutterMode": "release",
      "args": ["-d", "chrome", "--dart-define=BACKEND_URL=https://api.otakuhub.local"]
    }
  ]
}
```

For Android emulator, use `10.0.2.2` instead of `localhost` to reach the host machine.
For iOS simulator, `localhost` works since it shares the host network.
For physical Android device, use your machine's LAN IP (e.g. `http://192.168.1.100:8000`).

### Environment Variables (--dart-define)

Pass custom config at run or build time:

```bash
# Single variable
flutter run --dart-define=BACKEND_URL=https://staging.otakuhub.local

# Multiple variables
flutter run --dart-define=BACKEND_URL=https://staging.otakuhub.local --dart-define=API_TIMEOUT=30

# Read in code
const backendUrl = String.fromEnvironment('BACKEND_URL', defaultValue: 'http://localhost:8000');
const apiTimeout = int.fromEnvironment('API_TIMEOUT', defaultValue: 15);
```

The same `--dart-define` flag works with `flutter build`, `flutter test`, and `flutter analyze`.

### Common Dev Commands

```bash
# Run with debug logging in terminal
flutter run --verbose

# Run tests with a custom backend
flutter test --dart-define=BACKEND_URL=http://test.api.local

# Clear build cache (fix stale artifacts)
flutter clean && flutter pub get && dart run build_runner build --delete-conflicting-outputs

# Check connected devices / emulators
flutter devices
```

### Analyze

```bash
flutter analyze
```
Checks for errors, warnings, and lints. **Must pass with 0 errors, 0 warnings before any commit.**

### Test

```bash
# Run all tests
flutter test

# Run a specific test file
flutter test test/features/auth/login_screen_test.dart

# Run all tests in a directory
flutter test test/features/social/
```

Tests use `flutter_test` + `mocktail`. Widget tests mock Dio via **provider overrides** (not a real HTTP client) using the following pattern:

```dart
// Mock notifier that returns data synchronously (no HTTP calls)
class _MockFeedNotifier extends GroupFeedNotifier {
  @override
  Future<FeedResponse> build() async => const FeedResponse();
}

ProviderScope(
  overrides: [
    groupFeedNotifierProvider.overrideWith(
      () => _MockFeedNotifier(),
    ),
  ],
  child: MaterialApp(...)
)
```

**Important**: Always use `pump()` not `pumpAndSettle()` when Dio would be involved, because Dio creates internal microtask timers that cause "A Timer is still pending" errors in `FakeAsync`.

### Build

#### Web
```bash
flutter build web
# Output: build/web/
```

#### Android (APK)
```bash
flutter build apk
# Output: build/app/outputs/flutter-apk/app-release.apk
```

#### Android (App Bundle — for Play Store / Amazon Appstore)
```bash
flutter build appbundle
# Output: build/app/outputs/bundle/release/app-release.aab
```

#### Windows (native executable)
```bash
# Requires Windows host with Visual Studio build tools
flutter build windows
# Output: build/windows/x64/runner/Release/
```

#### macOS (native app)
```bash
# Requires macOS host with Xcode
flutter build macos
# Output: build/macos/Build/Products/Release/
```

#### Linux (native executable)
```bash
# Requires Linux host with GTK development libraries
flutter build linux
# Output: build/linux/x64/release/bundle/
```

#### iOS (IPA)
```bash
# Requires macOS host with Xcode
flutter build ios
# Output: build/ios/iphoneos/Runner.app
```

---

## Project Structure

```
flutter/
├── lib/
│   ├── core/                    # Shared infrastructure
│   │   ├── api/                 # Dio client, endpoints, exceptions
│   │   ├── auth/                # AuthNotifier, storage service
│   │   ├── router/              # GoRouter config, route names
│   │   ├── theme/               # Dark M3 theme, semantic colors
│   │   └── widgets/             # Shared widgets (AdaptiveScaffold, AppEmptyState, etc.)
│   ├── features/                # Feature-first modules
│   │   ├── auth/                # Login, Register, Setup
│   │   ├── discover/            # Search, Trending, New Releases
│   │   ├── media_detail/        # Media detail with tabs
│   │   ├── tracking/            # My List, Calendar, Import
│   │   ├── social/              # Feed, Recommendations, Discussions
│   │   ├── watchparty/          # Watch Party
│   │   ├── notifications/       # Notifications inbox & preferences
│   │   └── profile/             # Profile, edit, account security
│   └── tv/                      # TV-specific focus navigation
├── test/
│   ├── features/                # Tests mirror lib/features/ structure
│   └── integration_test/        # Full flow integration tests
├── android/                     # Android / Android TV specific config
├── ios/                         # iOS specific config
├── web/                         # Web specific config
├── windows/                     # Windows specific config
├── macos/                       # macOS specific config
├── linux/                       # Linux specific config
└── pubspec.yaml                 # Dependencies
```

---

## Architecture

### Feature Pattern
Every feature follows this module structure:

```
features/<name>/
├── models/        ← freezed data classes with json_serializable
├── providers/     ← riverpod_generator (@riverpod) notifiers
├── screens/       ← ConsumerWidget / ConsumerStatefulWidget pages
└── widgets/       ← Reusable sub-components
```

### State Management — Riverpod 2.x
- `FutureProvider` / `FutureProvider.family` — async data (GET endpoints)
- `AsyncNotifierProvider` — mutable state with actions (loadMore, create, update)
- `NotifierProvider` — simple mutable state with methods

All HTTP calls use `ref.read(apiClientProvider)` (Dio instance with auth interceptor).

### Navigation — GoRouter + ShellRoute
- Standalone routes: `/auth/login`, `/auth/register`, `/setup`
- Shell routes (with AdaptiveScaffold): all other pages
- AdaptiveScaffold switches between bottom nav (<600px), nav rail (600-1024px), drawer (>1024px)
- Auth redirect guard: not logged in → `/auth/login`, setup required → `/setup`

### Dio + Auth Interceptor
- Automatic JWT `Authorization: Bearer <token>` on every request
- 401 catch → attempt token refresh → retry original request
- Refresh failure → logout → redirect to login

---

## Current Feature Status

| Feature | Status | Tests |
|---------|--------|-------|
| Auth & Setup | ✅ Complete | 29 |
| Discover & Media Detail | ✅ Complete | 9 |
| Tracking & Lists | ✅ Complete | 21 |
| Social Feed | ✅ Complete | 13 |
| Watch Party | ✅ Complete | — |
| Notifications | ⏳ | — |
| Profile | ⏳ | — |
| TV Optimization | ⏳ | — |
| **Total** | **94 tests passing** | **94** |

---

## Troubleshooting

### `build_runner` fails with conflicts
```bash
dart run build_runner build --delete-conflicting-outputs
```

### Tests fail with "A Timer is still pending"
This happens when a test inadvertently leaves a Dio request pending. Fix by overriding the provider with a mock notifier that returns data synchronously (no Dio calls at all). See existing tests in `test/features/social/` for the correct pattern.

### Web build has `flutter_secure_storage` warnings
These are expected. The web fallback uses `shared_preferences`. To suppress, add to `web/index.html`:
```html
<script>
  // Flutter web secure storage fallback
  window.flutter_secure_storage = { web: { read: () => {}, write: () => {}, delete: () => {} } };
</script>
```

### Flutter analyze shows info-level lints only
Info-level lints (prefer_const_constructors, directives_ordering, unnecessary_underscores) are pre-existing and acceptable. **Errors and warnings must be 0 before committing.**
