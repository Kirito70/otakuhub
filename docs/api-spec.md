# OtakuHub API Specification (OpenAPI‑style summary)

## Phase Notes
- **2026-05-11 (Phase 15.1)**: No API contract changes. Frontend design-token/theming work is internal UI architecture only.
- **2026-05-11 (Phase 15.2)**: No API contract changes. Typography/spacing scale work is frontend presentation architecture only.
- **2026-05-11 (Phase 15.3)**: No API contract changes. Shared UI primitive contracts are frontend component architecture only.
- **2026-05-11 (Phase 15.4)**: No API contract changes. Dashboard template work is frontend layout architecture only.
- **2026-05-11 (Phase 15.5)**: No API contract changes. Responsive validation work is frontend behavior architecture only.
- **2026-05-11 (Phase 16.1)**: No new endpoints. Clarified frontend mapping expectations for `/api/v1/auth/login` error cases (401/429/5xx).
- **2026-05-11 (Phase 16.2)**: No new endpoints. Clarified frontend mapping expectations for `/api/v1/auth/register` error cases (400/403/429/5xx).
- **2026-05-11 (Phase 16.3)**: No new endpoints. Clarified frontend handling expectations for `/api/v1/setup/bootstrap-admin` error cases (409/429/5xx).
- **2026-05-11 (Phase 16.4)**: No new endpoints. Established frontend auth/setup test matrix coverage expectations for existing auth/setup contracts.
- **2026-05-11 (Phase 17.1)**: No new endpoints. Discover Search tab standardizes frontend use of existing `GET /api/v1/media/search` contract.
- **2026-05-11 (Phase 17.2)**: No new endpoints. Discover Trending tab standardizes frontend behavior over existing trending/popular media contract(s).
- **2026-05-11 (Phase 17.3)**: No new endpoints. Discover New Releases tab standardizes frontend behavior over existing recent-release media contract(s).
- **2026-05-11 (Phase 17.4)**: No new endpoints. Media Detail Overview tab standardizes frontend behavior over existing `GET /api/v1/media/{id}` and list-action contracts.
- **2026-05-11 (Phase 17.5)**: No new endpoints. Media Detail Episodes/Chapters tab standardizes frontend behavior over existing installment/list-update contracts.
- **2026-05-11 (Phase 17.6)**: No new endpoints. Media Detail Relations tab standardizes frontend behavior over existing media-relation contracts.
- **2026-05-11 (Phase 18.1)**: No new endpoints. My List Watching/Reading tab standardizes frontend behavior over existing authenticated list + patch-update contracts.
- **2026-05-11 (Phase 18.2)**: No new endpoints. My List Completed tab standardizes frontend behavior over existing completed-list + patch-update contracts.
- **2026-05-11 (Phase 18.3)**: No new endpoints. My List Paused tab standardizes frontend behavior over existing paused-list + patch-update contracts.
- **2026-05-11 (Phase 18.4)**: No new endpoints. My List Dropped tab standardizes frontend behavior over existing dropped-list + patch-update contracts.
- **2026-05-11 (Phase 18.5)**: No new endpoints. My List Plan tab standardizes frontend behavior over existing plan-list + patch-update contracts.
- **2026-05-11 (Phase 18.6)**: No new endpoints. My List Custom Lists tab standardizes frontend behavior over existing custom-list CRUD and entry-ordering contracts.
- **2026-05-11 (Phase 18.7)**: No new endpoints. Airing Calendar page standardizes frontend behavior over existing media airing contract(s).
- **2026-05-11 (Phase 19.1)**: No new endpoints. Feed Group Activity tab standardizes frontend behavior over existing authenticated social feed contract(s).
- **2026-05-11 (Phase 19.2)**: No new endpoints. Feed My Activity tab standardizes frontend behavior over existing authenticated activity feed contract(s).
- **2026-05-11 (Phase 19.3)**: No new endpoints. Recommendations Inbox tab standardizes frontend behavior over existing recommendations inbox/acknowledge contracts.
- **2026-05-11 (Phase 19.4)**: No new endpoints. Recommendations Sent tab standardizes frontend behavior over existing sender-scoped recommendations contracts.
- **2026-05-11 (Phase 19.5)**: No new endpoints. Discussions Threads tab standardizes frontend behavior over existing discussions listing contracts.
- **2026-05-11 (Phase 19.6)**: No new endpoints. Discussions Thread Detail tab standardizes frontend behavior over existing discussion detail/replies contracts.
- **2026-05-11 (Phase 19.7)**: No new endpoints. Discussions Create tab standardizes frontend behavior over existing discussion-create contract(s).
- **2026-05-11 (Phase 19.8)**: No new endpoints. Social page test expansion standardizes validation coverage for existing feed/recommendations/discussions contracts.
- **2026-05-11 (Phase 20.1)**: No new endpoints. Watch Party Upcoming tab standardizes frontend behavior over existing watch-party listing contract(s).
- **2026-05-11 (Phase 20.2)**: No new endpoints. Watch Party Create tab standardizes frontend behavior over existing watch-party create contract(s).
- **2026-05-11 (Phase 20.3)**: No new endpoints. Watch Party Detail tab standardizes frontend behavior over existing watch-party detail/RSVP contracts.
- **2026-05-11 (Phase 20.4)**: No new endpoints. Watch Party Past tab standardizes frontend behavior over existing watch-party listing contracts for completed/cancelled sessions.
- **2026-05-11 (Phase 20.5)**: No new endpoints. Watch Party page test expansion standardizes validation coverage for existing upcoming/create/detail/past contracts.
- **2026-05-11 (Phase 21.1)**: No new endpoints. Notifications Inbox All tab standardizes frontend behavior over existing notifications listing contract(s).
- **2026-05-11 (Phase 21.2)**: No new endpoints. Notifications Inbox Unread tab standardizes frontend behavior over existing unread-filter and mark-read workflows.
- **2026-05-11 (Phase 21.3)**: No new endpoints. Notification Preferences Content tab standardizes frontend behavior over existing notification-preferences GET/PATCH contract(s).
- **2026-05-11 (Phase 21.4)**: No new endpoints. Notification Preferences Channels tab standardizes frontend behavior over existing notification-preferences GET/PATCH contract(s) for channel settings.
- **2026-05-11 (Phase 22.1)**: No new endpoints. Profile Overview tab standardizes frontend behavior over existing profile/me and summary surfaces.
- **2026-05-11 (Phase 22.2)**: No new endpoints. Profile Edit tab standardizes frontend behavior over existing profile update contract(s).
- **2026-05-11 (Phase 22.3)**: No new endpoints. Profile Account & Security tab standardizes frontend behavior over existing account-security/password-session contracts.
- **2026-05-11 (Phase 22.4)**: No new endpoints. Profile test expansion standardizes validation coverage for existing overview/edit/security contracts.

## Authentication Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **POST** | `/api/v1/auth/register` | No | `RegisterRequest { username: string, email: string, password: string }` | `UserProfile` | 400 Username/email exists |
| **POST** | `/api/v1/auth/login` | No | `LoginRequest { username: string, password: string }` | `TokenResponse { access_token: string, refresh_token: string, expires_in: int }` | 401 Invalid credentials |
| **POST** | `/api/v1/auth/refresh` | No (refresh token in body) | `RefreshRequest { refresh_token: string }` | `TokenResponse` | 401 Invalid/expired refresh token |
| **POST** | `/api/v1/auth/logout` | Yes (access token) | `RefreshRequest { refresh_token: string }` | `LogoutResponse { success: true }` | 401 Unauthorized |

## User Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **GET** | `/api/v1/users/me` | Yes | – | `UserProfile` | 401 |
| **PATCH** | `/api/v1/users/me` | Yes | `UserUpdate { display_name?, avatar_url?, bio?, timezone? }` | `UserProfile` | 400 / 401 |
| **POST** | `/api/v1/users` | Yes (admin) | `RegisterRequest { username, email, password }` | `UserProfile` | 400 / 401 / 403 |

## Setup Endpoints (Phase 12)
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **GET** | `/api/v1/setup/status` | No | – | `SetupStatusResponse { setup_required: bool }` | – |
| **GET** | `/api/v1/setup/bootstrap` | Optional bearer | – | `AppBootstrapResponse { site_status: "up"|"degraded", logged_in_user?: { id, username, display_name?, is_admin }, setup_required?: true }` | – |
| **POST** | `/api/v1/setup/bootstrap-admin` | No (one-time) | `BootstrapAdminRequest { username, email, password }` | `UserProfile` | 409 Setup already completed |

### Setup/Auth Policy Notes
- `POST /api/v1/auth/register` is allowed only before bootstrap is completed.
- After bootstrap, public register returns `403` and admin-managed user creation uses `POST /api/v1/users`.

## Group Management Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **POST** | `/api/v1/groups` | Yes | `GroupCreate { name, description?, is_private? }` | `GroupDetail` | 400 / 401 |
| **GET** | `/api/v1/groups/{group_id}` | Yes | – | `GroupDetail` | 403 / 404 |
| **POST** | `/api/v1/groups/join/{invite_code}` | Yes | – | `JoinGroupResponse` | 404 |
| **GET** | `/api/v1/groups/{group_id}/members` | Yes | – | `{ items: Member[], total: int }` | 403 / 404 |

## Rate Limiting (Auth & Group)
| Endpoint | Limit | Burst |
|----------|-------|-------|
| POST /api/v1/auth/login | 5 req/s per IP | 10 |
| POST /api/v1/auth/refresh | 5 req/s per IP | 10 |
| POST /api/v1/groups | 2 req/s per user | 5 |
| POST /api/v1/groups/join/{invite_code} | 2 req/s per user | 5 |

## Media Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **GET** | `/api/v1/media/{media_id}` | Yes | – | `MediaDetailResponse` | 404 Not found |
| **GET** | `/api/v1/media/search` | Yes | `MediaSearchRequest { query?: string, type?: string, page?: int }` | `MediaSearchResponse` | 400 Bad request |
| **GET** | `/api/v1/media/popular` | Yes | – | `MediaListResponse` | – |
| **GET** | `/api/v1/media/trending` | Yes | – | `MediaListResponse` | – |
| **GET** | `/api/v1/media/airing` | Yes | `AiringRequest { start_date?: string, end_date?: string, media_type?: string, limit?: int, offset?: int }` | `AiringResponse { items: AiringEpisodeItem[], total: int, limit: int, offset: int }` | 400 Bad request |

## Tracking Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **GET** | `/api/v1/lists/me` | Yes | `ListQuery { status?: string, media_type?: string, limit?: int, offset?: int }` | `UserListResponse { items: ListEntryResponse[], total: int, limit: int, offset: int }` | 401 Unauthorized |
| **GET** | `/api/v1/lists/entries/{media_id}` | Yes | – | `ListEntryResponse` | 404 Not found |
| **POST** | `/api/v1/lists` | Yes | `ListEntryCreate { media_id: UUID, status: string, progress?: int, score?: float, notes?: string }` | `ListEntryResponse` | 400 Validation / 409 Conflict |
| **POST** | `/api/v1/lists/entries` | Yes | `ListEntryCreate { media_id: UUID, status: string, progress?: int, score?: float, notes?: string }` | `ListEntryResponse` | 400 Validation / 409 Conflict (legacy alias) |
| **PATCH** | `/api/v1/lists/{media_id}` | Yes | `ListEntryUpdate { status?: string, progress?: int, score?: float, notes?: string }` | `ListEntryResponse` | 400 Validation / 404 Not found |
| **PATCH** | `/api/v1/lists/entries/{media_id}` | Yes | `ListEntryUpdate { status?: string, progress?: int, score?: float, notes?: string }` | `ListEntryResponse` | 400 Validation / 404 Not found (legacy alias) |
| **DELETE** | `/api/v1/lists/{media_id}` | Yes | – | `{ "message": "Entry deleted successfully" }` | 404 Not found |
| **DELETE** | `/api/v1/lists/entries/{media_id}` | Yes | – | `{ "message": "Entry deleted successfully" }` | 404 Not found (legacy alias) |
| **GET** | `/api/v1/lists/me/history` | Yes | `HistoryQuery { limit?: int }` | `UserListHistoryResponse { items: ListEntryHistoryResponse[], total: int, limit: int }` | 401 Unauthorized |
| **POST** | `/api/v1/lists/custom` | Yes | `CustomListCreate { name: string, description?: string, is_public?: bool, cover_image?: string, sort_order?: int }` | `CustomListResponse` | 400 Validation |
| **PUT** | `/api/v1/lists/custom/{list_id}/entries` | Yes | `CustomListEntriesReplaceRequest { entries: { media_id: UUID, sort_order?: int, note?: string }[] }` | `CustomListEntriesReplaceResponse { list_id: UUID, total_entries: int }` | 404 Not found |
| **GET** | `/api/v1/lists/statistics` | Yes | – | `UserStatistics` | – |

## Sync Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **POST** | `/api/v1/sync/import/anilist` | Yes | `SyncImportRequest { username?: string, overwrite_existing?: bool }` | `SyncImportResponse { job_id: UUID, provider: string, status: string, job_type: string, started_at: datetime, message: string }` | 401 Unauthorized |
| **POST** | `/api/v1/sync/import/mal` | Yes | `SyncImportRequest { username?: string, overwrite_existing?: bool }` | `SyncImportResponse` | 401 Unauthorized |

## Operational Sync Job Endpoints (planned contract)
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **POST** | `/api/v1/admin/sync/seed` | Yes (admin) | `SeedRequest { batch_size?: int }` | `JobEnqueueResponse { job_id: UUID, job_type: "seed", status: "queued" }` | 401 / 403 |
| **POST** | `/api/v1/admin/sync/weekly-refresh` | Yes (admin) | – | `JobEnqueueResponse { job_id: UUID, job_type: "weekly_refresh", status: "queued" }` | 401 / 403 |
| **GET** | `/api/v1/admin/sync/jobs` | Yes (admin) | `SyncJobsQuery { job_type?: string, status?: string, limit?: int, offset?: int }` | `SyncJobsResponse { items: SyncJob[], total: int, limit: int, offset: int }` | 401 / 403 |
| **GET** | `/api/v1/admin/sync/jobs/{job_id}` | Yes (admin) | – | `SyncJobDetail` | 401 / 403 / 404 |

### Sync job response notes
- `SyncJob.status` uses: `running | completed | failed | partial`.
- `error_log` should be structured JSON for retry tooling.
- `processed_items`, `failed_items`, and `total_items` must be present for all long-running fetch jobs.

## Media Schemas

### `AiringEpisodeItem`
```json
{
  "id": "uuid (episode ID)",
  "media_id": "uuid (media entry ID)",
  "media_title": "string — title_romaji from media_entries",
  "media_cover": "string | null — cover_image_medium from media_entries",
  "media_type": "string — anime, manga, manhwa, etc.",
  "episode_number": "int",
  "title": "string | null — episode title",
  "air_date": "datetime | null — ISO 8601",
  "duration_minutes": "int | null"
}
```

### `AiringResponse`
```json
{
  "items": ["AiringEpisodeItem[]"],
  "total": "int",
  "limit": "int (default 20, max 100)",
  "offset": "int (default 0)"
}
```
