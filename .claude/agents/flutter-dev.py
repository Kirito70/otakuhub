"""Flutter frontend developer agent for OtakuHub.

Reads flutter-architecture.md and the flutter-dev skill.
Builds Flutter features: Dart models, Riverpod providers, GoRouter pages,
widgets, and tests for all platforms (mobile, desktop, web, TV).

Always reads the relevant architecture doc and existing code before building.
"""

from skill_library import SkillLibrary

# Load the Flutter skill
skills = SkillLibrary.load("flutter-dev")

# Lazy-init module-level state
_agent_init = False


def init_agent() -> None:
    global _agent_init
    if _agent_init:
        return
    print("[flutter-dev] Agent initialized. Flutter feature development ready.")
    print("[flutter-dev] Targets: mobile, desktop, web, TV.")
    _agent_init = True


def help() -> str:
    return """flutter-dev — Flutter Feature Builder

  Builds OtakuHub frontend features for all target platforms.

  Execution sequence:
    1. Models (freezed, fromJson/toJson)
    2. Providers (Riverpod notifiers + futures)
    3. Widgets/Screens (ConsumerWidget, AdaptiveLayout)
    4. Router integration (GoRouter + ShellRoute)
    5. Tests (flutter_test + mocktail)

  Reads: docs/flutter-architecture.md
  Skill: .claude/skills/flutter-dev/SKILL.md
  """
