# Full PR Code Review

Run a comprehensive review of the current diff or specified files.
Use `git diff main` or read the files listed by the user.

## Review Structure

### Summary
One paragraph: what does this change do, is the approach sound?

### Issues Found
For each issue use this format:
```
**[SEVERITY]** `path/to/file:line`
**Issue**: What is wrong and why it matters
**Fix**: The exact change needed
```
Severity: BLOCKER | MAJOR | MINOR | NIT

### Checklist Results

#### Python / FastAPI
- [ ] Type hints complete on all functions
- [ ] Pydantic v2 response models (no raw dict returns)
- [ ] Repository pattern: DB queries only in repositories/
- [ ] Async SQLAlchemy: no sync calls in async context
- [ ] N+1 check: relationships loaded with selectinload/joinedload
- [ ] Write operations wrapped in `async with session.begin()`
- [ ] Auth dependency on all protected routes
- [ ] Correct HTTP status codes
- [ ] No internal errors exposed to users
- [ ] Celery tasks idempotent

#### Dart / Flutter
- [ ] No setState in screens (Riverpod only)
- [ ] AsyncValue.when() handles data/loading/error
- [ ] No hardcoded colors (Theme.of(context) used)
- [ ] ListView.builder for lists (not Column + map)
- [ ] CachedNetworkImage for remote images
- [ ] const constructors used
- [ ] GoRouter named navigation (no Navigator.push)
- [ ] Responsive layout considered

#### Database / Migrations
- [ ] downgrade() implemented in migration
- [ ] UUID v7 PK on new tables
- [ ] TIMESTAMPTZ for timestamps
- [ ] Soft delete (deleted_at) not hard DELETE
- [ ] Indexes on FK and filter columns

#### Security
- [ ] No secrets in code
- [ ] No raw SQL string building
- [ ] Auth checked before user-specific data
- [ ] IDOR risk assessed for ID-based endpoints

#### Tests
- [ ] Happy path test
- [ ] Auth failure test
- [ ] Not-found/validation test
- [ ] Flutter: loading state tested

### Verdict
**✅ Approved** | **🔄 Changes Requested** | **🚫 Blocked**

If changes requested, list them in priority order.
