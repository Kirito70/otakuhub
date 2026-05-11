# ADR 044 — Discover New Releases Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 17.3 defines the Discover New Releases tab behavior so users can browse recent episode/chapter updates with reliable pagination and fallback states.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 17.3**.

## Decision
1. New Releases tab consumes existing backend media-release/airing update surface(s); no direct external API calls.
2. State includes `items`, `isLoading`, `error`, and `page/cursor + hasMore` for incremental loading.
3. Initial tab activation triggers fetch; subsequent pagination appends in stable order (newest first by release timestamp).
4. Loading uses skeleton list/grid; empty and error states use `AppEmptyState` with retry.
5. Item cards navigate to `media-detail` and expose release context (episode/chapter label + timestamp).
6. Responsive parity preserved across xs/sm/md+.
7. Tests cover loading, empty, error, retry, pagination append, and navigation.

## Consequences
**Good**: Clear recent-release discovery and reusable paginated-tab pattern.
**Bad**: Additional list-state complexity and pagination tests.
**Neutral**: No DB/API schema changes.
