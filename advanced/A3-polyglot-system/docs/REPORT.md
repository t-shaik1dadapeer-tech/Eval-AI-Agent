# A3 — Polyglot Fraud System Report

**Date:** 2026-06-17  
**Location:** `advanced/A3-polyglot-system/`

---

# Executive Summary

Built a three-component fraud scoring mini-system:

| Component | Technology | Status |
|-----------|------------|--------|
| Ingestion API | FastAPI (Python) | Complete |
| Processing worker | Node.js | Complete |
| Risk engine | Rust CLI | Complete |

All unit tests pass. End-to-end integration verified: POST → queue → worker → Rust → processed output with **risk_score 82 / HIGH**.

---

# Architecture

See `docs/ARCHITECTURE.md` for diagrams. High-level flow:

```
User → FastAPI → transactions.json → Node Worker → Rust Engine → processed_transactions.json
```

---

# Component Details

## FastAPI

- `POST /transactions` — validates and enqueues transactions
- `GET /health` — returns `{"status": "UP"}`
- Queue: `shared/data/transactions.json`

## Node.js Worker

- Polls pending queue entries
- Spawns Rust binary per transaction
- Writes to `shared/data/processed_transactions.json`
- Skips malformed records with warning logs

## Rust Engine

- CLI: `fraud-engine '<json>'`
- Deterministic scoring rules (documented in `DATA_CONTRACT.md`)
- Example: `15000 / electronics / IN` → score **82**, level **HIGH**

---

# Data Flow

1. Client POSTs transaction to FastAPI
2. FastAPI appends `{..., status: "pending"}` to queue file
3. Worker reads pending items
4. Worker calls Rust with `{amount, merchant, country}`
5. Rust returns `{risk_score, risk_level}`
6. Worker appends full result to processed file and clears queue entry

---

# Test Results

## Rust (`cargo test`)

**Command:**

```bash
cd rust-engine && cargo test
```

**Output:**

```
running 3 tests
test high_risk_score ... ok
test low_risk_score ... ok
test medium_risk_score ... ok
test result: ok. 3 passed; 0 failed
```

| Exit code | Result |
|-----------|--------|
| `0` | 3/3 passed |

## FastAPI (`pytest -v`)

**Command:**

```bash
cd fastapi-service && pytest -v
```

**Output:**

```
tests/test_transactions.py::test_valid_transaction PASSED
tests/test_transactions.py::test_invalid_amount PASSED
tests/test_transactions.py::test_health_endpoint PASSED
========================= 3 passed in 0.33s =========================
```

| Exit code | Result |
|-----------|--------|
| `0` | 3/3 passed |

## Node.js (`npm test`)

**Command:**

```bash
cd node-worker && npm test
```

**Output:**

```
PASS tests/worker.test.js
  queue processing
    ✓ processes pending transactions and writes processed output
  invalid transaction handling
    ✓ skips malformed transactions without crashing
Tests: 2 passed, 2 total
```

| Exit code | Result |
|-----------|--------|
| `0` | 2/2 passed |

---

# Integration Verification

**Command:**

```bash
bash scripts/integration-test.sh
```

**Captured output:**

```
=== Step 2: Verify Rust CLI ===
Rust output: {"risk_score":82,"risk_level":"HIGH"}

=== Step 3: POST transaction via FastAPI TestClient ===
POST status: 202
POST body: {'status': 'accepted', 'transaction_id': 'txn-001'}
Queue entries: 1

=== Step 4: Run Node worker (once) ===
processed txn-001: score=82 level=HIGH
{"mode":"once","processed":1,"malformed":0}

=== Step 5: Verify processed output ===
Integration verification: PASSED
{
  "transaction_id": "txn-001",
  "risk_score": 82,
  "risk_level": "HIGH"
}
```

| Check | Result |
|-------|--------|
| Queue file created | Yes — 1 entry after POST |
| Worker processed entry | Yes — `processed: 1` |
| Rust score generated | Yes — `risk_score: 82` |
| Output file written | Yes — `processed_transactions.json` |
| Exit code | `0` |

---

# Known Limitations

1. **File queue** — no file locking; not safe for high concurrency
2. **Polling worker** — not event-driven; uses interval or `--once` mode
3. **No authentication** — ingestion API is open
4. **No persistence guarantees** — crash between read/write could lose data
5. **Rust binary path** — worker expects pre-built `target/release/fraud-engine`
6. **Single-machine** — designed for local evaluation, not distributed deployment

---

# Files Created

```
advanced/A3-polyglot-system/
├── README.md
├── fastapi-service/
├── node-worker/
├── rust-engine/
├── shared/
├── docs/
└── scripts/integration-test.sh
```

See component READMEs for per-folder file lists.
