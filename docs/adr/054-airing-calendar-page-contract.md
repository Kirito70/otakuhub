# ADR 054 — Airing Calendar Page Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 18.7 defines the Airing Calendar page behavior so users can see upcoming/recent episode releases in a timezone-safe, schedule-oriented format.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 18.7**.

## Decision
1. Airing Calendar uses existing authenticated media airing endpoint contract(s) with paginated fetch support.
2. State includes `items`, `isLoading`, `error`, paging state, and selected date/window context where applicable.
3. Render grouped schedule entries by date/time with timezone-aware labels based on user profile timezone preference (fallback UTC).
4. Loading/empty/error states use shared primitives (`AppEmptyState`) and retry behavior.
5. Calendar entries navigate to `media-detail` route.
6. Responsive behavior supports readable date grouping and touch-friendly actions across xs/sm/md+.
7. Tests cover loading/empty/error/success rendering, timezone/date-label formatting expectations, pagination behavior, retry, and navigation.

## Consequences
**Good**: Improves release-awareness and planning for active watchers.
**Bad**: Timezone/date formatting introduces additional edge-case handling.
**Neutral**: No API or DB schema changes.
