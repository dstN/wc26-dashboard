import { test, expect } from "@playwright/test";

test.describe("Accessibility", () => {
  test("page has a main landmark", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("main")).toBeVisible();
  });

  test("all images have alt text", async ({ page }) => {
    await page.goto("/");
    const images = page.locator("img:not([alt])");
    await expect(images).toHaveCount(0);
  });

  test("nav tabs are keyboard accessible", async ({ page }) => {
    await page.goto("/");
    const firstTab = page.locator("[role='tab']").first();
    await firstTab.focus();
    await expect(firstTab).toBeFocused();
    await page.keyboard.press("ArrowRight");
    const secondTab = page.locator("[role='tab']").nth(1);
    await expect(secondTab).toBeFocused();
  });

  test("theme switch has accessible label", async ({ page }) => {
    await page.goto("/");
    const toggle = page.locator("[role='switch']");
    await expect(toggle).toHaveAttribute("aria-label");
  });

  test("section headings are present", async ({ page }) => {
    await page.goto("/");
    const headings = page.locator("h2, h3");
    const count = await headings.count();
    expect(count).toBeGreaterThan(0);
  });
});
