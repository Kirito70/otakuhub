# ADR 049 — My List Completed Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 18.2 defines the My List Completed tab behavior so users can review finished titles, adjust personal scores, and trigger rewatch/reread flows with clear context.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 18.2**.

## Decision
1. Completed tab uses existing authenticated list endpoints filtered to completed statuses.
2. State includes `items`, `isLoading`, `error`, and per-entry action state for score/rewatch actions.
3. Entries surface completion metadata (completed date, final progress, score where present).
4. Quick actions support score edits and rewatch/reread initiation through existing PATCH list contract.
5. Loading/empty/error fallback uses shared primitives with retry action.
6. Responsive layout preserves score/action discoverability on xs/sm/md+.
7. Tests cover loading/empty/error/success rendering, score update flow, rewatch/reread action behavior, and retry.

## Consequences
**Good**: Better post-completion management and retrospective scoring workflows.
**Bad**: Added action-state complexity for mixed score and status transitions.
**Neutral**: No API or DB schema changes.
