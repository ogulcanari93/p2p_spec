# Demo walkthrough video

## In-repo recording

[walkthrough.webm](./walkthrough.webm) — slow-paced Playwright tour (`e2e/tests/demo-walkthrough.spec.ts`):

- Wrong password login
- Unknown recipient & self-request errors
- Create request + **public share link** (`/r/...`)
- **Insufficient balance** when paying (mehmet, 5000 TRY request vs 2000 TRY wallet)
- **Pay via share link** → open details → pay success modal
- Dashboard search & status filter
- Decline, cancel, expired request
- Invalid share token

Pacing: `slowMo: 400` + ~2–3s pauses between steps (~2–3 min total).

## Re-record

```bash
./scripts/record-demo.sh
```

Or:

```bash
cd e2e && npm run demo:record
cp test-results/demo-walkthrough-*/video.webm ../docs/demo/walkthrough.webm
```

## Optional: YouTube / Loom

Upload `walkthrough.webm` and add the URL in root `README.md` under **Demo video**.
