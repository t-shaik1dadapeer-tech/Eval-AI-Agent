# A5 — Agent Code Review Report

**PR reviewed:** `fb47c7b` — `A3: Polyglot fraud scoring system`  
**Reviewer stance:** Adversarial — assume agent claims are false until verified  
**Review date:** 2026-06-17  
**Output:** `advanced/A5-agent-review/`

---

# Executive Summary

| Field | Value |
|-------|-------|
| **Files reviewed** | 33 files in `advanced/A3-polyglot-system/` (commit `fb47c7b`) |
| **Lines changed** | +5,345 |
| **Tests claimed** | 8 unit/integration suites passing |
| **Tests verified locally** | Yes — but only with `FRAUD_SYSTEM_ROOT` / env overrides |

## Overall assessment

The A3 polyglot fraud system **demonstrates the intended architecture** and passes tests when environment variables are correctly set (as in `scripts/integration-test.sh`). However, adversarial verification found **two critical path-configuration bugs** that break the worker under default `npm start` / unset env, and **silent data loss** when scoring fails. The agent's `docs/REPORT.md` claims "Complete" status and successful end-to-end flow without documenting that **default Node paths do not align with FastAPI paths**.

## Approval recommendation

## **REQUEST CHANGES**

| Verdict | Rationale |
|---------|-----------|
| Not APPROVE | Critical default-path mismatch prevents worker from reading API queue without env |
| Not APPROVE WITH CHANGES | Blocking issues require code fixes, not documentation alone |
| **REQUEST CHANGES** | Fix path resolution + failed-transaction handling before merge to production |
| Not REJECT | Core design is sound; issues are fixable with focused changes |

**Minimum to re-review:** Fix findings **A5-001**, **A5-002** (blocking). Address **A5-003** or document as accepted limitation with mitigation plan.

---

# Phase 1 — Change Summary

## Purpose

Build a three-language fraud scoring pipeline: FastAPI ingestion → JSON file queue → Node worker → Rust CLI → processed JSON output.

## Files changed (by area)

| Area | Key files | Purpose |
|------|-----------|---------|
| FastAPI | `fastapi-service/app/routes/transactions.py`, `queue_service.py` | HTTP ingestion + file queue writes |
| Node worker | `node-worker/src/processor.js`, `queue.js`, `rustClient.js` | Poll queue, spawn Rust, write results |
| Rust engine | `rust-engine/src/lib.rs`, `main.rs` | Risk scoring CLI |
| Shared | `shared/*.json` | JSON schema documentation |
| Docs | `docs/REPORT.md`, `ARCHITECTURE.md` | Claims full system completion |
| Tests | `*/tests/*`, `scripts/integration-test.sh` | Unit + E2E verification |

## Risk areas identified upfront

| Area | Risk |
|------|------|
| File-based queue | Concurrency, TOCTOU races |
| Cross-language paths | Default path resolution |
| CLI invocation | `spawnSync` per transaction |
| Error handling | Failed job disposition |
| Security | No auth on ingestion API |

---

# Correctness Review

## Verified behavior

| Claim | Evidence | Verified? |
|-------|----------|-----------|
| POST returns 202 + accepted | `routes/transactions.py` L9-17 | Yes (pytest) |
| Scoring example 82/HIGH | `rust-engine/src/lib.rs` L19-40 | Yes (`cargo test`) |
| E2E integration works | `scripts/integration-test.sh` | Yes **with env vars set** |
| Worker polls shared queue by default | `queue.js` L7-11 | **No — wrong default path** |

## Findings

### Silent loss of failed transactions (A5-002)

When Rust scoring fails, `processor.js` adds the transaction to `malformed` and removes it from the queue via `markQueueRemaining(cleanedRemaining)`. Pending items are never re-queued.

**Verified:** Queue empty after failure; processed file empty.

```javascript
// processor.js L50-54 — failed pending items are discarded
const failedIds = new Set(malformed.map((item) => item.transaction_id));
markQueueRemaining(remaining.filter(...));
```

### Default path mismatch — API vs worker (A5-001)

| Component | Default queue path |
|-----------|-------------------|
| FastAPI | `advanced/A3-polyglot-system/shared/data/transactions.json` |
| Node worker | `advanced/A3-polyglot-system/node-worker/shared/data/transactions.json` |

**Verified via runtime:**

```
FastAPI queue: .../A3-polyglot-system/shared/data/transactions.json
Node queue:    .../A3-polyglot-system/node-worker/shared/data/transactions.json
```

### Duplicate `transaction_id` accepted (A5-007)

`enqueue_transaction` appends without uniqueness check. Verified: two POSTs with same ID → queue length 2.

### Hidden scoring rule (A5-006)

Task spec listed 3 rules; agent added `amount >= 15000 → +12` in `lib.rs` L31-33 to produce score 82. Documented in `DATA_CONTRACT.md` but **not in original task spec** — spec drift.

### Edge cases not handled

| Case | Behavior |
|------|----------|
| Corrupt queue JSON | `json.loads` / `JSON.parse` throws — worker crashes |
| Missing `status` field | Item excluded from `pending` filter — stuck forever in queue |
| `amount: null` via direct queue edit | Node `isValidTransaction` rejects — dropped (A5-002) |

---

# Security Review

| Finding | Severity | Evidence |
|---------|----------|----------|
| No authentication on `POST /transactions` | High | `main.py` — no auth middleware |
| No authorization / rate limiting | High | Open ingestion endpoint |
| `spawnSync` with JSON arg — no shell | OK | `rustClient.js` L33 — argv array, no shell |
| Sensitive data in logs | Medium | `processor.js` L35-36 logs transaction_id + score |
| Shared JSON files world-readable | Medium | Default file permissions; no encryption |
| No secrets in repo | OK | Grep — no hardcoded credentials |
| JSON schema `additionalProperties: false` not enforced | Low | FastAPI adds `status` field not in schema |

**No injection via shell** — `spawnSync(enginePath, [payload])` avoids shell interpolation. Merchant strings with quotes are JSON-encoded.

---

# Test Review

## Existing coverage

| Suite | Count | Coverage |
|-------|------:|----------|
| FastAPI pytest | 3 | Happy path, invalid amount, health |
| Node jest | 2 | Happy path (with env), malformed skip |
| Rust | 3 | LOW/MEDIUM/HIGH scores |
| Integration script | 1 | Full E2E **with env vars** |

## Gaps

| Missing scenario | Finding |
|------------------|---------|
| Default path alignment (no env) | **A5-001** — untested |
| Worker `npm start` without `FRAUD_SYSTEM_ROOT` | Not tested |
| Scoring failure → queue disposition | **A5-002** — not tested |
| Duplicate `transaction_id` | **A5-007** — not tested |
| Concurrent FastAPI + worker access | **A5-003** — not tested |
| Corrupt queue file | Not tested |
| Rust output validation (invalid JSON shape) | **A5-010** — not tested |
| Missing required fields in POST | Only `amount` negative tested |
| `country` non-alpha (e.g. `"12"`) | Not tested |

## Agent assumption in tests

All Node tests set `FRAUD_SYSTEM_ROOT` or `RUST_ENGINE_BIN` explicitly (`worker.test.js` L24-27). **This masks the default-path bug.**

---

# Performance Review

| Finding | Severity | Evidence |
|---------|----------|----------|
| `spawnSync` per transaction | Medium | `rustClient.js` L33 — blocks Node event loop |
| Full-file read/write per operation | Medium | `queue.js` L32-44 — O(n) per enqueue/process |
| No batching of Rust calls | Low | One process spawn per transaction |
| Polling interval 2s fixed | Low | `worker.js` L3 — idle latency |

**Evidence:** For 1000 transactions, worker spawns 1000 processes sequentially in one `processQueueOnce` loop.

No N+1 DB or network patterns (file-based system).

---

# Maintainability Review

| Finding | Severity | Evidence |
|---------|----------|----------|
| Duplicated path logic Python vs Node | Medium | `queue_service.py` vs `queue.js` — divergent defaults |
| JSON schemas are documentation-only | Medium | Not validated at runtime |
| `isValidTransaction` duplicates Pydantic rules | Low | `processor.js` L63-76 vs `transaction.py` |
| Undocumented env var requirement | Medium | README says set `FRAUD_SYSTEM_ROOT` but implies optional |
| Large `package-lock.json` in repo | Low | 3665 lines — standard for npm |

Code is readable, functions are small, separation of concerns is good.

---

# Adversarial Review

## 1. What assumptions did the agent make?

- `FRAUD_SYSTEM_ROOT` will always be set when running the worker
- File queue operations are atomic enough for eval/demo use
- Integration test config represents production-like deployment
- Failed transactions can be dropped without dead-letter queue
- Three scoring rules in task spec were insufficient; added fourth rule silently
- Shared JSON schemas are equivalent to runtime validation

## 2. Which assumptions were verified?

| Assumption | Result |
|------------|--------|
| E2E works with correct env | **Verified** — integration script exit 0 |
| Scoring math for documented rules | **Verified** — `cargo test` |
| Tests prove system works out of box | **Disproved** — default paths diverge |
| Malformed transactions are "skipped" safely | **Partially false** — skipped **and deleted** |

## 3. Which assumptions remain unverified?

- Behavior under concurrent API + worker load
- Recovery from corrupt queue JSON
- Production security posture (no auth accepted as limitation?)
- Long-running worker stability (`setInterval` error handling)

## 4. What could break in production?

1. Operator runs `npm start` without env → worker polls empty/wrong queue forever
2. Rust binary missing → all pending transactions deleted, none processed
3. Two FastAPI workers race on queue file → lost updates
4. Duplicate transaction IDs → double processing / double charges in downstream systems

## 5. What is the highest-risk issue?

**A5-001 — Node worker default paths resolve to `node-worker/` subtree, not A3 system root.** FastAPI writes to a different file than the worker reads under default configuration. The integration test and documentation create a false sense of correctness.

---

# Issue count summary

| Metric | Count |
|--------|------:|
| Total issues | 13 |
| Critical | 2 |
| High | 4 |
| Medium | 5 |
| Low | 2 |
| Blocking | 2 |

See `FINDINGS_MATRIX.md` for full table and `VERIFICATION_PLAN.md` for reproduction steps.
