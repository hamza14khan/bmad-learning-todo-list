"""
Tests for GET /api/v1/todos endpoint (Story 1.1).

Test strategy:
- All tests use the TestClient fixture from conftest.py
- Database is reset before each test (autouse setup_db fixture)
- Tests insert data directly via the db fixture, then call the API to verify
"""

from datetime import datetime, timedelta, timezone

from models import Todo


class TestGetTodos:
    """Tests for GET /api/v1/todos"""

    def test_get_todos_returns_200(self, client):
        """Endpoint should always return 200, even when empty."""
        response = client.get("/api/v1/todos")
        assert response.status_code == 200

    def test_get_todos_empty_returns_empty_list(self, client):
        """Returns [] when no todos exist — not 404."""
        response = client.get("/api/v1/todos")
        assert response.json() == []

    def test_get_todos_returns_list_type(self, client):
        """Response body must be a JSON array."""
        response = client.get("/api/v1/todos")
        assert isinstance(response.json(), list)

    def test_get_todos_response_shape(self, client, db):
        """Each todo in the response has the required fields."""
        todo = Todo(
            text="Buy groceries",
            is_complete=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(todo)
        db.commit()

        response = client.get("/api/v1/todos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        item = data[0]
        assert "id" in item
        assert "text" in item
        assert "is_complete" in item
        assert "created_at" in item

    def test_get_todos_returns_correct_values(self, client, db):
        """Returned todo values match what was inserted."""
        todo = Todo(
            text="Write tests",
            is_complete=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(todo)
        db.commit()

        response = client.get("/api/v1/todos")
        data = response.json()
        assert data[0]["text"] == "Write tests"
        assert data[0]["is_complete"] is False

    def test_get_todos_sorted_by_created_at_ascending(self, client, db):
        """Todos are returned oldest first (created_at ASC)."""
        now = datetime.now(timezone.utc)
        older = Todo(
            text="Older todo", is_complete=False, created_at=now - timedelta(hours=1)
        )
        newer = Todo(text="Newer todo", is_complete=False, created_at=now)
        db.add(older)
        db.add(newer)
        db.commit()

        response = client.get("/api/v1/todos")
        data = response.json()
        assert len(data) == 2
        assert data[0]["text"] == "Older todo"
        assert data[1]["text"] == "Newer todo"

    def test_get_todos_returns_multiple_todos(self, client, db):
        """Returns all todos when multiple exist."""
        now = datetime.now(timezone.utc)
        for i in range(3):
            db.add(
                Todo(
                    text=f"Todo {i}",
                    is_complete=False,
                    created_at=now + timedelta(seconds=i),
                )
            )
        db.commit()

        response = client.get("/api/v1/todos")
        assert len(response.json()) == 3

    def test_get_todos_includes_completed_todos(self, client, db):
        """Returns both active and completed todos."""
        now = datetime.now(timezone.utc)
        db.add(Todo(text="Active", is_complete=False, created_at=now))
        db.add(
            Todo(text="Done", is_complete=True, created_at=now + timedelta(seconds=1))
        )
        db.commit()

        response = client.get("/api/v1/todos")
        data = response.json()
        assert len(data) == 2
        assert any(t["is_complete"] is True for t in data)
        assert any(t["is_complete"] is False for t in data)
