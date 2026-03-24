# Story 1.3: Empty State & Error State

Status: done

## Story

As a **user**,
I want clear feedback when there are no todos or the backend is unavailable,
so that I always understand the state of the app.

## Acceptance Criteria

1. **Given** the backend returns an empty array
   **When** the todo list renders
   **Then** the app displays an empty state message prompting the user to add their first task
   **And** no list container or placeholder items are shown

2. **Given** the backend is unreachable or returns a non-200 response
   **When** the app attempts to load todos
   **Then** a graceful error state is displayed describing the issue
   **And** the app does not crash or show a blank screen
   **And** the user can see instructions to check the backend connection

## Tasks / Subtasks

- [x] Task 1: Add empty state to `TodoList` component (AC: 1)
  - [x] Modify `frontend/src/components/TodoList/TodoList.tsx` — when `!isLoading && todos.length === 0`, render a `<p>` with empty state message instead of an empty `<ul>`
  - [x] Add `.empty` style to `frontend/src/components/TodoList/TodoList.module.css`
  - [x] Add empty state test to `frontend/src/components/TodoList/TodoList.test.tsx` — verify the message text appears when `todos=[]` and `isLoading=false`

- [x] Task 2: Create `ErrorMessage` component (AC: 2)
  - [x] Create `frontend/src/components/ErrorMessage/ErrorMessage.tsx` with `role="alert"` on root element
  - [x] Create `frontend/src/components/ErrorMessage/ErrorMessage.module.css`
  - [x] Create `frontend/src/components/ErrorMessage/ErrorMessage.test.tsx` — test that `role="alert"` is present and error text renders

- [x] Task 3: Wire error state in `App.tsx` (AC: 2)
  - [x] Modify `frontend/src/App.tsx` — destructure `isError` and `error` from `useGetTodos()`
  - [x] Conditionally render `<ErrorMessage />` when `isError` is true, else render `<TodoList />`
  - [x] Pass error message string to `ErrorMessage` when `error instanceof Error`

- [x] Task 4: Run tests and verify coverage (AC: 1, 2)
  - [x] Run `npm run test:coverage` from `frontend/` — 8/8 tests pass, 100% coverage (threshold: 70%)

- [ ] Task 5: Manual verification — requires all services running
  - [ ] Run `make up` then `make migrate`
  - [ ] Open `http://localhost:5173` with empty DB — confirm empty state message appears (no `<ul>`)
  - [ ] Stop the backend — confirm error state renders without crash

## Dev Notes

### What exists from Story 1.2

- `App.tsx` currently: `const { data: todos = [], isLoading } = useGetTodos()` — `isError` and `error` NOT yet destructured
- `TodoList.tsx` currently: handles `isLoading` → `<LoadingSpinner />`, renders empty `<ul>` when `todos=[]` — **no empty state message**
- `useGetTodos()` already returns `isError` and `error` from React Query — nothing new needed in the hook
- Component subfolder pattern is established: `components/ComponentName/ComponentName.tsx` + `.module.css` + `.test.tsx`

### Component: `ErrorMessage`

```tsx
// frontend/src/components/ErrorMessage/ErrorMessage.tsx
import styles from './ErrorMessage.module.css'

interface Props {
  message?: string
}

export function ErrorMessage({ message }: Props) {
  return (
    <div role="alert" className={styles.error}>
      <p>Something went wrong. Please check the backend connection.</p>
      {message && <p className={styles.detail}>{message}</p>}
    </div>
  )
}
```

- `role="alert"` is required — tests use `screen.getByRole('alert')` to find it
- `message` prop is optional — pass the raw error message string for detail display
- No external dependencies — plain CSS Modules only

### Empty State in `TodoList`

```tsx
// Modified section of TodoList.tsx — insert before the return <ul>
if (todos.length === 0) {
  return <p className={styles.empty}>No todos yet. Add your first task!</p>
}
```

This replaces the current empty `<ul>` rendered when `todos=[]`. The existing `if (isLoading)` guard stays at the top unchanged.

### Updated `App.tsx`

```tsx
import { useGetTodos } from './hooks/useTodos'
import { TodoList } from './components/TodoList/TodoList'
import { ErrorMessage } from './components/ErrorMessage/ErrorMessage'
import './App.css'

export default function App() {
  const { data: todos = [], isLoading, isError, error } = useGetTodos()

  return (
    <main className="app">
      <h1>Todo List</h1>
      {isError ? (
        <ErrorMessage message={error instanceof Error ? error.message : undefined} />
      ) : (
        <TodoList todos={todos} isLoading={isLoading} />
      )}
    </main>
  )
}
```

**Key pattern:** Error state replaces the todo list entirely — they never render simultaneously.

### Updated Tests

**`TodoList.test.tsx` — add one test:**
```tsx
it('shows empty state message when todos is [] and not loading', () => {
  render(<TodoList todos={[]} isLoading={false} />)
  expect(screen.getByText(/add your first task/i)).toBeInTheDocument()
  expect(screen.queryByRole('list')).not.toBeInTheDocument()
})
```

**`ErrorMessage.test.tsx` — new file:**
```tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ErrorMessage } from './ErrorMessage'

describe('ErrorMessage', () => {
  it('renders alert role', () => {
    render(<ErrorMessage />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })

  it('shows detail message when provided', () => {
    render(<ErrorMessage message="Failed to fetch todos: 503" />)
    expect(screen.getByText('Failed to fetch todos: 503')).toBeInTheDocument()
  })

  it('renders without message prop', () => {
    render(<ErrorMessage />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})
```

### Architecture Constraints

- **Error and empty states are separate concerns** — error is in `App.tsx`, empty state is in `TodoList.tsx`
- **`role="alert"`** on `ErrorMessage` root — required for accessibility (WCAG) and for tests
- **`role="status"`** on `LoadingSpinner` — already in place from Story 1.2, do not change
- **No `alert()` calls** — error displayed inline, never via browser alert
- **CSS Modules only** — no Tailwind, no inline styles
- **70% coverage threshold** — `npm run test:coverage` must pass after changes
- **`error instanceof Error` guard** — React Query types `error` as `Error | null`; guard prevents passing `null` as string

### What NOT to implement in this story

- Add Todo form (`AddTodoForm`) — Story 2.1
- Complete/delete todo actions — Stories 2.2, 2.3
- Retry button on error state — not in AC, defer to Epic 2
- Toast notifications — not in architecture, keep error inline

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Story 1.3 ACs]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — Error Handling Patterns, Frontend Architecture, Component Boundary]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — Complete Project Directory Structure (ErrorMessage subfolder)]
- [Source: `_bmad-output/implementation-artifacts/1-2-react-frontend-shell.md` — Dev Agent Record, existing App.tsx and TodoList.tsx code]
- [Source: PRD — FR-07, FR-09, NFR-04]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — clean implementation, no blockers.

### Completion Notes List

- Empty state added to `TodoList.tsx` — replaces empty `<ul>` with `<p>` message when `todos.length === 0 && !isLoading`
- `ErrorMessage` component created with `role="alert"` for accessibility; optional `message` prop surfaces React Query error detail
- `App.tsx` updated — `isError` and `error` destructured from `useGetTodos()`; `ErrorMessage` renders in place of `TodoList` when `isError` is true
- All 8 Vitest tests pass with 100% coverage (threshold: 70%)
- Task 5 (manual verification) left open — requires live Docker services

### File List

- `frontend/src/components/TodoList/TodoList.tsx` — MODIFIED (empty state)
- `frontend/src/components/TodoList/TodoList.module.css` — MODIFIED (`.empty` style)
- `frontend/src/components/TodoList/TodoList.test.tsx` — MODIFIED (empty state test)
- `frontend/src/components/ErrorMessage/ErrorMessage.tsx` — NEW
- `frontend/src/components/ErrorMessage/ErrorMessage.module.css` — NEW
- `frontend/src/components/ErrorMessage/ErrorMessage.test.tsx` — NEW
- `frontend/src/App.tsx` — MODIFIED (isError wiring)
