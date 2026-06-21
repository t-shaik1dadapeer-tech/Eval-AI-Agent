# B2 — API Endpoint Map

**Repository:** `Eval-Ai` (Eval AI Agent)  
**Scan date:** 2026-06-18  
**Scanner scope:** Application source under `beginner/`, `intermediate/`, `advanced/`, `devops/` — FastAPI `@app`/`@router` and Express `app.get`/`router.post` patterns  
**Task output:** `beginner/B2-api-endpoint-map/`

---

## Executive Summary

A full scan found **25 application-defined HTTP routes** across **6 runnable HTTP services**. No GraphQL, WebSocket, or webhook endpoints were detected. **B6** is a Rust CLI only (no HTTP server).

| Metric | Count |
|--------|------:|
| **Total REST routes (application)** | **25** |
| **Services with HTTP APIs** | **6** |
| **Health check endpoints** | **6** (`/health` per service) |
| **Observability endpoints** | **1** (`GET /metrics` on D6) |
| **GraphQL endpoints** | **0** |
| **WebSocket endpoints** | **0** |
| **Webhook endpoints** | **0** |
| **Authenticated endpoints** | **0** (all public in current code) |

**Conclusion:** Transaction-domain APIs repeat in B4, B5, D2, and D6; I4 adds currency conversion; A3 accepts transactions into a file queue. See `endpoints.csv` for the full export.

---

## Services scanned

| Service | Folder | Default port (local) | Routes |
|---------|--------|---------------------|-------:|
| B4 FastAPI | `beginner/B4-fastapi-service/` | 8000 | 6 |
| B5 Express | `beginner/B5-nodejs-api-cli/` | 3001 | 5 |
| I4 FastAPI | `intermediate/I4-fastapi-node-pair/fastapi-service/` | 8000 | 2 |
| A3 FastAPI | `advanced/A3-polyglot-system/fastapi-service/` | 8000 | 2 |
| D2 FastAPI | `devops/D2-docker-compose/api/` | 8200 (compose) | 3 |
| D6 FastAPI | `devops/D6-observability/service/` | 8000/18080 (compose) | 7 |

---

## Scan methodology

| Step | Action | Result |
|------|--------|--------|
| 1 | Grep FastAPI `@app.get/post`, `@router.get/post` | 23 handler definitions |
| 2 | Grep Express `app.get/post`, `router.get/post` | 5 handler definitions |
| 3 | Cross-check B1 inventory controllers | Consistent |
| 4 | Exclude tests, CI fixtures, K8s ingress-only paths | Applied |
| 5 | Export | `endpoints.csv` (25 data rows) |

**Note:** Each FastAPI service also auto-exposes OpenAPI UI at `/docs`, `/redoc`, and `/openapi.json` (framework-generated; not listed in CSV).

---

## API inventory (summary)

### B4 — full transaction CRUD + balance

| Method | Path | Handler | Request | Response |
|--------|------|---------|---------|----------|
| GET | `/` | `root` | — | Service info |
| GET | `/health` | `health_check` | — | `{status}` |
| POST | `/transactions` | `create_transaction` | `TransactionCreate` | `TransactionResponse` |
| GET | `/transactions` | `get_transactions` | — | `list[TransactionResponse]` |
| GET | `/transactions/{transaction_id}` | `get_transaction` | — | `TransactionResponse` |
| GET | `/balance` | `get_balance` | — | `BalanceResponse` |

### B5 — Express mirror (no get-by-id route)

| Method | Path | Handler |
|--------|------|---------|
| GET | `/`, `/health` | App handlers |
| POST | `/transactions` | `createTransaction` |
| GET | `/transactions`, `/balance` | `getTransactions`, `getBalance` |

### I4 — currency conversion

| Method | Path | Handler | Request | Response |
|--------|------|---------|---------|----------|
| GET | `/health` | `health_check` | — | `{status}` |
| POST | `/convert` | `convert_currency` | `ConvertRequest` | `ConvertResponse` |

### A3 — queue ingest only

| Method | Path | Status | Request | Response |
|--------|------|--------|---------|----------|
| GET | `/health` | 200 | — | `{status}` |
| POST | `/transactions` | **202** | `TransactionCreate` | `TransactionAccepted` |

### D2 — Postgres-backed API

| Method | Path | Handler |
|--------|------|---------|
| GET | `/health` | `health_check` |
| POST | `/transactions` | `create_transaction` (201) |
| GET | `/transactions` | `get_transactions` |

### D6 — B4 + observability

Same transaction routes as B4 plus:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/metrics` | Prometheus scrape endpoint |

---

## Authentication analysis

| Category | Count | Notes |
|----------|------:|-------|
| Public endpoints | 25 | No auth middleware on any route |
| Authenticated endpoints | 0 | — |
| API keys / JWT | 0 | — |

---

## Cross-validation with B1

B1 inventory lists **23 controllers** including `create_transaction`, `convert_currency`, and `metrics` across the same file paths referenced in this map. B2 route count aligns with implemented handlers (duplicate handler names across task folders are disambiguated by source path in `endpoints.csv`).

---

## Infrastructure routes (not in CSV)

| Location | Type | Notes |
|----------|------|-------|
| `devops/D4-kubernetes/k8s/ingress.yaml` | Ingress | Routes external traffic to K8s service (not app source) |
| D6 Grafana | HTTP UI | Port 3002 — monitoring UI, not application API |
| D6 Prometheus | HTTP UI | Port 9090 — metrics server |

---

## Verification summary

| Metric | Value |
|--------|------:|
| CSV data rows | 25 |
| HTTP services | 6 |
| Health endpoints | 6 |
| GraphQL / WebSocket / Webhook | 0 |

Full export: **`endpoints.csv`**
