#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
E2E="$ROOT/e2e"
OUT="$ROOT/docs/demo/walkthrough.webm"

cd "$E2E"
npm run demo:record

LATEST="$(find test-results -path '*demo-walkthrough*' -name video.webm 2>/dev/null | head -1)"
if [[ -z "$LATEST" ]]; then
  LATEST="$(find test-results -name video.webm -newer "$E2E/package.json" 2>/dev/null | head -1)"
fi
if [[ -z "$LATEST" ]]; then
  echo "No demo video.webm under e2e/test-results" >&2
  exit 1
fi
cp "$LATEST" "$OUT"
echo "Wrote $OUT ($(du -h "$OUT" | cut -f1))"
