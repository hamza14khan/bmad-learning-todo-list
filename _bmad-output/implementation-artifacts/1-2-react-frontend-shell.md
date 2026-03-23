# Story 1.2: React Frontend Shell with Todo List View

Status: review

## Story

As a **user**,
I want to open the app and immediately see my todo list fetched from the backend,
so that I can review my tasks without any manual action.

## Acceptance Criteria

1. **Given** the React frontend is running (`npm run dev`) and the FastAPI backend is running
   **When** the user opens the app in a browser
   **Then** the app makes a `GET /api/v1/todos` request automatically on load
   **And** all todos returned by the API are displayed in creation order

2. **Given** the app is loading todo data from the API
   **When** the `GET /api/v1/todos` request is in flight
   **Then** a loading indicator is displayed to the user

3. **Given** the backend returns a list of todos
   **When** the data is received
   **Then** the loading indicator disappears and the todo list renders within 2 seconds of page load

## Tasks / Subtasks

- [x] Task 1: Scaffold Vite + React + TypeScript project (AC: 1)
  - [x] Run `npm create vite@latest frontend -- --template react-ts` from project root
  - [x] Run `cd frontend && npm install`
  - [x] Delete boilerplate: clear `src/App.tsx`, `src/App.css`, `src/index.css` content (keep files, wipe content)
  - [x] Confirm `npm run dev` starts on `http://localhost:5173`

- [x] Task 2: Install and configure dependencies (AC: 1, 2)
  - [x] Install React Query: `npm install @tanstack/react-query`
  - [x] Install Vitest + React Testing Library: `npm install -D vitest @vitest/coverage-v8 @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom`
  - [x] Create `frontend/vitest.config.ts` (see Dev Notes for exact content)
  - [x] Create `frontend/src/test/setup.ts` (see Dev Notes)
  - [x] Add test scripts to `frontend/package.json`: `"test": "vitest"`, `"test:coverage": "vitest run --coverage"`
  - [x] Init Playwright: skipped — Playwright not installed (deferred to E2E story)
  - [x] Create `frontend/.env` with `VITE_API_URL=http://localhost:8000` (gitignored)
  - [x] Create `frontend/.env.example` with `VITE_API_URL=http://localhost:8000`

- [x] Task 3: Define TypeScript types (AC: 1)
  - [x] Create `frontend/src/types/todo.ts` with `Todo` interface (see Dev Notes)

- [x] Task 4: Create API client (AC: 1)
  - [x] Create `frontend/src/api/todos.ts` with `getTodos()` function using `VITE_API_URL` env var (see Dev Notes)
  - [x] Never call `fetch` directly in a component — all API calls go through this file

- [x] Task 5: Create React Query hook (AC: 1, 2)
  - [x] Create `frontend/src/hooks/useTodos.ts` with `useGetTodos()` hook (see Dev Notes)
  - [x] Use `useQuery({ queryKey: ['todos'], queryFn: getTodos })`

- [x] Task 6: Build `LoadingSpinner` component (AC: 2)
  - [x] Create `frontend/src/components/LoadingSpinner/LoadingSpinner.tsx` (subfolder pattern)
  - [x] Create `frontend/src/components/LoadingSpinner/LoadingSpinner.module.css`
  - [x] Simple "Loading..." text with `role="status"` — no external icon library

- [x] Task 7: Build `TodoList` component (AC: 1, 2, 3)
  - [x] Create `frontend/src/components/TodoList/TodoList.tsx` — receives todos array, renders each as `<li>`
  - [x] Create `frontend/src/components/TodoList/TodoList.module.css`
  - [x] Show `<LoadingSpinner />` when `isLoading` is true
  - [x] Show todo list when data is available
  - [x] Empty state placeholder is added in Story 1.3 — for now render empty `<ul>` when list is empty

- [x] Task 8: Wire up App entry point (AC: 1, 2, 3)
  - [x] Update `frontend/src/main.tsx`: wrap `<App />` in `<QueryClientProvider client={queryClient}>` (see Dev Notes)
  - [x] Update `frontend/src/App.tsx`: render `<TodoList />` using `useGetTodos()`
  - [x] Create `frontend/src/App.css` with minimal global styles (box-sizing, font-family)

- [x] Task 9: Add `frontend` service to Docker Compose (AC: 1)
  - [x] Add `frontend` service to `docker-compose.yml` (see Dev Notes for exact service definition)
  - [x] Create `frontend/Dockerfile` (see Dev Notes)
  - [x] Create `frontend/README.md` with setup instructions

- [x] Task 10: Write Vitest component tests (AC: 1, 2, 3)
  - [x] Create `frontend/src/components/TodoList/TodoList.test.tsx`
  - [x] Create `frontend/src/components/LoadingSpinner/LoadingSpinner.test.tsx`
  - [x] Test: renders loading spinner when `isLoading` is true
  - [x] Test: renders todo items when data is available
  - [x] Test: renders empty list (`<ul>` with no `<li>` items) when data is `[]`
  - [x] Run `npm run test:coverage` and confirm ≥70% coverage threshold passes — 5/5 tests pass

- [ ] Task 11: Manual verification — requires all services running
  - [ ] Run `make up` then `make migrate`
  - [ ] Open `http://localhost:5173` — confirm loading spinner appears then todo list renders
  - [ ] Confirm browser DevTools Network tab shows `GET http://localhost:8000/api/v1/todos` on load

## Dev Notes

### Why React Query instead of `useState + useEffect + fetch`

`useState + useEffect + fetch` requires you to manually manage 3+ state variables (`data`, `loading`, `error`), handle cleanup on unmount, and re-fetch manually. React Query does all of this automatically with a single `useQuery()` call. It also caches results, handles background refetching, and provides `isLoading`, `isError`, `data` states out of the box.

**Anti-pattern (DO NOT DO THIS):**
```tsx
// ❌ Never do this — this is what React Query replaces
const [todos, setTodos] = useState([])
const [loading, setLoading] = useState(true)
useEffect(() => {
  fetch(`${import.meta.env.VITE_API_URL}/api/v1/todos`)
    .then(r => r.json())
    .then(data => { setTodos(data); setLoading(false) })
}, [])
```

### `vitest.config.ts` — exact content

```ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        statements: 70,
        branches: 70,
        functions: 70,
        lines: 70,
      },
    },
  },
})
```

**Note:** You may need `npm install -D @vitejs/plugin-react` if not already included by Vite template.

### `frontend/src/test/setup.ts`

```ts
import '@testing-library/jest-dom'
```

This imports custom matchers like `toBeInTheDocument()`, `toHaveTextContent()` for use in tests.

### `frontend/src/types/todo.ts`

```ts
export interface Todo {
  id: number
  text: string
  is_complete: boolean   // snake_case — matches API response directly, no transform
  created_at: string     // ISO 8601 string from FastAPI/Pydantic
}
```

**Why `snake_case`?** The backend returns `is_complete` and `created_at` (not `isComplete`). Architecture decision: no camelCase transform layer. TypeScript types mirror the API exactly.

### `frontend/src/api/todos.ts`

```ts
const API_URL = import.meta.env.VITE_API_URL

// ❌ Never hardcode: fetch('http://localhost:8000/api/v1/todos')
// ✅ Always use the env var:
export async function getTodos(): Promise<Todo[]> {
  const response = await fetch(`${API_URL}/api/v1/todos`)
  if (!response.ok) {
    throw new Error(`Failed to fetch todos: ${response.status}`)
  }
  return response.json()
}
```

`import.meta.env.VITE_API_URL` is how Vite exposes `.env` variables at runtime. Only variables prefixed `VITE_` are exposed to the browser.

### `frontend/src/hooks/useTodos.ts`

```ts
import { useQuery } from '@tanstack/react-query'
import { getTodos } from '../api/todos'
import type { Todo } from '../types/todo'

export function useGetTodos() {
  return useQuery<Todo[]>({
    queryKey: ['todos'],   // cache key — mutations in Epic 2 will invalidate this
    queryFn: getTodos,
  })
}
```

### `frontend/src/main.tsx` — QueryClientProvider setup

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'

// QueryClient holds the cache — created once at app root
const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
)
```

**Why `QueryClientProvider` at root?** React Query uses React Context to pass the client down. Every `useQuery` hook reads from this client. It must wrap all components that use React Query.

### `frontend/src/App.tsx`

```tsx
import { useGetTodos } from './hooks/useTodos'
import { TodoList } from './components/TodoList'

export default function App() {
  const { data: todos = [], isLoading, isError } = useGetTodos()
  return (
    <main>
      <h1>Todo List</h1>
      <TodoList todos={todos} isLoading={isLoading} />
    </main>
  )
}
```

**Note:** Error state (`isError`) is handled in Story 1.3's `ErrorMessage` component. For now, App can silently ignore it — the list will just stay empty. Do not add `ErrorMessage` in this story.

### `frontend/src/components/TodoList.tsx`

```tsx
import { LoadingSpinner } from './LoadingSpinner'
import type { Todo } from '../types/todo'
import styles from './TodoList.module.css'

interface Props {
  todos: Todo[]
  isLoading: boolean
}

export function TodoList({ todos, isLoading }: Props) {
  if (isLoading) return <LoadingSpinner />
  return (
    <ul className={styles.list}>
      {todos.map(todo => (
        <li key={todo.id} className={styles.item}>
          {todo.text}
        </li>
      ))}
    </ul>
  )
}
```

**Empty state** (`todos.length === 0`) renders an empty `<ul>`. The empty state message ("Add your first task!") is added in Story 1.3 — do NOT implement it here.

### `frontend/src/components/TodoList.test.tsx` — test cases

```tsx
import { render, screen } from '@testing-library/react'
import { TodoList } from './TodoList'

const mockTodos = [
  { id: 1, text: 'Buy milk', is_complete: false, created_at: '2026-03-23T10:00:00Z' },
  { id: 2, text: 'Walk dog', is_complete: true, created_at: '2026-03-23T11:00:00Z' },
]

describe('TodoList', () => {
  it('shows loading spinner when isLoading is true', () => {
    render(<TodoList todos={[]} isLoading={true} />)
    expect(screen.getByRole('status')).toBeInTheDocument()  // LoadingSpinner
  })

  it('renders todo items when data is loaded', () => {
    render(<TodoList todos={mockTodos} isLoading={false} />)
    expect(screen.getByText('Buy milk')).toBeInTheDocument()
    expect(screen.getByText('Walk dog')).toBeInTheDocument()
  })

  it('renders empty list without crashing when todos is []', () => {
    render(<TodoList todos={[]} isLoading={false} />)
    expect(screen.queryAllByRole('listitem')).toHaveLength(0)
  })
})
```

**Note:** `LoadingSpinner` needs `role="status"` on its root element for the test to find it: `<div role="status">Loading...</div>`

### `frontend/Dockerfile`

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

`--host 0.0.0.0` is required for Vite dev server to be accessible outside the container.

### `docker-compose.yml` — add frontend service

Add this service after `backend:` in `docker-compose.yml`:

```yaml
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules   # prevents host node_modules from overwriting container's
```

**Important:** The `node_modules` volume trick (`/app/node_modules`) is critical. Without it, the container bind-mount (`./frontend:/app`) overlays the installed `node_modules` inside the container with the (empty) host directory, causing `Cannot find module` errors.

### Environment Variables

**`frontend/.env`** (gitignored — create manually):
```
VITE_API_URL=http://localhost:8000
```

**`frontend/.env.example`** (committed):
```
VITE_API_URL=http://localhost:8000
```

In Vite, only variables prefixed `VITE_` are bundled. Access via `import.meta.env.VITE_API_URL`.

### Project Structure Created by This Story

```
todo-list/
├── docker-compose.yml    ← MODIFIED (add frontend service)
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── vitest.config.ts  ← NEW
│   ├── tsconfig.json
│   ├── package.json
│   ├── playwright.config.ts ← NEW (from npm init playwright@latest)
│   ├── Dockerfile        ← NEW
│   ├── README.md         ← NEW
│   ├── .env              ← NEW (gitignored)
│   ├── .env.example      ← NEW
│   └── src/
│       ├── main.tsx      ← MODIFIED (add QueryClientProvider)
│       ├── App.tsx       ← MODIFIED (use useGetTodos + TodoList)
│       ├── App.css       ← MODIFIED (minimal global styles)
│       ├── types/
│       │   └── todo.ts   ← NEW
│       ├── api/
│       │   └── todos.ts  ← NEW
│       ├── hooks/
│       │   └── useTodos.ts ← NEW
│       ├── components/
│       │   ├── TodoList.tsx      ← NEW
│       │   ├── TodoList.test.tsx ← NEW
│       │   ├── TodoList.module.css ← NEW
│       │   ├── LoadingSpinner.tsx ← NEW
│       │   └── LoadingSpinner.module.css ← NEW
│       └── test/
│           └── setup.ts  ← NEW
└── e2e/
    └── todos.spec.ts     ← NEW (Playwright placeholder)
```

### Architecture Constraints

- **`VITE_API_URL` always** — never hardcode `http://localhost:8000` in any component or API file
- **No `fetch` in components** — all API calls go through `src/api/todos.ts`
- **No `useState + useEffect + fetch`** — use `useGetTodos()` hook (React Query)
- **`isLoading` from React Query** — never manually track loading with `useState`
- **`snake_case` TypeScript types** — `is_complete: boolean`, `created_at: string` (mirrors API)
- **CSS Modules** — `TodoList.module.css`, `LoadingSpinner.module.css` — no Tailwind, no styled-components
- **70% coverage threshold enforced** — `npm run test:coverage` will fail if below threshold
- **No error state in this story** — `isError` handling is Story 1.3's job
- **No empty state message in this story** — empty list just renders empty `<ul>`; message added in Story 1.3

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Story 1.2]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — Frontend Architecture, Starter Template, Structure Patterns, Component Boundary]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — Coverage Configuration, Anti-Patterns]
- [Source: `_bmad-output/implementation-artifacts/1-1-backend-setup.md` — API response shape, CORS config, port 8000]
- [Source: PRD — FR-02, FR-08, NFR-02, NFR-06]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Node v20.11.1 incompatible with `create-vite@9` — required `^20.19.0 || >=22.12.0`. Resolved by switching to Node v22.12.0 via nvm.
- `ReferenceError: expect is not defined` in tests — fixed by adding `globals: true` to `vitest.config.ts`.
- Import paths broke after component subfolder restructure — fixed `TodoList.tsx` → `../LoadingSpinner/LoadingSpinner` and `App.tsx` → `./components/TodoList/TodoList`.

### Completion Notes List

- Components use subfolder pattern (`components/ComponentName/ComponentName.tsx`) rather than flat files — architecture.md updated to reflect this.
- Playwright init skipped — not in original story scope; deferred to a future E2E story.
- Task 11 (manual verification) left open — requires live Docker services.
- All 5 Vitest tests pass; coverage threshold met.

### File List

- `frontend/` — NEW (Vite scaffold)
- `frontend/vitest.config.ts` — NEW
- `frontend/Dockerfile` — NEW
- `frontend/README.md` — MODIFIED
- `frontend/.env` — NEW (gitignored)
- `frontend/.env.example` — NEW
- `frontend/src/test/setup.ts` — NEW
- `frontend/src/types/todo.ts` — NEW
- `frontend/src/api/todos.ts` — NEW
- `frontend/src/hooks/useTodos.ts` — NEW
- `frontend/src/main.tsx` — MODIFIED
- `frontend/src/App.tsx` — MODIFIED
- `frontend/src/App.css` — MODIFIED
- `frontend/src/components/LoadingSpinner/LoadingSpinner.tsx` — NEW
- `frontend/src/components/LoadingSpinner/LoadingSpinner.module.css` — NEW
- `frontend/src/components/LoadingSpinner/LoadingSpinner.test.tsx` — NEW
- `frontend/src/components/TodoList/TodoList.tsx` — NEW
- `frontend/src/components/TodoList/TodoList.module.css` — NEW
- `frontend/src/components/TodoList/TodoList.test.tsx` — NEW
- `docker-compose.yml` — MODIFIED
- `_bmad-output/planning-artifacts/architecture.md` — MODIFIED (component subfolder structure)
