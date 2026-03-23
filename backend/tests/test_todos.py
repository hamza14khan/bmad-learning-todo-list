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


class TestCreateTodo:
    """Tests for POST /api/v1/todos"""

    def test_create_todo_returns_201(self, client):
        """Successful creation returns 201 Created."""
        response = client.post("/api/v1/todos", json={"text": "Buy milk"})
        assert response.status_code == 201

    def test_create_todo_response_shape(self, client):
        """Response includes all required fields with correct values."""
        response = client.post("/api/v1/todos", json={"text": "Buy milk"})
        data = response.json()
        assert "id" in data
        assert data["text"] == "Buy milk"
        assert data["is_complete"] is False
        assert "created_at" in data

    def test_create_todo_persists(self, client):
        """Created todo is retrievable via GET."""
        client.post("/api/v1/todos", json={"text": "Buy milk"})
        response = client.get("/api/v1/todos")
        assert len(response.json()) == 1
        assert response.json()[0]["text"] == "Buy milk"

    def test_create_todo_empty_text_returns_422(self, client):
        """Empty text is rejected by Pydantic validation."""
        response = client.post("/api/v1/todos", json={"text": ""})
        assert response.status_code == 422

    def test_create_todo_too_long_text_returns_422(self, client):
        """Text exceeding 200 characters is rejected."""
        response = client.post("/api/v1/todos", json={"text": "x" * 201})
        assert response.status_code == 422


class TestToggleTodo:
    """Tests for PATCH /api/v1/todos/{id}"""

    def test_toggle_todo_returns_200(self, client, db):
        """Successful toggle returns 200."""
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo)
        db.commit()
        response = client.patch(f"/api/v1/todos/{todo.id}", json={"is_complete": True})
        assert response.status_code == 200

    def test_toggle_todo_marks_complete(self, client, db):
        """Toggle sets is_complete to true."""
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo)
        db.commit()
        response = client.patch(f"/api/v1/todos/{todo.id}", json={"is_complete": True})
        assert response.json()["is_complete"] is True

    def test_toggle_todo_marks_active(self, client, db):
        """Toggle sets is_complete back to false."""
        todo = Todo(text="Buy milk", is_complete=True, created_at=datetime.now(timezone.utc))
        db.add(todo)
        db.commit()
        response = client.patch(f"/api/v1/todos/{todo.id}", json={"is_complete": False})
        assert response.json()["is_complete"] is False

    def test_toggle_todo_response_contains_all_fields(self, client, db):
        """Response includes all TodoResponse fields."""
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo)
        db.commit()
        response = client.patch(f"/api/v1/todos/{todo.id}", json={"is_complete": True})
        data = response.json()
        assert "id" in data
        assert "text" in data
        assert "is_complete" in data
        assert "created_at" in data

    def test_toggle_todo_not_found_returns_404(self, client):
        """Non-existent todo id returns 404."""
        response = client.patch("/api/v1/todos/999", json={"is_complete": True})
        assert response.status_code == 404


class TestDeleteTodo:
    """Tests for DELETE /api/v1/todos/{id}"""

    def test_delete_todo_returns_204(self, client, db):
        """Successful delete returns 204 No Content."""
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo)
        db.commit()
        response = client.delete(f"/api/v1/todos/{todo.id}")
        assert response.status_code == 204

    def test_delete_todo_removes_from_db(self, client, db):
        """Deleted todo no longer appears in GET /todos."""
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo)
        db.commit()
        client.delete(f"/api/v1/todos/{todo.id}")
        response = client.get("/api/v1/todos")
        assert response.json() == []

    def test_delete_todo_not_found_returns_404(self, client):
        """Non-existent todo id returns 404."""
        response = client.delete("/api/v1/todos/999")
        assert response.status_code == 404

    def test_delete_todo_response_has_no_body(self, client, db):
        """204 response has an empty body."""
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo)
        db.commit()
        response = client.delete(f"/api/v1/todos/{todo.id}")
        assert response.content == b""

    def test_delete_todo_does_not_affect_other_todos(self, client, db):
        """Deleting one todo leaves others intact."""
        now = datetime.now(timezone.utc)
        todo1 = Todo(text="Keep this", is_complete=False, created_at=now)
        todo2 = Todo(text="Delete this", is_complete=False, created_at=now + timedelta(seconds=1))
        db.add(todo1)
        db.add(todo2)
        db.commit()
        client.delete(f"/api/v1/todos/{todo2.id}")
        response = client.get("/api/v1/todos")
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "Keep this"
