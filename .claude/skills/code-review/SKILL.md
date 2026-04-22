---
name: code-review
description: Perform a structured code review of a diff, file, or PR. Returns severity-tagged findings and a final verdict.
---

# Code Review Skill

## Inputs Needed
- The diff (`git diff main`) or specific files to review
- Context: what feature does this implement?

## Review Process

### Pass 1 — Architecture (read all changed files first)
- Does this change respect the layered architecture (router → service → repository)?
- Are responsibilities in the right layer?
- Are there new dependencies that weren't designed?

### Pass 2 — Correctness (line by line)
- Logic errors, off-by-one, wrong conditions
- Async/await correctness — missing awaits on coroutines
- SQLAlchemy: sync calls in async context? Missing selectinload causing N+1?

### Pass 3 — Types & Contracts
- Python: type hints complete? Pydantic models used for all responses?
- Dart: no dynamic types? AsyncValue.when() complete?

### Pass 4 — Security
- Auth on all protected routes?
- IDOR risk on any ID-based endpoint?
- User input going into raw SQL?
- Secrets in code?
- Flutter calling external APIs directly?

### Pass 5 — Tests
- Tests present for new endpoints?
- Coverage of error cases?

## Output Format
```
## Code Review — <feature name>
**Files reviewed**: list of files
**Summary**: 2-sentence summary of what changed and overall quality

### Findings

**[BLOCKER]** `backend/routers/media.py:45`
Issue: No auth dependency on GET /media/{id}
Fix: Add `current_user: Annotated[User, Depends(get_current_user)]` parameter

**[MAJOR]** `backend/repositories/media_repository.py:23`
Issue: N+1 query — genres loaded lazily in a loop
Fix: Add `.options(selectinload(MediaEntry.genres))` to the base query

**[MINOR]** `mobile/lib/features/media/presentation/screens/detail_screen.dart:67`
Issue: Missing error state handler
Fix: Add `error: (e, _) => ErrorView(message: e.toString())` to .when()

**[NIT]** `backend/services/media_service.py:12`
Issue: Variable name `d` is not descriptive
Fix: Rename to `media_detail`

### Verdict
🔄 Changes Requested — 1 BLOCKER, 1 MAJOR must be fixed before merge
```
