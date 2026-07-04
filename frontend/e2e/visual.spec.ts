import { test, expect } from "@playwright/test";

test.describe("Visual / dark mode", () => {
  test("dark mode toggle changes data-theme attribute", async ({ page }) => {
    await page.goto("/");

    const html = page.locator("html");
    const initialTheme = await html.getAttribute("data-theme");

    const toggle = page.locator("[role='switch']");
    await toggle.click();

    const newTheme = await html.getAttribute("data-theme");
    expect(newTheme).not.toEqual(initialTheme);
    expect(["light", "dark"]).toContain(newTheme);
  });

  test("no flash on dark mode load", async ({ browser }) => {
    const context = await browser.newContext({
      storageState: {
        cookies: [],
        origins: [
          {
            origin: "http://localhost:3000",
            localStorage: [{ name: "efi-theme", value: "dark" }],
          },
        ],
      },
    });
    const page = await context.newPage();
    await page.goto("/");
    const theme = await page.locator("html").getAttribute("data-theme");
    expect(theme).toBe("dark");
    await context.close();
  });

  test("possession bar renders with visible segments", async ({ page }) => {
    await page.goto("/");
    const bar = page.locator("[data-testid='possession-bar']");
    await expect(bar).toBeVisible();
    const box = await bar.boundingBox();
    expect(box?.width).toBeGreaterThan(200);
    expect(box?.height).toBeGreaterThan(10);
  });
});
