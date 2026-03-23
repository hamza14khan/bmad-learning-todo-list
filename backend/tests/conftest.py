"""
pytest fixtures for backend tests.

Key decisions:
- Uses SQLite (in-memory) instead of PostgreSQL — no external service needed to run tests
- Each test gets a fresh database (setup_db fixture drops and recreates tables)
- FastAPI's dependency override swaps the real get_db for a test version that
  uses our test database instead of the production one
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# SQLite in-memory database for tests.
# StaticPool ensures all connections share the same in-memory database —
# without it, each engine.connect() call gets a separate empty DB.
# check_same_thread=False is required for SQLite when used with FastAPI's TestClient.
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    """
    Runs before every test: creates all tables.
    Runs after every test: drops all tables.
    autouse=True means this runs automatically — you don't need to add it to each test.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provides a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """
    Provides a FastAPI test client that uses the test database.

    app.dependency_overrides replaces get_db (the real DB dependency) with
    a version that uses our test SQLite database instead of PostgreSQL.
    This is cleaned up after each test with dependency_overrides.clear().
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass  # db fixture handles closing

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
