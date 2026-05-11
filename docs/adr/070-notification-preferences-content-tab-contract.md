# ADR 070 — Notification Preferences Content Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 21.3 defines Notification Preferences Content tab behavior so users can control which notification categories they receive with clear, reversible settings.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 21.3**.

## Decision
1. Content tab uses existing authenticated notification-preferences GET/PATCH contract(s).
2. State includes preferences payload, `isLoading`, `isSaving`, `error`, and success-feedback status.
3. UI exposes per-notification-type toggles (episode/chapter/activity/recommendation/watch-party/system as supported).
4. Save flow persists only changed fields where possible; disable submit while saving.
5. Loading/error states use shared primitives; failed save surfaces actionable form-level message.
6. Preferences changes should be immediately reflected in UI state after successful save.
7. Responsive behavior preserves toggle readability and save action accessibility across xs/sm/md+.
8. Tests cover initial load, toggle mutation, save success, save failure, disabled-while-saving, and retry behavior.

## Consequences
**Good**: Users can tune notification signal-to-noise effectively.
**Bad**: Additional settings-state synchronization and partial-update handling.
**Neutral**: No API or DB schema changes.
