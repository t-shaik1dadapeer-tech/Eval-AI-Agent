# A5 — Findings Matrix

**PR:** `fb47c7b` — A3 Polyglot fraud scoring system

| ID | Category | Severity | Blocking | Description | Evidence | Suggested Fix |
|----|----------|----------|----------|-------------|----------|---------------|
| A5-001 | Correctness | **Critical** | **Yes** | Node worker default paths resolve to `node-worker/` not A3 root — API and worker use different queue files and Rust binary path | `queue.js` L10: `path.resolve(__dirname, "..")` → `node-worker/`; `queue_service.py` L12: `parents[3]` → `A3-polyglot-system/`; verified: Node queue `.../node-worker/shared/data/transactions.json`, FastAPI `.../A3-polyglot-system/shared/data/transactions.json`; Rust default `.../node-worker/rust-engine/...` does not exist | Change `getSystemRoot()` to `path.resolve(__dirname, "../..")`; align `getRustEnginePath()` to `{root}/rust-engine/target/release/fraud-engine` |
| A5-002 | Correctness | **Critical** | **Yes** | Failed/scoring-error transactions silently removed from queue — no dead-letter, no retry | `processor.js` L38-54: pending items not re-queued on failure; verified: queue `[]` and processed `[]` after `/nonexistent` Rust bin | Move failed items to `dead_letter.json` or set `status: "failed"` and retain in queue; add retry policy |
| A5-003 | Correctness | High | No | File queue read-modify-write without locking — TOCTOU data loss under concurrency | `queue_service.py` L48-53, `queue.js` L42-44, `appendProcessedResults` L74-76 | File locking (`fcntl`/`proper-lockfile`) or single-writer design |
| A5-004 | Security | High | No | No authentication on transaction ingestion API | `fastapi-service/app/main.py` — no auth middleware on router | Add API key middleware or mTLS for non-eval deployments |
| A5-005 | Performance | High | No | `spawnSync` blocks Node event loop for each transaction | `rustClient.js` L33-36 | Use `spawn` async + worker pool, or batch scoring API |
| A5-006 | Correctness | Medium | No | Hidden fourth scoring rule (`amount >= 15000` +12) not in original task spec | `rust-engine/src/lib.rs` L31-33; task spec listed only 3 rules | Remove rule and adjust tests, or document as intentional business rule with stakeholder sign-off |
| A5-007 | Correctness | Medium | No | Duplicate `transaction_id` accepted — double processing possible | `queue_service.py` L48-53 no uniqueness check; verified: 2 POSTs same ID → queue length 2 | Reject duplicate IDs with 409 or upsert idempotently |
| A5-008 | Maintainability | Medium | No | JSON schemas in `shared/` are documentation-only — not enforced at runtime | No jsonschema validation in FastAPI/Node; `transaction-schema.json` `additionalProperties: false` violated by `status` field | Add runtime schema validation or remove misleading `additionalProperties` |
| A5-009 | Correctness | Medium | No | `setInterval` in worker does not catch `processQueueOnce` errors | `worker.js` L20-22 — unhandled throw stops interval silently | Wrap in try/catch + log + metrics |
| A5-010 | Correctness | Medium | No | Rust CLI output not validated against `score-schema.json` | `rustClient.js` L48-49 — `JSON.parse` only, no field checks | Validate `risk_score` number and `risk_level` enum before persisting |
| A5-011 | Correctness | Low | No | `country` validated only by length (2 chars), not ISO alpha-2 | `transaction.py` L9: `min_length=2, max_length=2` — `"12"` accepted | Add regex `^[A-Z]{2}$` validator |
| A5-012 | Maintainability | Low | No | A3 `requirements.txt` uses open lower bounds (no upper cap) | `fastapi-service/requirements.txt` vs B4 capped pins | Align pinning with B4/I4 pattern |
| A5-013 | Testing | Medium | No | Tests mask path bug by always setting `FRAUD_SYSTEM_ROOT` | `worker.test.js` L24-27, `integration-test.sh` exports env | Add test for default paths without env overrides |

---

## Severity summary

| Severity | Count | Blocking |
|----------|------:|---------:|
| Critical | 2 | 2 |
| High | 3 | 0 |
| Medium | 6 | 0 |
| Low | 2 | 0 |
| **Total** | **13** | **2** |

---

## Suggested fix priority

1. **A5-001** — Fix path resolution (minimal: one-line root change in `queue.js` + `rustClient.js`)
2. **A5-002** — Dead-letter or failed status retention
3. **A5-013** — Regression test without env vars
4. **A5-007** — Idempotency
5. **A5-003** — Locking (or document single-process constraint)
