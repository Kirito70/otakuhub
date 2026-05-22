## Security Audit Follow-up — OtakuHub
Date: 2026-05-23
Scope: backend/src/app, backend/tests, frontend/src (boundary spot-check)
Baseline: `docs/security-audit-2026-05-21.md`

### Executive Summary
- Previously reported **critical findings (2/2) are remediated**.
- Key auth hardening has been implemented and covered by regression tests.
- One previously noted **high-risk quality/security-adjacent gap** remains in placeholder social-service watch-party query logic.

### Status Delta Since 2026-05-21

#### ✅ Resolved Critical Findings
1. **Weak password hashing in production code path** — RESOLVED
   - Was: unsalted deterministic SHA-256.
   - Now: bcrypt via `passlib` with legacy SHA-256 compatibility during migration.
   - Files:
     - `backend/src/app/core/security.py`
     - `backend/src/app/services/auth_service.py`
     - `backend/tests/test_security_password_hashing.py`
   - Security behavior:
     - New/updated passwords hashed with bcrypt.
     - Legacy SHA-256 hashes accepted only for verification and upgraded on successful login (`needs_password_rehash` + login-time rehash).

2. **Insecure runtime defaults for secrets/CORS** — RESOLVED
   - Was: `jwt_secret="test-secret"`, `cors_origins="*"` fallback.
   - Now: strict settings validation rejects insecure JWT secret and wildcard CORS.
   - Files:
     - `backend/src/app/config.py`
     - `backend/tests/test_config_security_defaults.py`
     - `backend/.env.example`

#### ✅ Additional Hardening Delivered
1. **Refresh token replay/reuse handling strengthened**
   - If a revoked refresh token is replayed, service now revokes all active refresh tokens for that user and denies request.
   - File:
     - `backend/src/app/services/auth_service.py`
   - Test coverage:
     - `backend/tests/test_auth_service_unit.py`
     - `backend/tests/test_security_regressions_auth_config.py`

2. **Security regression suite expanded**
   - Consolidated targeted regressions for auth/config boundaries and replay edge cases.
   - Files:
     - `backend/tests/test_security_regressions_auth_config.py`
     - plus auth/config/hash suites

### Remaining Findings

#### High
1. **Placeholder social-service watch-party query remains in codebase**
   - File: `backend/src/app/services/social_service.py`
   - Method: `get_user_watch_parties()` currently uses placeholder select string columns and returns empty list.
   - Risk: not an immediate exploit path by itself, but fragile placeholder DB logic in service layer can cause undefined behavior if wired into active API surfaces without strict validation and authorization checks.
   - Recommendation:
     - Replace with fully typed SQLModel/SQLAlchemy query and explicit group membership auth boundary checks.
     - Add service + router tests before exposing/using this path.

### Verification Evidence (executed)
- `uv run pytest tests/test_security_password_hashing.py tests/test_config_security_defaults.py tests/test_auth_service_unit.py tests/test_security_regressions_auth_config.py -q`
- Result: **22 passed**

### Risk Posture
- Critical: **0**
- High: **1**
- Medium: **0** (from prior critical list)
- Low/Info: several non-blocking engineering hygiene items remain (e.g., deprecation warnings in test output).

### Overall Verdict
**CONDITIONAL PASS ⚠️**
- Safe to proceed with next hardening/documentation sub-phases.
- Recommended to close remaining high finding before broad release exposure.
