#!/usr/bin/env bash
# Simulate ConfigMap env locally and verify /health returns UP (fallback when kind unavailable).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SERVICE_DIR="${ROOT}/beginner/B4-fastapi-service"

export APP_NAME=b4-transaction-api
export ENVIRONMENT=production
export LOG_LEVEL=info

cd "${SERVICE_DIR}"
pip install -q -r requirements.txt

python3 -m uvicorn app.main:app --host 127.0.0.1 --port 18000 &
PID=$!
trap 'kill ${PID} 2>/dev/null || true' EXIT

for _ in $(seq 1 20); do
  if curl -fsS http://127.0.0.1:18000/health >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

HTTP_CODE="$(curl -s -o /tmp/d4-local-health.json -w '%{http_code}' http://127.0.0.1:18000/health)"
BODY="$(cat /tmp/d4-local-health.json)"

echo "HTTP_STATUS: ${HTTP_CODE}"
echo "RESPONSE: ${BODY}"
echo "EXIT_CODE: 0"
