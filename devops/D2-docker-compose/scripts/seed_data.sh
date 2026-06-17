#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE="${COMPOSE_CMD:-docker compose}"
API_URL="${API_URL:-http://localhost:8200}"
MAX_WAIT="${MAX_WAIT:-60}"

log() {
  echo "[seed] $*"
}

wait_for_api() {
  local attempt=1
  while [ "$attempt" -le "$MAX_WAIT" ]; do
    if curl -fsS "${API_URL}/health" >/dev/null 2>&1; then
      log "API healthy at ${API_URL}"
      return 0
    fi
    log "waiting for API (${attempt}/${MAX_WAIT})..."
    sleep 2
    attempt=$((attempt + 1))
  done
  echo "API not ready at ${API_URL}" >&2
  return 1
}

seed_transaction() {
  local txn_id="$1"
  local amount="$2"
  local response
  response=$(curl -fsS -X POST "${API_URL}/transactions" \
    -H "Content-Type: application/json" \
    -d "{\"transaction_id\":\"${txn_id}\",\"amount\":${amount}}")
  log "seeded ${txn_id}: ${response}"
}

main() {
  log "starting seed against ${API_URL}"
  wait_for_api

  seed_transaction "seed-txn-001" 500
  seed_transaction "seed-txn-002" 1200

  log "verifying seeded transactions via GET /transactions"
  curl -fsS "${API_URL}/transactions" | tee /tmp/d2-seed-list.json
  echo

  if grep -q "seed-txn-001" /tmp/d2-seed-list.json && grep -q "seed-txn-002" /tmp/d2-seed-list.json; then
    log "seed verification PASSED"
  else
    echo "seed verification FAILED" >&2
    exit 1
  fi
}

main "$@"
