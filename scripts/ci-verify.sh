#!/usr/bin/env bash
# Local verification mirror of .github/workflows/ci.yml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

run() {
  if command -v mise >/dev/null 2>&1; then
    mise exec -- "$@"
  else
    "$@"
  fi
}

if command -v mise >/dev/null 2>&1; then
  eval "$(mise activate bash)"
fi

export FRAUD_SYSTEM_ROOT="${FRAUD_SYSTEM_ROOT:-$ROOT/advanced/A3-polyglot-system}"
export RUST_ENGINE_BIN="${RUST_ENGINE_BIN:-$ROOT/advanced/A3-polyglot-system/rust-engine/target/release/fraud-engine}"

echo "=== Python tests ==="
for service in \
  beginner/B4-fastapi-service \
  intermediate/I4-fastapi-node-pair/fastapi-service \
  advanced/A3-polyglot-system/fastapi-service; do
  echo "--- $service ---"
  (cd "$service" && run python -m pip install -q -r requirements.txt && run pytest -v)
done

echo ""
echo "=== Rust tests ==="
for service in \
  beginner/B6-rust-cli \
  advanced/A3-polyglot-system/rust-engine; do
  echo "--- $service ---"
  (cd "$service" && run cargo test -q)
done

echo ""
echo "=== Node tests ==="
(run cargo build --release -q --manifest-path advanced/A3-polyglot-system/rust-engine/Cargo.toml)

for service in \
  beginner/B5-nodejs-api-cli \
  intermediate/I4-fastapi-node-pair/node-client \
  advanced/A3-polyglot-system/node-worker; do
  echo "--- $service ---"
  (cd "$service" && run npm ci --silent && run npm test)
done

echo ""
echo "=== CI verification PASSED ==="
