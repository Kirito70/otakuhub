# ADR 034 — Frontend Typography and Spacing Scale (Quasar-native)
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 15.2 requires a consistent typography and spacing system so all pages share the same visual rhythm and hierarchy. After Phase 15.1 introduced semantic tokens, the next risk is inconsistent font sizing, heading depth, and spacing patterns across components.

For OtakuHub's small-group scope, we prioritize a simple, explicit scale that is easy to apply in Quasar components and reusable primitives.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 15.2**.

## Decision
Adopt fixed semantic typography and spacing scales for frontend primitives and pages.

1. **Typography semantic levels**
   - Display: `display-lg`, `display-md`
   - Headings: `heading-xl`, `heading-lg`, `heading-md`, `heading-sm`
   - Body: `body-lg`, `body-md`, `body-sm`
   - Utility: `label-md`, `label-sm`, `caption`

2. **Typography usage rules**
   - One primary page title (`heading-xl` or `heading-lg`) per page.
   - Section headers use heading levels in descending order (no skipping up/down arbitrarily).
   - Long-form metadata and helper text use body/caption levels only.

3. **Spacing scale**
   - Base unit: 4px.
   - Semantic spacing steps: `space-1`..`space-12` mapped to 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 56, 64.
   - Core layout defaults:
     - Page horizontal gutter: `space-6` (desktop), `space-4` (mobile)
     - Card padding: `space-4` default, `space-5` for dense dashboard cards
     - Section gaps: `space-6`
     - Form control vertical gap: `space-3`

4. **Quasar integration contract**
   - Prefer Quasar utility classes/composition where possible; custom CSS variables only for scale tokens.
   - Components consume semantic typography/spacing tokens; avoid one-off pixel literals in component templates.

5. **Primitive readiness**
   - Upcoming primitives (`AppCard`, `AppToolbar`, `AppEmptyState`, `AppBadge`) must expose size variants mapped to semantic typography/spacing values.

## Consequences
**Good**:
- Predictable visual hierarchy across all pages.
- Faster component implementation for upcoming phases due to reusable sizing rules.
- Better cross-platform consistency (web/electron/mobile) with fewer layout regressions.

**Bad**:
- Requires touching existing page markup/styles that currently use ad-hoc margins/text classes.
- Slightly constrains experimental layouts unless new semantic steps are added deliberately.

**Neutral**:
- No backend, API, or database changes.
- No external dependency or sync-pipeline impact.
