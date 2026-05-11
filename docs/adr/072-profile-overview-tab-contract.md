# ADR 072 — Profile Overview Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 22.1 defines the Profile Overview tab behavior so users can view core identity, activity summary, and account context in one stable layout.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 22.1**.

## Decision
1. Overview tab uses existing authenticated profile/me endpoint contracts and existing activity/stat surfaces where available.
2. State includes `profile`, `isLoading`, `error`, and optional recent-activity/stat collections.
3. Layout includes avatar, display name/username, bio, timezone, and lightweight summary metrics.
4. Loading/empty/error states use shared primitives with retry.
5. Related actions (edit profile, account settings) are clearly discoverable and route to profile sub-tabs.
6. Responsive behavior preserves identity/readability hierarchy across xs/sm/md+.
7. Tests cover loading/empty/error/success rendering, key metadata visibility, and sub-route/action navigation.

## Consequences
**Good**: Clear account landing context and better profile discoverability.
**Bad**: Optional stats/activity blocks introduce conditional rendering complexity.
**Neutral**: No API or DB schema changes.
