# Todo App — Backend

FastAPI + PostgreSQL backend for the Todo App.

## Tech Stack

- **FastAPI** 0.115.x — Python web framework
- **SQLAlchemy** 2.x — ORM for database access
- **Alembic** — database migration tool
- **PostgreSQL** 16 — database
- **Pydantic** v2 — request/response validation
- **pytest** — testing

## Prerequisites

- Python 3.11+
- PostgreSQL 16 running locally **or** Docker + Docker Compose

## Setup — Docker (recommended)

```bash
# From the project root
make up       # starts db + backend containers
make migrate  # creates the todos table via Alembic
```

Verify it's working: open http://localhost:8000/docs

## Setup — Manual (without Docker)

```bash
# 1. Create and activate a virtual environment
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set DATABASE_URL to your local PostgreSQL instance

# 4. Run database migrations
alembic upgrade head

# 5. Start the development server
uvicorn main:app --reload
```

## API

| Method | Endpoint           | Description        |
|--------|--------------------|--------------------|
| GET    | /api/v1/todos      | List all todos     |

More endpoints added in Epic 2 (Stories 2.1–2.3).

Swagger UI: http://localhost:8000/docs

## Running Tests

```bash
# From the backend/ directory (with venv activated)
pytest --cov --cov-report=term-missing

# Or from project root
make test-be
```

Tests use an in-memory SQLite database — no PostgreSQL needed to run tests.

## Project Structure

```
backend/
├── main.py          # App entry point, CORS, router registration
├── database.py      # DB engine, session, Base class
├── models.py        # SQLAlchemy ORM models
├── schemas.py       # Pydantic request/response schemas
├── routers/
│   └── todos.py     # /api/v1/todos routes
├── migrations/
│   └── versions/    # Alembic migration files
├── tests/
│   ├── conftest.py  # pytest fixtures
│   └── test_todos.py
├── requirements.txt
├── Dockerfile
├── alembic.ini
├── .env             # gitignored — your local config
└── .env.example     # template — safe to commit
```

## Code Style

```bash
ruff check .        # lint
ruff format --check .  # format check
ruff check --fix .  # auto-fix
ruff format .       # auto-format
```
