import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
	const DASHBOARD_URL = "http://localhost:3000/dashboard";
	const EXPECTED_DOWNLOAD_URL = "http://localhost:8000/download-file";

	test.beforeEach(async ({ page }) => {
		await page.goto(DASHBOARD_URL);
	});

	test("should display Sync New Data button", async ({ page }) => {
		const syncButton = await page.locator('[data-testid="sync-new-data"]');
		await expect(syncButton).toBeVisible();
	});

	test("should display Download CSV button", async ({ page }) => {
		const downloadButton = await page.locator('[data-testid="download-csv"]');
		await expect(downloadButton).toBeVisible();
	});

	test("should have correct download link", async ({ page }) => {
		const downloadButton = await page.locator('[data-testid="download-csv"]');
		const downloadHref = await downloadButton.getAttribute("href");
		expect(downloadHref).toBe(`${EXPECTED_DOWNLOAD_URL}`);
	});

	test("should display table", async ({ page }) => {
		const jobsTable = await page.locator('[data-testid="jobs-table"]');
		await expect(jobsTable).toBeVisible();
	});
});
