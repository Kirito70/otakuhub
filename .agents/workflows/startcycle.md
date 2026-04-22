---
description: Start the full Flutter feature development pipeline from an idea to reviewed code.
---

When the user types `/startcycle <idea>`, orchestrate the full development pipeline using `.agents/agents.md` and `.antigravity/skills/`.

## Execution Sequence

### Phase 1 — Specification
Act as the **Product Manager** persona from `.agents/agents.md`.
Using the `<idea>`, write a spec document with user stories and acceptance criteria.
Save to `docs/specs/<feature-slug>-spec.md`.
**PAUSE — show the spec to the user and wait for explicit "approved" before continuing.**

### Phase 2 — Design
Act as the **UI Designer** persona.
Read the approved spec.
Write a design brief describing layouts, responsive behaviour, and key widgets.
Save to `docs/specs/<feature-slug>-design.md`.
**PAUSE — show the design brief and wait for "approved" before continuing.**

### Phase 3 — Implementation
Act as the **Flutter Engineer** persona.
Execute the `flutter-screen` skill from `.antigravity/skills/flutter-screen.md`.
Use the spec and design brief as inputs.
Run `dart run build_runner build --delete-conflicting-outputs` after generating providers.
Run `dart analyze` — fix all errors before continuing.
Save all code to `mobile/lib/features/<feature>/`.
**PAUSE — show a summary of files created and wait for "approved".**

### Phase 4 — Tests
Act as the **Test Engineer** persona.
Write widget tests and provider tests for the implementation.
Run `flutter test test/features/<feature>/` — all must pass.
Save to `test/features/<feature>/`.
**PAUSE — show test results.**

### Phase 5 — Review
Act as the **Code Reviewer** persona.
Run a full review using `.claude/skills/code-review/SKILL.md`.
Output findings with BLOCKER/MAJOR/MINOR/NIT severity.
If blockers exist: return to Phase 3 with the specific fixes needed.
If no blockers: output "✅ Feature ready for commit."

## Rework Loop
If the reviewer finds BLOCKERs or MAJORs:
1. Show the findings to the user
2. Act as Flutter Engineer to fix them
3. Re-run the reviewer
4. Repeat until "✅ Feature ready for commit"
