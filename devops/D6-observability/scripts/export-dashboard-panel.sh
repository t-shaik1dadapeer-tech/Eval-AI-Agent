#!/usr/bin/env bash
# Export live Grafana panel JSON when D6 stack is running (PML D6 rubric: screenshot or JSON)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/docs/DASHBOARD_PANEL_LIVE.json"
GRAFANA="${GRAFANA_URL:-http://127.0.0.1:3000}"
DS_UID="${PROM_DS_UID:-prometheus}"

if ! curl -sf "$GRAFANA/api/health" >/dev/null 2>&1; then
  echo "Grafana not reachable at $GRAFANA — start stack: bash devops/D6-observability/scripts/start-stack.sh"
  exit 1
fi

# Query Prometheus via Grafana datasource proxy for http_requests_total (proves live panel data)
QUERY='sum(rate(http_requests_total[1m]))'
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$QUERY'''))")
curl -sf "$GRAFANA/api/datasources/uid/$DS_UID/resources/api/v1/query?query=$ENCODED" \
  | python3 -m json.tool > "$OUT"

echo "Wrote live panel query result to docs/DASHBOARD_PANEL_LIVE.json"
python3 -c "import json; d=json.load(open('$OUT')); print('series:', len(d.get('data',{}).get('result',[])))"
