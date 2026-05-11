# ADR 073 — Profile Edit Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 22.2 defines the Profile Edit tab behavior so users can safely update profile metadata (display name, avatar, bio, timezone) with clear validation and save feedback.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 22.2**.

## Decision
1. Edit Profile tab uses existing authenticated profile update endpoint contract(s).
2. Form state includes editable profile fields, `isLoading`, `isSaving`, `error`, and save status.
3. Validation enforces required/format constraints for supported fields (e.g., display-name length, avatar URL format, timezone value shape as applicable).
4. Submit is disabled while invalid or in-flight; duplicate save attempts blocked.
5. Successful save updates local profile state and shows confirmation feedback.
6. Failed save maps backend validation errors to actionable form-level and/or field-level feedback.
7. Responsive behavior preserves form readability and save CTA visibility across xs/sm/md+.
8. Tests cover initial load, validation behavior, save success/failure, in-flight disable, and retry.

## Consequences
**Good**: Reliable profile editing with lower risk of malformed profile data.
**Bad**: Additional field-validation and partial-update state handling complexity.
**Neutral**: No API or DB schema changes.
