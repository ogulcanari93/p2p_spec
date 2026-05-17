import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { expect, type Locator, type Page } from "@playwright/test";

const backendDir = path.resolve(__dirname, "../../backend");

function resolvePython(): string {
  const candidates = [
    path.join(backendDir, ".venv", "bin", "python"),
    path.join(backendDir, ".venv", "Scripts", "python.exe"),
    "python3",
    "python",
  ];
  for (const candidate of candidates) {
    if (candidate.includes(path.sep) || candidate.includes("/")) {
      if (fs.existsSync(candidate)) return candidate;
    } else {
      const result = spawnSync(candidate, ["--version"], { encoding: "utf8" });
      if (result.status === 0) return candidate;
    }
  }
  throw new Error("Python not found for E2E seed reset.");
}

export function resetE2eDatabase(): void {
  fs.mkdirSync(path.join(backendDir, "data"), { recursive: true });
  const result = spawnSync(resolvePython(), ["seed.py", "--reset"], {
    cwd: backendDir,
    env: { ...process.env, DATABASE_URL: "sqlite:///./data/e2e.db" },
    stdio: "pipe",
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || "seed.py --reset failed");
  }
}

export async function login(page: Page, email: string, password = "1234") {
  await page.goto("/login");
  await page.getByTestId("login-email").fill(email);
  await page.getByTestId("login-password").fill(password);
  await page.getByTestId("login-submit").click();
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByTestId("wallet-summary")).toBeVisible();
}

export async function logout(page: Page) {
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/login/);
}

/** Pause for demo video pacing (ms). */
export async function demoPause(page: Page, ms = 1600) {
  await page.waitForTimeout(ms);
}

export function sharePathFromUrl(shareUrl: string): string {
  const match = shareUrl.match(/\/r\/([^/?#]+)/);
  if (!match) throw new Error(`Not a share URL: ${shareUrl}`);
  return `/r/${match[1]}`;
}

export async function submitCreateRequest(
  page: Page,
  opts: { recipient: string; amount: string; note?: string },
) {
  await goToCreateRequest(page);
  await page.getByTestId("create-recipient").fill(opts.recipient);
  await page.getByTestId("create-amount").fill(opts.amount);
  if (opts.note) await page.locator("#note").fill(opts.note);
  await page.getByTestId("create-submit").click();
}

export async function expectCreateFormError(page: Page, pattern: RegExp) {
  await expect(page.locator(".form-error")).toContainText(pattern, { timeout: 10_000 });
}

export async function parseWalletMinor(page: Page): Promise<number> {
  const amount = page.getByTestId("wallet-summary").locator(".amount");
  await expect(amount).toBeVisible();
  const text = await amount.innerText();
  const match = text.match(/([\d]+(?:[.,]\d{2})?)/);
  if (!match) return 0;
  const normalized = match[1].replace(",", ".");
  return Math.round(parseFloat(normalized) * 100);
}

export async function goToCreateRequest(page: Page) {
  await page.goto("/requests/new");
  await expect(page.getByTestId("destination-select")).toBeVisible();
}

export function requestTable(section: Locator): Locator {
  return section.locator("table.requests-table");
}

/** Pay/decline/cancel when the API may fail quickly (overlay can be skipped). */
export async function clickActionAndExpectErrorModal(page: Page, button: Locator, pattern: RegExp) {
  await button.click();
  const modal = page.getByTestId("action-result-modal");
  await expect(modal).toBeVisible({ timeout: 10_000 });
  await expect(page.getByTestId("action-result-message")).toContainText(pattern);
  await page.getByTestId("action-result-ok").click();
  await expect(modal).toBeHidden();
}

/** Dismiss the in-app success/error modal after an action. */
export async function dismissActionResultModal(
  page: Page,
  messagePattern: RegExp,
  referencePattern?: RegExp,
) {
  const modal = page.getByTestId("action-result-modal");
  await expect(modal).toBeVisible({ timeout: 10_000 });
  await expect(page.getByTestId("action-result-message")).toContainText(messagePattern);
  if (referencePattern) {
    await expect(page.getByTestId("action-result-reference")).toContainText(referencePattern);
  }
  await page.getByTestId("action-result-ok").click();
  await expect(modal).toBeHidden();
}
