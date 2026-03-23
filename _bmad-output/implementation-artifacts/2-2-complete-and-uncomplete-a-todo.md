# Story 2.2: Complete and Uncomplete a Todo

Status: review

## Story

As a **user**,
I want to toggle a todo between active and complete,
so that I can track which tasks I've finished.

## Acceptance Criteria

1. **Given** an active todo is displayed in the list
   **When** the user clicks the complete action
   **Then** a PATCH /api/v1/todos/{id} request updates `is_complete` to true
   **And** the todo immediately displays with strikethrough text and a muted visual style
   **And** the UI update occurs within 300ms of the click

2. **Given** a completed todo is displayed
   **When** the user clicks the complete action again
   **Then** a PATCH /api/v1/todos/{id} request updates `is_complete` to false
   **And** the todo reverts to active styling immediately

## Tasks / Subtasks

- [x] Task 1: Add PATCH /api/v1/todos/{id} backend endpoint (AC: 1, 2)
  - [x] Add `toggle_todo` route to `backend/routers/todos.py` — accepts `TodoUpdate` body (`is_complete: bool`), returns `TodoResponse` 200, raises 404 if not found
  - [x] Add `TestToggleTodo` class to `backend/tests/test_todos.py`
  - [x] Run `pytest` to confirm all backend tests pass

- [x] Task 2: Add `toggleTodo()` to frontend API client (AC: 1, 2)
  - [x] Add `toggleTodo(id: number, is_complete: boolean): Promise<Todo>` to `frontend/src/api/todos.ts`
  - [x] Uses `PATCH` with `Content-Type: application/json` and `{ is_complete }` body

- [x] Task 3: Add `useToggleTodo()` React Query mutation hook (AC: 1, 2)
  - [x] Add `useToggleTodo()` to `frontend/src/hooks/useTodos.ts`
  - [x] Uses `useMutation` with `mutationFn: ({ id, is_complete }) => toggleTodo(id, is_complete)`
  - [x] On success: `queryClient.invalidateQueries({ queryKey: ['todos'] })`

- [x] Task 4: Build `TodoItem` component (AC: 1, 2)
  - [x] Create `frontend/src/components/TodoItem/TodoItem.tsx`
  - [x] Create `frontend/src/components/TodoItem/TodoItem.module.css`
  - [x] Renders todo text + a toggle button
  - [x] Completed todo: strikethrough text + muted style (CSS class on `is_complete`)
  - [x] On toggle click: calls `useToggleTodo` with `{ id: todo.id, is_complete: !todo.is_complete }`

- [x] Task 5: Update `TodoList` to render `TodoItem` (AC: 1, 2)
  - [x] Modify `frontend/src/components/TodoList/TodoList.tsx` — replace raw `<li>` with `<TodoItem todo={todo} />`
  - [x] Update `frontend/src/components/TodoList/TodoList.test.tsx` — mock `useToggleTodo` (it's called inside TodoItem which TodoList now renders)

- [x] Task 6: Write `TodoItem` tests (AC: 1, 2)
  - [x] Create `frontend/src/components/TodoItem/TodoItem.test.tsx`
  - [x] Test: renders todo text
  - [x] Test: clicking toggle calls mutate with `is_complete: true` for active todo
  - [x] Test: clicking toggle calls mutate with `is_complete: false` for completed todo
  - [x] Test: completed todo has completed CSS class on text span
  - [x] Run `npm run test:coverage` — confirm ≥70% threshold passes

- [ ] Task 7: Manual verification — requires all services running
  - [ ] Run `make up` then `make migrate`
  - [ ] Create a todo, click the toggle — confirm strikethrough appears immediately
  - [ ] Click toggle again — confirm active styling returns

## Dev Notes

### What exists from Stories 2.1 / Epic 1

- `backend/schemas.py`: `TodoUpdate` already defined as `is_complete: bool` — do NOT recreate it
- `backend/routers/todos.py`: GET + POST endpoints exist — add PATCH after them
- `frontend/src/api/todos.ts`: `getTodos` + `createTodo` exist — add `toggleTodo` here
- `frontend/src/hooks/useTodos.ts`: `useGetTodos` + `useCreateTodo` exist — add `useToggleTodo` here
- `TodoList.tsx` currently renders raw `<li>{todo.text}</li>` — replace with `<TodoItem>`
- Component subfolder pattern: `components/TodoItem/TodoItem.tsx` + `.module.css` + `.test.tsx`
- **`TodoList.test.tsx` must mock `useToggleTodo`** — after this story, `TodoList` renders `TodoItem` which calls that hook internally

### Backend: PATCH /todos/{id} endpoint

```python
# Add to backend/routers/todos.py (needs HTTPException import)
from fastapi import APIRouter, Depends, HTTPException

@router.patch("/todos/{todo_id}", response_model=schemas.TodoResponse)
def toggle_todo(todo_id: int, todo_in: schemas.TodoUpdate, db: DbDep) -> models.Todo:
    """
    Toggle a todo's is_complete status.

    Returns 404 if the todo_id does not exist.
    db.refresh(todo) re-reads the row so the response reflects what's in the DB.
    """
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.is_complete = todo_in.is_complete
    db.commit()
    db.refresh(todo)
    return todo
```

### Backend Tests: `TestToggleTodo`

```python
class TestToggleTodo:
    """Tests for PATCH /api/v1/todos/{id}"""

    def test_toggle_todo_returns_200(self, client, db):
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo); db.commit()
        response = client.patch(f"/api/v1/todos/{todo.id}", json={"is_complete": True})
        assert response.status_code == 200

    def test_toggle_todo_marks_complete(self, client, db):
        todo = Todo(text="Buy milk", is_complete=False, created_at=datetime.now(timezone.utc))
        db.add(todo); db.commit()
        response = client.patch(f"/api/v1/todos/{todo.id}", json={"is_complete": True})
        assert response.json()["is_complete"] is True

    def test_toggle_todo_marks_active(self, client, db):
        todo = Todo(text="Buy milk", is_complete=True, created_at=datetime.now(timezone.utc))
        db.add(todo); db.commit()
        response = client.patch(f"/api/v1/todos/{todo.id}", json={"is_complete": False})
        assert response.json()["is_complete"] is False

    def test_toggle_todo_not_found_returns_404(self, client):
        response = client.patch("/api/v1/todos/999", json={"is_complete": True})
        assert response.status_code == 404
```

### Frontend: `toggleTodo()` in `api/todos.ts`

```ts
export async function toggleTodo(id: number, is_complete: boolean): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/v1/todos/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_complete }),
  })
  if (!response.ok) {
    throw new Error(`Failed to update todo: ${response.status}`)
  }
  return response.json()
}
```

### Frontend: `useToggleTodo()` in `hooks/useTodos.ts`

```ts
export function useToggleTodo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, is_complete }: { id: number; is_complete: boolean }) =>
      toggleTodo(id, is_complete),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

### Frontend: `TodoItem` component

```tsx
// frontend/src/components/TodoItem/TodoItem.tsx
import { useToggleTodo } from '../../hooks/useTodos'
import type { Todo } from '../../types/todo'
import styles from './TodoItem.module.css'

interface Props {
  todo: Todo
}

export function TodoItem({ todo }: Props) {
  const { mutate: toggleTodo } = useToggleTodo()

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
    </li>
  )
}
```

**CSS — completed style must include strikethrough:**
```css
.completed {
  text-decoration: line-through;
  color: #999;
}
```

### Frontend: Updated `TodoList.tsx`

```tsx
// Replace the <li> block with:
import { TodoItem } from '../TodoItem/TodoItem'

// In the return:
<ul className={styles.list}>
  {todos.map(todo => (
    <TodoItem key={todo.id} todo={todo} />
  ))}
</ul>
```

Note: `key` moves from `<li>` to `<TodoItem>` — `TodoItem` renders the `<li>` internally.

### Frontend: Updated `TodoList.test.tsx`

Add mock for `useToggleTodo` since `TodoList` now renders `TodoItem` which calls it:

```tsx
import * as useTodosModule from '../../hooks/useTodos'

beforeEach(() => {
  vi.spyOn(useTodosModule, 'useToggleTodo').mockReturnValue({
    mutate: vi.fn(),
    isPending: false,
  } as any)
})
```

Existing tests (`shows loading spinner`, `renders todo items when data is loaded`, `shows empty state message`) do not need to change — they test `TodoList` behaviour, not `TodoItem` internals.

### Frontend: `TodoItem.test.tsx` — test approach

```tsx
import * as useTodosModule from '../../hooks/useTodos'

const mockToggle = vi.fn()
beforeEach(() => {
  mockToggle.mockReset()
  vi.spyOn(useTodosModule, 'useToggleTodo').mockReturnValue({
    mutate: mockToggle,
    isPending: false,
  } as any)
})

const activeTodo = { id: 1, text: 'Buy milk', is_complete: false, created_at: '2026-03-23T10:00:00Z' }
const completedTodo = { id: 2, text: 'Walk dog', is_complete: true, created_at: '2026-03-23T11:00:00Z' }

describe('TodoItem', () => {
  it('renders todo text', () => { ... })
  it('clicking toggle on active todo calls mutate with is_complete: true', () => { ... })
  it('clicking toggle on completed todo calls mutate with is_complete: false', () => { ... })
  it('completed todo text has completed CSS class', () => { ... })
})
```

### Architecture Constraints

- **PATCH → 200 OK** (not 204) — returns updated `TodoResponse` so frontend can sync state
- **404 for unknown id** — `raise HTTPException(status_code=404, detail="Todo not found")`
- **`HTTPException` import** — add to `from fastapi import APIRouter, Depends, HTTPException`
- **`key` prop on `<TodoItem>`** — not on internal `<li>` — React requires it on the outermost element in a map
- **No `fetch` in `TodoItem`** — all API calls through `src/api/todos.ts` via hook
- **`useToggleTodo` mock required in `TodoList.test.tsx`** — without it, React complains about missing QueryClientProvider
- **`snake_case` in API body** — `{ is_complete: true }` not `{ isComplete: true }` — matches Pydantic model
- **70% coverage threshold** — `npm run test:coverage` must pass

### What NOT to implement in this story

- Delete button on `TodoItem` — Story 2.3
- Visual distinction beyond strikethrough/muted — no icons, badges, or animations (deferred to Epic 3)
- Error state on toggle failure — deferred; React Query surfaces it via `isError` if needed later

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Story 2.2 ACs]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — HTTP Status Codes, React Query Key Conventions, Component Boundary, Anti-Patterns]
- [Source: `backend/schemas.py` — `TodoUpdate` already defined]
- [Source: `backend/routers/todos.py` — existing GET/POST patterns]
- [Source: `backend/tests/test_todos.py` — `TestCreateTodo` class for test structure]
- [Source: `_bmad-output/implementation-artifacts/2-1-create-a-todo.md` — mock pattern for hooks in tests, vitest coverage exclude]
- [Source: PRD — FR-03, FR-06, NFR-01]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `expect.anything()` removed from `TodoItem.test.tsx` toggle tests — component calls `mutate({ id, is_complete })` with one arg; test was incorrectly expecting a second argument

### Completion Notes List

- All 18 frontend tests pass, 100% coverage
- All backend tests pass

### File List

- `backend/routers/todos.py` — added PATCH endpoint
- `backend/tests/test_todos.py` — added TestToggleTodo class
- `frontend/src/api/todos.ts` — added toggleTodo()
- `frontend/src/hooks/useTodos.ts` — added useToggleTodo()
- `frontend/src/components/TodoItem/TodoItem.tsx` — new
- `frontend/src/components/TodoItem/TodoItem.module.css` — new
- `frontend/src/components/TodoItem/TodoItem.test.tsx` — new
- `frontend/src/components/TodoList/TodoList.tsx` — updated to render TodoItem
- `frontend/src/components/TodoList/TodoList.test.tsx` — added useToggleTodo mock
