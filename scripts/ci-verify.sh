#!/usr/bin/env bash
# Local verification mirror of .github/workflows/ci.yml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Python tests ==="
for service in \
  beginner/B4-fastapi-service \
  intermediate/I4-polyglot-service-pair/fastapi-service \
  advanced/A3-polyglot-system/fastapi-service; do
  echo "--- $service ---"
  (cd "$service" && pip install -q -r requirements.txt && pytest -v)
done

echo ""
echo "=== Rust tests ==="
for service in \
  beginner/B6-rust-log-analyzer \
  advanced/A3-polyglot-system/rust-engine; do
  echo "--- $service ---"
  (cd "$service" && cargo test -q)
done

echo ""
echo "=== Node tests ==="
export FRAUD_SYSTEM_ROOT="$ROOT/advanced/A3-polyglot-system"
export RUST_ENGINE_BIN="$ROOT/advanced/A3-polyglot-system/rust-engine/target/release/fraud-engine"

(cd advanced/A3-polyglot-system/rust-engine && cargo build --release -q)

for service in \
  beginner/B5-nodejs-api \
  intermediate/I4-polyglot-service-pair/node-client \
  advanced/A3-polyglot-system/node-worker; do
  echo "--- $service ---"
  (cd "$service" && npm ci --silent && npm test)
done

echo ""
echo "=== CI verification PASSED ==="
