#!/usr/bin/env bash
# Verify metrics endpoint, Prometheus scrape, and optional Grafana API.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_BASE="${API_BASE:-http://localhost:8000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"

pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

log() { printf '\n==> %s\n' "$*"; }

log "1) Metrics endpoint"
metrics_body="$(curl -fsS "${API_BASE}/metrics")"
echo "${metrics_body}" | head -20
echo "${metrics_body}" | grep -q 'http_requests_total' || fail "http_requests_total missing"
echo "${metrics_body}" | grep -q 'http_request_duration_seconds' || fail "histogram missing"
echo "${metrics_body}" | grep -q 'request_count_by_endpoint' || fail "endpoint counter missing"
echo "${metrics_body}" | grep -q 'error_count' || fail "error_count missing"
pass "metrics endpoint exposes required series"

log "2) Prometheus targets"
if curl -fsS "${PROMETHEUS_URL}/-/healthy" >/dev/null 2>&1; then
  targets_json="$(curl -fsS "${PROMETHEUS_URL}/api/v1/targets")"
  echo "${targets_json}" | grep -q '"health":"up"' || fail "no healthy prometheus targets"
  pass "prometheus target is UP"

  log "3) Prometheus query — request rate"
  query='sum(rate(http_requests_total[1m]))'
  result="$(curl -fsS --get "${PROMETHEUS_URL}/api/v1/query" --data-urlencode "query=${query}")"
  echo "${result}" | head -c 500
  echo
  pass "prometheus query executed"
else
  echo "SKIP: Prometheus not reachable at ${PROMETHEUS_URL}"
fi

log "4) Grafana provisioning"
if curl -fsS "${GRAFANA_URL}/api/health" >/dev/null 2>&1; then
  dashboards="$(curl -fsS -u admin:admin "${GRAFANA_URL}/api/search?query=API%20Observability")"
  echo "${dashboards}"
  echo "${dashboards}" | grep -q 'API Observability' || fail "dashboard not provisioned"
  pass "grafana dashboard provisioned"
else
  echo "SKIP: Grafana not reachable at ${GRAFANA_URL}"
fi

log "Verification complete"
