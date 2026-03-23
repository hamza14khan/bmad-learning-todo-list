"""
Todo API routes — all endpoints for /api/v1/todos.

The prefix /api/v1 is added in main.py when this router is registered,
so routes here use /todos (not /api/v1/todos).

FastAPI's Depends(get_db) automatically:
1. Creates a database session before the route runs
2. Injects it as the 'db' parameter
3. Closes the session after the response is sent
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter()

# Type alias to avoid repeating the full Depends() expression in every route
DbDep = Annotated[Session, Depends(get_db)]


@router.get("/todos", response_model=list[schemas.TodoResponse])
def get_todos(db: DbDep) -> list[models.Todo]:
    """
    Return all todos sorted by creation time (oldest first).

    Returns an empty list [] when no todos exist — never a 404.
    The response_model=list[schemas.TodoResponse] tells FastAPI how to
    serialise the SQLAlchemy objects into JSON.
    """
    return db.query(models.Todo).order_by(models.Todo.created_at.asc()).all()
