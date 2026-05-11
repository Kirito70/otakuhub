# ADR 048 — My List Watching/Reading Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 18.1 defines the My List Watching/Reading tab behavior so users can quickly update in-progress titles with minimal friction.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 18.1**.

## Decision
1. Tab consumes existing authenticated list endpoints with status-scoped filtering for active progress states.
2. State includes `items`, `isLoading`, `error`, and per-entry action state for progress/score quick updates.
3. Default ordering prioritizes recently updated entries to support fast continuation flows.
4. Each row/card shows current progress context and direct update controls (episode/chapter increment/edit).
5. Loading, empty, and error states use shared primitives with retry.
6. Update actions route through existing list PATCH flows and provide clear success/failure feedback.
7. Responsive behavior preserves one-tap access to progress actions on xs/sm/md+.
8. Tests cover loading/empty/error/success rendering, progress update behavior, and retry flow.

## Consequences
**Good**: Faster day-to-day tracking updates for active titles.
**Bad**: More per-item interaction state to manage.
**Neutral**: No API or DB schema changes.
