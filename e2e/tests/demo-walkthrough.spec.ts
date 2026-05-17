import { expect, test } from "@playwright/test";
import {
  clickActionAndExpectErrorModal,
  demoPause,
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

/**
 * Single slow-paced tour for docs/demo/walkthrough.webm — run with: npm run demo:record
 */
test.describe("Demo walkthrough (video)", () => {
  test.setTimeout(720_000);

  test("full product tour with edge cases", async ({ page }) => {
    const note = `Demo share pay ${Date.now()}`;

    // —— Login failure ——
    await page.goto("/login");
    await demoPause(page, 1200);
    await page.getByTestId("login-email").fill(OGULCAN);
    await page.getByTestId("login-password").fill("wrong");
    await page.getByTestId("login-submit").click();
    await expect(page.locator(".form-error")).toBeVisible();
    await demoPause(page, 2800);

    // —— Sender dashboard ——
    await page.getByTestId("login-password").fill("1234");
    await page.getByTestId("login-submit").click();
    await expect(page).toHaveURL(/\/dashboard/);
    await demoPause(page, 2500);

    // —— Create: unknown recipient ——
    await submitCreateRequest(page, {
      recipient: "nobody@example.com",
      amount: "50.00",
    });
    await expectCreateFormError(page, /no registered user found/i);
    await demoPause(page, 2800);

    // —— Create: self ——
    await page.getByTestId("create-recipient").fill(OGULCAN);
    await page.getByTestId("create-amount").fill("25.00");
    await page.getByTestId("create-submit").click();
    await expectCreateFormError(page, /yourself/i);
    await demoPause(page, 2800);

    // —— Create: valid + share link ——
    await page.getByTestId("create-recipient").fill(AYCA);
    await page.getByTestId("create-amount").fill("33.00");
    await page.locator("#note").fill(note);
    await page.getByTestId("create-submit").click();
    await expect(page.getByTestId("request-reference-code")).toContainText(/PR-\d{8}-\d{4}/);
    await expect(page.getByTestId("create-share-link")).toBeVisible();
    const shareHref = await page.getByTestId("create-share-link").getAttribute("href");
    const sharePath = sharePathFromUrl(shareHref!);
    await demoPause(page, 3200);

    // —— Public share page (logged out) ——
    await logout(page);
    await page.goto(sharePath);
    await expect(page.getByTestId("share-page")).toBeVisible();
    await demoPause(page, 3000);

    // —— Insufficient balance (mehmet) ——
    await login(page, MEHMET);
    await demoPause(page, 2000);
    const mehmetIncoming = requestTable(page.getByTestId("dashboard-incoming"));
    const bigRow = mehmetIncoming.locator("tr", { hasText: "E2E insufficient balance target" });
    await clickActionAndExpectErrorModal(
      page,
      bigRow.getByTestId("pay-button"),
      /insufficient wallet balance/i,
    );
    await demoPause(page, 3200);

    // —— Pay via share link (ayca) ——
    await logout(page);
    await login(page, AYCA);
    await page.goto(sharePath);
    await expect(page.getByTestId("share-page")).toBeVisible();
    await expect(page.getByTestId("request-reference-code")).toBeVisible();
    await demoPause(page, 2500);
    await page.getByTestId("share-open-details").click();
    await demoPause(page, 2000);
    await page.getByTestId("detail-pay-button").click();
    await expect(page.getByTestId("action-overlay")).toContainText("Paying");
    await expect(page.getByTestId("action-overlay")).toBeHidden({ timeout: 15_000 });
    await dismissActionResultModal(page, /Payment successful/i, /PR-\d{8}-\d{4}/);
    await demoPause(page, 3200);

    // —— Sender sees Paid + filters ——
    await logout(page);
    await login(page, OGULCAN);
    await page.getByTestId("status-filter").selectOption("paid");
    await demoPause(page, 2000);
    await page.getByTestId("request-search").fill(note);
    await expect(requestTable(page.getByTestId("dashboard-outgoing")).getByText(note)).toBeVisible();
    await demoPause(page, 2500);

    // —— Decline incoming ——
    await page.getByTestId("request-search").fill("");
    await page.getByTestId("status-filter").selectOption("all");
    await demoPause(page, 1500);
    const incoming = requestTable(page.getByTestId("dashboard-incoming"));
    const declineRow = incoming.locator("tr", { hasText: "E2E decline target" });
    await declineRow.getByTestId("decline-button").click();
    await expect(page.getByTestId("action-overlay")).toContainText("Declining");
    await expect(page.getByTestId("action-overlay")).toBeHidden({ timeout: 15_000 });
    await dismissActionResultModal(page, /declined successfully/i);
    await demoPause(page, 2800);

    // —— Cancel outgoing ——
    const outgoing = requestTable(page.getByTestId("dashboard-outgoing"));
    const cancelRow = outgoing.locator("tr", { hasText: "E2E cancel target" });
    await cancelRow.getByTestId("cancel-button").click();
    await expect(page.getByTestId("action-overlay")).toContainText("Cancelling");
    await expect(page.getByTestId("action-overlay")).toBeHidden({ timeout: 15_000 });
    await dismissActionResultModal(page, /cancelled successfully/i);
    await demoPause(page, 2800);

    // —— Expired (no pay button) ——
    const expiredRow = incoming.locator("tr", { hasText: "Expired sample" });
    await expect(expiredRow.locator(".badge--expired")).toBeVisible();
    await expect(expiredRow.getByTestId("pay-button")).toHaveCount(0);
    await demoPause(page, 2800);

    // —— Bad share link ——
    await page.goto("/r/invalid-share-token-demo");
    await expect(page.locator(".form-error")).toBeVisible();
    await demoPause(page, 3000);
  });
});
