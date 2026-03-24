# Security Audit Report — todo-list

**Date:** 2026-03-24
**Scope:** Backend (FastAPI + SQLAlchemy) · Frontend (React + TypeScript)
**Auditor:** bmad-quick-dev (claude-sonnet-4-6)
**Methodology:** Static source code review
**Revision:** v2 — post adversarial review

> **Authentication / authorization** is intentionally absent from this application (single-user personal app, localhost-only). This is explicitly out of scope for this audit. Readers evaluating production readiness should treat the absence of auth as the primary concern before any finding in this report.

---

## Summary Table — Actionable Findings

| ID | Severity | Title | File |
|----|----------|-------|------|
| SEC-001 | **High** | CORS: `allow_credentials` + wildcard headers | `backend/main.py` |
| SEC-002 | **Medium** | Plaintext credentials in `.env` file | `backend/.env` |
| SEC-003 | Low | CORS: `allow_methods=["*"]` includes non-standard methods | `backend/main.py` |
| SEC-004 | Low | Missing HTTP security response headers | `backend/main.py` |
| SEC-005 | Low | 422 responses echo submitted input values | `backend/main.py` |
| SEC-006 | Low | `VITE_API_URL` undefined — total app failure, not silent | `frontend/src/api/todos.ts` |
| SEC-007 | Low | Frontend error messages expose HTTP status codes to DOM | `frontend/src/App.tsx`, `frontend/src/api/todos.ts` |

**Severity breakdown:** High: 1 · Medium: 1 · Low: 5

See [Reviewed Clean](#reviewed-clean) section for areas audited and found to have no issues.

---

## Finding SEC-001 — CORS: `allow_credentials=True` with Wildcard Headers

**Severity:** High
**File(s):** `backend/main.py` (lines 27–36)
**Description:** The CORS middleware is configured with `allow_credentials=True` and `allow_headers=["*"]` simultaneously. This means the server accepts credentialed cross-origin requests (carrying cookies or `Authorization` headers) with any request header from any allowed origin. While `allow_origins` is currently restricted to two localhost addresses — making this safe today — this is a deployment trap. The moment `allow_origins` is expanded to include a production domain (the standard next step for any project going to production), this configuration enables CSRF and session-hijacking from a malicious page on any other origin. The remediation is a one-line change and eliminates the risk entirely.
**Evidence:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,   # ← cookies/auth headers allowed cross-origin
    allow_methods=["*"],
    allow_headers=["*"],      # ← any header accepted on credentialed requests
)
```
**Remediation:** Replace `allow_headers=["*"]` with an explicit allowlist. The frontend only ever sends `Content-Type: application/json`:
```python
allow_headers=["Content-Type"],
```

---

## Finding SEC-002 — Plaintext Credentials in `.env` File

**Severity:** Medium
**File(s):** `backend/.env`
**Description:** The file `backend/.env` exists in the working tree and contains a plaintext database password. The `.gitignore` was added in the second commit ("chore: update gitignore"), which means this file may have been present before the ignore rule was applied. If it was ever committed to git history, the credential is permanently exposed in version control even if the file is subsequently deleted — git history preserves it. Even setting git history aside, storing credentials in a plain text file that lives in the project root is risky: it can be accidentally committed, backed up to cloud storage, or exposed in editor sync tools.
**Evidence:**
```
# backend/.env
DATABASE_URL=postgresql://postgres:password@localhost:5432/todoapp
```
**Remediation:**
1. Verify the file is not tracked: `git ls-files backend/.env` — if it returns output, the file is tracked and the credential must be rotated and purged from history using `git filter-repo` or BFG Repo Cleaner.
2. Ensure `backend/.env` is listed in `.gitignore` and not staged: `git check-ignore -v backend/.env`.
3. For production deployments, inject `DATABASE_URL` as an environment variable via the deployment platform (Docker, Heroku, Railway, etc.) rather than a `.env` file.
4. Even for local development, document that developers must create their own `.env` from a `.env.example` template (which contains no real credentials).

---

## Finding SEC-003 — CORS: `allow_methods=["*"]` Includes Non-Standard Methods

**Severity:** Low
**File(s):** `backend/main.py` (line 34)
**Description:** `allow_methods=["*"]` in the CORS middleware includes all HTTP methods in the `Access-Control-Allow-Methods` preflight response header. This means browsers will permit cross-origin requests using any HTTP method, including `TRACE`, `CONNECT`, and `HEAD`, to the allowed origins. While the Classic Cross-Site Tracing (XST) attack (which required browsers to send `TRACE` cross-origin via `XMLHttpRequest`) is blocked by all modern browsers regardless of CORS headers, explicitly advertising non-standard methods in preflight responses increases the attack surface unnecessarily and may confuse security scanners.

Note: `allow_methods` controls CORS preflight headers only — it does not open up those methods at the ASGI/Uvicorn level. The actual server-side method handling is determined by the registered FastAPI routes (GET, POST, PATCH, DELETE only).
**Evidence:**
```python
allow_methods=["*"],
```
**Remediation:** Replace with the explicit set of methods the API actually uses:
```python
allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
```

---

## Finding SEC-004 — Missing HTTP Security Response Headers

**Severity:** Low
**File(s):** `backend/main.py`
**Description:** FastAPI does not add security-oriented HTTP response headers by default. The following headers are absent from all API responses. Note that these headers primarily protect HTML page contexts — their impact on a pure JSON API is limited. They become material if the API is proxied, if responses are ever rendered as HTML, or if the frontend is served from the same origin as the API.

| Header | Recommended Value | Purpose |
|--------|------------------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Prevents iframe embedding of API responses |
| `Referrer-Policy` | `no-referrer` | Prevents API URL leaking in `Referer` header |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | Disables browser feature APIs |
| `Content-Security-Policy` | `default-src 'none'` | For JSON API responses only — has no effect on the React frontend which is served separately |

**Evidence:** No `SecurityHeadersMiddleware` or equivalent registered in `main.py`.

**Remediation:** Add a Starlette middleware in `backend/main.py`. Register it **before** the CORS middleware:
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # NOTE: This CSP applies to API JSON responses only.
        # Do NOT apply default-src 'none' to the frontend static file server —
        # it would block all scripts, styles, and assets, breaking the React app.
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Finding SEC-005 — 422 Responses Echo Submitted Input Values

**Severity:** Low
**File(s):** `backend/main.py` (fix location), triggered by `backend/schemas.py` validation
**Description:** FastAPI's default 422 Unprocessable Entity handler includes the submitted input value verbatim in the response body. For example, submitting a 201-character string returns:
```json
{
  "detail": [{
    "type": "string_too_long",
    "loc": ["body", "text"],
    "msg": "String should have at most 200 characters",
    "input": "<the full 201-character string>",
    "ctx": {"max_length": 200}
  }]
}
```
The `"input"` field echoes the submitted value and exposes internal schema structure (`loc`, `type`, `ctx`). This is low severity — the client already knows what they submitted — but the schema exposure reduces friction for an attacker probing the API.
**Evidence:** FastAPI default — no custom `RequestValidationError` handler registered in `main.py`.
**Remediation:** Add a custom exception handler in **`backend/main.py`** (not in `routers/todos.py` — routers cannot own global exception handlers):
```python
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data."},
    )
```

---

## Finding SEC-006 — `VITE_API_URL` Undefined: Total Application Failure

**Severity:** Low
**File(s):** `frontend/src/api/todos.ts` (line 4)
**Description:** `VITE_API_URL` is read from `import.meta.env` with no guard for the undefined case. This is primarily a **reliability and misconfiguration** risk rather than a security vulnerability: if the environment variable is not set at Vite build time, every API call targets `"undefined/api/v1/todos"` — a network request that will always fail — causing total loss of application functionality. In a CI/CD or production deployment, this means a misconfigured build silently ships a broken application with no build-time error.
**Evidence:**
```typescript
// frontend/src/api/todos.ts
const API_URL = import.meta.env.VITE_API_URL
// No guard — if undefined, all fetch calls go to "undefined/api/v1/todos"
```
**Remediation:** Add an explicit fail-fast guard that throws at module load time:
```typescript
const API_URL = import.meta.env.VITE_API_URL
if (!API_URL) {
  throw new Error('VITE_API_URL is not set. Add VITE_API_URL=http://localhost:8000 to frontend/.env')
}
```
Also create a `frontend/.env.example` file documenting required variables.

---

## Finding SEC-007 — Frontend Error Messages Expose HTTP Status Codes to DOM

**Severity:** Low
**File(s):** `frontend/src/App.tsx` (line 15), `frontend/src/api/todos.ts`
**Description:** When an API call fails, `todos.ts` constructs error messages that include the raw HTTP status code (e.g., `"Failed to fetch todos: 422"`). `App.tsx` passes `error.message` directly to `ErrorMessage`, which renders it in a visible DOM element (`<p className={styles.detail}>{message}</p>`). This means HTTP status codes — and any other text in the error message — are surfaced to the end user in the UI and visible in page source. An attacker probing the API can confirm backend error codes by inspecting the rendered page, which reveals backend behaviour without needing to call the API directly.
**Evidence:**
```typescript
// frontend/src/api/todos.ts
throw new Error(`Failed to fetch todos: ${response.status}`)  // exposes status code
```
```tsx
// frontend/src/App.tsx
<ErrorMessage message={error instanceof Error ? error.message : undefined} />
```
```tsx
// frontend/src/components/ErrorMessage/ErrorMessage.tsx
{message && <p className={styles.detail}>{message}</p>}  // rendered to DOM
```
**Remediation:** Strip technical details from user-facing error messages. In `todos.ts`, throw user-friendly errors without status codes:
```typescript
throw new Error('Unable to load todos. Please try again.')
```
Or keep the status code for logging but pass a generic message to the UI:
```tsx
// App.tsx — log technical detail, show generic message
{isError && <ErrorMessage message="Something went wrong. Please refresh." />}
```

---

## Reviewed Clean

The following areas were audited and found to have no actionable issues:

| Area | Verdict | Key Evidence |
|------|---------|-------------|
| **SQL / ORM Injection** | No issues | All DB access via SQLAlchemy ORM (`db.query().filter()`). Zero raw SQL or `.execute()` with string formatting found across all backend files. |
| **XSS** | No issues | All `todo.text` rendered via React JSX children and attributes — auto-escaped by framework. No `dangerouslySetInnerHTML` anywhere. React serialises all prop values safely, including `aria-label` template literals. |
| **FastAPI Debug Mode** | No issues | `FastAPI(...)` instantiated without `debug=True`. Stack traces are not included in error responses. |
| **Input Validation** | No issues | `TodoCreate.text` enforced at Pydantic layer (`min_length=1, max_length=200`) and DB layer (`String(200)`). `TodoUpdate` accepts only `bool`. Client-side validation mirrors server rules. |
| **Session & Transaction Safety** | No issues | `get_db()` uses `try/finally` + `db.close()`. `autocommit=False, autoflush=False`. All commits explicit. No session leak risk. |

---

## Appendix: Recommended Remediation Priority

| Priority | Finding | Effort | Impact |
|----------|---------|--------|--------|
| 1 | SEC-002 — Check `.env` git tracking + credential audit | 5 min | Prevent credential exposure in git history |
| 2 | SEC-001 — CORS wildcard headers → `["Content-Type"]` | 1 line | Eliminates production CSRF/session-hijacking trap |
| 3 | SEC-003 — CORS explicit methods allowlist | 1 line | Removes non-standard method advertising |
| 4 | SEC-004 — Security headers middleware | ~12 lines | Baseline HTTP hardening |
| 5 | SEC-005 — Sanitised 422 responses | ~8 lines | Reduces schema exposure |
| 6 | SEC-006 — `VITE_API_URL` fail-fast guard | 3 lines | Catches misconfigured deployments at startup |
| 7 | SEC-007 — Generic frontend error messages | 2 lines | Removes status code exposure from DOM |

## Appendix: Out-of-Scope Notes

- **Rate limiting / pagination:** `GET /api/v1/todos` returns all rows unbounded. For a production deployment with real user data, consider adding pagination and rate limiting (e.g., `slowapi`).
- **Authentication / authorization:** All endpoints are fully open. Treat this as the primary concern for any production deployment — it supersedes all findings in this report.
- **Third-party dependencies:** Not audited. Run `pip audit` (backend) and `npm audit` (frontend) for dependency vulnerability scanning.
