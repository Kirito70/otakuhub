# ADR 050 — My List Paused Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 18.3 defines the My List Paused tab behavior so users can quickly resume stalled titles while retaining progress context and notes visibility.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 18.3**.

## Decision
1. Paused tab uses existing authenticated list endpoints filtered to paused status.
2. State includes `items`, `isLoading`, `error`, and per-entry action state for resume/progress actions.
3. Entries emphasize resume context (last progress, updated timestamp, notes snippet when available).
4. Quick actions support transition back to watching/reading and optional progress update via existing PATCH contract.
5. Loading/empty/error states use shared primitives (`AppEmptyState`) with retry.
6. Responsive layout keeps resume CTA and progress context visible across xs/sm/md+.
7. Tests cover loading/empty/error/success rendering, resume action flow, and retry behavior.

## Consequences
**Good**: Easier recovery of paused titles and stronger continuity for tracking workflows.
**Bad**: More status-transition paths to validate in frontend state.
**Neutral**: No API or DB schema changes.
