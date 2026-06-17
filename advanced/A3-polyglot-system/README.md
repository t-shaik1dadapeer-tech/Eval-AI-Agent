# A3 Polyglot Fraud Scoring System

Mini fraud-scoring pipeline across **FastAPI**, **Node.js**, and **Rust** using file-based queues — no external infrastructure required.

## Architecture

```
User → FastAPI → transactions.json → Node Worker → Rust Engine → processed_transactions.json
```

## Quick start

```bash
# 1. Build Rust engine
cd rust-engine && cargo build --release

# 2. FastAPI tests
cd ../fastapi-service && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pytest -v

# 3. Node worker tests
cd ../node-worker && npm install && npm test

# 4. End-to-end integration
cd .. && bash scripts/integration-test.sh
```

## Components

| Component | Path | Role |
|-----------|------|------|
| FastAPI | `fastapi-service/` | Ingest and validate transactions |
| Node worker | `node-worker/` | Poll queue, invoke Rust, save results |
| Rust engine | `rust-engine/` | Compute fraud risk score |
| Shared contracts | `shared/` | JSON schemas + data files |
| Documentation | `docs/` | Architecture, contracts, report |

## Environment variables

| Variable | Used by | Purpose |
|----------|---------|---------|
| `FRAUD_SYSTEM_ROOT` | All | Root of this A3 project |
| `TRANSACTIONS_QUEUE_FILE` | FastAPI, Worker | Pending transaction queue |
| `PROCESSED_TRANSACTIONS_FILE` | Worker | Scored output file |
| `RUST_ENGINE_BIN` | Worker | Path to compiled `fraud-engine` |

See `docs/ARCHITECTURE.md` and `docs/REPORT.md` for full details.
