import { test, expect } from "@playwright/test";

test.describe("Navbar Tests", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("http://localhost:3000");
	});

	test("should render navbar properly", async ({ page }) => {
		const navbar = await page.locator("nav");
		await expect(navbar).toBeVisible();
	});

	test("should navigate to home when clicking the brand logo", async ({ page }) => {
		const brandLogo = page.locator('[data-testid="Logo"]');
		await expect(brandLogo).toBeVisible();
		await brandLogo.click();
		await expect(page).toHaveURL("http://localhost:3000");
	});

	test("should contain GitHub link", async ({ page }) => {
		const githubLink = page.locator('a[aria-label="Github"]').first();
		await expect(githubLink).toHaveAttribute("href", /github\.com/);
		await expect(githubLink).toHaveAttribute("target", "_blank");
	});

	test("should have a theme switch button", async ({ page }) => {
		const themeSwitch = await page.locator('[data-testid="theme-switch-button"] >> nth=0');
		await expect(themeSwitch).toBeVisible();
	});

	test("should contain Sponsor button with correct link", async ({ page }) => {
		const sponsorButton = await page.locator('[data-testid="Sponsor"]');
		await expect(sponsorButton).toBeVisible();
		await expect(sponsorButton).toHaveAttribute("href", "https://buymeacoffee.com/liano");
	});

	test("should display logout button on success page navbar", async ({ page }) => {
		await page.goto("http://localhost:3000/success");
		const logoutButton = await page.locator("text=Logout");
		await expect(logoutButton).toBeVisible();
	});
});
