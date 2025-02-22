import { test, expect } from "@playwright/test";

test.describe("Success Page", () => {
	const SUCCESS_PAGE_URL = "http://localhost:3000/success";
	const EXPECTED_DOWNLOAD_URL = "http://localhost:8000/download-file";

	test.beforeEach(async ({ page }) => {
		await page.goto(SUCCESS_PAGE_URL);
	});

	test("should display success message and download button", async ({ page }) => {
		await expect(page.getByRole("heading", { name: /Success! Your file is ready./i })).toBeVisible();
		await expect(page.getByText("Click the button below to download your file.")).toBeVisible();
		const downloadButton = page.getByRole("link", { name: "Download Job Application Data" });
		await expect(downloadButton).toBeVisible();
	});

	test("should have correct download link", async ({ page }) => {
		const downloadButton = page.getByRole("link", { name: "Download Job Application Data" });
		const downloadHref = await downloadButton.getAttribute("href");
		expect(downloadHref).toBe(`${EXPECTED_DOWNLOAD_URL}`);
	});
});
