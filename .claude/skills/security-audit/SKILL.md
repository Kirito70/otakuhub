---
name: security-audit
description: Run a full security audit covering auth, SQL injection, IDOR, secrets, prompt injection, Flutter-to-API boundaries, and CORS.
---

# Security Audit Skill

## Audit Sequence

### 1. Secrets Scan (run these commands)
```bash
# Check git history
git log --all -S "SECRET" --oneline
git log --all -S "API_KEY" --oneline
git log --all -S "sk-ant" --oneline
git log --all -S "Bearer " --oneline

# Check current files
grep -rn "api_key\s*=" backend/ --include="*.py" | grep -v ".env" | grep -v "test_"
grep -rn "password\s*=" backend/ --include="*.py" | grep -v "hash" | grep -v "test_"
grep -rn "ANILIST_\|MAL_\|MANGADEX_" mobile/ --include="*.dart"
grep -rn "jwt_secret\|JWT_SECRET" backend/ --include="*.py" | grep -v "settings\."
```
Any hit that isn't reading from an environment variable = CRITICAL finding.

### 2. Auth Coverage Map
List every router file. For each route:
```
GET  /api/v1/media/search     → public ✓  (no auth needed for search)
GET  /api/v1/media/{id}       → auth ✓
POST /api/v1/lists/            → auth ✓
GET  /api/v1/social/feed       → auth ✓
POST /api/v1/auth/login        → public ✓ (it IS the auth endpoint)
```
Flag any non-public route missing `Depends(get_current_user)` as BLOCKER.

### 3. IDOR Check
Search for patterns like `/users/{user_id}/lists` — any endpoint where a user ID is in the URL.
Verify the service layer does: `if requested_user_id != current_user.id: raise HTTPException(403)`.
Exception: group endpoints where membership check replaces user ID check.

### 4. Raw SQL Check
```bash
grep -rn 'f"SELECT\|f"INSERT\|f"UPDATE\|f"DELETE' backend/ --include="*.py"
grep -rn 'text(f"' backend/ --include="*.py"
grep -rn '% user\|% request\|format(user\|format(request' backend/ --include="*.py"
```
Any result = HIGH or CRITICAL depending on whether user input reaches it.

### 5. Flutter External API Calls
```bash
grep -rn "anilist\.co\|graphql\.anilist\|api\.mangadex\|api\.jikan" mobile/ --include="*.dart"
grep -rn "http\.get\|http\.post\|Dio\(\)" mobile/lib/ --include="*.dart" | grep -v "interceptor\|test"
```
Any direct call to AniList/MangaDex/Jikan from Flutter = BLOCKER.
All HTTP in Flutter must go through the Dio client pointing to our FastAPI backend.

### 6. Token Security
Check `backend/core/auth.py`:
- Access token expiry ≤ 15 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- Refresh token expiry ≤ 30 days
- JWT algorithm is `HS256` or `RS256` — not `none`
Check `mobile/lib/core/storage/`:
- Tokens stored in `flutter_secure_storage` — not `SharedPreferences` or plain file

### 7. CORS
Check `backend/main.py` CORSMiddleware:
```python
# FAIL — never in production
allow_origins=["*"]
# PASS
allow_origins=settings.ALLOWED_ORIGINS  # e.g. ["https://otakuhub.local"]
```

### 8. Prompt Injection (if AI features present)
If any endpoint passes anime metadata into an LLM prompt:
- Anime titles/descriptions arrive from AniList — treat as untrusted data
- Check that they are included as data, not instructions: wrap in delimiters
- `f"Here is the anime: <data>{anime.title}</data>\nNow recommend similar titles."`
- Never interpolate user-provided text into system prompts

## Report Template
```
## Security Audit — OtakuHub
Date: {date}
Scope: {files or 'full codebase'}

### Critical (fix before any deployment)
[findings]

### High (fix before next release)
[findings]

### Medium (fix in next sprint)
[findings]

### Low / Info
[findings]

### Summary
Critical: N | High: N | Medium: N | Low: N
Overall: PASS ✅ | CONDITIONAL PASS ⚠️ | FAIL 🚫
```
