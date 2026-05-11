# ADR 051 — My List Dropped Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 18.4 defines the My List Dropped tab behavior so users can review discontinued titles, understand why entries were dropped, and recover items back into active states when desired.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 18.4**.

## Decision
1. Dropped tab uses existing authenticated list endpoints filtered to dropped status.
2. State includes `items`, `isLoading`, `error`, and per-entry action state for recovery/status-change actions.
3. Entries surface dropped-context metadata (progress snapshot, notes excerpt, updated timestamp) where available.
4. Quick actions support recovery transitions (e.g., back to watching/reading or plan states) through existing PATCH list contract.
5. Loading/empty/error states use shared primitives with retry behavior.
6. Responsive behavior keeps recovery CTA visible and avoids hover-only interactions across xs/sm/md+.
7. Tests cover loading/empty/error/success rendering, recovery action flow, and retry behavior.

## Consequences
**Good**: Improves list recovery workflows and reduces permanently abandoned entries.
**Bad**: Adds additional status-transition combinations in frontend state logic.
**Neutral**: No API or DB schema changes.
