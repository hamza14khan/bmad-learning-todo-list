# Chore 1: Test Isolation and Migration Config Fixes

Status: done

## Story

As a **developer**,
I want the test database to be fully isolated and the Alembic config to fail clearly when misconfigured,
so that test runs are always reproducible and migration errors are easy to diagnose.

## Acceptance Criteria

1. **Given** the test suite is run
   **When** `pytest` executes
   **Then** no `test.db` file is written to disk — all test data lives in memory only

2. **Given** `DATABASE_URL` is not set in the environment
   **When** `alembic upgrade head` is run
   **Then** Alembic raises a clear `ValueError` ("DATABASE_URL not set") instead of a confusing internal SQLAlchemy error

## Tasks / Subtasks

- [x] Task 1: Fix test database to use in-memory SQLite (AC: 1)
  - [x] In `backend/tests/conftest.py` line 21, change `sqlite:///./test.db` → `sqlite:///:memory:`
  - [x] Verify `pytest` passes and no `test.db` file appears in the filesystem after the run

- [x] Task 2: Add `DATABASE_URL` guard in Alembic env (AC: 2)
  - [x] In `backend/migrations/env.py`, after `load_dotenv()`, add DATABASE_URL guard
  - [x] Remove the existing `config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))` line
  - [x] Verify `ruff check .` passes (no lint errors)

## Dev Notes

### Why `sqlite:///:memory:` instead of `sqlite:///./test.db`

`sqlite:///./test.db` creates a real file. If a test run is interrupted mid-teardown (e.g. Ctrl-C, crash), the file persists with stale schema data. The next test run may then see tables from the previous run before `setup_db` has a chance to drop them — causing intermittent failures that are very hard to debug.

`sqlite:///:memory:` lives entirely in process memory. It's destroyed automatically when the connection is closed. No cleanup needed, no file contamination between runs.

**One important note:** in-memory SQLite databases are connection-scoped. The `check_same_thread=False` arg is still needed for FastAPI's `TestClient`, and the engine must stay open for the entire test session. The current `setup_db` + `db` + `client` fixture chain already handles this correctly — no other changes required.

### Why the `env.py` guard matters

`database.py` raises a clear `ValueError` if `DATABASE_URL` is missing (line 20-23). Without the same guard in `env.py`, the call `config.set_main_option("sqlalchemy.url", None)` silently passes `None`, and SQLAlchemy raises an obscure internal error like `AttributeError: 'NoneType' object has no attribute 'split'` deep inside Alembic internals. The guard makes the failure fast and obvious.

### Files to modify

- `backend/tests/conftest.py` — line 21 only (one word change)
- `backend/migrations/env.py` — lines 30-32 (replace one line with three)

### Architecture Constraints

- Do NOT change anything else in `conftest.py` — the existing fixture chain (setup_db → db → client) is correct
- Do NOT add a `DATABASE_URL` guard to `database.py` — it already has one

### References

- [Source: code review findings P1 and P2 — Story 1.1]
- [Source: `backend/tests/conftest.py:21`]
- [Source: `backend/migrations/env.py:32`]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Applied during Story 1.1 code review session — changes were made directly before formal story execution.

### Completion Notes List

- ✅ `backend/tests/conftest.py`: `sqlite:///./test.db` → `sqlite:///:memory:` (AC1)
- ✅ `backend/migrations/env.py`: Added `DATABASE_URL` None guard before `config.set_main_option` (AC2)

### File List

- backend/tests/conftest.py
- backend/migrations/env.py
