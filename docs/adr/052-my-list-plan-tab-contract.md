# ADR 052 — My List Plan to Watch/Read Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 18.5 defines the My List Plan to Watch/Read tab behavior so users can manage backlog entries and promote items into active watching/reading states efficiently.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 18.5**.

## Decision
1. Plan tab uses existing authenticated list endpoints filtered to `plan_to_watch` / `plan_to_read` statuses.
2. State includes `items`, `isLoading`, `error`, and per-entry action state for backlog-to-active transitions.
3. Default sorting supports backlog prioritization (recency and/or user-driven priority controls where available).
4. Entries expose core planning context (title metadata, notes, last update) and direct “start now” actions.
5. Quick actions route through existing PATCH list contract to transition into active states.
6. Loading/empty/error states use shared primitives (`AppEmptyState`) with retry.
7. Responsive behavior preserves action clarity and avoids hover-only critical interactions.
8. Tests cover loading/empty/error/success rendering, transition action flow, sort/prioritization behavior, and retry.

## Consequences
**Good**: Stronger backlog management and faster movement into active tracking.
**Bad**: Additional sorting/prioritization state complexity in UI.
**Neutral**: No API or DB schema changes.
