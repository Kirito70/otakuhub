# ADR 063 — Watch Party Upcoming Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 20.1 defines the Watch Party Upcoming tab behavior so users can quickly see scheduled sessions, RSVP state, and countdown context.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 20.1**.

## Decision
1. Upcoming tab uses existing authenticated watch-party listing endpoint(s) scoped to upcoming events.
2. State includes `items`, `isLoading`, `error`, pagination state, and optional group/time-window filters.
3. Cards show party title/media, host, scheduled time (timezone-safe), RSVP summary, and status.
4. Loading/empty/error states use shared primitives with retry.
5. Card actions navigate to watch-party detail and expose RSVP affordances where allowed.
6. Responsive behavior preserves schedule clarity and CTA visibility across xs/sm/md+.
7. Tests cover loading/empty/error/success states, pagination/retry, date-label behavior, and navigation.

## Consequences
**Good**: Improves visibility of upcoming shared sessions and attendance planning.
**Bad**: Additional temporal formatting edge cases.
**Neutral**: No API or DB schema changes.
