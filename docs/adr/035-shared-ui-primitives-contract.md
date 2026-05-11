# ADR 035 — Shared UI Primitives Contract (AppCard, AppBadge, AppToolbar, AppEmptyState)
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 15.3 requires reusable UI primitives so all pages share one consistent visual and interaction language. After Phase 15.1 (token semantics) and 15.2 (typography/spacing), we now need component-level contracts that implementation agents can build without ambiguity.

OtakuHub is a private small-group app; consistency and maintainability are more important than a large, highly-abstracted design system.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 15.3**.

## Decision
Define four mandatory shared primitives in frontend:

1. **`AppCard`**
   - Purpose: Standard container for dashboard blocks, media summaries, and settings sections.
   - Variants:
     - `tone`: `default | muted | elevated | destructive`
     - `padding`: `sm | md | lg`
     - `border`: `default | strong | subtle | none`
   - Slots: `header`, `default`, `footer`, optional `actions`.

2. **`AppBadge`**
   - Purpose: Compact semantic status labels (e.g., Watching, Completed, Warning, Sync Failed).
   - Variants:
     - `tone`: `primary | success | warning | destructive | info | muted`
     - `size`: `sm | md`
   - Accessibility: must include text label; icon-only badge is disallowed.

3. **`AppToolbar`**
   - Purpose: Page-level heading + action bar used by all top-level screens.
   - Props:
     - `title` (required)
     - `subtitle` (optional)
     - `dense` (optional boolean)
   - Slots: `leading`, `actions`, `meta`.
   - Behavior: responsive stack on mobile; inline row on md+ screens.

4. **`AppEmptyState`**
   - Purpose: Shared no-data/error-retry presentation contract.
   - Props:
     - `mode`: `empty | error | loading_hint`
     - `title` (required)
     - `description` (optional)
     - `actionLabel` / `onAction` (optional)
   - Rules: actionable mode must always provide explicit CTA text.

Cross-primitive rules:
- All tones/sizes map only to semantic tokens from ADR 033 + ADR 034.
- No primitive accepts raw hex color props.
- No primitive exposes pixel-based spacing props; use semantic size variants only.

## Consequences
**Good**:
- Standardized UX across Discover, Tracking, Social, Watch Party, Notifications, and Profile pages.
- Faster implementation in upcoming phases via reusable, bounded components.
- Lower styling regressions from ad-hoc CSS.

**Bad**:
- Initial migration effort to replace page-local card/badge/toolbar/empty implementations.
- Requires strict review discipline to avoid bypassing primitives.

**Neutral**:
- No backend/API/database changes.
- No changes to auth/security model.
