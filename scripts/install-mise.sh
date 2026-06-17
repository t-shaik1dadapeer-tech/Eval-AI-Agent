#!/usr/bin/env bash
# Install mise (jdx) when missing — idempotent.
set -euo pipefail

if command -v mise >/dev/null 2>&1; then
  echo "mise already installed: $(mise --version)"
  exit 0
fi

echo "==> Installing mise..."
curl -fsSL https://mise.run | sh

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v mise >/dev/null 2>&1; then
  echo "mise install failed — add ~/.local/bin to PATH and retry" >&2
  exit 1
fi

echo "mise installed: $(mise --version)"
echo "Add to your shell profile: eval \"\$(mise activate bash)\""
