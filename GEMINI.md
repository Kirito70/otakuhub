# Gemini / Antigravity Instructions — OtakuHub

> This file extends AGENTS.md. Read AGENTS.md first.

## Antigravity Agent Configuration

### Primary Role in This Project
Antigravity / Gemini is the **reference code specialist** for OtakuHub.
The primary frontend is now Flutter (see `frontend/flutter/`). The Vue 3 code in `frontend/` is kept for design/UX reference only.

### Autonomy Profile
Use **Agent-Assisted** mode (not full autopilot) for this project.
- Plan first for any change touching more than 2 files
- Ask for confirmation before modifying: backend routes, database schema
- Auto-execute safe operations: linting, analysis, documentation

### Skills Available (`.antigravity/skills/`)
- `quasar-page.md` — Contents updated for shadcn-vue + Tailwind (kept for reference)
- `pinia-store.md` — Create a typed Pinia store with async actions (reference patterns)

### Workflow Slash Commands
Use `/startcycle <feature>` to trigger the full dev pipeline:
1. PM agent reads spec → writes user stories
2. UI Designer describes screen layout
3. Flutter Engineer implements the screen + provider
4. Test agent writes widget tests
5. Reviewer checks against AGENTS.md conventions

### Flutter-Specific Rules for Gemini
- All screens: `ConsumerWidget` or `ConsumerStatefulWidget` — no `StatelessWidget` for API-dependent screens
- State: Riverpod providers — no `setState` for shared data
- HTTP: Dio via `lib/core/api/api_client.dart` — no direct `http` calls
- Routing: GoRouter with named routes from `lib/core/router/route_names.dart`
- Layout: `AdaptiveScaffold` — `LayoutBuilder` with breakpoints (600/1024)
- Responsive: `LayoutBuilder` with breakpoints — not hardcoded sizes
- Images: `CachedNetworkImage` for remote images — not bare `Image.network`
- TV: `Focus` widget wrapping all interactive elements for D-pad navigation
- Forms: `Form` + `TextFormField` with validators — never unvalidated form submission

### After Building a Screen
```bash
cd frontend/flutter
flutter analyze          # zero errors
flutter test             # all tests pass
flutter build web        # confirm web build succeeds
flutter build apk        # confirm Android build succeeds
```

### Build Targets Reference
```bash
# Web (CanvasKit)
flutter build web

# Android
flutter build apk              # APK
flutter build appbundle        # Play Store AAB

# iOS (requires macOS + Xcode)
flutter build ios

# Desktop
flutter build windows
flutter build macos
flutter build linux

# TV — same as Android APK
flutter build apk --target-platform android-arm64
```
