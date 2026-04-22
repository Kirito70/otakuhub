# Gemini / Antigravity Instructions — OtakuHub

> This file extends AGENTS.md. Read AGENTS.md first.

## Antigravity Agent Configuration

### Primary Role in This Project
Antigravity / Gemini is the **Flutter UI specialist** for OtakuHub.
Focus areas: Flutter screens, widgets, Riverpod state, responsive layout, animations.

### Autonomy Profile
Use **Agent-Assisted** mode (not full autopilot) for this project.
- Plan first for any change touching more than 2 files
- Ask for confirmation before modifying: `lib/main.dart`, `pubspec.yaml`, any Riverpod provider
- Auto-execute safe operations: linting, widget creation, test file generation

### Skills Available (`.antigravity/skills/`)
- `flutter-screen.md` — Scaffold a new feature screen
- `flutter-widget.md` — Create a reusable widget with proper theming
- `flutter-riverpod.md` — Create a Riverpod provider + notifier
- `flutter-responsive.md` — Make a screen work across web/desktop/mobile

### Workflow Slash Commands
Use `/startcycle <feature>` to trigger the full flutter dev pipeline:
1. Architect agent reads `docs/flutter-architecture.md`
2. Designs screen layout and state shape
3. Writes Riverpod providers
4. Builds the screen widget
5. Writes widget tests
6. Generates screenshots as Artifacts for review

### Flutter-Specific Rules for Gemini
- Use `flutter_riverpod` + `riverpod_annotation` + `riverpod_generator`
- Use code generation: run `dart run build_runner build` after creating annotated providers
- Theme: use `Theme.of(context)` tokens — no hardcoded colours
- All images/assets through `AssetImage` or `CachedNetworkImage` — never `Image.network` directly
- Platform detection: use `defaultTargetPlatform` or `kIsWeb`, not `Platform.isAndroid`
- Navigation: `GoRouter` named routes only — no `Navigator.push` directly
- For lists of anime: `SliverList` + `SliverAppBar` for smooth scroll performance

### Browser Testing
After building a screen, use Antigravity's built-in browser to:
1. Test the Flutter web build: `flutter run -d web-server --web-port=8080`
2. Verify the layout at mobile (375px), tablet (768px), desktop (1280px) widths
3. Screenshot each breakpoint as an Artifact

### Multi-Agent Pipeline (agents.md in .agents/workflows/)
The `flutter-feature` workflow orchestrates:
- **PM Agent**: reads spec, writes acceptance criteria
- **UI Designer Agent**: proposes screen layout using Figma-style description
- **Flutter Dev Agent**: implements the screen
- **Test Agent**: writes widget + integration tests
- **Reviewer Agent**: checks against code standards
