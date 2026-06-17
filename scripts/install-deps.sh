#!/usr/bin/env bash
# Install language runtimes (mise) and project dependencies.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v mise >/dev/null 2>&1; then
  echo "mise not found — run: bash scripts/install-mise.sh" >&2
  exit 1
fi

echo "==> Installing pinned runtimes (mise)..."
mise trust -y 2>/dev/null || mise trust
mise install

# shellcheck disable=SC1090
eval "$(mise activate bash)"

echo "==> Runtime versions"
mise current

PYTHON_SERVICES=(
  beginner/B4-fastapi-service
  intermediate/I4-fastapi-node-pair/fastapi-service
  advanced/A3-polyglot-system/fastapi-service
)

NODE_SERVICES=(
  beginner/B5-nodejs-api-cli
  intermediate/I4-fastapi-node-pair/node-client
  advanced/A3-polyglot-system/node-worker
)

RUST_SERVICES=(
  beginner/B6-rust-cli
  advanced/A3-polyglot-system/rust-engine
)

echo ""
echo "==> Python dependencies"
mise exec -- python -m pip install --upgrade pip
mise exec -- python -m pip install -r requirements-dev.txt
for service in "${PYTHON_SERVICES[@]}"; do
  echo "--- ${service} ---"
  (cd "${service}" && mise exec -- python -m pip install -r requirements.txt)
done

echo ""
echo "==> Rust dependencies (fetch + release build for A3 node tests)"
for service in "${RUST_SERVICES[@]}"; do
  echo "--- ${service} ---"
  (cd "${service}" && mise exec -- cargo fetch -q)
done
mise exec -- cargo build --release -q --manifest-path advanced/A3-polyglot-system/rust-engine/Cargo.toml

echo ""
echo "==> Node dependencies"
for service in "${NODE_SERVICES[@]}"; do
  echo "--- ${service} ---"
  (cd "${service}" && mise exec -- npm ci --silent)
done

echo ""
echo "==> Install complete"
