# Todo App

A full-stack todo application — React frontend + FastAPI backend + PostgreSQL database + BMAD SDD.

## Services

| Service  | URL                        | Description           |
| -------- | -------------------------- | --------------------- |
| Backend  | http://localhost:8000      | FastAPI REST API      |
| API Docs | http://localhost:8000/docs | Swagger UI            |
| Frontend | http://localhost:5173      | React app (Story 1.2) |
| Database | localhost:5432             | PostgreSQL            |

## Quick Start (Docker — recommended)

```bash
# 1. Start all services
make up

# 2. In a new terminal, run database migrations
make migrate

# 3. Open http://localhost:8000/docs to verify the API is running
```

## Service Setup Guides

- [Backend Setup](./backend/README.md)
- [Frontend Setup](./frontend//README.md)

## Available Commands

```bash
make up          # Start all services
make up-build    # Rebuild and start (after changing dependencies)
make down        # Stop all services
make logs        # Tail service logs
make migrate     # Run pending database migrations
make migration msg="your message"  # Generate a new migration
make test-be     # Run backend tests with coverage
make lint        # Check code style
make lint-fix    # Auto-fix code style issues
```
