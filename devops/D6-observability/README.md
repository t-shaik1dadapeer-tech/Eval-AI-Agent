# Overview

Evaluation task **D6** adds observability to the **B4 FastAPI transaction service**:

- **Structured JSON logging** per request
- **Prometheus metrics** at `GET /metrics`
- **Prometheus** scraper (Docker Compose)
- **Grafana** with auto-provisioned datasource and dashboard

**Service:** `devops/D6-observability/service/` (B4-based instrumented API)

# Start Stack

Requires **Docker Desktop** (running).

```bash
cd devops/D6-observability
./scripts/start-stack.sh
```

This starts API, Prometheus, and Grafana, waits until healthy, and opens Grafana in your browser.

| Service | URL |
|---------|-----|
| **Grafana (dashboards)** | http://localhost:3002 (admin / admin) |
| API | http://localhost:8000 |
| Prometheus | http://localhost:9090 |

> Grafana is on **port 3002** (not 3000) to avoid conflicts with other local apps.

**Troubleshooting:** run `./scripts/check-stack.sh` if a URL does not load.

Manual start:

```bash
docker compose up -d --build
```

# Generate Traffic

```bash
./scripts/generate_load.sh
```

Optional: `API_BASE=http://localhost:8000 DURATION_SEC=45 ./scripts/generate_load.sh`

# Verify Metrics

```bash
curl http://localhost:8000/metrics
./scripts/verify_metrics.sh
```

# Access Prometheus

http://localhost:9090/targets — verify `b4-transaction-api` target is **UP**

Query example:

```promql
sum(rate(http_requests_total[1m]))
```

# Access Grafana

http://localhost:3002 — dashboard **API Observability** (folder D6)

Login: `admin` / `admin`

Primary panel: **Request Rate** — `sum(rate(http_requests_total[1m]))`

> **Do not** open http://localhost:8000/ expecting Grafana — that is the API.
> If you see `{"error":"Not found","path":"/"}`, you hit the wrong port or another app.

# Local Development (no Docker)

```bash
cd service
pip install -r requirements.txt
ENVIRONMENT=production uvicorn app.main:app --host 127.0.0.1 --port 18000

# another terminal
API_BASE=http://127.0.0.1:18000 ./scripts/generate_load.sh
curl http://127.0.0.1:18000/metrics
```

# Stop Stack

```bash
docker compose down
```

# Tests

```bash
cd service && pytest -v
```
