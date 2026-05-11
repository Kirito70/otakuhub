# ADR 043 — Discover Trending Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 17.2 defines the Discover Trending tab behavior so users can quickly browse currently popular titles with stable loading/error handling.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 17.2**.

## Decision
1. Trending tab consumes existing backend media discovery endpoint(s) dedicated to trending/popular surfaces.
2. Frontend state includes `items`, `isLoading`, `error`, and pagination cursor/page where supported.
3. Loading uses skeleton cards; failure uses `AppEmptyState(mode='error')` with retry.
4. Empty results use `AppEmptyState(mode='empty')` with actionable text.
5. Cards navigate to `media-detail`.
6. Preserve responsive parity across xs/sm/md+ and avoid hover-only actions.
7. Tests cover loading, error, empty, success, retry, and navigation behavior.

## Consequences
**Good**: Consistent discovery UX and reusable state patterns.
**Bad**: Additional tab-state and test maintenance.
**Neutral**: No DB or API schema changes.
