#!/usr/bin/env bash
# Reset local eval config
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EVAL_DIR="$ROOT/.eval"
mkdir -p "$EVAL_DIR"

cat > "$EVAL_DIR/eval-config.json" <<'EOF'
{
  "default_api_id": null,
  "task_api_map": {},
  "output_map": {}
}
EOF

echo "Reset $EVAL_DIR/eval-config.json"
echo "Register APIs: make eval-orch-config API_ID=my-api API_BASE_URL=http://127.0.0.1:8090"
