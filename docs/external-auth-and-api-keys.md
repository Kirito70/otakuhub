# External API Keys, OAuth Flows, and Data Coverage Guide

This guide explains how to configure external providers and how OtakuHub should connect user accounts (especially MyAnimeList) for data import.

## 1) Providers Used by OtakuHub

- **AniList** (GraphQL): core metadata source and canonical external ID.
- **MangaDex** (REST v5): manga metadata + chapter feed.
- **Jikan** (REST): supplemental MAL-derived metadata (unofficial API).
- **MyAnimeList (official OAuth)**: user account linking + personal list import.

---

## 2) Required Environment Variables (backend)

Set these in backend `.env` (or deployment secret store):

```env
ANILIST_CLIENT_ID=<anilist client id>
ANILIST_CLIENT_SECRET=<anilist client secret>

MAL_CLIENT_ID=<myanimelist oauth client id>
MAL_CLIENT_SECRET=<myanimelist oauth client secret>
MAL_REDIRECT_URI=https://<your-backend-domain>/api/v1/auth/mal/callback

MANGADEX_USERNAME=<optional>
MANGADEX_PASSWORD=<optional>
```

> Never expose client secrets in frontend code.

---

## 3) How to Obtain Keys / App Credentials

## 3.1 AniList
1. Log in to AniList.
2. Go to developer/app settings and create an OAuth app.
3. Set callback URL to your backend callback endpoint.
4. Save `client_id` and `client_secret`.

## 3.2 MyAnimeList (official)
1. Log in at MyAnimeList.
2. Create an API application in MAL API settings.
3. Use **Authorization Code + PKCE** flow.
4. Register backend callback URI exactly (must match).
5. Save `client_id` and `client_secret`.

## 3.3 MangaDex
- Public metadata endpoints usually work without app keys.
- If authenticated routes are needed later, create MangaDex account credentials for server-side use only.

## 3.4 Jikan
- Jikan is public and generally keyless.
- Respect strict rate limits.

---

## 4) MAL OAuth Authorization Flow (recommended backend contract)

## Step A — Start link
- Frontend opens backend endpoint:
  - `GET /api/v1/auth/mal/connect`
- Backend returns/redirects to MAL authorize URL with:
  - `client_id`
  - `redirect_uri`
  - `response_type=code`
  - `code_challenge` (PKCE)
  - `state` (CSRF protection)

## Step B — User consents on MAL
- MAL redirects to backend callback with `code` + `state`.

## Step C — Backend exchanges code
- Backend calls MAL token endpoint with `code_verifier`.
- Backend stores tokens in `external_auth` (`provider='myanimelist'`) encrypted at rest.

## Step D — Import user list
- Backend triggers import task/command (sync pipeline) to read MAL list and map into `user_list_entries`.

## Step E — Refresh/revoke handling
- If token expires, backend refreshes with stored refresh token.
- Provide unlink endpoint to revoke/deactivate integration.

Security requirements:
- Keep PKCE verifier and `state` server-side only.
- Never send provider refresh tokens to frontend.

---

## 5) Are we fetching the required data today?

Below is a practical check against core requirements.

| Requirement | Source | Current status |
|---|---|---|
| Canonical media identity via AniList ID | AniList | **Implemented** in current AniList client/query usage |
| Core media fields (titles, format, status, synopsis, score, season, images) | AniList | **Implemented** in `anilist_client.py` queries |
| Genres/tags/studios/relations | AniList | **Implemented** in detailed media query |
| Manga chapter feed | MangaDex | **Partially implemented** (`get_chapters`) |
| MAL user account linking (OAuth) | MAL official API | **Not yet implemented end-to-end** (schema exists, full flow pending) |
| MAL personal list import via linked account | MAL official API | **Not yet implemented end-to-end** |
| Supplemental MAL metadata via Jikan | Jikan | **Basic client implemented** |

### Immediate gaps to address
1. Implement official MAL OAuth connect/callback endpoints.
2. Implement provider token refresh lifecycle in backend service.
3. Implement linked-account MAL list import job using stored `external_auth`.
4. Add tests for connect/callback/error/retry paths.

---

## 6) Minimal endpoint plan for MAL linking

- `GET /api/v1/auth/mal/connect` (auth required)
- `GET /api/v1/auth/mal/callback` (public callback)
- `POST /api/v1/sync/import/mal-linked` (auth required)
- `DELETE /api/v1/auth/mal/unlink` (auth required)

---

## 7) Validation checklist before shipping MAL integration

- [ ] Callback URI exact-match verified in MAL settings
- [ ] PKCE + state CSRF protection implemented
- [ ] Access/refresh token encrypted at rest in DB
- [ ] Token refresh + expired token fallback tested
- [ ] Import job idempotency tested
- [ ] External API rate limiting configured and monitored
