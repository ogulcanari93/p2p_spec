# Push to GitHub (ogulcanari93/p2p_spec)

Do this **after** local tests pass and (recommended) live demo is deployed.

## 1. What to include

| Include | Path |
|---------|------|
| Spec Kit spec & plan | `specs/001-p2p-payment-request/` |
| Spec Kit tooling (optional but recommended) | `.specify/`, `.cursor/skills/` |
| Backend | `backend/` (not `.venv/`, not `data/`) |
| Frontend source | `frontend/src/`, configs — not `node_modules/` or `dist/` |
| E2E suite | `e2e/` (not `node_modules/`, `test-results/`) |
| Demo video | `docs/demo/walkthrough.webm` |
| Deploy config | `render.yaml`, `docs/DEPLOY.md` |

## 2. Pre-push checks

```bash
cd backend && source .venv/bin/activate && pytest -v
cd ../frontend && npm run build
cd ../e2e && npm run test
```

## 3. Connect remote and push

```bash
cd /path/to/p2p-payment-request
git remote add origin https://github.com/ogulcanari93/p2p_spec.git
# or: git remote set-url origin https://github.com/ogulcanari93/p2p_spec.git

git add specs/ backend/ frontend/ e2e/ docs/ render.yaml README.md .gitignore .vscode/
git add .specify/ .cursor/skills/   # if you want Spec Kit files in the repo
git status   # review — no secrets, no .venv, no node_modules

git commit -m "P2P payment requests: Spec Kit prototype with E2E and demo"
git push -u origin main
```

Use `master` instead of `main` if that is your default branch on GitHub.

## 4. After push

1. Deploy on Render — [docs/DEPLOY.md](./DEPLOY.md)
2. Paste live URL into `README.md` → **Live demo**
3. Confirm repo is **Public** on GitHub
