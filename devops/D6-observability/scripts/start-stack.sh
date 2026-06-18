#!/usr/bin/env bash
# Start D6 stack and wait until Grafana is ready.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_PORT="${API_PORT:-8000}"
GRAFANA_PORT="${GRAFANA_PORT:-3002}"
export API_HOST_PORT="$API_PORT"
export GRAFANA_HOST_PORT="$GRAFANA_PORT"

GRAFANA_URL="http://127.0.0.1:${GRAFANA_PORT}"
API_BASE="http://127.0.0.1:${API_PORT}"

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }

is_d6_api() {
  local base="$1"
  curl -fsS "${base}/metrics" 2>/dev/null | grep -q 'http_requests_total'
}

find_free_port() {
  local port="$1"
  while lsof -iTCP:"${port}" -sTCP:LISTEN -P -n >/dev/null 2>&1; do
    port=$((port + 1))
  done
  echo "${port}"
}

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker not found."
  echo "Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
  echo "Grafana dashboards cannot run without Docker."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon is not running. Start Docker Desktop, then retry."
  exit 1
fi

# Auto-pick a free port if the default is taken by another local app
if lsof -iTCP:"${API_PORT}" -sTCP:LISTEN -P -n >/dev/null 2>&1 && ! is_d6_api "${API_BASE}"; then
  new_port="$(find_free_port "${API_PORT}")"
  log "Port ${API_PORT} is in use by another app — using ${new_port} instead"
  API_PORT="${new_port}"
  API_BASE="http://127.0.0.1:${API_PORT}"
  export API_HOST_PORT="$API_PORT"
fi

log "Starting D6 stack (API :${API_PORT}, Grafana :${GRAFANA_PORT})"
docker compose up -d --build

log "Waiting for API ${API_BASE}/health"
for _ in $(seq 1 30); do
  if curl -fsS "${API_BASE}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS "${API_BASE}/health" >/dev/null || {
  echo "ERROR: D6 API did not become healthy on port ${API_PORT}"
  docker compose ps
  exit 1
}
is_d6_api "${API_BASE}" || {
  echo "ERROR: Port ${API_PORT} is not serving the D6 API (check for local apps on the same port)."
  lsof -iTCP:"${API_PORT}" -sTCP:LISTEN -P -n | head -5
  exit 1
}

log "Waiting for Grafana ${GRAFANA_URL}"
for _ in $(seq 1 45); do
  if curl -fsS "${GRAFANA_URL}/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS "${GRAFANA_URL}/api/health" >/dev/null || {
  echo "ERROR: Grafana did not start on port ${GRAFANA_PORT}"
  docker compose logs grafana --tail 30
  exit 1
}

echo
echo "Stack is ready."
echo "  Grafana:    ${GRAFANA_URL}  (admin / admin)"
echo "  Dashboard:  folder D6 → API Observability"
echo "  API:        ${API_BASE}"
echo "  Prometheus: http://127.0.0.1:9090"
echo
echo "Generate traffic: API_BASE=${API_BASE} ./scripts/generate_load.sh"
echo "Verify metrics:   API_BASE=${API_BASE} ./scripts/verify_metrics.sh"
echo "Check status:     API_PORT=${API_PORT} ./scripts/check-stack.sh"

if [[ "$(uname -s)" == "Darwin" ]] && command -v open >/dev/null 2>&1; then
  open "${GRAFANA_URL}"
fi
