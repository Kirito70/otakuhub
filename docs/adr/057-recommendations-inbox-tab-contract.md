# ADR 057 — Recommendations Inbox Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.3 defines the Recommendations Inbox tab behavior so users can review incoming recommendations, acknowledge them, and navigate to suggested titles.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.3**.

## Decision
1. Inbox tab uses existing authenticated recommendations inbox endpoint(s).
2. State includes `items`, `isLoading`, `error`, pagination state, and acknowledge-action state per recommendation.
3. Cards show sender, media, optional message, recency, and acknowledgement state.
4. Quick actions support acknowledge/update flow through existing recommendation endpoints.
5. Loading/empty/error states use `AppEmptyState` with retry.
6. Media/sender links navigate to relevant routes.
7. Responsive behavior preserves triage actions on xs/sm/md+.
8. Tests cover loading/empty/error/success, acknowledge flow, pagination/retry, and navigation.

## Consequences
**Good**: Clear triage flow for social recommendations.
**Bad**: Additional per-item action state management.
**Neutral**: No API or DB schema changes.
