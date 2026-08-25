#!/usr/bin/env bash
# Release gate: every check the site must pass before it ships, in order.
# Stops at the first failure unless --keep-going. Runs from the repo root.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

usage() {
  cat <<'EOF'
Usage: scripts/gate.sh [--quick] [--keep-going] [--help]

Runs, in order:
  1. .venv/bin/ruff check code solutions          Python lint
  2. .venv/bin/python -m pytest                   every template and solution
  3. npx tsx scripts/check-catalogue.ts           slugs exist, anchors valid, lists deep enough
  4. npx biome check .                            JS/TS lint + format
  5. npx astro check                              types + content-collection schemas
  6. npx astro build                              the build itself
  7. npx tsx scripts/check-links.ts --sample 40   sampled outbound links   (skipped with --quick)

Options:
  --quick       skip step 7 (the only one that needs network)
  --keep-going  run every step even after a failure; exit code still 1
  -h, --help    show this help
EOF
}

QUICK=0
KEEP_GOING=0
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=1 ;;
    --keep-going) KEEP_GOING=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "gate.sh: unknown option '$arg'" >&2; usage >&2; exit 2 ;;
  esac
done

FAILED=0
STEP=0

run() {
  local name="$1"; shift
  STEP=$((STEP + 1))
  printf '\n\033[1m── %d. %s\033[0m\n' "$STEP" "$name"
  if "$@"; then
    printf '\033[32m   ok\033[0m\n'
  else
    printf '\033[31m   FAILED: %s\033[0m\n' "$name"
    FAILED=1
    [ "$KEEP_GOING" -eq 1 ] || { printf '\n\033[31mGate failed at step %d.\033[0m\n' "$STEP"; exit 1; }
  fi
}

if [ ! -x .venv/bin/python ]; then
  echo "No .venv — run: uv venv .venv -p 3.12 && uv pip install --python .venv/bin/python pytest ruff" >&2
  exit 1
fi

run "ruff"            .venv/bin/ruff check code solutions
run "pytest"          .venv/bin/python -m pytest
run "catalogue"       npx tsx scripts/check-catalogue.ts
run "biome"           npx biome check .
run "astro check"     npx astro check
run "astro build"     npx astro build
if [ "$QUICK" -eq 0 ]; then
  run "links"         npx tsx scripts/check-links.ts --sample 40
fi

if [ "$FAILED" -eq 0 ]; then
  printf '\n\033[32mGate passed.\033[0m\n'
else
  printf '\n\033[31mGate failed.\033[0m\n'
  exit 1
fi
