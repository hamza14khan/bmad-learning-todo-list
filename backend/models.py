"""
SQLAlchemy ORM models — defines the structure of our database tables.

The Todo class maps directly to the 'todos' table in PostgreSQL.
SQLAlchemy 2.x uses Mapped[] type hints and mapped_column() for better
IDE support and type checking compared to the older style.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Todo(Base):
    """
    Represents a single todo item in the database.

    Table name: todos
    Columns:
        id          - auto-incrementing primary key
        text        - the todo description (max 200 chars)
        is_complete - whether the todo is done (defaults to False)
        created_at  - when the todo was created (auto-set to UTC now)
    """

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
