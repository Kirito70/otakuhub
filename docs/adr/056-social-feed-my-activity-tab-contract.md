# ADR 056 — Social Feed My Activity Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.2 defines the Feed My Activity tab behavior so each user can review their own tracking timeline and quickly navigate back to relevant media/actions.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.2**.

## Decision
1. My Activity tab uses existing authenticated activity/feed endpoint capabilities scoped to current user events.
2. State includes `items`, `isLoading`, `error`, pagination state, and optional event-type filters.
3. Activity items prioritize personal delta context (status/progress/score changes) and relative recency.
4. Loading/empty/error states use shared primitives with retry action.
5. Activity cards navigate to relevant routes (media detail/list context) where applicable.
6. Responsive behavior preserves readability and tap targets across xs/sm/md+.
7. Tests cover loading/empty/error/success, filters, pagination, retry, and navigation.

## Consequences
**Good**: Better self-tracking visibility and easier recovery of recent actions.
**Bad**: Additional event rendering/state branches in feed UI.
**Neutral**: No API or DB schema changes.
