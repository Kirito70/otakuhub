# ADR 069 — Notifications Inbox Unread Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 21.2 defines Notifications Inbox Unread tab behavior so users can focus on pending items and clear unread backlog efficiently.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 21.2**.

## Decision
1. Unread tab uses existing notifications listing/filter capabilities restricted to unread items.
2. State includes `items`, `isLoading`, `error`, pagination state, and bulk-action state where mark-all-read is supported.
3. UI emphasizes unread prioritization and optional “mark all as read” action with confirmation/feedback.
4. Loading/empty/error states use shared primitives with retry.
5. Item navigation behavior mirrors Inbox All tab route mapping.
6. Responsive behavior preserves unread triage actions across xs/sm/md+.
7. Tests cover loading/empty/error/success states, mark-all/read action behavior, pagination/retry, and navigation.

## Consequences
**Good**: Faster notification triage and reduced inbox overload.
**Bad**: Added bulk-action state and edge-case handling.
**Neutral**: No API or DB schema changes.
