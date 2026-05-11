# ADR 071 — Notification Preferences Channels Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 21.4 defines Notification Preferences Channels tab behavior so users can configure delivery channels (Discord/Telegram/email/push) with safe validation and clear save feedback.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 21.4**.

## Decision
1. Channels tab uses existing authenticated notification-preferences GET/PATCH contract(s).
2. State includes channel fields, `isLoading`, `isSaving`, `error`, and save status.
3. Channel inputs apply basic validators:
   - Discord webhook format,
   - Telegram chat id format,
   - email enable/disable consistency,
   - push enable flag handling.
4. Save is disabled while invalid or in-flight; duplicate submissions blocked.
5. Save failures surface actionable form-level errors; success provides confirmation feedback.
6. Channel secrets/identifiers are displayed and edited with cautious UX (no accidental disclosure patterns beyond current policy).
7. Responsive layout preserves form readability and primary save action visibility across xs/sm/md+.
8. Tests cover initial load, validation behavior, save success/failure, in-flight disable, and retry.

## Consequences
**Good**: Safer channel configuration and fewer malformed delivery settings.
**Bad**: More validation logic and platform-specific edge cases in frontend forms.
**Neutral**: No API or DB schema changes.
