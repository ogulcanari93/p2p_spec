import { expect, test } from "@playwright/test";
import { login } from "./helpers";

test("dashboard usable on mobile viewport", async ({ page }) => {
  await login(page, "ogulcan@example.com");
  await expect(page.getByTestId("dashboard-incoming")).toBeVisible();
  await expect(page.getByTestId("dashboard-outgoing")).toBeVisible();
  await expect(page.getByTestId("wallet-summary")).toBeVisible();
  await expect(page.locator(".request-card-list .request-card").first()).toBeVisible();
});
