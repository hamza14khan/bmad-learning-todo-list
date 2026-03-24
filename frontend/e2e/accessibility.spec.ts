import { test, expect } from '@playwright/test'

test('tab from input reaches add button', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('New todo').focus()
  await page.keyboard.press('Tab')
  const addButton = page.getByRole('button', { name: /add/i })
  await expect(addButton).toBeFocused()
})

test('enter key on empty input shows validation error', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('New todo').focus()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('alert')).toBeVisible()
})

test('page has h1 heading', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
})
