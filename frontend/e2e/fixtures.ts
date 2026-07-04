import { test as base, expect } from "@playwright/test";

export type TestFixtures = {
  dashboardLoaded: void;
};

export const test = base.extend<TestFixtures>({
  dashboardLoaded: [
    async ({ page }, use) => {
      await page.goto("/");
      await page.waitForSelector("[data-testid='dashboard']", { timeout: 10_000 });
      await use();
    },
    { auto: false },
  ],
});

export { expect };
