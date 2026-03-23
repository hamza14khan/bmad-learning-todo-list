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

from fastapi import APIRouter, Depends, HTTPException, Response
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


@router.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo_in: schemas.TodoCreate, db: DbDep) -> models.Todo:
    """
    Create a new todo.

    Pydantic validates todo_in.text (min_length=1, max_length=200) automatically.
    FastAPI returns 422 if validation fails — no manual checks needed here.
    db.refresh(todo) is required to populate auto-generated id and created_at
    after the INSERT is committed.
    """
    todo = models.Todo(text=todo_in.text)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.patch("/todos/{todo_id}", response_model=schemas.TodoResponse)
def toggle_todo(todo_id: int, todo_in: schemas.TodoUpdate, db: DbDep) -> models.Todo:
    """
    Toggle a todo's is_complete status.

    Returns 404 if todo_id does not exist.
    db.refresh(todo) re-reads the row after commit so the response
    reflects exactly what was persisted.
    """
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.is_complete = todo_in.is_complete
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: DbDep) -> None:
    """
    Permanently delete a todo.

    Returns 204 No Content on success — no response body.
    Returns 404 if todo_id does not exist.
    """
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
