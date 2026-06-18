# B1 — Repository Artifact Inventory

**Repository:** `Evil-Ai` (Eval AI Agent scaffold)  
**Scan date:** 2026-06-17  
**Scanner scope:** Full recursive scan from repository root, excluding `.git/`, `node_modules/`, `target/`, `.venv/`, and `__pycache__/`  
**Task output:** `beginner/B1-repo-artifact-inventory/`

---

## Executive Summary

A complete recursive scan of the `Evil-Ai` repository found **108 classified application artifacts** across **61 non-test source files** (Python, JavaScript, Rust). The repo is a **multi-track exercise monorepo** with implementations in `beginner/`, `intermediate/`, `advanced/`, and `devops/` task folders.

Primary stacks: **FastAPI** (transaction and currency APIs), **Express** (Node.js REST API and workers), and **Rust** (CLI log analyzer and risk-scoring engine). No Java, Go, Kotlin, or C# application code was detected. **Zero interfaces** (no `interface` keyword in TypeScript/Java or Rust traits declared as interfaces).

| Category | Count |
|----------|------:|
| Controllers | 23 |
| Models / Entities | 21 |
| Utility / Helper classes | 25 |
| Services | 14 |
| Configuration classes | 7 |
| Repositories / DAOs | 6 |
| Jobs / Scheduled tasks | 5 |
| Middleware / Filters | 3 |
| Consumers / Listeners | 2 |
| Validators | 1 |
| Classes | 1 |
| Interfaces | 0 |
| **Total classified artifacts** | **108** |

**Conclusion:** The repository has evolved from scaffold-only to a polyglot exercise codebase. Transaction-domain patterns repeat across B4/B5/D2/D6/A3 with in-memory, PostgreSQL, and file-queue persistence variants. See `inventory.csv` for the full machine-readable export.

---

## Architecture Overview

```
Evil-Ai/                              ← Git repository root
├── README.md                         ← Project overview, make bootstrap
├── mise.toml                         ← Pinned runtimes (Python, Node, Rust)
├── beginner/                         ← B1–B6 implementations
│   ├── B4-fastapi-service/           ← FastAPI in-memory transaction API
│   ├── B5-nodejs-api-cli/            ← Express transaction API + CLI
│   └── B6-rust-cli/                  ← Rust log-level analyzer CLI
├── intermediate/
│   └── I4-fastapi-node-pair/         ← Currency conversion API + Node client
├── advanced/
│   └── A3-polyglot-system/           ← FastAPI → file queue → Node worker → Rust scorer
└── devops/
    ├── D1-terraform/                 ← AWS Lambda (Python handler)
    ├── D2-docker-compose/            ← FastAPI + PostgreSQL + polling worker
    └── D6-observability/             ← FastAPI + Prometheus middleware
```

**Observed architecture type:** Multi-track exercise monorepo with per-task isolated services.  
**Runtime topology:** Standalone HTTP APIs, background polling workers, AWS Lambda, and CLI binaries — no unified production deployment.  
**Primary languages:** Python (53 files), JavaScript (19), Rust (9) — excluding virtualenv/build caches.  
**Frameworks detected:** FastAPI, Express, Pydantic, Starlette, psycopg2, serde, Prometheus client.

### Evidence — repository purpose

```1:5:README.md
# Eval AI Agent

Hands-on exercises for evaluating AI coding agents across beginner, intermediate, advanced, and DevOps tracks.

Each subfolder is a self-contained task. Put all deliverables (reports, code, configs) directly in that task folder — not under a separate `docs/` mirror. Then commit and push when ready.
```

---

## Scan Methodology

| Step | Action | Result |
|------|--------|--------|
| 1 | `find . -type f` excluding `.git/`, `node_modules/`, `target/`, `.venv/` | **240** files |
| 2 | Application source glob (`*.py`, `*.js`, `*.rs`) excl. tests | **61** files |
| 3 | Total source incl. tests | **81** files |
| 4 | Pattern extraction | Classes, structs, enums, route handlers, services, middleware, validators, DAO functions, workers |
| 5 | Categorization | 12 taxonomy buckets per B1 spec |
| 6 | Export | `inventory.csv` (108 data rows) |

**Exclusions:** Test files (`tests/`, `*_test.py`, `*.test.js`, `conftest.py`), CI fixtures (`broken_*.py`), dependency trees (`node_modules/`, `.venv/`, `target/`).

---

## Artifact Counts by Category

| Category | Count | Notes |
|----------|------:|-------|
| Classes | 1 | `LogAnalyzerError` enum (Rust) |
| Interfaces | 0 | No TS/Java interfaces; no Rust `trait` artifacts inventoried |
| Controllers | 23 | FastAPI route handlers + Express controller functions |
| Services | 14 | `TransactionService`, `ConverterService`, queue/risk scoring |
| Models / Entities | 21 | Pydantic schemas, dataclasses, Rust structs |
| Repositories / DAOs | 6 | `database.py` PostgreSQL accessors (D2) |
| Jobs / Scheduled tasks | 5 | D2/A3 polling workers, D1 Lambda `handler` |
| Consumers / Listeners | 2 | A3 `processQueueOnce`, `isValidTransaction` |
| Configuration classes | 7 | FastAPI app bootstrap, `createApp`, logging config |
| Utility / Helper classes | 25 | Queue I/O, CLI client, log analysis, exceptions |
| Middleware / Filters | 3 | B5 error handlers, D6 `ObservabilityMiddleware` |
| Validators | 1 | B5 `validateCreateTransaction` |
| **Total** | **108** | |

### Artifacts by track (source files with implementations)

| Track | Application source files | Primary artifacts |
|-------|-------------------------:|-------------------|
| beginner | 23 | B4 FastAPI, B5 Express, B6 Rust CLI |
| intermediate | 7 | I4 currency conversion pair |
| advanced | 12 | A3 polyglot queue system |
| devops | 19 | D1 Lambda, D2 Compose stack, D6 observability |

---

## Detailed Inventory Highlights

### Controllers (23)

Repeated transaction CRUD handlers appear in B4, D6 (full CRUD + balance), D2 (create + list), and A3 (create only). I4 exposes `convert_currency`. D6 adds `metrics` and `root` endpoints.

| Name | File Path | Framework |
|------|-----------|-----------|
| `create_transaction` | `beginner/B4-fastapi-service/app/routes/transactions.py` | FastAPI |
| `createTransaction` | `beginner/B5-nodejs-api-cli/src/controllers/transactionController.js` | Express |
| `convert_currency` | `intermediate/I4-fastapi-node-pair/fastapi-service/app/routes/convert.py` | FastAPI |
| `metrics` | `devops/D6-observability/service/app/main.py` | FastAPI |

### Services (14)

| Name | File Path | Purpose |
|------|-----------|---------|
| `TransactionService` | `beginner/B4-fastapi-service/app/services/transaction_service.py` | In-memory transaction store |
| `TransactionService` | `beginner/B5-nodejs-api-cli/src/services/transactionService.js` | In-memory transaction store (JS) |
| `ConverterService` | `intermediate/I4-fastapi-node-pair/fastapi-service/app/services/converter.py` | Currency conversion logic |
| `calculate_risk_score` | `advanced/A3-polyglot-system/rust-engine/src/lib.rs` | Risk scoring engine |
| `enqueue_transaction` | `advanced/A3-polyglot-system/fastapi-service/app/services/queue_service.py` | File-backed queue writer |

### Models / Entities (21)

Domain models center on **transactions** (`Transaction`, `TransactionType`, `TransactionCreate`, `TransactionResponse`, `BalanceResponse`) and **currency conversion** (`ConvertRequest`, `ConvertResponse`). A3 adds `ScoreInput` / `ScoreOutput` for risk scoring.

### Repositories / DAOs (6)

All in `devops/D2-docker-compose/api/app/database.py`:

- `get_connection`, `wait_for_database` — connection lifecycle
- `insert_transaction`, `list_transactions`, `get_transaction_by_id` — PostgreSQL CRUD

No JPA `@Repository`, Spring Data, or ORM entity mappings were found (consistent with I1 ER diagram findings).

### Jobs / Consumers (7 combined)

| Name | Category | File Path |
|------|----------|-----------|
| `handler` | Jobs | `devops/D1-terraform/lambda/index.py` |
| `run`, `processPendingTransactions` | Jobs | `devops/D2-docker-compose/worker/src/worker.js` |
| `runLoop` | Jobs | `advanced/A3-polyglot-system/node-worker/src/worker.js` |
| `processQueueOnce` | Consumers | `advanced/A3-polyglot-system/node-worker/src/processor.js` |

---

## Notable Findings

1. **Polyglot repetition.** Transaction APIs are implemented three ways: FastAPI in-memory (B4, D6), Express in-memory (B5), and FastAPI + PostgreSQL (D2). Useful for cross-task comparison but increases duplicate artifact names in the inventory.

2. **No traditional ORM layer.** Persistence is either in-memory lists, raw `psycopg2` SQL, or JSON file queues — no SQLAlchemy models, Hibernate entities, or `@Entity` annotations.

3. **B1 output location resolved.** Deliverables (`REPORT.md`, `inventory.csv`) are written directly to `beginner/B1-repo-artifact-inventory/` per README workflow.

4. **Observability extension.** D6 adds `ObservabilityMiddleware` and Prometheus `metrics` endpoint atop the B4 transaction service pattern.

5. **Documentation-heavy tracks.** Many tasks (B2, B3, I1–I3, A1–A2, A4–A6, D3–D5) contain reports and plans without additional application source code beyond markdown.

6. **Build/CI present.** Root `.github/workflows/ci.yml`, `Makefile`, `mise.toml`, Terraform (`devops/D1-terraform/`), Kubernetes manifests (`devops/D4-kubernetes/`), and Docker Compose files exist but are infrastructure/config — outside the B1 application-artifact taxonomy.

---

## Areas Requiring Manual Verification

| # | Area | Reason |
|---|------|--------|
| 1 | Ignored paths | `node_modules/`, `.venv/`, `target/` excluded; local-only deps not scanned |
| 2 | Function vs. class controllers | FastAPI uses function-based handlers classified as Controllers, not classes |
| 3 | Duplicate names across tasks | Same symbol (e.g. `TransactionService`) in multiple task folders — paths disambiguate |
| 4 | Pydantic validators | `@field_validator` methods on schema classes counted as part of Models, not separate Validators |
| 5 | Report-only tasks | Markdown deliverables in A1, I1, D3, etc. are not application artifacts |

---

## Verification Summary

| Metric | Verified Value |
|--------|---------------:|
| Total files scanned (excl. deps) | 240 |
| Application source files (excl. tests) | 61 |
| Total directories (excl. `.git/`, deps) | 181 |
| **Total classified artifacts** | **108** |
| **Total controllers** | **23** |
| **Total services** | **14** |
| **Total repositories / DAOs** | **6** |
| **Total entities/models** | **21** |
| **Total jobs** | **5** |
| **Total consumers** | **2** |
| **Total config classes** | **7** |
| **Total utilities** | **25** |
| **Total middleware** | **3** |
| **Total validators** | **1** |
| **Total interfaces** | **0** |

---

## Appendix — Machine-Readable Export

Full artifact listing: **`inventory.csv`** (108 rows + header).

Columns: `Name`, `Category`, `File Path`, `Purpose`, `Key Dependencies`, `Confidence Level`.
