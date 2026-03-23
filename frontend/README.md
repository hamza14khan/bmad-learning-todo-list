# Todo App — Frontend

React + TypeScript frontend for the Todo App.

## Prerequisites

- Node.js 22.12.0+ (use `nvm use v22.12.0`)
- Backend running on port 8000

## Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`

## Tests

```bash
npm run test:coverage   # run tests with coverage (must be ≥70%)
npm test                # run tests in watch mode
```

## E2E Tests (Playwright)

Requires all services running (`make up`):

```bash
npx playwright test
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |
