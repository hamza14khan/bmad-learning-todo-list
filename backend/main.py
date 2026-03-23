"""
FastAPI application entry point.

Responsibilities:
- Create the FastAPI app instance
- Configure CORS middleware (allows the React frontend to call this API)
- Register routers (groups of related routes)

Note: We do NOT call create_all() here.
Schema management is handled exclusively by Alembic migrations.
Run `alembic upgrade head` (or `make migrate`) to set up the database.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import todos

app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="REST API for the Todo App — FastAPI + PostgreSQL",
)

# CORS: allows the React frontend (running on a different port) to call this API.
# Without this, browsers block cross-origin requests as a security measure.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (default port)
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the todos router.
# The prefix "/api/v1" is prepended to all routes defined in routers/todos.py.
# So @router.get("/todos") becomes GET /api/v1/todos.
app.include_router(todos.router, prefix="/api/v1", tags=["todos"])
