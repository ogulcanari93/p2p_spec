import { expect, test } from "@playwright/test";
import {
  dismissActionResultModal,
  goToCreateRequest,
  login,
  parseWalletMinor,
  requestTable,
} from "./helpers";

const OGULCAN = "ogulcan@example.com";
const AYCA = "ayca@example.com";

test.describe.configure({ mode: "serial" });

test.describe("P2P payment requests", () => {
  test("login ensures wallet and destination on create", async ({ page }) => {
    await login(page, OGULCAN);
    await goToCreateRequest(page);
  });

  test("create request appears as outgoing Pending", async ({ page }) => {
    const note = `E2E create ${Date.now()}`;
    await login(page, OGULCAN);
    await goToCreateRequest(page);
    await page.getByTestId("create-recipient").fill(AYCA);
    await page.getByTestId("create-amount").fill("42.00");
    await page.locator("#note").fill(note);
    await page.getByTestId("create-submit").click();
    await expect(page.getByTestId("request-reference-code")).toContainText(/PR-\d{8}-\d{4}/);
    await expect(page.getByTestId("create-share-link")).toBeVisible();

    await page.goto("/dashboard");
    const outgoing = requestTable(page.getByTestId("dashboard-outgoing"));
    const row = outgoing.locator("tr", { hasText: note });
    await expect(row).toBeVisible();
    await expect(row.locator(".badge--pending")).toBeVisible();
  });

  test("recipient pays with loading and both see Paid; sender wallet credited", async ({ page }) => {
    const note = `E2E pay ${Date.now()}`;
    await login(page, OGULCAN);
    const balanceBefore = await parseWalletMinor(page);

    await goToCreateRequest(page);
    await page.getByTestId("create-recipient").fill(AYCA);
    await page.getByTestId("create-amount").fill("42.00");
    await page.locator("#note").fill(note);
    await page.getByTestId("create-submit").click();
    await page.goto("/dashboard");

    await page.getByRole("button", { name: "Log out" }).click();
    await expect(page).toHaveURL(/\/login/);
    await login(page, AYCA);

    const incoming = requestTable(page.getByTestId("dashboard-incoming"));
    const row = incoming.locator("tr", { hasText: note });
    await expect(row).toBeVisible();
    const payButton = row.getByTestId("pay-button");
    await payButton.click();
    await expect(page.getByTestId("action-overlay")).toContainText("Paying");
    await expect(page.getByTestId("action-overlay")).toBeHidden({ timeout: 10_000 });
    await dismissActionResultModal(page, /Payment successful/i, /PR-\d{8}-\d{4}/);
    await expect(row.locator(".badge--paid")).toBeVisible({ timeout: 15_000 });

    await page.getByRole("button", { name: "Log out" }).click();
    await expect(page).toHaveURL(/\/login/);
    await login(page, OGULCAN);

    const balanceAfter = await parseWalletMinor(page);
    expect(balanceAfter).toBeGreaterThanOrEqual(balanceBefore + 4200);

    await page.getByTestId("status-filter").selectOption("paid");
    await expect(requestTable(page.getByTestId("dashboard-outgoing")).getByText(note)).toBeVisible();
  });

  test("recipient declines pending request", async ({ page }) => {
    await login(page, OGULCAN);
    const incoming = requestTable(page.getByTestId("dashboard-incoming"));
    const row = incoming.locator("tr", { hasText: "E2E decline target" });
    await expect(row).toBeVisible();
    const decline = row.getByTestId("decline-button");
    await decline.click();
    await expect(page.getByTestId("action-overlay")).toContainText("Declining");
    await expect(page.getByTestId("action-overlay")).toBeHidden({ timeout: 10_000 });
    await dismissActionResultModal(page, /declined successfully/i);
    await expect(row.locator(".badge--declined")).toBeVisible({ timeout: 15_000 });
  });

  test("sender cancels outgoing pending request", async ({ page }) => {
    await login(page, OGULCAN);
    const outgoing = requestTable(page.getByTestId("dashboard-outgoing"));
    const row = outgoing.locator("tr", { hasText: "E2E cancel target" });
    await expect(row).toBeVisible();
    const cancel = row.getByTestId("cancel-button");
    await cancel.click();
    await expect(page.getByTestId("action-overlay")).toContainText("Cancelling");
    await expect(page.getByTestId("action-overlay")).toBeHidden({ timeout: 10_000 });
    await dismissActionResultModal(page, /cancelled successfully/i);
    await expect(row.locator(".badge--cancelled")).toBeVisible({ timeout: 15_000 });
  });

  test("expired request cannot be paid", async ({ page }) => {
    await login(page, OGULCAN);
    const incoming = requestTable(page.getByTestId("dashboard-incoming"));
    const row = incoming.locator("tr", { hasText: "Expired sample" });
    await expect(row).toBeVisible();
    await expect(row.locator(".badge--expired")).toBeVisible();
    await expect(row.getByTestId("pay-button")).toHaveCount(0);
  });

  test("dashboard status filter works", async ({ page }) => {
    await login(page, OGULCAN);
    const outgoing = requestTable(page.getByTestId("dashboard-outgoing"));
    await page.getByTestId("status-filter").selectOption("paid");
    await expect(outgoing.getByText("Paid request")).toBeVisible({ timeout: 10_000 });
    await expect(outgoing.getByText("Dinner split")).toHaveCount(0, { timeout: 10_000 });
    await expect(outgoing.locator("tr", { hasText: "E2E cancel target" })).toHaveCount(0);
  });

  test("dashboard search works", async ({ page }) => {
    await login(page, OGULCAN);
    await page.getByTestId("request-search").fill("Dinner split");
    await expect(
      requestTable(page.getByTestId("dashboard-outgoing")).getByText("Dinner split"),
    ).toBeVisible({
      timeout: 5000,
    });
  });

});
