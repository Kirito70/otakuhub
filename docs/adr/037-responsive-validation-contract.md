# ADR 037 — Responsive Behavior Validation Contract (Web/Electron/Mobile)
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 15.5 requires validating that the new design-system contracts (tokens, typography/spacing, primitives, dashboard template) behave consistently across OtakuHub targets: web, Electron desktop, and mobile shells.

Without explicit responsive validation rules, pages can silently regress into desktop-only assumptions (hover-only actions, cramped mobile spacing, hidden CTAs).

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 15.5**.

## Decision
Define a responsive validation contract and acceptance checklist for all top-level pages:

1. **Breakpoint acceptance criteria**
   - `xs (<600)`: single-column page flow, stacked toolbar actions, no clipped primary CTA.
   - `sm (600–1024)`: collapsible/compact layout allowed, but no hidden critical actions.
   - `md+ (>1024)`: multi-column dashboard composition with persistent desktop affordances.

2. **Interaction rules**
   - Critical actions must be visible/tappable without hover dependency.
   - Drawer + bottom-nav transitions must not strand users without navigation access.
   - Focus-visible ring must remain present in keyboard navigation flows.

3. **State rendering parity**
   - Loading, empty, and error states must render through `AppEmptyState` across breakpoints.
   - No breakpoint may suppress error/CTA feedback.

4. **Spacing and typography compliance**
   - Breakpoint-specific gutters follow ADR 034 defaults.
   - Typography hierarchy remains semantically consistent; only density/stacking changes.

5. **Validation evidence requirements**
   - Maintain targeted component tests for layout behavior where feasible.
   - Run baseline frontend verification commands before phase completion:
     - `npx vitest run`
     - `quasar build`
     - Platform-mode checks as available (`-m electron`, capacitor modes in environment permitting).

## Consequences
**Good**:
- Catches responsive regressions before later feature phases.
- Enforces consistent UX quality across the small multi-platform user base.
- Reduces rework in Phases 16–22.

**Bad**:
- Adds validation workload during each page migration.
- Some legacy layouts may need refactors to satisfy stricter CTA visibility rules.

**Neutral**:
- No database/API changes.
- No auth/sync worker behavior changes.
