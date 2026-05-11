# ADR 042 — Discover Search Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 17.1 defines the frontend contract for the Discover page Search tab. Users need fast, predictable title discovery with strong loading/error handling and no direct external API calls from frontend.

The backend media search endpoint already exists. This phase formalizes UX/state rules for resilient query behavior before implementing additional Discover tabs.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 17.1**.

## Decision
Adopt the following Discover Search tab contract:

1. **Data source and boundaries**
   - Frontend Search tab uses only `GET /api/v1/media/search`.
   - No direct AniList/MangaDex calls from frontend.

2. **Query behavior**
   - Debounced query input for incremental search.
   - Ignore stale responses when newer queries are in flight.
   - Preserve last successful result set until replacement or explicit clear.

3. **State model**
   - `query`, `results`, `isLoading`, `error`, `page`, `hasMore`.
   - Empty query uses discover guidance state (not an error).
   - Empty results use `AppEmptyState(mode='empty')` with clear wording.

4. **Error and retry policy**
   - API/network failure shows `AppEmptyState(mode='error')` with retry CTA.
   - Retry reuses last attempted query parameters.

5. **Interaction contract**
   - Result cards navigate to media detail route.
   - Primary controls remain accessible on xs/sm/md+ breakpoints.
   - Loading skeletons used while fetching to avoid layout shift.

6. **Testing requirements (TDD-aligned)**
   - Debounce behavior and stale-response safety.
   - Loading/empty/error/success state assertions.
   - Retry behavior after error.
   - Result-click navigation assertion.

## Consequences
**Good**:
- Predictable discover behavior with fewer flickers/race issues.
- Strong alignment with existing backend/API boundaries.
- Reusable state contract for other tabbed discovery experiences.

**Bad**:
- Extra composable complexity for request cancellation/stale-response handling.
- Additional test harness setup for debounce timing and async races.

**Neutral**:
- No database schema changes.
- No API endpoint additions.
