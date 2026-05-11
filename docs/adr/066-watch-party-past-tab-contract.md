# ADR 066 — Watch Party Past Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 20.4 defines the Watch Party Past tab behavior so users can review completed/cancelled sessions and retain lightweight history context.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 20.4**.

## Decision
1. Past tab uses existing authenticated watch-party listing capabilities scoped to non-upcoming statuses (completed/cancelled).
2. State includes `items`, `isLoading`, `error`, pagination state, and optional time-range/group filters.
3. Cards show media/title, host, scheduled/completed timestamps, final status, and summary context.
4. Loading/empty/error states use shared primitives with retry behavior.
5. Card actions allow detail navigation; no RSVP mutation actions for finalized sessions.
6. Responsive behavior preserves history readability and status clarity across xs/sm/md+.
7. Tests cover loading/empty/error/success states, filter behavior, pagination/retry, status labeling, and navigation.

## Consequences
**Good**: Gives users an auditable social watch-history trail.
**Bad**: Additional status-specific rendering and filtering branches.
**Neutral**: No API or DB schema changes.
