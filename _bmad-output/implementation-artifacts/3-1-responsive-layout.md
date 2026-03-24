# Story 3.1: Responsive Layout

Status: review

## Story

As a **user**,
I want the app to display and function correctly on my phone, tablet, or desktop,
so that I can manage my todos on any device.

## Acceptance Criteria

1. **Given** the user opens the app on a mobile device (320px viewport)
   **When** the page renders
   **Then** all UI elements (input, todo list, complete/delete actions) are visible and usable without horizontal scrolling

2. **Given** the user opens the app at 768px (tablet) and 1280px (desktop) viewports
   **When** the page renders
   **Then** the layout adapts appropriately and all functionality remains fully accessible

3. **Given** the user interacts with the app on Chrome, Firefox, or Safari (latest stable)
   **When** they perform any todo action (create, complete, delete)
   **Then** all features behave correctly with no browser-specific errors

## Tasks / Subtasks

- [x] Task 1: Clean up `index.css` — remove Vite scaffold CSS that conflicts with app styles (AC: 1, 2, 3)
  - [x] Replace `frontend/src/index.css` with a minimal reset — only `box-sizing`, `body { margin: 0 }`, `#root { min-height: 100vh }`
  - [x] All body font, color, and background styles live in `App.css` — do NOT duplicate in `index.css`

- [x] Task 2: Update `App.css` — responsive layout for the `.app` container (AC: 1, 2)
  - [x] Reduce top margin at small viewports: at `max-width: 480px` use `margin: 1rem auto` instead of `2rem`
  - [x] Keep `max-width: 600px; padding: 0 1rem` unchanged — works at all breakpoints already

- [x] Task 3: Improve touch targets in `TodoItem` (AC: 1, 2)
  - [x] Update `frontend/src/components/TodoItem/TodoItem.module.css`
  - [x] Toggle button: add `min-height: 44px; min-width: 44px` — current 2rem × 2rem (32px) is below WCAG 2.5.5 minimum
  - [x] Delete button: add `min-height: 44px; min-width: 44px; display: flex; align-items: center; justify-content: center`

- [x] Task 4: Install and configure Playwright for viewport E2E tests (AC: 1, 2)
  - [x] Installed `@playwright/test` 1.58.2 — approved by user
  - [x] `npx playwright install --with-deps chromium`
  - [x] Create `frontend/playwright.config.ts`
  - [x] Add `test:e2e` script to `frontend/package.json`

- [x] Task 5: Write Playwright viewport tests (AC: 1, 2)
  - [x] Create `frontend/e2e/responsive.spec.ts`
  - [x] Test at 320px: app renders without horizontal scrolling
  - [x] Test at 768px: app renders without horizontal scrolling
  - [x] Test at 1280px: app renders without horizontal scrolling
  - [x] All 6 E2E tests pass; `vitest.config.ts` updated to exclude `e2e/**` from Vitest

- [ ] Task 6: Manual cross-browser verification (AC: 3)
  - [ ] Test in Chrome, Firefox, Safari — create, complete, delete a todo
  - [ ] Verify no console errors in any browser

## Dev Notes

### Current CSS State (as of Story 2.3)

**`frontend/src/index.css`** — THIS IS THE PROBLEM FILE:
- Still contains Vite scaffold CSS: CSS variables (`--text`, `--bg`, `--accent`), dark mode, `#root` with `width: 1126px; text-align: center; border-inline: 1px solid var(--border)`, and 56px h1 font size
- Conflicts with `App.css`: `index.css` sets `:root { font: 18px; color: #6b6375; background: #fff }` while `App.css` sets `body { color: #333; background: #f9f9f9 }`
- The `#root { text-align: center }` centers all text in the app incorrectly
- **Must be replaced with minimal reset**

**`frontend/src/App.css`** — already mostly correct:
```css
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f9f9f9; color: #333; }
.app { max-width: 600px; margin: 2rem auto; padding: 0 1rem; }
h1 { font-size: 1.5rem; margin-bottom: 1rem; }
```
Only needs: reduce `margin` at small viewports.

**`frontend/src/components/TodoItem/TodoItem.module.css`** — `.toggle` is 2rem × 2rem (32px) which is below the 44px WCAG touch target minimum.

**`frontend/src/components/AddTodoForm/AddTodoForm.module.css`** — `.button` has padding but no explicit min-height. At default font-size, it's approximately 38px tall. Should add `min-height: 44px`.

**`frontend/src/components/TodoList/TodoList.module.css`** — no changes needed; list layout is already flexible.

**`frontend/src/components/ErrorMessage/ErrorMessage.module.css`** — no changes needed.

**`frontend/src/components/LoadingSpinner/LoadingSpinner.module.css`** — no changes needed.

### Task 1: Replacement `index.css`

Replace the entire file with:
```css
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
}

#root {
  min-height: 100vh;
}
```

The box-sizing rule in `index.css` and `App.css` will both exist — that's fine, it's idempotent. But it's cleaner to keep it only in `index.css` (global reset) and remove it from `App.css`.

Actually — keep both. `App.css` sets box-sizing on `*` which is fine as a safety net. No functional difference.

### Task 2: Responsive App.css

```css
/* Add this responsive adjustment */
@media (max-width: 480px) {
  .app {
    margin: 1rem auto;
  }
}
```

### Task 3: TodoItem touch targets

```css
/* Update .toggle */
.toggle {
  background: none;
  border: 2px solid #ccc;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  min-width: 44px;
  min-height: 44px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #666;
  transition: border-color 0.2s, color 0.2s;
}

/* Update .delete */
.delete {
  background: none;
  border: none;
  cursor: pointer;
  color: #ccc;
  font-size: 1rem;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: color 0.2s;
}
```

Also update AddTodoForm `.button`:
```css
.button {
  padding: 0.5rem 1.25rem;
  min-height: 44px;
  font-size: 1rem;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
```

### Task 4: Playwright config

```ts
// frontend/playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
})
```

Add to `package.json` scripts:
```json
"test:e2e": "playwright test"
```

### Task 5: Viewport E2E tests

```ts
// frontend/e2e/responsive.spec.ts
import { test, expect } from '@playwright/test'

const viewports = [
  { name: '320px (mobile)', width: 320, height: 568 },
  { name: '768px (tablet)', width: 768, height: 1024 },
  { name: '1280px (desktop)', width: 1280, height: 800 },
]

for (const vp of viewports) {
  test(`renders without horizontal scrolling at ${vp.name}`, async ({ page }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height })
    await page.goto('/')

    // No horizontal scrollbar — scrollWidth should equal clientWidth
    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })
    expect(hasOverflow).toBe(false)
  })

  test(`input and add button visible at ${vp.name}`, async ({ page }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height })
    await page.goto('/')
    await expect(page.getByLabel('New todo')).toBeVisible()
    await expect(page.getByRole('button', { name: /add/i })).toBeVisible()
  })
}
```

**Important:** Playwright E2E tests require the Vite dev server running (`npm run dev`). They do NOT run as part of `npm run test:coverage` (Vitest only). Run with `npm run test:e2e` separately.

### Coverage Impact

Story 3.1 is CSS-only changes + Playwright setup. The Vitest coverage threshold (`npm run test:coverage`) is NOT affected — no component logic changes. The 100% coverage from Story 2.3 remains.

If Playwright is not approved in Task 4, skip Tasks 4 and 5. The CSS changes alone satisfy the ACs — viewport tests are verification only.

### Architecture Constraints

- **CSS Modules for components, plain CSS for globals** — `index.css` and `App.css` are global; component-specific styles stay in `.module.css`
- **No Tailwind, no CSS-in-JS** — architecture explicitly prohibits these
- **No new CSS framework** — responsive layout uses standard media queries only
- **Touch target 44px minimum** — WCAG 2.5.5 requirement, relevant to Story 3.2 (accessibility) which builds on this story
- **Breakpoints** — architecture specifies 320px, 768px, 1280px as the three target viewports
- **`box-sizing: border-box`** already set in both `App.css` and `index.css` — removing from one is fine but not required
- **`index.css` is imported in `main.tsx`** — replacing it replaces the global base; `App.css` is imported in `App.tsx` and adds layout styles on top

### What NOT to implement in this story

- ARIA attributes, focus management, contrast checking — Story 3.2
- Dark mode — not in PRD
- Animations or transitions (beyond existing hover transitions) — not in PRD
- Tablet-specific layout changes (multi-column) — ACs only require "adapts appropriately", which is already satisfied by the centered max-width container

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Story 3.1 ACs]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — Styling: CSS Modules, no Tailwind; Testing: Playwright for E2E; breakpoints 320/768/1280]
- [Source: `frontend/src/index.css` — current conflicting Vite scaffold CSS]
- [Source: `frontend/src/App.css` — current layout CSS]
- [Source: `frontend/src/components/TodoItem/TodoItem.module.css` — buttons need touch target fix]
- [Source: `frontend/package.json` — Playwright not yet installed]
- [Source: PRD — FR-12, NFR-05, NFR-08 (partial — full WCAG in Story 3.2)]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Replaced `index.css` Vite scaffold CSS — removed conflicting `#root` width/text-align/border, 56px h1, CSS variables, dark mode
- `App.css` responsive: reduces top margin from 2rem → 1rem at ≤480px
- TodoItem toggle and delete buttons now meet 44×44px WCAG touch target minimum
- AddTodoForm Add button gets `min-height: 44px`
- Playwright 1.58.2 installed; 6 viewport E2E tests pass at 320px, 768px, 1280px
- Added `e2e/**` to Vitest `exclude` so Playwright tests don't run under Vitest

### File List

- `frontend/src/index.css` — replaced Vite scaffold with minimal reset
- `frontend/src/App.css` — added `@media (max-width: 480px)` margin reduction
- `frontend/src/components/TodoItem/TodoItem.module.css` — min-width/min-height 44px on toggle + delete
- `frontend/src/components/AddTodoForm/AddTodoForm.module.css` — min-height 44px on Add button
- `frontend/playwright.config.ts` — new Playwright config
- `frontend/package.json` — added `@playwright/test` dev dep + `test:e2e` script
- `frontend/vitest.config.ts` — added `exclude: ['**/node_modules/**', 'e2e/**']`
- `frontend/e2e/responsive.spec.ts` — new Playwright viewport tests (6 tests)
