---
name: code-review
description: Full code review of a diff or PR. Returns severity-tagged findings and a final verdict.
---

# Code Review Skill

## Review Process

### Pass 1 — Architecture
- Backend: router → service → repository layer respected?
- Frontend: store logic in Pinia (not in components), composables for reusable async?
- No business logic leaking into components?

### Pass 2 — TypeScript / Vue 3 (Frontend)
- `<script setup lang="ts">` on every component?
- No `any` types — every value has a proper interface?
- Props typed with `defineProps<{...}>()`?
- Every async action has `isLoading`, `error`, `data` pattern?
- Loading state shown while fetching?
- Error state shown with retry option?
- No raw `fetch()` calls — Axios boot file used?
- No AniList/MangaDex calls from frontend?
- Long lists use `QVirtualScroll`?
- Routing uses named routes (not raw paths)?

### Pass 3 — Python / FastAPI (Backend)
- Type hints on every function signature?
- Pydantic v2 response models — no raw dict returns?
- Repository pattern — no DB queries in routers or services?
- Async SQLAlchemy — no sync calls in async context?
- N+1 check — `selectinload`/`joinedload` used for relationships?
- `async with session.begin()` wrapping all writes?
- Auth dependency on all protected routes?
- Correct HTTP status codes?

### Pass 4 — Security
- No secrets in code?
- No raw SQL string building?
- Auth checked before user-specific data returned?
- IDOR risk on ID-based endpoints?
- No external API calls from frontend?

### Pass 5 — Tests
- New endpoint: happy path, auth failure, not-found?
- New page: loading state, error state, data state?
- Vitest tests run: `npx vitest run`?
- Pytest tests run: `pytest tests/ -v`?

## Output Format
```
## Code Review — <feature>
**Summary**: 2-sentence overview

### Findings

**[BLOCKER]** `src/stores/tracking.ts:45`
Issue: Calling AniList API directly from Pinia store
Fix: Move the call to the FastAPI backend and call /api/v1/... instead

**[MAJOR]** `src/pages/DiscoverPage.vue:23`
Issue: No error state — if API call fails, page shows nothing
Fix: Add v-else-if="store.error" block with QBanner

**[MINOR]** `backend/routers/lists.py:67`
Issue: Missing selectinload on UserListEntry.media relationship
Fix: Add .options(selectinload(UserListEntry.media)) to the query

**[NIT]** `src/stores/media.ts:12`
Issue: Variable name `d` is not descriptive
Fix: Rename to `mediaDetail`

### Verdict
✅ Approved | 🔄 Changes Requested | 🚫 Blocked
```
