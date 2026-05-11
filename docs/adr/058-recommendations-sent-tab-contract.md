# ADR 058 — Recommendations Sent Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.4 defines the Recommendations Sent tab behavior so users can review outbound recommendations, track acknowledgement state, and revisit suggested titles.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.4**.

## Decision
1. Sent tab uses existing authenticated recommendations query capabilities for sender-scoped records.
2. State includes `items`, `isLoading`, `error`, pagination state, and optional filters (acknowledged/unacknowledged).
3. Cards show recipient, media, message preview, recency, and acknowledgement status.
4. Loading/empty/error states use `AppEmptyState` with retry behavior.
5. Card actions navigate to relevant routes (media/profile) where applicable.
6. Responsive behavior preserves status readability and action discoverability across xs/sm/md+.
7. Tests cover loading/empty/error/success states, filter behavior, pagination/retry, and navigation.

## Consequences
**Good**: Better visibility into outbound recommendation outcomes.
**Bad**: Additional feed-style rendering/filter maintenance.
**Neutral**: No API or DB schema changes.
