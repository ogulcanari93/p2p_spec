const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

function resolvePython(backendDir) {
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
  throw new Error(
    "Python not found. Create backend venv: cd backend && python -m venv .venv && pip install -r requirements.txt",
  );
}

module.exports = async function globalSetup() {
  const e2eDir = __dirname;
  const backendDir = path.resolve(e2eDir, "../backend");
  const python = resolvePython(backendDir);
  const dataDir = path.join(backendDir, "data");
  fs.mkdirSync(dataDir, { recursive: true });

  const result = spawnSync(python, ["seed.py", "--reset"], {
    cwd: backendDir,
    env: {
      ...process.env,
      DATABASE_URL: "sqlite:///./data/e2e.db",
    },
    stdio: "inherit",
  });

  if (result.status !== 0) {
    throw new Error(`seed.py --reset failed (exit ${result.status ?? "unknown"})`);
  }
};
