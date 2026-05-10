# Security Audit

Perform a full security audit of the specified files or the entire codebase.

## Audit Steps (run all of these)

### 1. Secrets Scan
```bash
# Check git history for accidentally committed secrets
git log --all -S "API_KEY" --oneline
git log --all -S "SECRET" --oneline
git log --all -S "sk-ant" --oneline
git log --all -S "Bearer " --oneline
# Grep current files
grep -r "api_key\s*=" backend/ --include="*.py" | grep -v ".env" | grep -v "test"
grep -r "ANILIST_\|MAL_\|JWT_" mobile/ --include="*.dart"
```

### 2. Auth Coverage Check
List every FastAPI router. For each route, confirm:
- Public routes (login, register, health): no auth dependency ✓
- All other routes: `Depends(get_current_user)` present ✓
- Group-scoped routes: membership check in service layer ✓

### 3. IDOR Scan
Find all endpoints with `{user_id}` or `{list_id}` in the path.
Confirm the service layer checks `current_user.id == requested_user_id` or group membership.

### 4. SQL Injection Check
Search for raw SQL:
```bash
grep -rn "f\"SELECT\|f\"INSERT\|f\"UPDATE\|f\"DELETE" backend/ --include="*.py"
grep -rn "text(f\"" backend/ --include="*.py"
```
Any result is a finding.

### 5. Prompt Injection Risk (AI features)
If any AI recommendation or search feature exists:
- Find where anime titles/descriptions are inserted into prompts
- Verify they are escaped or sandboxed
- Flag any user-supplied text going into system prompts

### 6. CORS Configuration
Check `backend/main.py` for:
```python
# BAD
allow_origins=["*"]
# GOOD
allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"]
```

### 7. Token Security
- Access token expiry ≤ 15 minutes
- Refresh token expiry ≤ 30 days
- Flutter: tokens stored in `flutter_secure_storage` not SharedPreferences
- Refresh token rotation on use

### 8. Flutter — External Calls
Search for any direct AniList/MangaDex calls from Flutter:
```bash
grep -rn "anilist.co\|mangadex.org\|jikan.moe" mobile/ --include="*.dart"
```
Any result is a BLOCKER — all external API calls must go through FastAPI.

## Report Format
```
## Security Audit Report — OtakuHub
Date: [today]
Audited: [files/scope]

### Findings
[numbered list using CRITICAL/HIGH/MEDIUM/LOW/INFO severity]

### Summary
- Critical: N
- High: N
- Medium: N
- Low: N
- Status: PASS | CONDITIONAL PASS | FAIL
```
