#!/usr/bin/env bash
set -euo pipefail

# Simple environment verifier. It loads common .env files if present and
# checks a short list of required variables. Returns exit code 0 when all
# variables are present, otherwise exits with 1 and prints missing vars.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILES=("$ROOT_DIR/.env" "$ROOT_DIR/backend/.env" "$ROOT_DIR/frontend/redmineAgentUI/.env")

for f in "${ENV_FILES[@]}"; do
  if [ -f "$f" ]; then
    # shellcheck disable=SC1090
    set -a
    # shellcheck source=/dev/null
    source "$f"
    set +a
  fi
done

VARS=(OPENROUTER_API_KEY REDMINE_URL REDMINE_API_KEY BACKEND_PORT VITE_API_BASE_URL)
missing=()
for var in "${VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    missing+=("$var")
  fi
done

if [ "${#missing[@]}" -gt 0 ]; then
  echo "Missing environment variables: ${missing[*]}" >&2
  echo "Tip: copy ".env.sample" files to the appropriate locations and fill values." >&2
  exit 1
fi

echo "All required environment variables appear to be set."
