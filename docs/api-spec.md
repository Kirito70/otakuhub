# OtakuHub API Specification (OpenAPI‑style summary)

## Authentication Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **POST** | `/api/v1/auth/login` | No | `LoginRequest { username: string, password: string }` | `TokenResponse { access_token: string, refresh_token: string, expires_in: int }` | 401 Invalid credentials |
| **POST** | `/api/v1/auth/refresh` | No (refresh token in body) | `RefreshRequest { refresh_token: string }` | `TokenResponse` | 401 Invalid/expired refresh token |
| **POST** | `/api/v1/auth/logout` | Yes (access token) | `{}` (optional `device_name`) | `{ "success": true }` | 401 Unauthorized |

## Group Management Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **GET** | `/api/v1/groups` | Yes | – | `PaginatedResponse<GroupSummary>` | 403 Forbidden (if user not member) |
| **POST** | `/api/v1/groups` | Yes | `CreateGroup { name: string, description?: string, is_private?: bool }` | `GroupDetail` | 400 Validation |
| **GET** | `/api/v1/groups/{group_id}` | Yes | – | `GroupDetail` | 404 Not found / 403 Forbidden |
| **PATCH** | `/api/v1/groups/{group_id}` | Yes (owner/admin) | `UpdateGroup { name?: string, description?: string, is_private?: bool }` | `GroupDetail` | 403 Forbidden |
| **DELETE** | `/api/v1/groups/{group_id}` | Yes (owner) | – | `{ "success": true }` | 403 Forbidden |
| **POST** | `/api/v1/groups/{group_id}/members` | Yes (owner/admin) | `AddMember { user_id: UUID, role?: string }` | `{ "success": true }` | 404 / 403 |
| **DELETE** | `/api/v1/groups/{group_id}/members/{user_id}` | Yes (owner/admin) | – | `{ "success": true }` | 404 / 403 |
| **GET** | `/api/v1/users/me` | Yes | – | `UserProfile` | 401 |
| **PATCH** | `/api/v1/users/me` | Yes | `UserUpdate { display_name?: string, avatar_url?: string, bio?: string, timezone?: string }` | `UserProfile` | 400 |

## Rate Limiting (Auth & Group)
| Endpoint | Limit | Burst |
|----------|-------|-------|
| POST /api/v1/auth/login | 5 req/s per IP | 10 |
| POST /api/v1/auth/refresh | 5 req/s per IP | 10 |
| POST /api/v1/groups | 2 req/s per user | 5 |
| PATCH /api/v1/groups/{group_id} | 2 req/s per user | 5 |
| DELETE /api/v1/groups/{group_id} | 2 req/s per user | 5 |
| POST /api/v1/groups/{group_id}/members | 2 req/s per user | 5 |

*All request/response bodies are defined as Pydantic models in `backend/schemas/auth.py` and `backend/schemas/group.py`.*

## Media Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **GET** | `/api/v1/media/{media_id}` | No | – | `MediaDetailResponse` | 404 Not found |
| **GET** | `/api/v1/media/search` | No | `MediaSearchRequest { query?: string, type?: string, page?: int }` | `MediaSearchResponse` | 400 Bad request |
| **GET** | `/api/v1/media/popular` | No | – | `MediaListResponse` | – |
| **GET** | `/api/v1/media/trending` | No | – | `MediaListResponse` | – |
| **GET** | `/api/v1/media/airing` | No | `AiringRequest { page?: int, per_page?: int }` | `AiringResponse` | 400 Bad request |

## Tracking Endpoints
| Method | Path | Auth | Request Schema | Response Schema | Errors |
|--------|------|------|----------------|----------------|--------|
| **GET** | `/api/v1/lists/entries/{entry_id}` | Yes | – | `ListEntryResponse` | 404 Not found / 403 Forbidden |
| **GET** | `/api/v1/lists/entries` | Yes | `ListRequest { status?: string, page?: int }` | `ListResponse` | 400 Bad request |
| **POST** | `/api/v1/lists/entries` | Yes | `ListEntryCreate { media_id: UUID, status: string, progress?: int, score?: float }` | `ListEntryResponse` | 400 Validation / 409 Conflict |
| **PATCH** | `/api/v1/lists/entries/{entry_id}` | Yes | `ListEntryUpdate { status?: string, progress?: int, score?: float, notes?: string }` | `ListEntryResponse` | 400 Validation / 404 Not found |
| **DELETE** | `/api/v1/lists/entries/{entry_id}` | Yes | – | `{ "success": true }` | 404 Not found / 403 Forbidden |
| **GET** | `/api/v1/lists/statistics` | Yes | – | `UserStatistics` | – |

*All request/response bodies are defined as Pydantic models in `backend/schemas/tracking.py`.*