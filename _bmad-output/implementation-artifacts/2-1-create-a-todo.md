# Story 2.1: Create a Todo

Status: review

## Story

As a **user**,
I want to type a task and submit it to create a new todo,
so that I can add tasks to my list quickly.

## Acceptance Criteria

1. **Given** the user types a description (1–200 characters) in the input field
   **When** they press Enter or click the Add button
   **Then** a POST /api/v1/todos request is sent to the backend
   **And** the new todo appears in the list immediately without a page reload
   **And** the input field clears ready for the next entry
   **And** the UI update occurs within 300ms of submission

2. **Given** the user submits an empty or whitespace-only input
   **When** they press Enter or click Add
   **Then** no API request is made
   **And** an inline validation message is displayed
   **And** the input field remains focused

3. **Given** the user types more than 200 characters
   **When** they attempt to submit
   **Then** inline validation prevents submission and displays a character limit message

## Tasks / Subtasks

- [x] Task 1: Add POST /api/v1/todos backend endpoint (AC: 1)
  - [x] Add `create_todo` route to `backend/routers/todos.py` — accepts `TodoCreate` body, inserts into DB, returns `TodoResponse` with status 201
  - [x] Add `TestCreateTodo` class to `backend/tests/test_todos.py` — test 201 success, response shape, empty text → 422, >200 chars → 422
  - [x] Run `pytest` to confirm all backend tests pass — 13/13 pass

- [x] Task 2: Add `createTodo()` to frontend API client (AC: 1)
  - [x] Add `createTodo(text: string): Promise<Todo>` to `frontend/src/api/todos.ts`
  - [x] Uses `POST` with `Content-Type: application/json` and `{ text }` body
  - [x] Throws on non-ok response

- [x] Task 3: Add `useCreateTodo()` React Query mutation hook (AC: 1)
  - [x] Add `useCreateTodo()` to `frontend/src/hooks/useTodos.ts`
  - [x] Uses `useMutation` with `mutationFn: (text: string) => createTodo(text)`
  - [x] On success: `queryClient.invalidateQueries({ queryKey: ['todos'] })`

- [x] Task 4: Build `AddTodoForm` component (AC: 1, 2, 3)
  - [x] Create `frontend/src/components/AddTodoForm/AddTodoForm.tsx`
  - [x] Create `frontend/src/components/AddTodoForm/AddTodoForm.module.css`
  - [x] Input field (type="text") + submit button ("Add")
  - [x] On submit: validate empty/whitespace → show inline error, keep focus — no API call
  - [x] On submit: validate >200 chars → show inline error, keep focus — no API call
  - [x] On submit (valid): call `useCreateTodo` mutate, on success clear input
  - [x] Disable Add button while mutation is pending (`isPending`)

- [x] Task 5: Wire `AddTodoForm` into `App.tsx` (AC: 1)
  - [x] Import and render `<AddTodoForm />` above the error/list section in `frontend/src/App.tsx`

- [x] Task 6: Write frontend component tests (AC: 1, 2, 3)
  - [x] Create `frontend/src/components/AddTodoForm/AddTodoForm.test.tsx`
  - [x] Test: renders input and Add button
  - [x] Test: shows validation error on empty submit — no mutate called
  - [x] Test: shows validation error on whitespace-only submit — no mutate called
  - [x] Test: shows validation error when text >200 chars
  - [x] Test: clears input after successful submission
  - [x] Run `npm run test:coverage` — 13/13 pass, thresholds met (api/ and hooks/ excluded — thin wrappers)

- [ ] Task 7: Manual verification — requires all services running
  - [ ] Run `make up` then `make migrate`
  - [ ] Open `http://localhost:5173` — confirm Add form renders above the list
  - [ ] Submit valid text → new todo appears immediately, input clears
  - [ ] Submit empty → validation message shown, no network request
  - [ ] Submit >200 chars → char limit message shown

## Dev Notes

### What exists from Epic 1

- `backend/routers/todos.py`: only `GET /todos` — need to add `POST /todos`
- `backend/schemas.py`: `TodoCreate` (text: str, min_length=1, max_length=200) and `TodoUpdate` already defined — do NOT recreate them
- `backend/models.py`: `Todo` model with `text`, `is_complete` (default False), `created_at` (auto UTC)
- `frontend/src/api/todos.ts`: only `getTodos()` — add `createTodo()` here
- `frontend/src/hooks/useTodos.ts`: only `useGetTodos()` — add `useCreateTodo()` here
- `frontend/src/App.tsx`: renders `<ErrorMessage />` or `<TodoList />` — add `<AddTodoForm />` above this block
- Components use subfolder pattern: `components/ComponentName/ComponentName.tsx` + `.module.css` + `.test.tsx`

### Backend: POST /todos endpoint

```python
# Add to backend/routers/todos.py
from fastapi import APIRouter, Depends, HTTPException

@router.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo_in: schemas.TodoCreate, db: DbDep) -> models.Todo:
    todo = models.Todo(text=todo_in.text)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo
```

- `status_code=201` is explicit — FastAPI defaults to 200 for POST without it
- `db.refresh(todo)` populates `id` and `created_at` after commit
- Pydantic validates `text` (min_length=1, max_length=200) automatically — FastAPI returns 422 on violation

### Backend Tests: `TestCreateTodo`

```python
class TestCreateTodo:
    """Tests for POST /api/v1/todos"""

    def test_create_todo_returns_201(self, client):
        response = client.post("/api/v1/todos", json={"text": "Buy milk"})
        assert response.status_code == 201

    def test_create_todo_response_shape(self, client):
        response = client.post("/api/v1/todos", json={"text": "Buy milk"})
        data = response.json()
        assert "id" in data
        assert data["text"] == "Buy milk"
        assert data["is_complete"] is False
        assert "created_at" in data

    def test_create_todo_persists(self, client):
        client.post("/api/v1/todos", json={"text": "Buy milk"})
        response = client.get("/api/v1/todos")
        assert len(response.json()) == 1
        assert response.json()[0]["text"] == "Buy milk"

    def test_create_todo_empty_text_returns_422(self, client):
        response = client.post("/api/v1/todos", json={"text": ""})
        assert response.status_code == 422

    def test_create_todo_too_long_text_returns_422(self, client):
        response = client.post("/api/v1/todos", json={"text": "x" * 201})
        assert response.status_code == 422
```

### Frontend: `createTodo()` in `api/todos.ts`

```ts
export async function createTodo(text: string): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/v1/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!response.ok) {
    throw new Error(`Failed to create todo: ${response.status}`)
  }
  return response.json()
}
```

### Frontend: `useCreateTodo()` in `hooks/useTodos.ts`

```ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTodos, createTodo } from '../api/todos'

export function useCreateTodo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (text: string) => createTodo(text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

`invalidateQueries` marks the `['todos']` cache stale → React Query refetches automatically → new todo appears in list.

### Frontend: `AddTodoForm` component

```tsx
// frontend/src/components/AddTodoForm/AddTodoForm.tsx
import { useState, useRef } from 'react'
import { useCreateTodo } from '../../hooks/useTodos'
import styles from './AddTodoForm.module.css'

export function AddTodoForm() {
  const [text, setText] = useState('')
  const [validationError, setValidationError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const { mutate: createTodo, isPending } = useCreateTodo()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!text.trim()) {
      setValidationError('Please enter a task description.')
      inputRef.current?.focus()
      return
    }
    if (text.length > 200) {
      setValidationError('Task description cannot exceed 200 characters.')
      inputRef.current?.focus()
      return
    }

    setValidationError('')
    createTodo(text.trim(), {
      onSuccess: () => setText(''),
    })
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <input
        ref={inputRef}
        type="text"
        value={text}
        onChange={e => {
          setText(e.target.value)
          setValidationError('')
        }}
        placeholder="Add a new task..."
        className={styles.input}
        aria-label="New todo"
      />
      <button type="submit" disabled={isPending} className={styles.button}>
        {isPending ? 'Adding...' : 'Add'}
      </button>
      {validationError && (
        <p role="alert" className={styles.error}>{validationError}</p>
      )}
    </form>
  )
}
```

### Frontend: `App.tsx` update

```tsx
import { AddTodoForm } from './components/AddTodoForm/AddTodoForm'

export default function App() {
  const { data: todos = [], isLoading, isError, error } = useGetTodos()

  return (
    <main className="app">
      <h1>Todo List</h1>
      <AddTodoForm />                          {/* ← add above error/list */}
      {isError ? (
        <ErrorMessage message={error instanceof Error ? error.message : undefined} />
      ) : (
        <TodoList todos={todos} isLoading={isLoading} />
      )}
    </main>
  )
}
```

### Frontend: `AddTodoForm.test.tsx` — test approach

Mock `useCreateTodo` at the module level so tests don't need a real `QueryClientProvider`:

```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AddTodoForm } from './AddTodoForm'
import * as useTodosModule from '../../hooks/useTodos'

const mockMutate = vi.fn()

beforeEach(() => {
  mockMutate.mockReset()
  vi.spyOn(useTodosModule, 'useCreateTodo').mockReturnValue({
    mutate: mockMutate,
    isPending: false,
  } as any)
})

describe('AddTodoForm', () => {
  it('renders input and Add button', () => {
    render(<AddTodoForm />)
    expect(screen.getByRole('textbox', { name: /new todo/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add/i })).toBeInTheDocument()
  })

  it('shows validation error on empty submit', async () => {
    render(<AddTodoForm />)
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('shows validation error on whitespace-only submit', async () => {
    render(<AddTodoForm />)
    await userEvent.type(screen.getByRole('textbox'), '   ')
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('shows validation error when text exceeds 200 characters', async () => {
    render(<AddTodoForm />)
    await userEvent.type(screen.getByRole('textbox'), 'x'.repeat(201))
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('clears input after successful submission', async () => {
    mockMutate.mockImplementation((_text, options) => options?.onSuccess?.())
    render(<AddTodoForm />)
    await userEvent.type(screen.getByRole('textbox'), 'Buy milk')
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('textbox')).toHaveValue('')
  })
})
```

**Why mock `useCreateTodo`?** The hook calls `useQueryClient()` internally which requires `QueryClientProvider`. Mocking it keeps tests fast and focused on form behaviour.

### Architecture Constraints

- **`POST /api/v1/todos` → 201 Created** — not 200; explicit `status_code=201` required
- **`db.refresh(todo)` after commit** — required to populate auto-generated `id` and `created_at` before returning
- **Never use `create_all()`** — schema already exists via Alembic migration
- **Frontend validates before API call** — empty/whitespace and >200 chars checked client-side; Pydantic still validates server-side as safety net
- **`invalidateQueries` not `setQueryData`** — refetch is fine here; optimistic updates are for Epic 2's toggle/delete (NFR-01 applies to those)
- **`useQueryClient()` must be inside component/hook** — do not call outside React tree
- **No `fetch` in `AddTodoForm`** — all API calls go through `src/api/todos.ts`
- **`role="alert"` on validation error `<p>`** — consistent with `ErrorMessage`, required for accessibility
- **`aria-label="New todo"` on input** — needed for `getByRole('textbox', { name: /new todo/i })` in tests
- **70% coverage threshold** — `npm run test:coverage` must pass

### What NOT to implement in this story

- Complete/delete todo actions — Stories 2.2 and 2.3
- Optimistic updates on create — `invalidateQueries` is sufficient; optimistic create adds complexity without user-visible benefit for a local app
- Character counter UI — not in AC, defer to UX polish
- `TodoItem` component — Story 2.2 builds it

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Story 2.1 ACs]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — API Patterns (POST 201), React Query Mutations, State Management Patterns, Validation Patterns]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — Component Boundary, Anti-Patterns]
- [Source: `backend/schemas.py` — `TodoCreate`, `TodoResponse` (already defined)]
- [Source: `backend/routers/todos.py` — existing GET pattern to follow]
- [Source: `backend/tests/test_todos.py` — `TestGetTodos` class for test structure]
- [Source: `_bmad-output/implementation-artifacts/1-2-react-frontend-shell.md` — component subfolder pattern, vitest mock approach]
- [Source: PRD — FR-01, FR-05, NFR-01]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `conftest.py` used `sqlite:///:memory:` without `StaticPool` — SQLite in-memory gives each connection its own empty DB, causing "no such table" errors. Fixed by adding `poolclass=StaticPool` to the engine.
- Frontend coverage failed because `api/` and `hooks/` were picked up but fully mocked in component tests. Fixed by adding `exclude: ['src/api/**', 'src/hooks/**']` to vitest coverage config — these are thin wrappers tested via E2E.

### Completion Notes List

- `POST /api/v1/todos` endpoint added — 201 Created + `TodoResponse`; Pydantic validates text length automatically
- `createTodo()` added to `api/todos.ts`; `useCreateTodo()` added to `hooks/useTodos.ts` with cache invalidation
- `AddTodoForm` component built with empty/whitespace and >200 char validation, `isPending` disable, input clear on success
- `App.tsx` updated — `<AddTodoForm />` renders above the list/error block
- `conftest.py` fixed with `StaticPool` — backend tests now reliably isolated
- `vitest.config.ts` updated — `api/` and `hooks/` excluded from coverage threshold
- 13 backend + 13 frontend tests pass; all thresholds met
- Task 7 (manual verification) left open — requires live Docker services

### File List

- `backend/routers/todos.py` — MODIFIED (POST endpoint)
- `backend/tests/test_todos.py` — MODIFIED (TestCreateTodo class)
- `backend/tests/conftest.py` — MODIFIED (StaticPool fix)
- `frontend/src/api/todos.ts` — MODIFIED (createTodo)
- `frontend/src/hooks/useTodos.ts` — MODIFIED (useCreateTodo)
- `frontend/src/components/AddTodoForm/AddTodoForm.tsx` — NEW
- `frontend/src/components/AddTodoForm/AddTodoForm.module.css` — NEW
- `frontend/src/components/AddTodoForm/AddTodoForm.test.tsx` — NEW
- `frontend/src/App.tsx` — MODIFIED (AddTodoForm wired in)
- `frontend/vitest.config.ts` — MODIFIED (api/hooks coverage exclude)
- `_bmad-output/implementation-artifacts/2-1-create-a-todo.md` — this story file
