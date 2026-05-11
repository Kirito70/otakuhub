# ADR 068 — Notifications Inbox All Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 21.1 defines Notifications Inbox All tab behavior so users can review all notifications with clear read/unread distinction and consistent fallback states.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 21.1**.

## Decision
1. Inbox All tab uses existing authenticated notifications listing endpoint(s).
2. State includes `items`, `isLoading`, `error`, pagination state, and derived unread counters.
3. Notification rows/cards show type, title/body preview, related media/user context (when available), and recency.
4. Read/unread styling is explicit and accessible; no color-only state indication.
5. Loading/empty/error states use `AppEmptyState` with retry.
6. Notification actions navigate to linked destination where applicable.
7. Responsive behavior preserves readability and touch-target accessibility across xs/sm/md+.
8. Tests cover loading/empty/error/success, read/unread rendering, pagination/retry, and navigation.

## Consequences
**Good**: Better inbox clarity and actionability.
**Bad**: Additional UI-state management for read/unread rendering and badges.
**Neutral**: No API or DB schema changes.
