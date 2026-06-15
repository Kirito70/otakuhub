# ADR 092 — Phase F6: Watch Party Flutter Implementation
**Status**: Proposed
**Date**: 2026-06-15

## Context
Watch Party (Phases 10/20 for backend/Vue reference) is implemented and tested on the backend and Vue reference frontend. The Flutter app has wireframe screens (`WatchPartyListScreen`, `CreateWatchPartyScreen`) with no real content. We need to implement the full Watch Party experience in Flutter:

- Upcoming watch parties list
- Past watch parties list
- Create watch party form
- Party detail view with RSVP actions
- RSVP management (attending/declined/maybe)

The Vue reference uses a **single-page approach**: one `WatchPartyPage.vue` with four views (Upcoming, Past, Create, Detail dialog) controlled by an `activeTab` state. The Flutter design follows this consolidated pattern but uses a `TabBar` for the list/create views and a modal bottom sheet for detail.

## Project Status check
Current phase: F5 (Social Features) complete. Moving to F6 (Watch Party).

## Decision

### Architecture: Single screen with TabBar + Modal Bottom Sheet
Replace the two wireframe screens with a single `WatchPartyScreen` with 3-tab `TabBar`:
- **Upcoming** tab — list of upcoming/scheduled/live parties, each with quick "Attend" button
- **Past** tab — list of completed/cancelled parties
- **Create** tab — form with validation

Party detail is shown via a **modal bottom sheet** (`showModalBottomSheet`) triggered by tapping a party card, not a separate route. This matches the Vue reference's overlay dialog approach and avoids route bloat.

### Data Models (freezed + json_serializable)
Create `lib/features/watchparty/models/watch_party.dart` with:
- `WatchParty` — core model (id, mediaId, hostUserId, title, scheduledAt, status, streamUrl, notes, timestamps)
- `WatchPartyDetail` — extends watch party with host info + media info + RSVP summary
- `WatchPartyRsvp` — RSVP record (partyId, userId, status, timestamps)
- `WatchPartyCreateRequest` — create payload
- `WatchPartyRsvpRequest` — RSVP payload
- `WatchPartyListResponse` — paginated wrapper
- `WatchPartyDetailResponse` — detail wrapper  
- `WatchPartyRsvpListResponse` — RSVP list wrapper

All use `@JsonKey(name: 'snake_case')` to match backend Pydantic v2 JSON.

### Providers (riverpod_generator @riverpod)
Create `lib/features/watchparty/providers/watch_party_provider.dart` with:

| Provider | Type | Description |
|----------|------|-------------|
| `upcomingPartiesProvider` | FutureProvider | GET /api/v1/watchparty (upcoming list) |
| `pastPartiesProvider` | FutureProvider | GET /api/v1/watchparty/past (past list, lazy) |
| `partyDetailProvider(id)` | FutureProvider.family | GET /api/v1/watchparty/{id} |
| `partyRsvpsProvider(id)` | FutureProvider.family | GET /api/v1/watchparty/{id}/rsvps |
| `createPartyActionProvider` | AsyncNotifier | POST /api/v1/watchparty (create + invalidate) |
| `rsvpActionProvider(id)` | AsyncNotifier.family | POST /api/v1/watchparty/{id}/rsvp |

### API Endpoints (add to api_endpoints.dart)
| Constant | Path | Method | Status |
|----------|------|--------|--------|
| `watchParty` | `/api/v1/watchparty` | GET (list) + POST (create) | Already exists |
| `watchPartyPast` | `/api/v1/watchparty/past` | GET | **Add** |
| `watchPartyDetail` | `/api/v1/watchparty` | GET + `/{id}` | **Add** |
| `watchPartyRsvps` | `/api/v1/watchparty` | GET + `/{id}/rsvps` | **Add** |
| `watchPartyRsvp` | `/api/v1/watchparty` + `/{id}/rsvp` | POST | Already exists |

### Screens
- **`WatchPartyScreen`** — main screen with `TabController` (3 tabs), replaces both old wireframe screens
- **Widget: `PartyCard`** — reusable card showing title, date, episode, status badge, optional "Attend" button  
- **Widget: `PartyDetailSheet`** — modal bottom sheet with party info, host/media details, RSVP action buttons, attendee list

### Router Changes
- Remove `/watchparty/create` separate route (create is a tab within the main screen)
- Keep `/watchparty` as the single route pointing to `WatchPartyScreen`
- Remove `createWatchParty` route import, keep `watchParty` route

### Layer Boundaries
| Layer | Responsibility |
|-------|---------------|
| **Screen** | TabController, tab switching, passing callbacks to children, orchestrating bottom sheet |
| **UpcomingTab** (widget) | Watch `upcomingPartiesProvider`, render list with PartyCards, "Attend" quick-action, tap → bottom sheet |
| **PastTab** (widget) | Watch `pastPartiesProvider` (lazy - only on first tab visit), render list |
| **CreateTab** (widget) | Form fields + validation, `createPartyActionProvider` on submit, success → clear + switch to Upcoming |
| **PartyDetailSheet** (widget) | Watch `partyDetailProvider(id)` and `partyRsvpsProvider(id)`, show RSVP action buttons, attendee list |
| **PartyCard** (widget) | Pure presentational: title, date, status badge, episode number, optional Attend button |
| **Providers** | HTTP calls via Dio, AsyncValue states (loading/error/data), invalidate on mutations |
| **Models** | Immutable freezed data classes with JSON serialization |

### Tests (14 widget tests)
| Test file | Tests | Coverage |
|-----------|-------|----------|
| `watch_party_screen_test.dart` | 6 | AppBar title, all 3 tabs render, loading state, empty state, tab switching |
| `watch_party_create_test.dart` | 4 | Required field validation, submit disabled when empty, valid submit calls API, success clears form |
| `watch_party_detail_test.dart` | 4 | Detail loads, RSVP buttons render, attendee list shows, RSVP action calls API |

## Consequences
**Good**:
- Single screen approach matches Vue reference architecture
- Modal bottom sheet for detail is more Flutter-native than a separate route
- Reuses established patterns from F5 (FutureProvider family, freezed models, riverpod_generator)
- TabBar for Upcoming/Past/Create keeps navigation simple
- Quick "Attend" button on upcoming list items for one-tap RSVP

**Bad**:
- `/watchparty/create` route is removed (breaking change if linked from elsewhere)
- Single screen must handle all the state for 3 tabs + modal (complexity in one file)
- Lazy-loading past tab requires state tracking (hasLoadedPast flag)

**Neutral**:
- Detail bottom sheet means no deep-linkable watch party detail URL (acceptable for a small-group app)
- Mobile bottom nav doesn't show Watch Party (it's grouped under Feed index) — consistent with Vue reference where it's a secondary nav item
