import { test, expect } from "@playwright/test";

// Test to check if spinner icon is visible on the screen.
test("Spinner is visible", async ({ page }) => {
	await page.goto("http://localhost:3000/processing");

	await expect(page.getByRole("main").locator("path").first()).toBeVisible();
});
