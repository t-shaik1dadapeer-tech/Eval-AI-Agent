#!/usr/bin/env bash
# Generate HTTP traffic against the D6 API for 45 seconds.
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
DURATION_SEC="${DURATION_SEC:-45}"

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }

log "Generating traffic to ${API_BASE} for ${DURATION_SEC}s"

end=$((SECONDS + DURATION_SEC))
count=0

while (( SECONDS < end )); do
  curl -fsS -o /dev/null "${API_BASE}/health" || true
  count=$((count + 1))

  curl -fsS -o /dev/null -X POST "${API_BASE}/transactions" \
    -H 'Content-Type: application/json' \
    -d '{"type":"credit","amount":10.5,"description":"load-test"}' || true
  count=$((count + 1))

  curl -fsS -o /dev/null "${API_BASE}/balance" || true
  count=$((count + 1))

  curl -s -o /dev/null -w "" "${API_BASE}/transactions/00000000-0000-0000-0000-000000000000" || true
  count=$((count + 1))

  sleep 0.2
done

log "Completed ${count} requests"
echo "TRAFFIC_REQUESTS=${count}"
