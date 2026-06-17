#!/usr/bin/env bash
# Run linters across polyglot services.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"
eval "$(mise activate bash)"

echo "==> Python lint (ruff)"
for service in beginner/B4-fastapi-service; do
  echo "--- ${service} ---"
  (cd "${service}" && mise exec -- ruff check . && mise exec -- ruff format --check .)
done

echo ""
echo "==> Rust lint (fmt + clippy)"
for service in beginner/B6-rust-log-analyzer advanced/A3-polyglot-system/rust-engine; do
  echo "--- ${service} ---"
  (cd "${service}" && mise exec -- cargo fmt --check && mise exec -- cargo clippy -q -- -D warnings)
done

echo ""
echo "=== Lint PASSED ==="
