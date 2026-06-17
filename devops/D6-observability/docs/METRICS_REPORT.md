# Metrics Added

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | `method`, `path`, `status` | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | `method`, `path` | Request latency (seconds) |
| `request_count_by_endpoint` | Counter | `endpoint` | Per-path request count |
| `error_count` | Counter | `method`, `path`, `status` | Responses with status ≥ 400 |

> **Note:** `prometheus_client` exports counters with a `_total` suffix (e.g. `request_count_by_endpoint_total`).

---

# Metrics Endpoint Verification

**Command:**

```bash
curl http://127.0.0.1:18000/metrics
```

**Output (excerpt, after load):**

```text
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/health",status="200"} 54.0
http_requests_total{method="POST",path="/transactions",status="201"} 53.0
http_requests_total{method="GET",path="/balance",status="200"} 53.0
http_requests_total{method="GET",path="/transactions/not-a-uuid",status="422"} 53.0

request_count_by_endpoint_total{endpoint="/health"} 54.0
request_count_by_endpoint_total{endpoint="/transactions"} 53.0

error_count_total{method="GET",path="/transactions/not-a-uuid",status="422"} 53.0
```

**Exit code:** `0`

**Script verification:**

```bash
API_BASE=http://127.0.0.1:18000 ./scripts/verify_metrics.sh
# PASS: metrics endpoint exposes required series
```

---

# Prometheus Verification

**Configuration:** `monitoring/prometheus/prometheus.yml` scrapes `api:8000/metrics` every 5s.

**Expected targets page** (`http://localhost:9090/targets`):

| Target | State | Labels |
|--------|-------|--------|
| `api:8000` | UP | `job=b4-transaction-api`, `service=b4-transaction-api` |

**Query verification:**

```bash
curl -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=sum(rate(http_requests_total[1m]))'
```

**Local result:** Docker not installed in verification environment — Prometheus/Grafana checks skipped. Full stack runs via `docker compose up -d` when Docker is available.

---

# Traffic Generation

**Command:**

```bash
API_BASE=http://127.0.0.1:18000 DURATION_SEC=15 ./scripts/generate_load.sh
```

**Output:**

```text
[11:09:12] Generating traffic to http://127.0.0.1:18000 for 15s
[11:09:27] Completed 212 requests
TRAFFIC_REQUESTS=212
```

**Endpoints exercised per loop:**

- `GET /health`
- `POST /transactions` (credit)
- `GET /balance`
- `GET /transactions/{missing-uuid}` (404)

**Result:** `http_requests_total` increased from 1 → 214+ during load window.

---

# Structured Log Sample

```json
{"timestamp":"2026-06-17T11:09:12.898439+00:00","method":"POST","path":"/transactions","status":201,"latency_ms":2.54,"request_id":"e639fd5d-cf37-40d5-b483-9a47ab507b1b"}
```

**Library:** Python `logging` (JSON via `json.dumps` in middleware)
