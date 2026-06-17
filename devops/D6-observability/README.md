# Overview

Evaluation task **D6** adds observability to the **B4 FastAPI transaction service**:

- **Structured JSON logging** per request
- **Prometheus metrics** at `GET /metrics`
- **Prometheus** scraper (Docker Compose)
- **Grafana** with auto-provisioned datasource and dashboard

**Service:** `devops/D6-observability/service/` (B4-based instrumented API)

# Start Stack

Requires Docker Desktop.

```bash
cd devops/D6-observability
docker compose up -d
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin / admin) |

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

http://localhost:3000 — dashboard **API Observability** (folder D6)

Primary panel: **Request Rate** — `sum(rate(http_requests_total[1m]))`

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
