---
description: Start the full Quasar feature development pipeline from an idea to reviewed code.
---

When the user types `/startcycle <idea>`, orchestrate the full development pipeline using `.agents/agents.md`.

## Execution Sequence

### Phase 1 — Specification
Act as the **Product Manager** persona.
Write a spec document with user stories and acceptance criteria.
Save to `docs/specs/<feature-slug>-spec.md`.
**PAUSE — show the spec to the user and wait for "approved" before continuing.**

### Phase 2 — Design
Act as the **UI Designer** persona.
Write a design brief using Quasar component names, responsive grid classes, and Quasar breakpoints.
Save to `docs/specs/<feature-slug>-design.md`.
**PAUSE — show the design brief and wait for "approved" before continuing.**

### Phase 3 — Implementation
Act as the **Quasar Engineer** persona.
Execute the `quasar-page` skill from `.antigravity/skills/quasar-page.md`.
Run:
```bash
vue-tsc --noEmit
npx eslint src/
quasar build
```
All must pass before continuing.
**PAUSE — show a summary of files created and wait for "approved".**

### Phase 4 — Tests
Act as the **Test Engineer** persona.
Write Vitest component tests for the new page and store.
Run: `npx vitest run src/pages/__tests__/`
All tests must pass.
**PAUSE — show test results.**

### Phase 5 — Review
Act as the **Code Reviewer** persona.
Run a full review using `.claude/skills/code-review/SKILL.md`.
Output findings with BLOCKER/MAJOR/MINOR/NIT severity.
If blockers exist: return to Phase 3 with specific fixes needed.
If no blockers: output "✅ Feature ready for commit."

## Rework Loop
If the reviewer finds BLOCKERs or MAJORs:
1. Show the findings to the user
2. Act as Quasar Engineer to fix them
3. Re-run the reviewer
4. Repeat until "✅ Feature ready for commit"
