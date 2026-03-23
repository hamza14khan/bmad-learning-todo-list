---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - _bmad-output/planning-artifacts/PRD.md
---

# Todo App - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for the Todo App, decomposing the requirements from the PRD into implementable stories. Architecture: React (or similar) frontend + FastAPI Python backend + SQLite database (local dev).

## Requirements Inventory

### Functional Requirements

FR-01: Users can create a todo by entering a text description (1–200 characters) and submitting via Enter key or Add button.
FR-02: Users can view their complete todo list on app open, loaded from the API, sorted by creation order.
FR-03: Users can toggle a todo between active and complete states with a single click or tap.
FR-04: Users can delete a todo permanently with a single click or tap on the delete action.
FR-05: Users cannot submit an empty or whitespace-only todo — the app shows inline validation feedback without creating an entry.
FR-06: Completed todos display with strikethrough text and a visually muted style, distinguishable from active todos at a glance.
FR-07: The app displays an empty state when no todos exist, prompting the user to create their first task.
FR-08: The app displays a loading state while fetching todo data from the API on initial load.
FR-09: The app displays a graceful error state if the API is unavailable or returns an error response.
FR-10: All todo state (text, completion status, creation timestamp) persists in a backend database via API and survives server restarts.
FR-11: Todo data loads automatically on app open via a GET API request with no user action required.
FR-12: The interface renders correctly and is fully functional at viewport widths of 320px, 768px, and 1280px.
FR-13: The backend exposes a REST API with endpoints to create, read, toggle complete, and delete todos.
FR-14: Each todo stored in the database includes: id (auto-generated), text (string, 1–200 chars), is_complete (boolean), created_at (timestamp).

### NonFunctional Requirements

NFR-01: UI interactions (create, complete, delete) reflect visual updates within 300ms of user action, as measured in browser developer tools under normal conditions.
NFR-02: Initial app load (first contentful paint) completes within 2 seconds on localhost, as measured by browser developer tools.
NFR-03: The database persists todo data reliably across server restarts, supporting up to 500 todos without data corruption, as verified by functional testing.
NFR-04: The app handles API unavailability gracefully — displays an error state without crashing when the backend is unreachable.
NFR-05: The app functions correctly on the latest stable versions of Chrome, Firefox, and Safari on desktop and mobile.
NFR-06: The app runs locally via `npm run dev` (React frontend), `uvicorn` (FastAPI backend), and a local or Docker-hosted PostgreSQL instance with no cloud infrastructure required for development.
NFR-07: The codebase follows consistent formatting and naming conventions, enabling a new developer to understand and extend any module within 30 minutes of reading.
NFR-08: All interactive elements (add, complete, delete) are keyboard-accessible and meet WCAG 2.1 AA contrast ratio requirements (minimum 4.5:1 for normal text).

### Additional Requirements

- No Architecture document provided — technical stack decisions: React (frontend), FastAPI (Python) backend, PostgreSQL database.
- Frontend communicates with backend via REST API; CORS must be configured for local development.
- Database connection configured via environment variables (.env file); no hardcoded credentials.
- App must be extensible to a cloud deployment in a future phase without major refactoring.
- Local development only for MVP — no cloud infrastructure required.

### UX Design Requirements

None — no UX Design document provided. UI decisions to be made during development following PRD User Journey specifications.

### FR Coverage Map

FR-01: Epic 2 — Create todo with validation
FR-02: Epic 1 — View todo list via API
FR-03: Epic 2 — Toggle complete/incomplete
FR-04: Epic 2 — Delete todo
FR-05: Epic 2 — Empty/whitespace validation
FR-06: Epic 2 — Visual distinction for completed todos
FR-07: Epic 1 — Empty state display
FR-08: Epic 1 — Loading state during API fetch
FR-09: Epic 1 — Error state on API failure
FR-10: Epic 1 — Database persistence via API
FR-11: Epic 1 — Auto-load on app open
FR-12: Epic 3 — Responsive layout (320/768/1280px)
FR-13: Epic 1 — REST API endpoints (CRUD)
FR-14: Epic 1 — Todo data model (id, text, is_complete, created_at)

## Epic List

### Epic 1: Full-Stack Foundation — Working App with Todo List View
A developer can run the complete app locally (FastAPI + SQLite + frontend). A user can open the app and see their todo list fetched from the API — with proper loading, empty, and error states.
**FRs covered:** FR-02, FR-07, FR-08, FR-09, FR-10, FR-11, FR-13, FR-14
**NFRs covered:** NFR-02, NFR-03, NFR-04, NFR-06

### Epic 2: Core Todo Operations — Create, Complete & Delete
Users can perform the complete task management loop: create todos, mark them done (and undo), and delete them — with validation and visual feedback.
**FRs covered:** FR-01, FR-03, FR-04, FR-05, FR-06
**NFRs covered:** NFR-01, NFR-07

### Epic 3: Responsive & Accessible Experience
Users can use the app on any device (mobile, tablet, desktop) with a keyboard-accessible, WCAG 2.1 AA compliant interface that works across Chrome, Firefox, and Safari.
**FRs covered:** FR-12
**NFRs covered:** NFR-05, NFR-08

---

## Epic 1: Full-Stack Foundation — Working App with Todo List View

A developer can run the complete app locally (React + FastAPI + PostgreSQL). A user can open the app and see their todo list fetched from the API — with proper loading, empty, and error states.

### Story 1.1: Backend Setup — FastAPI Project, PostgreSQL Todo Model & GET /api/v1/todos Endpoint

As a **developer**,
I want a running FastAPI backend connected to PostgreSQL with a working GET /api/v1/todos endpoint,
So that the frontend has a live API to connect to and todo data persists reliably.

**Acceptance Criteria:**

**Given** a PostgreSQL instance is running and connection details are in a `.env` file
**When** the developer runs `uvicorn main:app --reload`
**Then** the FastAPI app starts on localhost:8000 without errors
**And** connects to the PostgreSQL database using the configured environment variables

**Given** the todos table does not exist
**When** the developer runs `alembic upgrade head`
**Then** the todos table is created via Alembic migration with columns: id (auto-int), text (varchar 200), is_complete (boolean, default false), created_at (timestamp with timezone, auto-set)

**Given** the backend is running
**When** a GET request is made to /api/v1/todos
**Then** the endpoint returns a JSON array of all todos sorted by created_at ascending
**And** returns an empty array [] when no todos exist
**And** responds in under 300ms for lists up to 500 items

---

### Story 1.2: React Frontend Shell with Todo List View

As a **user**,
I want to open the app and immediately see my todo list fetched from the backend,
So that I can review my tasks without any manual action.

**Acceptance Criteria:**

**Given** the React frontend is running (`npm run dev`) and the FastAPI backend is running
**When** the user opens the app in a browser
**Then** the app makes a GET /api/v1/todos request automatically on load
**And** all todos returned by the API are displayed in creation order

**Given** the app is loading todo data from the API
**When** the GET /api/v1/todos request is in flight
**Then** a loading indicator is displayed to the user

**Given** the backend returns a list of todos
**When** the data is received
**Then** the loading indicator disappears and the todo list renders within 2 seconds of page load

---

### Story 1.3: Empty State & Error State

As a **user**,
I want clear feedback when there are no todos or the backend is unavailable,
So that I always understand the state of the app.

**Acceptance Criteria:**

**Given** the backend returns an empty array
**When** the todo list renders
**Then** the app displays an empty state message prompting the user to add their first task
**And** no list container or placeholder items are shown

**Given** the backend is unreachable or returns a non-200 response
**When** the app attempts to load todos
**Then** a graceful error state is displayed describing the issue
**And** the app does not crash or show a blank screen
**And** the user can see instructions to check the backend connection

---

## Epic 2: Core Todo Operations — Create, Complete & Delete

Users can perform the complete task management loop: create todos, mark them done (and undo), and delete them — with validation and visual feedback.

### Story 2.1: Create a Todo

As a **user**,
I want to type a task and submit it to create a new todo,
So that I can add tasks to my list quickly.

**Acceptance Criteria:**

**Given** the user types a description (1–200 characters) in the input field
**When** they press Enter or click the Add button
**Then** a POST /api/v1/todos request is sent to the backend
**And** the new todo appears in the list immediately without a page reload
**And** the input field clears ready for the next entry
**And** the UI update occurs within 300ms of submission

**Given** the user submits an empty or whitespace-only input
**When** they press Enter or click Add
**Then** no API request is made
**And** an inline validation message is displayed
**And** the input field remains focused

**Given** the user types more than 200 characters
**When** they attempt to submit
**Then** inline validation prevents submission and displays a character limit message

---

### Story 2.2: Complete and Uncomplete a Todo

As a **user**,
I want to toggle a todo between active and complete,
So that I can track which tasks I've finished.

**Acceptance Criteria:**

**Given** an active todo is displayed in the list
**When** the user clicks the complete action
**Then** a PATCH /api/v1/todos/{id} request updates is_complete to true
**And** the todo immediately displays with strikethrough text and a muted visual style
**And** the UI update occurs within 300ms of the click

**Given** a completed todo is displayed
**When** the user clicks the complete action again
**Then** a PATCH /api/v1/todos/{id} request updates is_complete to false
**And** the todo reverts to active styling immediately

---

### Story 2.3: Delete a Todo

As a **user**,
I want to delete a todo permanently,
So that I can remove tasks I no longer need.

**Acceptance Criteria:**

**Given** a todo exists in the list
**When** the user clicks the delete action
**Then** a DELETE /api/v1/todos/{id} request is sent to the backend
**And** the todo is removed from the list immediately without a page reload
**And** the UI update occurs within 300ms of the click

**Given** the deleted todo was the last item in the list
**When** it is removed
**Then** the app transitions to the empty state

---

## Epic 3: Responsive & Accessible Experience

Users can use the app on any device (mobile, tablet, desktop) with a keyboard-accessible, WCAG 2.1 AA compliant interface that works across Chrome, Firefox, and Safari.

### Story 3.1: Responsive Layout

As a **user**,
I want the app to display and function correctly on my phone, tablet, or desktop,
So that I can manage my todos on any device.

**Acceptance Criteria:**

**Given** the user opens the app on a mobile device (320px viewport)
**When** the page renders
**Then** all UI elements (input, todo list, complete/delete actions) are visible and usable without horizontal scrolling

**Given** the user opens the app at 768px (tablet) and 1280px (desktop) viewports
**When** the page renders
**Then** the layout adapts appropriately and all functionality remains fully accessible

**Given** the user interacts with the app on Chrome, Firefox, or Safari (latest stable)
**When** they perform any todo action (create, complete, delete)
**Then** all features behave correctly with no browser-specific errors

---

### Story 3.2: Keyboard Accessibility & WCAG Compliance

As a **user who navigates by keyboard or uses assistive technology**,
I want all todo actions to be reachable and operable via keyboard,
So that I can use the app without a mouse.

**Acceptance Criteria:**

**Given** the user navigates the app using only the keyboard (Tab, Enter, Space)
**When** they tab through interactive elements
**Then** focus moves logically through: input field → Add button → each todo's complete action → each todo's delete action

**Given** a todo action (add, complete, delete) is focused
**When** the user presses Enter or Space
**Then** the action executes correctly

**Given** any interactive element is rendered
**When** inspected for contrast
**Then** all text meets WCAG 2.1 AA minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text

**Given** all interactive elements are rendered
**When** a keyboard focus indicator is visible
**Then** the focus outline is clearly visible and distinguishable from the background
