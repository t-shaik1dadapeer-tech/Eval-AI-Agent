#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE="${COMPOSE_CMD:-docker compose}"
API_URL="${API_URL:-http://localhost:8200}"
TXN_ID="e2e-txn-$(date +%s)"
AMOUNT=1000
MAX_WAIT=90

log() {
  echo "[e2e] $*"
}

fail() {
  echo "[e2e] FAIL: $*" >&2
  exit 1
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    fail "docker CLI not found — install Docker Desktop or Colima to run e2e tests"
  fi
}

wait_for_api() {
  local attempt=1
  while [ "$attempt" -le "$MAX_WAIT" ]; do
    if curl -fsS "${API_URL}/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
    attempt=$((attempt + 1))
  done
  fail "API health check timed out"
}

wait_for_processed() {
  local attempt=1
  while [ "$attempt" -le "$MAX_WAIT" ]; do
    local status
    status=$($COMPOSE exec -T postgres psql -U d2user -d transactions -tAc \
      "SELECT status FROM transactions WHERE transaction_id='${TXN_ID}';" | tr -d '[:space:]')
    if [ "$status" = "PROCESSED" ]; then
      log "transaction ${TXN_ID} status=PROCESSED"
      return 0
    fi
    log "waiting for worker (status='${status}', attempt ${attempt}/${MAX_WAIT})"
    sleep 2
    attempt=$((attempt + 1))
  done
  fail "worker did not process ${TXN_ID}"
}

main() {
  require_docker
  log "=== D2 End-to-End Test Suite ==="

  log "Step 1: Start stack"
  $COMPOSE up -d --build
  $COMPOSE ps

  log "Step 2: Verify health endpoint"
  wait_for_api
  health=$(curl -fsS "${API_URL}/health")
  log "health response: ${health}"
  echo "$health" | grep -q '"status":"UP"' || fail "health response invalid"

  log "Step 3: Create transaction ${TXN_ID}"
  create_resp=$(curl -fsS -X POST "${API_URL}/transactions" \
    -H "Content-Type: application/json" \
    -d "{\"transaction_id\":\"${TXN_ID}\",\"amount\":${AMOUNT}}")
  log "create response: ${create_resp}"

  log "Step 4: Verify database insert"
  db_row=$($COMPOSE exec -T postgres psql -U d2user -d transactions -tAc \
    "SELECT transaction_id, amount, status FROM transactions WHERE transaction_id='${TXN_ID}';")
  log "database row: ${db_row}"
  echo "$db_row" | grep -q "${TXN_ID}" || fail "database insert not found"
  echo "$db_row" | grep -q "PENDING" || fail "expected initial status PENDING"

  log "Step 5: Verify worker processing"
  wait_for_processed

  log "Step 6: Verify via API list"
  list_resp=$(curl -fsS "${API_URL}/transactions")
  echo "$list_resp" | grep -q "${TXN_ID}" || fail "transaction missing from API list"
  echo "$list_resp" | grep -q "PROCESSED" || fail "PROCESSED status not visible in API"

  log "Step 7: Collect communication logs"
  echo "--- API logs (tail) ---"
  $COMPOSE logs --no-color api | tail -20
  echo "--- Worker logs (tail) ---"
  $COMPOSE logs --no-color worker | tail -20
  echo "--- Postgres logs (tail) ---"
  $COMPOSE logs --no-color postgres | tail -10

  log "ALL TESTS PASSED"
}

main "$@"
