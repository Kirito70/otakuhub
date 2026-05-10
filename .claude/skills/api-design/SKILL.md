---
name: api-design
description: Design a complete REST API contract for a new OtakuHub feature. Produces endpoint specs, request/response schemas, and updates docs/api-spec.md.
---

# API Design Skill

## Process

### Step 1 — Read Existing Contracts
Read `docs/api-spec.md` before designing anything. Never create an endpoint
that duplicates or conflicts with an existing one.

### Step 2 — Identify All Needed Endpoints
For each user story, identify the minimum set of endpoints.
Prefer fewer, richer endpoints over many small ones (avoid RPC-style APIs).

### Step 3 — Design Each Endpoint

Use this template for every endpoint:

```markdown
### METHOD /api/v1/path/{param}
**Auth**: Required | Public
**Description**: One sentence — what this endpoint does

**Path Parameters**:
| Name | Type | Description |
|------|------|-------------|
| param | UUID | The thing being accessed |

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | int | 20 | Max results (max: 50) |
| after | UUID | — | Cursor for next page |
| sort | string | "updated_desc" | Allowed: updated_desc, score_desc, title_asc |

**Request Body** (for POST/PUT/PATCH):
```json
{
  "field": "type — description",
  "required_field": "string (required)"
}
```

**Response 200**:
```json
{
  "items": [...],
  "next_cursor": "uuid | null",
  "total": 123
}
```

**Error Responses**:
| Code | When |
|------|------|
| 401 | Not authenticated |
| 403 | Not a group member |
| 404 | Resource not found |
| 409 | Duplicate (e.g. already in list) |
| 422 | Validation error |
```

### Step 4 — Check These Rules
- Base path: always `/api/v1/`
- Pagination: cursor-based (`after` UUID + `limit`), never offset
- No `user_id` in URL for "my own data" endpoints — use `/users/me/`
- Group-scoped: `/groups/{group_id}/` prefix, validate membership in service
- Consistent naming: plural nouns for collections (`/lists/`, `/media/`)
- Bulk operations: POST `/media/batch` with array body if needed

### Step 5 — Update docs/api-spec.md
Append the new endpoints under the correct section.
Keep the file organized by resource prefix.

### Step 6 — Produce Pydantic Schema Stubs
For each request/response schema, output a skeleton Pydantic v2 class
in `backend/schemas/<resource>.py` for the backend-dev agent to flesh out.
