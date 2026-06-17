#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT/shared/data"
QUEUE_FILE="$DATA_DIR/transactions.json"
PROCESSED_FILE="$DATA_DIR/processed_transactions.json"
RUST_BIN="$ROOT/rust-engine/target/release/fraud-engine"
WORKER_DIR="$ROOT/node-worker"
FASTAPI_DIR="$ROOT/fastapi-service"

echo "=== A3 Integration Test ==="
echo "ROOT=$ROOT"

mkdir -p "$DATA_DIR"
echo '[]' > "$QUEUE_FILE"
echo '[]' > "$PROCESSED_FILE"

echo ""
echo "=== Step 1: Build Rust engine ==="
cd "$ROOT/rust-engine"
cargo build --release
echo "Rust build exit: $?"

echo ""
echo "=== Step 2: Verify Rust CLI ==="
RUST_OUTPUT=$(echo '{"amount":15000,"merchant":"electronics","country":"IN"}' | "$RUST_BIN")
echo "Rust output: $RUST_OUTPUT"

echo ""
echo "=== Step 3: POST transaction via FastAPI TestClient ==="
cd "$FASTAPI_DIR"
export FRAUD_SYSTEM_ROOT="$ROOT"
export TRANSACTIONS_QUEUE_FILE="$QUEUE_FILE"
export PROCESSED_TRANSACTIONS_FILE="$PROCESSED_FILE"

python3 - <<'PY'
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

queue = Path(os.environ["TRANSACTIONS_QUEUE_FILE"])
client = TestClient(app)
response = client.post(
    "/transactions",
    json={
        "transaction_id": "txn-001",
        "user_id": "user-123",
        "amount": 15000,
        "merchant": "electronics",
        "country": "IN",
    },
)
print("POST status:", response.status_code)
print("POST body:", response.json())
assert response.status_code == 202

queue_data = json.loads(queue.read_text())
print("Queue entries:", len(queue_data))
assert len(queue_data) == 1
assert queue_data[0]["transaction_id"] == "txn-001"
PY

echo ""
echo "=== Step 4: Run Node worker (once) ==="
cd "$WORKER_DIR"
export FRAUD_SYSTEM_ROOT="$ROOT"
export TRANSACTIONS_QUEUE_FILE="$QUEUE_FILE"
export PROCESSED_TRANSACTIONS_FILE="$PROCESSED_FILE"
export RUST_ENGINE_BIN="$RUST_BIN"
npm run worker:once

echo ""
echo "=== Step 5: Verify processed output ==="
cat "$PROCESSED_FILE"

python3 - <<'PY'
import json
import os
from pathlib import Path

processed = json.loads(Path(os.environ["PROCESSED_TRANSACTIONS_FILE"]).read_text())
assert len(processed) == 1
entry = processed[0]
assert entry["transaction_id"] == "txn-001"
assert entry["risk_score"] == 82
assert entry["risk_level"] == "HIGH"
print("Integration verification: PASSED")
print(json.dumps(entry, indent=2))
PY

echo ""
echo "=== Integration complete ==="
