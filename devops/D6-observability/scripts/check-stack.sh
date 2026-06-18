#!/usr/bin/env bash
# Diagnose D6 observability stack — ports, Docker, and HTTP probes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_PORT="${API_PORT:-8000}"
GRAFANA_PORT="${GRAFANA_PORT:-3002}"
PROM_PORT="${PROM_PORT:-9090}"

API_BASE="http://127.0.0.1:${API_PORT}"
GRAFANA_URL="http://127.0.0.1:${GRAFANA_PORT}"
PROM_URL="http://127.0.0.1:${PROM_PORT}"

ok() { printf '  OK   %s\n' "$*"; }
warn() { printf '  WARN %s\n' "$*"; }
fail() { printf '  FAIL %s\n' "$*"; }

echo "D6 observability stack check"
echo "  API:        ${API_BASE}"
echo "  Grafana:    ${GRAFANA_URL}"
echo "  Prometheus: ${PROM_URL}"
echo

echo "Docker"
if command -v docker >/dev/null 2>&1; then
  ok "docker found: $(command -v docker)"
  if docker info >/dev/null 2>&1; then
    ok "docker daemon running"
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'd6-grafana'; then
      ok "container d6-grafana is running"
    else
      warn "container d6-grafana not running — run: ./scripts/start-stack.sh"
    fi
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'd6-api'; then
      ok "container d6-api is running"
    else
      warn "container d6-api not running"
    fi
  else
    fail "docker daemon not running — start Docker Desktop"
  fi
else
  fail "docker not installed — Grafana requires Docker Desktop"
fi
echo

echo "Listening ports"
for port in "$API_PORT" "$GRAFANA_PORT" "$PROM_PORT"; do
  if lsof -iTCP:"${port}" -sTCP:LISTEN -P -n >/dev/null 2>&1; then
    ok "port ${port} in use ($(lsof -iTCP:"${port}" -sTCP:LISTEN -P -n | awk 'NR==2{print $1}'))"
  else
    warn "nothing listening on port ${port}"
  fi
done
echo

echo "HTTP probes"
if curl -fsS "${API_BASE}/health" >/dev/null 2>&1; then
  ok "D6 API /health"
else
  fail "D6 API /health — wrong service on ${API_PORT}? Stop other apps and run ./scripts/start-stack.sh"
fi

if curl -fsS "${GRAFANA_URL}/api/health" >/dev/null 2>&1; then
  ok "Grafana /api/health"
else
  fail "Grafana not reachable at ${GRAFANA_URL} — open this URL in your browser (not port 8000)"
fi

if curl -fsS "${PROM_URL}/-/healthy" >/dev/null 2>&1; then
  ok "Prometheus healthy"
else
  warn "Prometheus not reachable at ${PROM_URL}"
fi
echo

echo "Open Grafana:"
echo "  ${GRAFANA_URL}"
echo "  login: admin / admin"
echo "  dashboard: folder D6 → API Observability"
