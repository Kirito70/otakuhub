# ADR 053 — My List Custom Lists Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 18.6 defines the My List Custom Lists tab behavior so users can create and manage curated personal/group-facing lists (e.g., themed recommendations, watch-with-friends queues).

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 18.6**.

## Decision
1. Custom Lists tab uses existing authenticated custom-list endpoints for create/update/delete and entry replacement/ordering.
2. State includes `lists`, `selectedList`, `entries`, `isLoading`, `error`, and per-action loading/error states for CRUD/reorder flows.
3. UX supports:
   - create custom list,
   - edit list metadata,
   - delete list,
   - add/remove/reorder list entries.
4. Entry reordering uses deterministic sort order persistence via existing list-entry replace/update contract.
5. Loading/empty/error states use shared primitives with retry.
6. Destructive actions (delete list/remove entry) require explicit confirmation.
7. Responsive behavior preserves core list-management actions across xs/sm/md+.
8. Tests cover create/edit/delete flows, reorder persistence behavior, loading/empty/error states, and retry.

## Consequences
**Good**: Enables flexible curation workflows beyond status-based tracking tabs.
**Bad**: Highest UI-state complexity among My List tabs (selection + nested entry operations).
**Neutral**: No API or DB schema changes.
