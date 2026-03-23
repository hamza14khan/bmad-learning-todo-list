"""
Pydantic schemas — defines the shape of data going in and out of the API.

Pydantic v2 note:
- OLD syntax (v1): class Config: orm_mode = True
- NEW syntax (v2): model_config = ConfigDict(from_attributes=True)
  The 'from_attributes=True' setting lets Pydantic read data from
  SQLAlchemy model objects (not just plain dicts).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoResponse(BaseModel):
    """
    Shape of a todo item returned by the API.
    Fields match the database columns exactly (snake_case throughout).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    is_complete: bool
    created_at: datetime


class TodoCreate(BaseModel):
    """Shape of the request body when creating a new todo (used in Story 2.1)."""

    text: str = Field(min_length=1, max_length=200)


class TodoUpdate(BaseModel):
    """Shape of the request body when toggling a todo complete (used in Story 2.2)."""

    is_complete: bool
