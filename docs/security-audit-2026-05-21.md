## Security Audit — OtakuHub
Date: 2026-05-21
Scope: backend/src/app, frontend/src, git history indicators

### Critical (fix before any deployment)
1. **Weak password hashing in production code path**
   - File: `backend/src/app/core/security.py`
   - Current behavior: passwords are hashed with plain SHA-256 (`hashlib.sha256`) without salt/work factor.
   - Risk: offline cracking is significantly easier; does not meet project policy (bcrypt expected).
   - Recommendation: migrate to `passlib[bcrypt]` (or argon2), add phased hash migration on login.

2. **Insecure security defaults in runtime config**
   - File: `backend/src/app/config.py`
   - Findings:
     - `cors_origins: str = "*"`
     - `jwt_secret: str = "test-secret"`
   - Risk: if env configuration is missing/misconfigured in deployment, app can start with insecure CORS and weak JWT secret.
   - Recommendation: remove insecure defaults for production-sensitive settings; fail fast when env vars missing outside test/dev.

### High (fix before next release)
1. **CORS currently sourced from env but default wildcard remains permissive**
   - File: `backend/src/app/main.py` + `config.py`
   - `allow_origins=settings.cors_origins_list` is correct wiring, but fallback `*` in settings undermines safety.
   - Recommendation: set strict default to localhost dev origins only, or enforce explicit env value by environment.

2. **Known broken/placeholder service logic reachable in codebase**
   - File: `backend/src/app/services/social_service.py`
   - `get_user_watch_parties()` builds invalid textual select and currently returns placeholder semantics.
   - Risk: if wired later without hardening, can cause runtime errors and weakly-defined data access semantics.
   - Recommendation: replace placeholder with explicit typed query or remove method until implemented.

### Medium (fix in next sprint)
1. **JWT/refresh token policy is acceptable but key management needs hardening policy docs**
   - Files: `core/security.py`, `config.py`
   - Access token (15 min) and refresh (30 days) are aligned with target, but no explicit enforcement that prod uses high-entropy secret.

2. **Frontend test warnings on unresolved Quasar directives**
   - Impact: low direct security impact, but can hide UX edge cases in auth-sensitive interactions.
   - Recommendation: register directive stubs in Vitest global setup.

### Low / Info
1. **Auth coverage map review**
   - Protected domains (`lists`, `social`, `watchparty`, `notifications`, `groups`, `sync`, `users/me`) consistently use `Depends(get_current_user)`.
   - Public endpoints are limited to expected auth/setup/root/health surfaces.

2. **Raw SQL check**
   - No direct f-string SQL construction indicators found in backend source scan.

3. **Frontend external API boundary check**
   - No direct AniList/MangaDex/Jikan calls found in `frontend/src`.
   - Frontend HTTP flows through Axios boot client (`frontend/src/boot/axios.ts`) toward backend.

### Summary
Critical: 2 | High: 2 | Medium: 2 | Low: 3
Overall: **FAIL 🚫** (must resolve critical issues before deployment)

---

## Priority Remediation Order
1. Replace SHA-256 password hashing with bcrypt/argon2 and add migration path.
2. Remove insecure `jwt_secret` and `cors_origins` defaults; enforce env-required values in non-test env.
3. Tighten CORS environment policy by environment (dev vs prod explicit allowlist).
4. Fix/remove placeholder `SocialService.get_user_watch_parties` implementation.
