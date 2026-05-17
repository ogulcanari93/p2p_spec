// @ts-check
const { defineConfig, devices } = require("@playwright/test");
const path = require("node:path");

const e2eDir = __dirname;
const backendDir = path.resolve(e2eDir, "../backend");
const frontendDir = path.resolve(e2eDir, "../frontend");
const python =
  process.platform === "win32"
    ? path.join(backendDir, ".venv", "Scripts", "python.exe")
    : path.join(backendDir, ".venv", "bin", "python");

const e2eApiPort = process.env.E2E_API_PORT || "8001";
const e2eWebPort = process.env.E2E_WEB_PORT || "5174";

const backendCmd =
  process.platform === "win32"
    ? `cd /d "${backendDir}" && set DATABASE_URL=sqlite:///./data/e2e.db && "${python}" -m uvicorn app.main:app --host 127.0.0.1 --port ${e2eApiPort}`
    : `cd "${backendDir}" && export DATABASE_URL=sqlite:///./data/e2e.db && "${python}" -m uvicorn app.main:app --host 127.0.0.1 --port ${e2eApiPort}`;

const frontendCmd =
  process.platform === "win32"
    ? `cd /d "${frontendDir}" && set VITE_API_TARGET=http://127.0.0.1:${e2eApiPort} && set VITE_DEV_PORT=${e2eWebPort} && npm run dev -- --host 127.0.0.1 --port ${e2eWebPort}`
    : `cd "${frontendDir}" && export VITE_API_TARGET=http://127.0.0.1:${e2eApiPort} && export VITE_DEV_PORT=${e2eWebPort} && npm run dev -- --host 127.0.0.1 --port ${e2eWebPort}`;

module.exports = defineConfig({
  testDir: path.join(e2eDir, "tests"),
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  timeout: 90_000,
  expect: { timeout: 15_000 },
  reporter: [["list"], ["html", { open: "never", outputFolder: path.join(e2eDir, "playwright-report") }]],
  outputDir: path.join(e2eDir, "test-results"),
  globalSetup: path.join(e2eDir, "global-setup.js"),
  use: {
    baseURL: `http://127.0.0.1:${e2eWebPort}`,
    trace: "on-first-retry",
    video: "on",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      testIgnore: ["**/mobile-dashboard.spec.ts", "**/demo-walkthrough.spec.ts"],
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "demo",
      testMatch: "**/demo-walkthrough.spec.ts",
      use: {
        ...devices["Desktop Chrome"],
        launchOptions: { slowMo: 250 },
        video: { mode: "on", size: { width: 1280, height: 720 } },
      },
    },
    {
      name: "mobile",
      testMatch: "**/mobile-dashboard.spec.ts",
      use: {
        browserName: "chromium",
        viewport: { width: 390, height: 844 },
      },
    },
  ],
  webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? undefined
    : [
        {
          command: backendCmd,
          url: `http://127.0.0.1:${e2eApiPort}/health`,
          reuseExistingServer: false,
          timeout: 120_000,
        },
        {
          command: frontendCmd,
          url: `http://127.0.0.1:${e2eWebPort}`,
          reuseExistingServer: false,
          timeout: 120_000,
        },
      ],
});
