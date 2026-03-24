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
