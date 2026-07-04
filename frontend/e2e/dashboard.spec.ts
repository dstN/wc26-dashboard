import { test, expect } from "./fixtures";

test.describe("Dashboard page", () => {
  test("loads without error", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("[data-testid='dashboard']")).toBeVisible();
  });

  test("shows Germany vs Curaçao match header", async ({ page }) => {
    await page.goto("/");
    const header = page.locator("[data-testid='match-header']");
    await expect(header).toContainText("Germany");
    await expect(header).toContainText("Curaçao");
  });

  test("possession bar is visible and labelled", async ({ page }) => {
    await page.goto("/");
    const bar = page.locator("[data-testid='possession-bar']");
    await expect(bar).toBeVisible();
    await expect(bar).toContainText("%");
  });

  test("nav tabs switch content", async ({ page }) => {
    await page.goto("/");
    const tabs = page.locator("[role='tab']");
    const count = await tabs.count();
    expect(count).toBeGreaterThanOrEqual(3);

    await tabs.nth(1).click();
    await expect(page.locator("[role='tabpanel']")).toBeVisible();
  });

  test("score is 7-1", async ({ page }) => {
    await page.goto("/");
    const score = page.locator("[data-testid='score']");
    await expect(score).toContainText("7");
    await expect(score).toContainText("1");
  });
});
