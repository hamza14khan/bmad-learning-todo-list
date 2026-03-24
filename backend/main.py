"""
FastAPI application entry point.

Responsibilities:
- Create the FastAPI app instance
- Configure security headers middleware
- Configure CORS middleware (allows the React frontend to call this API)
- Register routers (groups of related routes)
- Register custom exception handlers

Note: We do NOT call create_all() here.
Schema management is handled exclusively by Alembic migrations.
Run `alembic upgrade head` (or `make migrate`) to set up the database.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from routers import todos

app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="REST API for the Todo App — FastAPI + PostgreSQL",
)


# Security headers middleware — applied to every response.
# NOTE: These headers target API JSON responses. Do NOT apply this config to
# the frontend static file server — default-src 'none' would break the React app.
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS: allows the React frontend (running on a different port) to call this API.
# Without this, browsers block cross-origin requests as a security measure.
# - allow_headers: explicit allowlist — frontend only sends Content-Type
# - allow_methods: explicit allowlist — only methods the API actually uses
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (default port)
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# Custom 422 handler — returns a generic message instead of echoing submitted
# input values and internal schema details back to the client.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data."},
    )


# Register the todos router.
# The prefix "/api/v1" is prepended to all routes defined in routers/todos.py.
# So @router.get("/todos") becomes GET /api/v1/todos.
app.include_router(todos.router, prefix="/api/v1", tags=["todos"])
