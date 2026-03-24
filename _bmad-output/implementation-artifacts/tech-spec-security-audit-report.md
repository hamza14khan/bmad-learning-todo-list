---
title: 'Security Audit Report'
slug: 'security-audit-report'
created: '2026-03-24'
status: 'Completed'
stepsCompleted: [1, 2, 3, 4]
tech_stack: ['FastAPI', 'SQLAlchemy 2.x', 'Pydantic v2', 'React 18', 'TypeScript', 'Vite', 'TanStack Query', 'python-dotenv']
files_to_modify: []
files_to_create: ['_bmad-output/security-audit-report.md']
code_patterns: ['ORM-only (no raw SQL)', 'Pydantic request validation', 'JSX auto-escaping', 'env-var config via dotenv / import.meta.env']
test_patterns: []
---

# Tech-Spec: Security Audit Report

**Created:** 2026-03-24

## Overview

### Problem Statement

The todo-list application (FastAPI backend + React frontend) has not had a formal security review. Common web vulnerabilities (XSS, injection, insecure headers, CORS misconfiguration, information disclosure, etc.) may be present and are currently undocumented.

### Solution

Perform a systematic read-only review of all application source code for common security issues. Produce a structured markdown report at `_bmad-output/security-audit-report.md` documenting each finding with a unique ID, severity, affected file, description, evidence snippet, and remediation. Defended patterns are documented as Informational findings. No code changes are applied.

### Scope

**In Scope:**
- Backend: `backend/main.py`, `backend/database.py`, `backend/routers/todos.py`, `backend/schemas.py`, `backend/models.py`
- Frontend: `frontend/src/api/todos.ts`, `frontend/src/hooks/useTodos.ts`, all `*.tsx` components
- Configuration: CORS settings, environment variable handling, HTTP response headers
- Vulnerability categories: XSS, SQL/ORM injection, CORS misconfiguration, missing HTTP security headers, input validation, information disclosure (422 bodies, debug mode), dangerous HTTP methods, env-var fallback safety

**Out of Scope:**
- Authentication / authorization (intentionally absent — single-user personal app)
- Infrastructure, deployment, secrets management
- Third-party dependencies / supply chain

### Report Output Format

Each finding uses this structure:

```markdown
## Finding SEC-NNN — [Title]

**Severity:** High | Medium | Low | Informational
**File(s):** `path/to/file` (line N if applicable)
**Description:** What the issue is and why it matters.
**Evidence:**
\`\`\`
relevant code snippet
\`\`\`
**Remediation:** Specific, actionable fix.
```

Sections with no actionable issues include: `> No issues found.`

The report opens with a summary table:

```markdown
| ID | Severity | Title | File |
|----|----------|-------|------|
```

## Context for Development

### Codebase Patterns

- **ORM-only**: All DB access via SQLAlchemy ORM — zero raw SQL or `.execute()` calls confirmed across all backend files
- **No debug mode**: `FastAPI(title=..., version=..., description=...)` — no `debug=True` — stack traces not exposed in responses
- **Pydantic dual-layer**: `TodoCreate.text` has `min_length=1, max_length=200`; `models.py` has `String(200)` — DB and schema constraints consistent. `TodoUpdate` accepts only `bool` — no text injection surface on PATCH
- **React JSX only**: No `dangerouslySetInnerHTML` in any component. `todo.text` rendered via JSX children and `aria-label` template literals — both auto-escaped by React
- **Typed IDs in URLs**: `todo.id` typed as TypeScript `number`; FastAPI path param typed as `int` — string injection not possible
- **No credential forwarding**: `fetch` calls contain no `credentials: 'include'` — cookies not sent cross-origin
- **Fail-fast env vars**: `DATABASE_URL` raises `ValueError` at startup if missing — `VITE_API_URL` has no equivalent guard (undefined → requests silently go to `"undefined/api/v1/todos"`)
- **CORS config**: `allow_origins` locked to `["http://localhost:5173", "http://localhost:3000"]`; `allow_credentials=True`; `allow_methods=["*"]`; `allow_headers=["*"]`
- **422 bodies**: FastAPI default — echoes submitted field values in validation error responses
- **Session lifecycle**: `get_db()` uses `try/finally` + `db.close()` — no leak risk. `autocommit=False, autoflush=False` — all commits explicit

### Files to Reference

| File | Purpose |
| ---- | ------- |
| `backend/main.py` | FastAPI app instantiation, CORS middleware config |
| `backend/database.py` | DB engine, session factory, `get_db` dependency |
| `backend/routers/todos.py` | All API route handlers (GET, POST, PATCH, DELETE) |
| `backend/schemas.py` | Pydantic input/output models with validation rules |
| `backend/models.py` | SQLAlchemy ORM models (`String(200)` on `text`) |
| `frontend/src/api/todos.ts` | All `fetch` calls to backend |
| `frontend/src/hooks/useTodos.ts` | TanStack Query mutations/queries wrapping API layer |
| `frontend/src/components/TodoItem/TodoItem.tsx` | Renders `todo.text` + `aria-label` template literals |
| `frontend/src/components/AddTodoForm/AddTodoForm.tsx` | User input form with client-side validation |

### Technical Decisions

- Output is a markdown report only — no code modifications
- Severity scale: **High / Medium / Low / Informational**
- Informational = defended, no action required, but worth documenting
- Report saved to `_bmad-output/security-audit-report.md`
- No `project-context.md` exists — patterns derived from direct code investigation

## Implementation Plan

### Tasks

- [x] Task 1: Initialise the report file
  - File: `_bmad-output/security-audit-report.md` (create)
  - Action: Create file with title, date, and empty summary table. Add all section headings for each finding category listed below. Do not fill findings yet.
  - Sections to pre-create: SQL/ORM Injection, XSS, CORS Configuration, HTTP Security Headers, Information Disclosure, HTTP Method Exposure, Environment Variable Safety, Input Validation, Session & Transaction Safety

- [x] Task 2: Document SQL/ORM Injection findings
  - Files: `backend/routers/todos.py`, `backend/database.py`
  - Action: Confirm zero raw SQL — all queries use `db.query().filter()` ORM pattern. Document as **SEC-001 (Informational)**.
  - Evidence to quote: one representative `db.query(models.Todo).filter(...)` call from `todos.py`

- [x] Task 3: Document XSS findings
  - Files: `frontend/src/components/TodoItem/TodoItem.tsx`, `frontend/src/components/AddTodoForm/AddTodoForm.tsx`
  - Action: Confirm no `dangerouslySetInnerHTML`. Confirm `todo.text` is rendered as JSX children (auto-escaped). Confirm `aria-label` template literals are React attributes (auto-escaped). Document as **SEC-002 (Informational)**.
  - Evidence to quote: `<span ...>{todo.text}</span>` and the `aria-label` line from `TodoItem.tsx`

- [x] Task 4: Document CORS configuration findings
  - File: `backend/main.py`
  - Action A: `allow_credentials=True` combined with `allow_headers=["*"]` — document as **SEC-003 (Medium)**. Safe now (localhost-only origins) but a latent risk if origins expand to production domains without tightening headers.
  - Action B: `allow_methods=["*"]` permits `TRACE` and `CONNECT` HTTP methods — document as **SEC-004 (Low)**. `TRACE` enables Cross-Site Tracing (XST); mitigated here by localhost origin restriction but should be explicit.
  - Evidence to quote: the `CORSMiddleware` block from `main.py`
  - Remediation for SEC-003: Replace `allow_headers=["*"]` with `allow_headers=["Content-Type"]` (the only header the frontend sends)
  - Remediation for SEC-004: Replace `allow_methods=["*"]` with `allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"]`

- [x] Task 5: Document HTTP security headers findings
  - File: `backend/main.py`
  - Action: FastAPI ships with no security response headers by default. Confirm absence of: `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy`. Document as **SEC-005 (Low)**.
  - Remediation: Add a custom middleware or use `slowapi`/`starlette` middleware to inject headers. Provide the exact header values to add.

- [x] Task 6: Document information disclosure findings
  - File: `backend/routers/todos.py` (FastAPI framework behaviour)
  - Action A: FastAPI 422 responses echo submitted input values by default. Document as **SEC-006 (Low)**. Example: submitting a 201-char string returns `{"detail":[{"input":"<full 201-char string>",...}]}`.
  - Action B: Confirm `FastAPI(debug=False)` (implicit default — no `debug=True` found). Document as **SEC-007 (Informational)** — no stack trace exposure.
  - Remediation for SEC-006: Add a custom exception handler to return a sanitised 422 response without echoing input.

- [x] Task 7: Document environment variable safety findings
  - File: `frontend/src/api/todos.ts`
  - Action: `VITE_API_URL` has no undefined guard. If the env var is missing at Vite build time, `import.meta.env.VITE_API_URL` is `undefined`, and all fetch calls go to the literal URL `"undefined/api/v1/todos"`. Document as **SEC-008 (Low)**.
  - Evidence to quote: `const API_URL = import.meta.env.VITE_API_URL` from `todos.ts`
  - Remediation: Add a build-time guard — e.g., throw in `todos.ts` if `API_URL` is falsy, or add a Vite plugin env validation.

- [x] Task 8: Document input validation findings
  - Files: `backend/schemas.py`, `backend/models.py`
  - Action: Confirm `TodoCreate.text` Pydantic validation (`min_length=1, max_length=200`) is consistent with `models.py` `String(200)`. Confirm `TodoUpdate` accepts only `bool`. Document as **SEC-009 (Informational)** — dual-layer validation is correctly implemented.

- [x] Task 9: Document session and transaction safety findings
  - File: `backend/database.py`
  - Action: Confirm `get_db()` uses `try/finally` for `db.close()`. Confirm `autocommit=False`. Document as **SEC-010 (Informational)** — no session leak or implicit commit risk.

- [x] Task 10: Populate summary table and finalise report
  - File: `_bmad-output/security-audit-report.md`
  - Action: Fill in the summary table at the top of the report with all SEC-NNN IDs, severities, titles, and affected files. Verify every section either has a finding or `> No issues found.` Verify no placeholder text remains.

### Acceptance Criteria

- **Given** the report is generated
  **When** the summary table at the top is read
  **Then** it lists all findings with ID, Severity, Title, and File columns populated

- **Given** a finding category was reviewed and issues found
  **When** that section is read
  **Then** it contains a `## Finding SEC-NNN` block with Severity, File, Description, Evidence, and Remediation all filled in

- **Given** a finding category was reviewed and no issues found
  **When** that section is read
  **Then** it contains `> No issues found.` (not omitted or left blank)

- **Given** the CORS section is written
  **When** SEC-003 is read
  **Then** it is rated Medium, references `backend/main.py`, quotes the `CORSMiddleware` block, and recommends replacing `allow_headers=["*"]` with `["Content-Type"]`

- **Given** the HTTP security headers section is written
  **When** SEC-005 is read
  **Then** it lists all five missing headers and provides the exact header values to add as remediation

- **Given** the report is complete
  **When** saved
  **Then** it exists at `_bmad-output/security-audit-report.md` with no placeholder text

## Additional Context

### Dependencies

None — read-only analysis task, no new packages required.

### Testing Strategy

N/A — output is a documentation artifact, not executable code. Manual verification: open the report and confirm all 10 SEC entries are present, summary table is complete, and no `{placeholder}` text remains.

### Notes

- **SEC-003 is the most actionable finding**: `allow_credentials=True` + `allow_headers=["*"]` is safe today but a production deployment trap. The fix is a one-liner.
- **SEC-005 (missing headers)** requires adding middleware to `main.py` — most impactful hardening for a future production deployment
- All "Informational" findings are genuine strengths worth preserving — ORM usage, JSX escaping, typed path params. A future dev agent should not "fix" these.
- **No High severity findings** are expected based on investigation — the most severe confirmed issue is Medium (CORS)

## Review Notes

- Adversarial review completed: 2026-03-24
- Findings: 12 total, 12 fixed, 0 skipped
- Resolution approach: auto-fix

### Changes Applied from Adversarial Review

- F1: Fixed phantom file reference `backend/input/todos.py` → `backend/routers/todos.py` in SEC-005 (now SEC-006)
- F2: Added new finding SEC-002 for plaintext credentials in `backend/.env`
- F3: Upgraded SEC-003 severity Medium → High (now SEC-001)
- F4: Revised SEC-004 (now SEC-003) — corrected TRACE/CORS technical description; `allow_methods` controls preflight headers only, not ASGI-level handling
- F5: Reframed SEC-008 (now SEC-006) as reliability/misconfiguration finding, not security vulnerability
- F6: Fixed SEC-006 (now SEC-005) remediation — clarified `@app.exception_handler` must go in `main.py`, not router files
- F7: Added clarifying comment to SEC-005 (now SEC-004) CSP recommendation — applies to API responses only, not frontend server
- F8: Added explicit auth/authz out-of-scope statement at top of report and in appendix
- F9: Added new finding SEC-007 for frontend error messages exposing HTTP status codes in DOM
- F10: Added rate limiting/pagination note in Out-of-Scope appendix
- F11: Improved SEC-002 (now in Reviewed Clean) aria-label description — clarified React serialises all prop values safely, not just HTML entities
- F12: Consolidated 5 Informational findings into a "Reviewed Clean" table — removed from main finding count, summary table now shows only actionable findings
