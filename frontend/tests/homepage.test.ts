import { test, expect } from "@playwright/test";

// Test to check if the Google Login button is visible on the screen.
test("Google Login button is visible", async ({ page }) => {
	await page.goto("http://localhost:3000");

	const button = page
		.locator("div")
		.filter({ hasText: /^Login with Google$/ })
		.getByRole("button");
	await expect(button).toBeVisible();
});

// Test to check if the Website Email link is visible on the screen.
test("Email link is visible", async ({ page }) => {
	await page.goto("http://localhost:3000");

	const buttons = page.getByRole("link", { name: "send us an email" });
	await expect(buttons.first()).toBeVisible();
	await expect(buttons.nth(1)).toBeVisible();
});

// Test to check if the Youtube Demo Video link is visible on the screen.
test("Iframe (YouTube video) is present", async ({ page }) => {
	await page.goto("http://localhost:3000");

	const iframe = page.locator('iframe[title="YouTube video player"]');
	await expect(iframe).toBeVisible();
});
