import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
	const DASHBOARD_URL = "http://localhost:3000/dashboard";

	test.beforeEach(async ({ page }) => {
		await page.goto(DASHBOARD_URL);
	});

	test("should display title Job Applications Dashboard", async ({ page }) => {
		await expect(page.getByRole("heading", { name: /Job Applications Dashboard/i })).toBeVisible();
	});

	// test("should display Start Date dropdown", async ({ page }) => {
	// 	const startDateDropdown = await page.locator('[data-testid="start-date"]');
	// 	await expect(startDateDropdown).toBeVisible();
	// });

	// test("should display Sync New Data button", async ({ page }) => {
	// 	const syncButton = await page.locator('[data-testid="sync-new-data"]');
	// 	await expect(syncButton).toBeVisible();
	// });

	// test("should display Download CSV button", async ({ page }) => {
	// 	const downloadButton = await page.locator('[data-testid="download-csv"]');
	// 	await expect(downloadButton).toBeVisible();
	// });

	// test("should have correct download link", async ({ page }) => {
	// 	const downloadButton = await page.locator('[data-testid="download-csv"]');
	// 	const downloadHref = await downloadButton.getAttribute("href");
	// 	expect(downloadHref).toBe(`${EXPECTED_DOWNLOAD_URL}`);
	// });

	// test("should display table", async ({ page }) => {
	// 	const jobsTable = await page.locator('[data-testid="jobs-table"]');
	// 	await expect(jobsTable).toBeVisible();
	// });

	test("should display failed to load applications", async ({ page }) => {
		await expect(page.getByText("Failed to load applications")).toBeVisible();
	});

	test("should display try again button", async ({ page }) => {
		const tryAgainButton = await page.getByRole("button", { name: "Try again" });
		await expect(tryAgainButton).toBeVisible();
	});
});
