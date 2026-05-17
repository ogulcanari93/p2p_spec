import { expect, test } from "@playwright/test";
import {
  clickActionAndExpectErrorModal,
  dismissActionResultModal,
  login,
  logout,
  requestTable,
  sharePathFromUrl,
  submitCreateRequest,
  expectCreateFormError,
} from "./helpers";

const OGULCAN = "ogulcan@example.com";
const AYCA = "ayca@example.com";
const MEHMET = "mehmet@example.com";

test.describe.configure({ mode: "serial" });

test.describe("P2P edge cases", () => {
  test("login rejects wrong password", async ({ page }) => {
    await page.goto("/login");
    await page.getByTestId("login-email").fill(OGULCAN);
    await page.getByTestId("login-password").fill("wrong-password");
    await page.getByTestId("login-submit").click();
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator(".form-error")).toContainText(/invalid email or password/i);
  });

  test("create request rejects unknown recipient", async ({ page }) => {
    await login(page, OGULCAN);
    await submitCreateRequest(page, {
      recipient: "not-a-user@example.com",
      amount: "10.00",
      note: "Should fail",
    });
    await expectCreateFormError(page, /no registered user found/i);
  });

  test("create request rejects self as recipient", async ({ page }) => {
    await login(page, OGULCAN);
    await submitCreateRequest(page, {
      recipient: OGULCAN,
      amount: "10.00",
      note: "Self request",
    });
    await expectCreateFormError(page, /yourself/i);
  });

  test("pay fails with insufficient wallet balance", async ({ page }) => {
    await login(page, MEHMET);
    const incoming = requestTable(page.getByTestId("dashboard-incoming"));
    const row = incoming.locator("tr", { hasText: "E2E insufficient balance target" });
    await expect(row).toBeVisible();
    await clickActionAndExpectErrorModal(
      page,
      row.getByTestId("pay-button"),
      /insufficient wallet balance/i,
    );
    await expect(row.locator(".badge--pending")).toBeVisible();
  });

  test("invalid share link shows error", async ({ page }) => {
    await page.goto("/r/does-not-exist-token-xyz");
    await expect(page.locator(".form-error")).toContainText(/not found|share/i, { timeout: 10_000 });
  });

  test("recipient pays via public share link", async ({ page }) => {
    const note = `E2E share pay ${Date.now()}`;
    await login(page, OGULCAN);
    await submitCreateRequest(page, {
      recipient: AYCA,
      amount: "33.00",
      note,
    });
    const referenceText = await page.getByTestId("request-reference-code").innerText();
    expect(referenceText).toMatch(/PR-\d{8}-\d{4}/);
    const shareHref = await page.getByTestId("create-share-link").getAttribute("href");
    expect(shareHref).toBeTruthy();
    const sharePath = sharePathFromUrl(shareHref!);

    await logout(page);

    await page.goto(sharePath);
    await expect(page.getByTestId("share-page")).toBeVisible();
    await expect(page.getByText(/log in/i)).toBeVisible();

    await login(page, AYCA);
    await page.goto(sharePath);
    await expect(page.getByTestId("share-page")).toBeVisible();
    await expect(page.getByTestId("request-reference-code")).toContainText(/PR-\d{8}-\d{4}/);
    await expect(page.getByText(note)).toBeVisible();
    await page.getByTestId("share-open-details").click();
    await expect(page).toHaveURL(/\/requests\//);

    await page.getByTestId("detail-pay-button").click();
    await expect(page.getByTestId("action-overlay")).toContainText("Paying");
    await expect(page.getByTestId("action-overlay")).toBeHidden({ timeout: 15_000 });
    await dismissActionResultModal(page, /Payment successful/i, /PR-\d{8}-\d{4}/);
    await expect(page.locator(".badge--paid")).toBeVisible({ timeout: 15_000 });
  });
});
