---
description: Run a full review of a completed feature — code quality, tests, security, and DB migration check.
---

When the user types `/reviewfeature <feature-name>`, run all review checks.

## Review Sequence

### Step 1 — Code Review
Act as **Code Reviewer** from `.agents/agents.md`.
Read all files in `mobile/lib/features/<feature>/` and `backend/routers/`, `backend/services/`, `backend/repositories/` for this feature.
Apply the checklist from `.claude/skills/code-review/SKILL.md`.
Output findings.

### Step 2 — Security Check
Apply the security checklist from `.claude/skills/security-audit/SKILL.md`.
Focus on: auth coverage, IDOR risk, Flutter-to-API boundaries, secrets.

### Step 3 — Database Migration Check
If any schema changes exist:
- Confirm `downgrade()` is implemented
- Confirm indexes match `docs/database-schema.md`
- Confirm `docs/database-schema.md` is updated

### Step 4 — Test Coverage Check
List all new routes/widgets/providers.
Verify each has a corresponding test file.
Flag any untested public methods as MINOR findings.

### Step 5 — Summary Verdict
```
## Review Summary — <feature>
Code: ✅ / 🔄 / 🚫
Security: ✅ / ⚠️ / 🚫
Migration: ✅ / N/A
Tests: ✅ / ⚠️

Total findings: N BLOCKER, N MAJOR, N MINOR, N NIT
Overall: ✅ Ready to commit | 🔄 Changes required | 🚫 Blocked
```
