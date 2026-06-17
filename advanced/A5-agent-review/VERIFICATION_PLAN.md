# A5 — Verification Plan

Adversarial verification procedures for each finding in `FINDINGS_MATRIX.md`.  
**PR:** `fb47c7b` — A3 Polyglot fraud scoring system

---

## A5-001 — Default path mismatch (Critical, Blocking)

### Issue

Node worker and FastAPI use different default file paths; worker cannot process API-ingested transactions without `FRAUD_SYSTEM_ROOT`.

### Verification steps

**Step 1 — Compare default paths**

```bash
cd advanced/A3-polyglot-system/node-worker
node -e "import { getQueuePath, getSystemRoot } from './src/queue.js'; console.log(getSystemRoot()); console.log(getQueuePath());"

cd ../fastapi-service
python3 -c "from app.services.queue_service import get_queue_file, SYSTEM_ROOT; print(SYSTEM_ROOT); print(get_queue_file())"
```

**Expected (correct):** Both print the same queue path under `A3-polyglot-system/shared/data/`.

**Actual (verified 2026-06-17):**

```
Node:   .../A3-polyglot-system/node-worker/shared/data/transactions.json
FastAPI: .../A3-polyglot-system/shared/data/transactions.json
```

**Result:** **FAIL**

**Step 2 — Rust binary default path**

```bash
cd advanced/A3-polyglot-system/node-worker
node -e "import { getRustEnginePath } from './src/rustClient.js'; import fs from 'fs'; const p=getRustEnginePath(); console.log(p, fs.existsSync(p));"
```

**Expected:** Path exists after `cargo build --release`.

**Actual:** `.../node-worker/rust-engine/target/release/fraud-engine false`

**Result:** **FAIL**

### Suggested fixes

| Type | Fix |
|------|-----|
| Minimal | `getSystemRoot(): path.resolve(__dirname, "../..")` in `queue.js` and `rustClient.js` |
| Preferred | Shared config module / `.env.example` with required vars validated at startup |
| Long-term | Service discovery or container volume mounts with explicit paths |

---

## A5-002 — Silent transaction loss on failure (Critical, Blocking)

### Issue

Transactions that fail scoring are removed from the queue without being written to processed output or a dead-letter store.

### Verification steps

```bash
cd advanced/A3-polyglot-system/node-worker
node -e "
import fs from 'fs'; import os from 'os'; import path from 'path';
import { processQueueOnce } from './src/processor.js';
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'a5-'));
const q = path.join(tmp, 'q.json');
const p = path.join(tmp, 'out.json');
fs.writeFileSync(q, JSON.stringify([{transaction_id:'fail-1',user_id:'u',amount:100,merchant:'m',country:'IN',status:'pending'}]));
fs.writeFileSync(p, '[]');
process.env.TRANSACTIONS_QUEUE_FILE = q;
process.env.PROCESSED_TRANSACTIONS_FILE = p;
process.env.RUST_ENGINE_BIN = '/nonexistent/fraud-engine';
processQueueOnce({ logger: { info(){}, warn(){}, error(){} } });
console.log('queue:', fs.readFileSync(q,'utf8'));
console.log('processed:', fs.readFileSync(p,'utf8'));
"
```

**Expected:** Failed transaction retained (retry queue or dead-letter file).

**Actual:**

```
queue: []
processed: []
```

**Result:** **FAIL** — transaction lost

### Suggested fixes

| Type | Fix |
|------|-----|
| Minimal | On failure, write to `shared/data/dead_letter.json` before removing from pending |
| Preferred | Set `status: "failed"` + `error` field; keep in queue for operator review |
| Long-term | Durable message broker with DLQ (SQS/RabbitMQ) |

---

## A5-003 — File queue race condition (High)

### Issue

Concurrent read-modify-write on JSON queue files can lose updates.

### Verification steps

```bash
# Terminal 1: rapid POST loop
cd advanced/A3-polyglot-system/fastapi-service
export TRANSACTIONS_QUEUE_FILE=/tmp/a5-race.json
export FRAUD_SYSTEM_ROOT=$(pwd)/..
python3 -c "
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
for i in range(50):
    c.post('/transactions', json={'transaction_id':f't-{i}','user_id':'u','amount':1,'merchant':'m','country':'IN'})
"

# Check queue count
python3 -c "import json; print(len(json.load(open('/tmp/a5-race.json'))))"
```

Run two POST loops simultaneously; compare count to 100.

**Expected:** 100 entries.

**Actual:** Not run in adversarial session (race-dependent); code inspection confirms no locking.

**Result:** **UNVERIFIED** — design risk confirmed by static analysis

### Suggested fix

Add `proper-lockfile` (Node) and `fcntl`/`filelock` (Python), or document single-writer constraint.

---

## A5-004 — No API authentication (High)

### Verification steps

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8100/transactions \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"x","user_id":"u","amount":1,"merchant":"m","country":"IN"}'
```

**Expected (secure system):** 401 without credentials.

**Actual:** 202 (when server running) — no auth check in `main.py`.

**Result:** **FAIL** (for production); acceptable for eval scaffold if documented.

---

## A5-005 — Blocking spawnSync (High)

### Verification steps

Inspect `rustClient.js` L33: `spawnSync(enginePath, [payload], ...)`.

**Expected (async):** Non-blocking `spawn` or worker pool.

**Actual:** Synchronous spawn per transaction.

**Result:** **CONFIRMED** by code inspection

---

## A5-006 — Hidden scoring rule (Medium)

### Verification steps

```bash
cd advanced/A3-polyglot-system/rust-engine
cargo test high_risk_score -- --nocapture
# Inspect lib.rs L31-33 for amount >= 15000 rule
./target/release/fraud-engine '{"amount":15000,"merchant":"electronics","country":"IN"}'
```

**Expected per original task (3 rules only):** 50+20=70 → MEDIUM.

**Actual:** 82 → HIGH (includes +12 rule).

**Result:** **SPEC DRIFT** — documented in DATA_CONTRACT but not original task

---

## A5-007 — Duplicate transaction_id (Medium)

### Verification steps

```bash
cd advanced/A3-polyglot-system/fastapi-service
python3 -c "
import tempfile, os, json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
q = Path(tempfile.mktemp(suffix='.json')); q.write_text('[]')
os.environ['TRANSACTIONS_QUEUE_FILE'] = str(q)
c = TestClient(app)
c.post('/transactions', json={'transaction_id':'dup','user_id':'u','amount':10,'merchant':'m','country':'IN'})
c.post('/transactions', json={'transaction_id':'dup','user_id':'u','amount':20,'merchant':'m','country':'IN'})
print(len(json.loads(q.read_text())))
"
```

**Expected:** 1 entry or 409 on duplicate.

**Actual:** `2`

**Result:** **FAIL**

---

## A5-008 through A5-013

| ID | Command / inspection | Expected | Actual | Result |
|----|---------------------|----------|--------|--------|
| A5-008 | Compare queue record fields vs `transaction-schema.json` | Schema enforced | `status` field added, no validator | FAIL |
| A5-009 | Throw inside `processQueueOnce` in continuous mode | Logged error, worker continues | No try/catch in `setInterval` | FAIL (inspection) |
| A5-010 | Mock Rust stdout `{"foo":1}` | Rejected | `JSON.parse` accepts | FAIL (inspection) |
| A5-011 | POST `country: "12"` | 422 | 202 accepted | FAIL |
| A5-012 | Compare A3 vs B4 `requirements.txt` | Consistent pinning | Open bounds in A3 | FAIL |
| A5-013 | Run `npm test` without env in new test file | Catches path bug | All tests set env | FAIL (gap) |

---

## Re-review checklist (post-fix)

After agent addresses blocking issues:

```bash
# 1. Default paths align
cd advanced/A3-polyglot-system/node-worker && npm test
# Add new test: default paths without env

# 2. Failed transaction retained
# Run A5-002 verification script — queue or DLQ must retain failed record

# 3. Full regression
bash scripts/integration-test.sh
bash ../../scripts/ci-verify.sh

# 4. E2E without manual env (stretch)
# POST via uvicorn + npm run worker:once with NO FRAUD_SYSTEM_ROOT
```

---

## Rollback (if rejecting PR)

```bash
git revert fb47c7b --no-edit
```

No production deployment dependencies identified — eval scaffold only.
