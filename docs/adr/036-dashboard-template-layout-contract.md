# ADR 036 — Dashboard Template Layout Contract (Desktop-first, Mobile-adaptive)
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 15.4 requires a shared dashboard template so all top-level pages present information with consistent structure and action placement across desktop, web, Electron, and mobile shells.

After defining semantic tokens (ADR 033), typography/spacing scales (ADR 034), and shared primitives (ADR 035), we now need a page-composition blueprint to prevent each page from creating bespoke layouts.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 15.4**.

## Decision
Adopt a standard dashboard page template composed from shared primitives and Quasar layout behavior.

1. **Desktop-first structure (md+)**
   - Top section: `AppToolbar` with title, subtitle, and right-aligned actions.
   - Main content: 12-column responsive grid using Quasar rows/cols.
   - Primary cards and lists use `AppCard` with semantic variants.
   - Empty/error/loading sections render via `AppEmptyState`.

2. **Mobile-adaptive structure (xs/sm)**
   - Toolbar stacks title/subtitle/actions vertically.
   - Grid collapses to single column by default.
   - Critical actions remain visible without requiring hover/desktop affordances.

3. **Content zone contract**
   - `hero` zone: page summary and primary KPIs.
   - `primary` zone: core task area for the page.
   - `secondary` zone: supplemental cards/metadata.
   - `state` zone: empty/error/loading state slot.

4. **Interaction consistency rules**
   - Primary CTA appears in toolbar actions on desktop and below title on mobile.
   - Status indicators use `AppBadge` only.
   - Section wrappers use semantic spacing tokens (ADR 034), not custom pixel gaps.

5. **Non-goals**
   - No new backend endpoints.
   - No route semantics change.
   - No special per-page custom layout framework.

## Consequences
**Good**:
- Provides a predictable UI skeleton for upcoming feature phases (16–22).
- Reduces page-level duplication and layout regressions.
- Improves implementation speed and review clarity.

**Bad**:
- Existing pages with bespoke structure require migration.
- Some edge-case pages may need approved exceptions.

**Neutral**:
- No database/API/auth changes.
- No sync pipeline or worker impact.
