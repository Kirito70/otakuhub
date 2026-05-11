# ADR 065 — Watch Party Detail Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 20.3 defines the Watch Party Detail tab behavior so users can inspect full party context and perform RSVP transitions with clear host/attendee visibility.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 20.3**.

## Decision
1. Detail tab uses existing authenticated watch-party detail/RSVP endpoint contract(s).
2. State includes `party`, `isLoading`, `error`, and RSVP action state.
3. View presents schedule, host, media context, stream/sync links, notes, and attendee RSVP summary.
4. RSVP controls support valid transitions (attending/declined/pending where allowed) through existing RSVP contract.
5. Loading/empty/error states use shared primitives with retry.
6. Host-only controls (if present) must be role-gated in UI and backed by backend authorization.
7. Responsive behavior preserves RSVP and join-link accessibility across xs/sm/md+.
8. Tests cover loading/empty/error/success rendering, RSVP transition behavior, permission-gated actions, retry, and navigation stability.

## Consequences
**Good**: Improves party coordination and attendance clarity.
**Bad**: More role/state-conditional UI branches.
**Neutral**: No API or DB schema changes.
