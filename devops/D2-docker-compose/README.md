# D2 — Multi-Service Docker Compose Stack

Three-service transaction processing stack:

```
FastAPI API → PostgreSQL ← Node.js Worker
```

---

## Overview

| Service | Technology | Port | Role |
|---------|------------|------|------|
| `api` | FastAPI + psycopg2 | `8200` | HTTP ingestion, list transactions |
| `postgres` | PostgreSQL 16 | `5432` | Persistent storage |
| `worker` | Node.js + `pg` | — | Polls `PENDING` rows, marks `PROCESSED` |

**Flow:** `POST /transactions` → DB (`PENDING`) → worker polls → `PROCESSED` → verified by e2e tests.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Colima + Docker CLI
- Docker Compose v2 (`docker compose`)
- `curl`, `bash`

Validate compose file without Docker:

```bash
./scripts/validate-compose.sh
```

---

## Start Stack

```bash
cd devops/D2-docker-compose
docker compose up -d --build
docker compose ps
```

Wait until all services are `healthy`.

---

## Seed Data

```bash
./scripts/seed_data.sh
```

Inserts `seed-txn-001` and `seed-txn-002` via the API and verifies via `GET /transactions`.

---

## Run E2E Tests

Full automated test (starts stack, health check, create, DB verify, worker verify):

```bash
./scripts/e2e_test.sh
```

Expected final line:

```
[e2e] ALL TESTS PASSED
```

---

## View Logs

```bash
docker compose logs api
docker compose logs worker
docker compose logs postgres
```

---

## Teardown

```bash
./scripts/teardown.sh
# or
docker compose down -v
```

Removes containers and the `postgres_data` volume.

---

## Rebuild From Scratch

```bash
docker compose down -v
docker compose up -d --build
./scripts/e2e_test.sh
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | `{"status":"UP"}` |
| `POST` | `/transactions` | Create transaction (`transaction_id`, `amount`) |
| `GET` | `/transactions` | List all transactions |

### Example

```bash
curl -X POST http://localhost:8200/transactions \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"txn-001","amount":1000}'

curl http://localhost:8200/transactions
```

---

## Project layout

```
D2-docker-compose/
├── docker-compose.yml
├── api/          # FastAPI service
├── worker/       # Node.js poller
├── database/     # init.sql
├── scripts/      # seed, e2e, teardown
└── docs/         # STACK_REPORT.md
```

See `docs/STACK_REPORT.md` for verification evidence.
