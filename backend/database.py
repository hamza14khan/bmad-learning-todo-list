"""
Database connection setup using SQLAlchemy 2.x.

Key concepts:
- engine: the actual connection to PostgreSQL
- SessionLocal: a factory that creates database sessions (one per request)
- Base: parent class for all SQLAlchemy models
- get_db: a dependency FastAPI uses to inject a DB session into route handlers
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()  # reads the .env file in the backend/ directory

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. Check your .env file."
    )

engine = create_engine(DATABASE_URL)

# autocommit=False: we control when transactions are committed
# autoflush=False: we control when changes are flushed to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this class."""

    pass


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    Usage in a route:
        @router.get("/todos")
        def get_todos(db: Session = Depends(get_db)):
            ...

    FastAPI calls this automatically — you never call get_db() yourself.
    The 'yield' means FastAPI runs the cleanup (db.close()) after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
