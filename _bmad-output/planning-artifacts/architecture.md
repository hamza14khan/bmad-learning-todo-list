---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-03-23'
inputDocuments:
  - _bmad-output/planning-artifacts/PRD.md
workflowType: 'architecture'
project_name: 'todo-list'
user_name: 'Hamza'
date: '2026-03-23'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (14 FRs):**
- Core CRUD: Create, read, toggle-complete, delete todos — all via REST API
- Data model: id (auto-int), text (varchar 200), is_complete (boolean), created_at (timestamp)
- States: loading, empty, and error states on initial fetch
- Validation: reject empty/whitespace input client-side before API call
- Visual feedback: strikethrough + muted style for completed todos

**Non-Functional Requirements (8 NFRs — architecturally significant):**
- NFR-01: UI interactions reflect in <300ms → requires optimistic updates
- NFR-02: Initial load <2s → bundle size discipline, no heavy dependencies
- NFR-03: PostgreSQL persists up to 500 todos reliably across restarts
- NFR-04: Graceful degradation when API unreachable → error boundary pattern
- NFR-05: Chrome, Firefox, Safari latest stable → no experimental browser APIs
- NFR-06: Local dev via `npm run dev` + `uvicorn` + PostgreSQL → Docker Compose
- NFR-07: Consistent formatting and naming conventions → linting/formatting tooling
- NFR-08: WCAG 2.1 AA — 4.5:1 contrast, keyboard navigation, focus management

**Scale & Complexity:**
- Primary domain: Full-stack web application (SPA + REST API + relational DB)
- Complexity level: Low — bounded scope, single user, no auth, no realtime
- Estimated architectural components: 4 (React frontend, FastAPI backend, PostgreSQL, Docker dev env)

### Technical Constraints & Dependencies

- No cloud infrastructure for MVP — local development only
- CORS required between frontend (localhost:5173) and backend (localhost:8000)
- Database connection via environment variables only — no hardcoded credentials
- Must be extensible to cloud deployment without major refactoring

### Cross-Cutting Concerns Identified

- **Error handling:** All 3 states (loading/empty/error) handled in React; FastAPI returns appropriate HTTP codes
- **Testing strategy:** Playwright E2E + pytest backend + React Testing Library — must be defined upfront and embedded per-story
- **Docker dev environment:** Docker Compose orchestrates all services for consistent local setup
- **CORS configuration:** Single CORS config in FastAPI covering all frontend origins
- **Environment configuration:** `.env` files for backend; Vite env vars for frontend — never hardcoded
- **Optimistic UI updates:** Frontend updates state immediately on user action, rolls back on API error

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web application — React SPA (frontend) + FastAPI REST API (backend) + PostgreSQL (database)

### Stack Already Defined

Technology preferences were established during PRD and epics phases. No open evaluation needed.

### Frontend Starter: Vite + React + TypeScript

**Rationale:** Create React App is deprecated. Vite is the current standard for React SPAs — fast HMR, minimal config, TypeScript support out of the box.

**Initialization Command:**

```bash
npm create vite@latest frontend -- --template react-ts
```

**Decisions provided by starter:**
- Language: TypeScript (strict mode)
- Build tooling: Vite (dev server on port 5173, production build via Rollup)
- Hot Module Replacement: enabled by default
- ESLint: included (extend with Prettier separately)
- No routing, no state management — decided in step 4

### Frontend Testing: Vitest + React Testing Library + Playwright

**Unit & Component Tests — Vitest:**

```bash
npm install -D vitest @vitest/coverage-v8 @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

- Vitest runs natively inside Vite's pipeline — zero extra transform config
- Jest-compatible API (`describe`, `it`, `expect`, `vi.mock`) — same developer experience
- **Coverage threshold: 70% minimum** (statements, branches, functions, lines) — enforced in `vitest.config.ts`, build fails if not met
- React Testing Library for component interaction tests
- `@testing-library/user-event` for realistic user interactions

**E2E Tests — Playwright:**

```bash
npm init playwright@latest
```

- Covers full user journeys (create → complete → delete todo)
- Runs against the live app (frontend + backend + DB must be running)
- Separate from unit coverage — not included in the 70% threshold

### Backend Scaffold: Manual FastAPI Setup

**Rationale:** No official FastAPI CLI. Standard practice is a minimal manual scaffold in `backend/` with pinned `requirements.txt`.

**Decisions provided:**
- Language: Python 3.11+
- Framework: FastAPI 0.115.x
- ORM: SQLAlchemy 2.x
- Validation: Pydantic v2
- Dev server: uvicorn with --reload (port 8000)

### Backend Testing: pytest

- `pytest` + `httpx` for API endpoint integration tests
- `pytest-asyncio` for async route tests
- Tests hit a real test database (no mocking the DB layer)
- Included in `backend/requirements.txt`

### Dev Environment: Docker Compose (Custom)

Docker Compose orchestrates all services for consistent local setup. Defined in architecture decisions (step 4).

### Coverage Configuration (`vitest.config.ts`)

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        statements: 70,
        branches: 70,
        functions: 70,
        lines: 70,
      },
    },
  },
})
```

**Note:** Vite scaffold + Vitest setup + Playwright init are the first implementation tasks of Story 1.2.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- PostgreSQL as database with Alembic for migrations
- FastAPI with `/api/v1/` URL prefix for all endpoints
- React Query for frontend API state management
- Docker Compose for local dev environment

**Important Decisions (Shape Architecture):**
- Vitest (70% coverage threshold) + Playwright for testing
- SQLAlchemy 2.x ORM with Pydantic v2 validation
- TypeScript strict mode on frontend

**Deferred Decisions (Post-MVP):**
- Authentication / user accounts
- CI/CD pipeline
- Cloud deployment strategy
- API rate limiting

### Data Architecture

- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.x (`DeclarativeBase`, `mapped_column` — not legacy 1.x style)
- **Migrations:** Alembic — versioned migration files under `backend/migrations/`. `create_all` is NOT used. All schema changes go through `alembic revision --autogenerate` + `alembic upgrade head`
- **Validation:** Pydantic v2 schemas for all request/response models (`ConfigDict(from_attributes=True)`, not deprecated `orm_mode`)
- **Caching:** None — not required for MVP scope (≤500 todos, local only)

### Authentication & Security

- **Auth:** None for MVP — single user, no sessions (explicit PRD decision)
- **CORS:** Configured in FastAPI middleware — allow origins `http://localhost:5173` and `http://localhost:3000`
- **Credentials:** All secrets via `.env` files — never hardcoded. Both `backend/.env` and `frontend/.env` are gitignored. `.env.example` files are committed.

### API & Communication Patterns

- **Style:** REST
- **URL prefix:** All endpoints prefixed `/api/v1/` (e.g. `GET /api/v1/todos`, `POST /api/v1/todos`)
- **Versioning rationale:** Future-proofs for proxied/shared domain deployment without breaking changes
- **Error format:** FastAPI default JSON `{ "detail": "message" }` — consistent across all error responses
- **HTTP status codes:** Standard — 200 OK, 201 Created, 204 No Content, 404 Not Found, 422 Unprocessable Entity
- **API docs:** FastAPI auto-generates `/docs` (Swagger UI) — enabled in development

### Frontend Architecture

- **State management:** React Query (TanStack Query v5) — handles loading, error, and cache states automatically. Reduces boilerplate for all API interactions. Optimistic updates used for create/complete/delete (NFR-01: <300ms)
- **Component architecture:** Flat — no deep nesting for a single-page app of this scope
- **Routing:** None — single page, no React Router needed
- **HTTP client:** Native `fetch` — no Axios. React Query wraps fetch calls
- **Styling:** CSS Modules or plain CSS — no CSS-in-JS, no Tailwind (keeps learning curve low)

### Infrastructure & Deployment

- **Local dev:** Docker Compose with three services:
  - `db` — postgres:16, port 5432
  - `backend` — FastAPI + uvicorn, port 8000, `depends_on: db`
  - `frontend` — Vite dev server, port 5173, `depends_on: backend`
- **Environment config:**
  - `backend/.env` → `DATABASE_URL`
  - `frontend/.env` → `VITE_API_URL=http://localhost:8000`
  - Both gitignored; `.env.example` committed for each
- **CI/CD:** Not required for MVP

### Decision Impact Analysis

**Implementation Sequence:**
1. Docker Compose + PostgreSQL service (Story 1.1)
2. FastAPI + Alembic + `/api/v1/todos` GET endpoint (Story 1.1)
3. Vite + React + Vitest + Playwright setup (Story 1.2)
4. React Query integration + todo list view (Story 1.2)
5. Empty/error states (Story 1.3)
6. CRUD operations with optimistic updates (Epic 2)
7. Responsive layout + WCAG compliance (Epic 3)

**Cross-Component Dependencies:**
- Frontend `VITE_API_URL` must match backend port in Docker Compose
- Alembic migrations must run before backend starts (Docker Compose `depends_on` + healthcheck)
- Playwright E2E tests require all three Docker services running
- React Query cache invalidation strategy must align with API response shapes

## Implementation Patterns & Consistency Rules

### Critical Conflict Points Identified

8 areas where AI agents could make different choices — all resolved below.

### Naming Patterns

**Database Naming Conventions:**
- Tables: `snake_case` plural — `todos` (not `Todo`, not `todo`)
- Columns: `snake_case` — `is_complete`, `created_at`, `user_id`
- Primary keys: always `id`
- Alembic migration files: `{revision}_{short_description}.py` e.g. `001_create_todos_table.py`

**API Naming Conventions:**
- All endpoints: `snake_case` plural nouns — `/api/v1/todos`, `/api/v1/todos/{id}`
- URL path parameters: `{id}` (FastAPI style)
- Query parameters: `snake_case` — `?sort_by=created_at`
- JSON field names in responses: `snake_case` — matches Python models directly, no transform layer

**Code Naming Conventions:**

*Backend (Python):*
- Files: `snake_case` — `main.py`, `todo_router.py`, `todo_schema.py`
- Classes: `PascalCase` — `Todo`, `TodoCreate`, `TodoResponse`
- Functions: `snake_case` — `get_todos()`, `create_todo()`
- Variables: `snake_case` — `todo_id`, `db_session`

*Frontend (TypeScript):*
- Component files: `PascalCase` — `TodoItem.tsx`, `TodoList.tsx`, `AddTodoForm.tsx`
- Non-component files: `camelCase` — `apiClient.ts`, `useTodos.ts`
- Functions/variables: `camelCase` — `todoId`, `isComplete`, `handleDelete`
- Types/interfaces: `PascalCase` — `Todo`, `CreateTodoRequest`
- CSS Module files: match component name — `TodoItem.module.css`
- Test files: co-located, suffix `.test.tsx` — `TodoItem.test.tsx`

### Structure Patterns

**Project Organisation:**
```
todo-list/
├── backend/
│   ├── main.py              # FastAPI app entry, CORS, router registration
│   ├── database.py          # Engine, SessionLocal, Base, get_db
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routers/
│   │   └── todos.py         # All /api/v1/todos routes
│   ├── migrations/          # Alembic migration files
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py      # pytest fixtures, test DB setup
│   │   └── test_todos.py    # endpoint integration tests
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # React components (PascalCase files)
│   │   ├── hooks/           # Custom hooks (useTodos.ts, etc.)
│   │   ├── api/             # API client functions (todos.ts)
│   │   ├── types/           # TypeScript type definitions (todo.ts)
│   │   └── test/
│   │       └── setup.ts     # Vitest global setup
│   ├── e2e/                 # Playwright tests
│   ├── vitest.config.ts
│   ├── .env
│   └── .env.example
├── docker-compose.yml
└── .gitignore
```

### Format Patterns

**API Response Format:**
- **Direct response** — no wrapper object. `GET /api/v1/todos` returns `[...]` not `{data: [...]}`
- Single todo: returns the `TodoResponse` object directly
- Delete: returns `204 No Content` with empty body

**JSON Field Naming:**
- `snake_case` throughout — backend sends `is_complete`, `created_at`; frontend reads them as-is
- No camelCase transform layer — keeps the stack simple
- TypeScript `Todo` type mirrors the API: `is_complete: boolean`, `created_at: string`

**Date/Time Format:**
- ISO 8601 strings — `"2026-03-23T14:00:00Z"` — FastAPI/Pydantic serialises `datetime` to ISO by default
- Frontend displays with `new Date(todo.created_at).toLocaleDateString()`

**HTTP Status Codes:**
- `200 OK` — GET (list or single)
- `201 Created` — POST (new todo)
- `204 No Content` — DELETE
- `404 Not Found` — todo ID doesn't exist
- `422 Unprocessable Entity` — validation failure (FastAPI default)

### Communication Patterns

**React Query Key Conventions:**
- Query key for todo list: `['todos']`
- Query key for single todo: `['todos', id]`
- All mutations invalidate `['todos']` on success

**State Management Patterns:**
- No global state store — React Query is the single source of truth for server state
- Local UI state (input field value, validation error) uses `useState` — never put in React Query
- Optimistic updates: update React Query cache immediately on mutation, rollback on error

### Process Patterns

**Error Handling:**

*Backend:*
- Raise `HTTPException(status_code=404, detail="Todo not found")` for not-found cases
- Let FastAPI's default handler return `{"detail": "..."}` — don't build a custom error wrapper
- Log errors to console in development — no external logging service for MVP

*Frontend:*
- React Query `error` state surfaces API errors — display inline, never `alert()`
- Error message shown in the same location as the data it failed to load
- On mutation error: show inline message, revert optimistic update, keep input data intact

**Loading State Patterns:**
- Use React Query `isLoading` / `isPending` for all async states — no manual `useState` loading flags
- Show a loading spinner/skeleton only on initial page load (`isLoading`)
- Subsequent refetches are silent — no spinner (`isFetching` ignored in UI)

**Validation Patterns:**
- Frontend validates before sending: empty/whitespace check, 200-char limit — no API call made
- Backend also validates via Pydantic — `text: str` with `min_length=1, max_length=200`
- Never rely solely on frontend validation — backend is the source of truth

### Enforcement Guidelines

**All AI Agents MUST:**
- Use `snake_case` for all Python identifiers, DB columns, and JSON API fields
- Use `PascalCase` for React component files and TypeScript types
- Never bypass Alembic — all DB changes via migration files
- Route all API calls through `src/api/` functions — no `fetch` calls inside components
- Co-locate test files with source (`TodoItem.test.tsx` next to `TodoItem.tsx`)
- Use React Query for all server state — no manual fetch in `useEffect`
- Always handle all three states: loading, error, empty — never assume success

**Anti-Patterns (never do these):**
- ❌ `create_all()` for schema changes after initial setup
- ❌ Hardcoded `localhost:8000` in frontend components — use `VITE_API_URL` env var
- ❌ `useState` + `useEffect` + `fetch` for API calls — use React Query instead
- ❌ camelCase JSON field names in API responses (`isComplete`) — use `snake_case`
- ❌ `fetch` calls directly inside React components — route through `src/api/`

## Project Structure & Boundaries

### Complete Project Directory Structure

```
todo-list/
├── docker-compose.yml           # Orchestrates db + backend + frontend
├── Makefile                     # Shortcut commands (make up, make test, make migrate, etc.)
├── .gitignore                   # Ignores .env files, __pycache__, node_modules, dist
├── README.md                    # Project overview — points to backend/README.md and frontend/README.md
│
├── backend/
│   ├── README.md                # Setup: venv, .env config, alembic upgrade head, uvicorn, pytest
│   ├── main.py                  # FastAPI app: CORS middleware, router registration, lifespan
│   ├── database.py              # Engine, SessionLocal, Base, get_db dependency
│   ├── models.py                # SQLAlchemy Todo model → todos table
│   ├── schemas.py               # Pydantic TodoResponse, TodoCreate, TodoUpdate
│   ├── routers/
│   │   └── todos.py             # All /api/v1/todos endpoints (GET, POST, PATCH, DELETE)
│   ├── migrations/              # Alembic migrations
│   │   ├── env.py               # Alembic environment config (reads DATABASE_URL)
│   │   ├── script.py.mako       # Migration file template
│   │   └── versions/
│   │       └── 001_create_todos_table.py   # Initial migration (Story 1.1)
│   ├── tests/
│   │   ├── conftest.py          # pytest fixtures: test DB, test client, seed data
│   │   └── test_todos.py        # Integration tests for all /api/v1/todos endpoints
│   ├── alembic.ini              # Alembic config (points to migrations/)
│   ├── requirements.txt         # Pinned Python dependencies
│   ├── Dockerfile               # Backend container (python:3.11-slim + uvicorn)
│   ├── .env                     # DATABASE_URL (gitignored)
│   └── .env.example             # DATABASE_URL=postgresql://USER:PASS@localhost:5432/todoapp
│
├── frontend/
│   ├── README.md                # Setup: npm install, .env config, npm run dev, test:coverage, playwright
│   ├── index.html               # Vite entry point
│   ├── vite.config.ts           # Vite config
│   ├── vitest.config.ts         # Vitest: jsdom env, 70% coverage thresholds, setup file
│   ├── tsconfig.json            # TypeScript strict mode config
│   ├── package.json             # Dependencies: react, @tanstack/react-query, vitest, playwright
│   ├── playwright.config.ts     # Playwright: baseURL, browsers, test dir
│   ├── Dockerfile               # Frontend container (node:20-alpine + vite dev server)
│   ├── .env                     # VITE_API_URL=http://localhost:8000 (gitignored)
│   ├── .env.example             # VITE_API_URL=http://localhost:8000
│   │
│   ├── src/
│   │   ├── main.tsx             # React entry: QueryClientProvider wraps App
│   │   ├── App.tsx              # Root component: renders TodoPage
│   │   │
│   │   ├── types/
│   │   │   └── todo.ts          # TypeScript: Todo, CreateTodoRequest, UpdateTodoRequest
│   │   │
│   │   ├── api/
│   │   │   └── todos.ts         # All fetch calls: getTodos, createTodo, toggleTodo, deleteTodo
│   │   │
│   │   ├── hooks/
│   │   │   └── useTodos.ts      # React Query hooks: useGetTodos, useCreateTodo, etc.
│   │   │
│   │   ├── components/
│   │   │   ├── TodoList/
│   │   │   │   ├── TodoList.tsx         # Renders list of TodoItem — handles empty state (Story 1.3)
│   │   │   │   ├── TodoList.test.tsx    # Vitest: loading, empty, error, populated states
│   │   │   │   └── TodoList.module.css
│   │   │   ├── TodoItem/
│   │   │   │   ├── TodoItem.tsx         # Single todo row: text, complete toggle, delete (Epic 2)
│   │   │   │   ├── TodoItem.test.tsx    # Vitest: renders, toggle click, delete click
│   │   │   │   └── TodoItem.module.css
│   │   │   ├── AddTodoForm/
│   │   │   │   ├── AddTodoForm.tsx      # Input + submit: validation, calls useCreateTodo (Story 2.1)
│   │   │   │   ├── AddTodoForm.test.tsx # Vitest: validation, submit, clear on success
│   │   │   │   └── AddTodoForm.module.css
│   │   │   ├── LoadingSpinner/
│   │   │   │   ├── LoadingSpinner.tsx   # Loading state UI (Story 1.2)
│   │   │   │   ├── LoadingSpinner.test.tsx
│   │   │   │   └── LoadingSpinner.module.css
│   │   │   └── ErrorMessage/
│   │   │       ├── ErrorMessage.tsx     # Error state UI (Story 1.3)
│   │   │       └── ErrorMessage.module.css
│   │   │
│   │   └── test/
│   │       └── setup.ts         # Vitest global setup: @testing-library/jest-dom matchers
│   │
│   └── e2e/
│       └── todos.spec.ts        # Playwright: full journey (create → complete → delete)
│
└── _bmad-output/                # BMAD planning artifacts (never modify during dev)
    ├── planning-artifacts/
    └── implementation-artifacts/
```

### Makefile Targets

```makefile
# Dev environment
make up          # docker compose up (all services)
make up-build    # docker compose up --build (after dep changes)
make down        # docker compose down
make logs        # docker compose logs -f

# Database
make migrate     # alembic upgrade head (inside backend container)
make migration   # alembic revision --autogenerate -m "description"

# Testing
make test        # run all tests (backend + frontend unit)
make test-be     # cd backend && pytest --cov
make test-fe     # cd frontend && npm run test:coverage
make test-e2e    # cd frontend && npx playwright test

# Utilities
make install     # install all deps (pip + npm)
make lint        # run linters (ruff for Python, eslint for TS)
```

### Architectural Boundaries

**API Boundary — Frontend ↔ Backend:**
- All communication via HTTP REST over `VITE_API_URL` (env var)
- Frontend never imports backend code — strict separation
- Contract: JSON with `snake_case` fields, direct responses (no wrapper)
- CORS enforced in FastAPI — only configured origins accepted

**Data Boundary — Backend ↔ Database:**
- Only `database.py` and `models.py` touch SQLAlchemy directly
- Routers receive a `db: Session` via `Depends(get_db)` — never import `engine` directly
- All schema changes go through Alembic — never `create_all` after initial setup

**Component Boundary — React:**
- Components never call `fetch` directly — all API calls go through `src/api/todos.ts`
- Components never own async state — React Query hooks in `src/hooks/` own it
- `useTodos.ts` is the only file that imports from `src/api/` and React Query

### Requirements to Structure Mapping

**Epic 1 — Full-Stack Foundation:**
- Story 1.1: `backend/` — `main.py`, `database.py`, `models.py`, `schemas.py`, `routers/todos.py` (GET only), `migrations/versions/001_create_todos_table.py`, `docker-compose.yml` (db + backend services), `Makefile`, root `README.md`, `backend/README.md`
- Story 1.2: `frontend/` scaffold — `src/main.tsx`, `src/App.tsx`, `src/api/todos.ts`, `src/hooks/useTodos.ts`, `src/components/TodoList.tsx`, `src/components/LoadingSpinner.tsx`, `frontend/README.md`
- Story 1.3: `src/components/ErrorMessage.tsx` — error state; empty state inside `TodoList.tsx`

**Epic 2 — Core Todo Operations:**
- Story 2.1: `src/components/AddTodoForm.tsx` + POST endpoint in `routers/todos.py`
- Story 2.2: `src/components/TodoItem.tsx` (complete toggle) + PATCH endpoint in `routers/todos.py`
- Story 2.3: delete action in `TodoItem.tsx` + DELETE endpoint in `routers/todos.py`

**Epic 3 — Responsive & Accessible:**
- Story 3.1: CSS Modules in all component `.module.css` files — responsive breakpoints
- Story 3.2: ARIA attributes, focus management, contrast — touches all component files

**Cross-Cutting Concerns:**
- Docker Compose + Makefile: set up in Story 1.1, used throughout
- Testing: `backend/tests/`, `frontend/src/**/*.test.tsx`, `frontend/e2e/` — every story adds tests
- Env config: `backend/.env` + `frontend/.env` — set up in Story 1.1, referenced throughout

### Integration Points

**Data Flow — Read todos:**
```
Browser → GET /api/v1/todos
  → FastAPI router (todos.py)
  → SQLAlchemy query (models.py, database.py)
  → PostgreSQL (todos table)
  ← JSON array [TodoResponse, ...]
  ← React Query cache (['todos'])
  ← TodoList renders items
```

**Data Flow — Create todo:**
```
User types → AddTodoForm validates (client-side)
  → POST /api/v1/todos {text: "..."}
  → FastAPI validates (Pydantic TodoCreate)
  → SQLAlchemy INSERT → Alembic-managed schema
  ← 201 TodoResponse
  ← React Query invalidates ['todos'] → refetch
  ← TodoList re-renders with new item
```

**Docker Compose Service Dependencies:**
```
db (postgres:16) ← backend (healthcheck wait) ← frontend
```

### Development Workflow

**With Docker Compose (recommended):**
```bash
make up          # start everything
make migrate     # run pending migrations
make test        # run all tests
make down        # stop everything
```

**Manual (per service):**
```bash
# Terminal 1: DB
docker run --name todoapp-db -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=todoapp -p 5432:5432 -d postgres:16

# Terminal 2: Backend
cd backend && uvicorn main:app --reload

# Terminal 3: Frontend
cd frontend && npm run dev
```

## Architecture Validation Results

### Coherence Validation ✅

All technology decisions are mutually compatible. No contradictory patterns identified.
snake_case used throughout API and TypeScript types — no transform layer needed.

### Requirements Coverage ✅

All 14 FRs and 8 NFRs have explicit architectural support. See mapping in Project Structure section.

### Implementation Readiness ✅

All critical decisions documented with versions. Project structure is specific and complete.
Implementation patterns cover all identified AI agent conflict points.

### Gap Analysis

**🔴 Critical:**
- Story 1.1 (`1-1-backend-setup.md`) was created before architecture and is now stale.
  Uses `create_all` (not Alembic) and `/todos` prefix (not `/api/v1/`).
  **Action:** Delete and regenerate via `/bmad-create-story` after architecture is complete.

**🟡 Important:**
- Add `ruff` to `backend/requirements.txt` as dev dependency
- Add `ruff.toml` / `pyproject.toml` and `.eslintrc.js` to project structure

**🟢 Nice-to-have (post-MVP):**
- `docker-compose.override.yml` for local dev overrides
- `pyproject.toml` to consolidate Python tool config

### Architecture Completeness Checklist

- [x] Requirements analysis complete
- [x] Scale and complexity assessed
- [x] All architectural decisions documented with rationale
- [x] Technology stack fully specified
- [x] Docker Compose + Makefile dev environment defined
- [x] Testing strategy: Vitest (70% threshold) + Playwright + pytest
- [x] Naming conventions established (snake_case / PascalCase / camelCase)
- [x] Complete project structure with all files mapped to epics
- [x] Architectural boundaries defined
- [x] Anti-patterns documented
- [x] All FRs and NFRs architecturally covered

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION (after Story 1.1 regeneration)

**Confidence Level:** High

**Key Strengths:**
- Simple, learner-friendly stack with no unnecessary complexity
- Docker Compose + Makefile removes environment setup friction
- Testing strategy embedded from the start — not deferred
- Clear boundaries prevent AI agents from making inconsistent choices

**Areas for Future Enhancement:**
- Alembic + CI/CD pipeline when moving to cloud
- API versioning already in place for `/api/v2/` when needed

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure — files go where the structure says they go
- Refer to this document for all architectural decisions

**First Implementation Priority:**
1. Regenerate Story 1.1 (delete stale file, run `/bmad-create-story`)
2. Then run `/bmad-dev-story` on the new Story 1.1
