# OtakuHub API Specification (OpenAPI‑style summary)

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
| **GET** | `/api/v1/media/airing` | Yes | `AiringRequest { page?: int, per_page?: int }` | `AiringResponse` | 400 Bad request |

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
