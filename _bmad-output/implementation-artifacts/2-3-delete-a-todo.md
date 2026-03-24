# Story 2.3: Delete a Todo

Status: done

## Story

As a **user**,
I want to delete a todo permanently,
so that I can remove tasks I no longer need.

## Acceptance Criteria

1. **Given** a todo exists in the list
   **When** the user clicks the delete action
   **Then** a DELETE /api/v1/todos/{id} request is sent to the backend
   **And** the todo is removed from the list immediately without a page reload
   **And** the UI update occurs within 300ms of the click

2. **Given** the deleted todo was the last item in the list
   **When** it is removed
   **Then** the app transitions to the empty state ("No todos yet. Add your first task!")

## Tasks / Subtasks

- [x] Task 1: Add DELETE /api/v1/todos/{id} backend endpoint (AC: 1, 2)
  - [x] Add `delete_todo` route to `backend/routers/todos.py` — raises 404 if not found, returns 204 No Content
  - [x] Add `TestDeleteTodo` class to `backend/tests/test_todos.py`
  - [x] Run `pytest` to confirm all backend tests pass

- [x] Task 2: Add `deleteTodo()` to frontend API client (AC: 1)
  - [x] Add `deleteTodo(id: number): Promise<void>` to `frontend/src/api/todos.ts`
  - [x] Uses `DELETE` method — no request body, no response body to parse (204)

- [x] Task 3: Add `useDeleteTodo()` React Query mutation hook (AC: 1, 2)
  - [x] Add `useDeleteTodo()` to `frontend/src/hooks/useTodos.ts`
  - [x] Uses `useMutation` with `mutationFn: (id: number) => deleteTodo(id)`
  - [x] On success: `queryClient.invalidateQueries({ queryKey: ['todos'] })`

- [x] Task 4: Add delete button to `TodoItem` component (AC: 1, 2)
  - [x] Modify `frontend/src/components/TodoItem/TodoItem.tsx` — add delete button
  - [x] Button calls `useDeleteTodo` with `todo.id` on click
  - [x] `aria-label="Delete todo"` on the delete button
  - [x] Add delete button styles to `frontend/src/components/TodoItem/TodoItem.module.css`

- [x] Task 5: Update `TodoItem` tests (AC: 1, 2)
  - [x] Update `frontend/src/components/TodoItem/TodoItem.test.tsx`
  - [x] Mock `useDeleteTodo` in `beforeEach` alongside existing `useToggleTodo` mock
  - [x] Test: delete button is present in the rendered output
  - [x] Test: clicking delete button calls mutate with the todo's id
  - [x] Run `npm run test:coverage` — confirm ≥70% threshold passes

- [ ] Task 6: Manual verification — requires all services running
  - [ ] Run `make up` then `make migrate`
  - [ ] Create two todos, delete one — confirm it disappears immediately
  - [ ] Delete the last todo — confirm empty state appears

## Dev Notes

### What exists from Stories 2.1 / 2.2

- `backend/schemas.py`: `TodoResponse`, `TodoCreate`, `TodoUpdate` — do NOT modify
- `backend/routers/todos.py`: GET + POST + PATCH endpoints exist — add DELETE after them
- `frontend/src/api/todos.ts`: `getTodos`, `createTodo`, `toggleTodo` exist — add `deleteTodo` here
- `frontend/src/hooks/useTodos.ts`: `useGetTodos`, `useCreateTodo`, `useToggleTodo` exist — add `useDeleteTodo` here
- `frontend/src/components/TodoItem/TodoItem.tsx`: renders toggle button and text — add delete button here
- `TodoList.tsx` already handles empty state when `todos.length === 0` — no changes needed after delete; React Query refetch covers it automatically
- `TodoList.test.tsx` already mocks `useToggleTodo` — after this story it must also mock `useDeleteTodo`

### Backend: DELETE /todos/{id} endpoint

```python
# Add to backend/routers/todos.py
from fastapi import APIRouter, Depends, HTTPException, Response

@router.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: DbDep) -> None:
    """
    Permanently delete a todo.

    Returns 204 No Content on success.
    Returns 404 if todo_id does not exist.
    FastAPI returns an empty body for 204 — no return value needed.
    """
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
```

**Important:** `Response` import may be needed for 204 — but FastAPI handles it automatically with `status_code=204` and `-> None`. No `return Response(status_code=204)` needed.

### Backend Tests: `TestDeleteTodo`

```python
class TestDeleteTodo:
    """Tests for DELETE /api/v1/todos/{id}"""

    def test_delete_todo_returns_204(self, client, db):
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo); db.commit()
        response = client.delete(f"/api/v1/todos/{todo.id}")
        assert response.status_code == 204

    def test_delete_todo_removes_from_db(self, client, db):
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo); db.commit()
        client.delete(f"/api/v1/todos/{todo.id}")
        response = client.get("/api/v1/todos")
        assert response.json() == []

    def test_delete_todo_not_found_returns_404(self, client):
        response = client.delete("/api/v1/todos/999")
        assert response.status_code == 404

    def test_delete_todo_response_has_no_body(self, client, db):
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo); db.commit()
        response = client.delete(f"/api/v1/todos/{todo.id}")
        assert response.content == b""

    def test_delete_todo_does_not_affect_other_todos(self, client, db):
        now = datetime.now(timezone.utc)
        todo1 = Todo(text="Keep this", is_complete=False, created_at=now)
        todo2 = Todo(text="Delete this", is_complete=False, created_at=now + timedelta(seconds=1))
        db.add(todo1); db.add(todo2); db.commit()
        client.delete(f"/api/v1/todos/{todo2.id}")
        response = client.get("/api/v1/todos")
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "Keep this"
```

### Frontend: `deleteTodo()` in `api/todos.ts`

```ts
export async function deleteTodo(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/todos/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`Failed to delete todo: ${response.status}`)
  }
  // No response body — 204 No Content
}
```

**Do NOT call `response.json()` on a 204 response — it will throw a parse error.**

### Frontend: `useDeleteTodo()` in `hooks/useTodos.ts`

```ts
export function useDeleteTodo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteTodo(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

### Frontend: Updated `TodoItem.tsx`

```tsx
import { useToggleTodo, useDeleteTodo } from '../../hooks/useTodos'
import type { Todo } from '../../types/todo'
import styles from './TodoItem.module.css'

interface Props {
  todo: Todo
}

export function TodoItem({ todo }: Props) {
  const { mutate: toggleTodo } = useToggleTodo()
  const { mutate: deleteTodo } = useDeleteTodo()

  return (
    <li className={styles.item}>
      <button
        className={styles.toggle}
        onClick={() => toggleTodo({ id: todo.id, is_complete: !todo.is_complete })}
        aria-label={todo.is_complete ? 'Mark as active' : 'Mark as complete'}
      >
        {todo.is_complete ? '✓' : '○'}
      </button>
      <span className={`${styles.text} ${todo.is_complete ? styles.completed : ''}`}>
        {todo.text}
      </span>
      <button
        className={styles.delete}
        onClick={() => deleteTodo(todo.id)}
        aria-label="Delete todo"
      >
        ✕
      </button>
    </li>
  )
}
```

**CSS additions for delete button:**
```css
.delete {
  background: none;
  border: none;
  cursor: pointer;
  color: #ccc;
  font-size: 1rem;
  padding: 0 0.25rem;
  transition: color 0.2s;
}

.delete:hover {
  color: #e74c3c;
}
```

### Frontend: Updated `TodoItem.test.tsx` — mock pattern

Both `useToggleTodo` AND `useDeleteTodo` must be mocked since `TodoItem` now calls both:

```tsx
import * as useTodosModule from '../../hooks/useTodos'

const mockToggle = vi.fn()
const mockDelete = vi.fn()

beforeEach(() => {
  mockToggle.mockReset()
  mockDelete.mockReset()
  vi.spyOn(useTodosModule, 'useToggleTodo').mockReturnValue({
    mutate: mockToggle,
    isPending: false,
  } as any)
  vi.spyOn(useTodosModule, 'useDeleteTodo').mockReturnValue({
    mutate: mockDelete,
    isPending: false,
  } as any)
})
```

**New tests to add:**
```tsx
it('renders a delete button', () => {
  render(<TodoItem todo={activeTodo} />)
  expect(screen.getByRole('button', { name: /delete todo/i })).toBeInTheDocument()
})

it('clicking delete calls mutate with the todo id', async () => {
  render(<TodoItem todo={activeTodo} />)
  await userEvent.click(screen.getByRole('button', { name: /delete todo/i }))
  expect(mockDelete).toHaveBeenCalledWith(1)
})
```

**Existing toggle tests still work** — they query the toggle button by `aria-label` (`/mark as active/i` or `getByRole('button')` needs updating if there are now two buttons). Use `{ name: /mark as/i }` to be specific:

```tsx
it('clicking toggle on active todo calls mutate with is_complete: true', async () => {
  render(<TodoItem todo={activeTodo} />)
  await userEvent.click(screen.getByRole('button', { name: /mark as complete/i }))
  expect(mockToggle).toHaveBeenCalledWith({ id: 1, is_complete: true })
})
```

**Important:** `screen.getByRole('button')` was used in existing tests. With two buttons now present, this will throw "found multiple elements". Update all existing toggle tests to use `{ name: /mark as/i }` selector.

### `TodoList.test.tsx` must also mock `useDeleteTodo`

Since `TodoList` renders `TodoItem` which now calls `useDeleteTodo`, add it to the existing mock:

```tsx
beforeEach(() => {
  vi.spyOn(useTodosModule, 'useToggleTodo').mockReturnValue({
    mutate: vi.fn(), isPending: false,
  } as any)
  vi.spyOn(useTodosModule, 'useDeleteTodo').mockReturnValue({
    mutate: vi.fn(), isPending: false,
  } as any)
})
```

### Architecture Constraints

- **DELETE → 204 No Content** (not 200) — architecture doc specifies this status code
- **204 body is empty** — never call `response.json()` on a 204, it throws
- **No confirmation dialog** — ACs say "single click" — no "are you sure?" prompt
- **React Query handles empty state** — after delete, `invalidateQueries(['todos'])` triggers a refetch; if the list is now empty, `TodoList` renders the empty state automatically — no extra code needed
- **`aria-label="Delete todo"` required** — for accessibility (WCAG 2.1 AA, Story 3.2 builds on this)
- **`screen.getByRole('button')` breaks** with two buttons — existing toggle tests must be updated to use named queries like `getByRole('button', { name: /mark as complete/i })`
- **Hook naming pattern** — `useDeleteTodo` (matches `useCreateTodo`, `useToggleTodo`)
- **Route through `src/api/`** — never call `fetch` directly inside `TodoItem`
- **`src/api/**` and `src/hooks/**` excluded from coverage** — added in Story 2.1 `vitest.config.ts`

### What NOT to implement in this story

- Undo/restore after delete — not in PRD
- Confirmation modal — ACs say single click, no dialog
- Batch delete / select-all — deferred to post-MVP
- Any change to `AddTodoForm` or `ErrorMessage` — not affected by this story

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Story 2.3 ACs]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — HTTP 204, anti-patterns, component boundary]
- [Source: `backend/routers/todos.py` — existing GET/POST/PATCH patterns to follow]
- [Source: `backend/tests/test_todos.py` — TestToggleTodo class for test structure]
- [Source: `frontend/src/components/TodoItem/TodoItem.tsx` — current component to extend]
- [Source: `frontend/src/components/TodoItem/TodoItem.test.tsx` — existing mock approach, tests to update]
- [Source: `frontend/src/components/TodoList/TodoList.test.tsx` — must add useDeleteTodo mock]
- [Source: PRD — FR-04, NFR-01]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- All 23 backend tests pass (5 new TestDeleteTodo tests)
- All 20 frontend tests pass, 100% coverage
- `TodoItem.test.tsx` toggle tests updated to use named button queries (`{ name: /mark as complete/i }`) since two buttons now exist
- `TodoList.test.tsx` updated to also mock `useDeleteTodo`

### File List

- `backend/routers/todos.py` — added DELETE endpoint
- `backend/tests/test_todos.py` — added TestDeleteTodo class (5 tests)
- `frontend/src/api/todos.ts` — added deleteTodo()
- `frontend/src/hooks/useTodos.ts` — added useDeleteTodo()
- `frontend/src/components/TodoItem/TodoItem.tsx` — added delete button
- `frontend/src/components/TodoItem/TodoItem.module.css` — added delete button styles
- `frontend/src/components/TodoItem/TodoItem.test.tsx` — added useDeleteTodo mock + 2 new tests, updated toggle tests to use named queries
- `frontend/src/components/TodoList/TodoList.test.tsx` — added useDeleteTodo mock
