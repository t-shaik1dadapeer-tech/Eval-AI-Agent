# PML / OCL Eval Verification — All 24 Tasks

**Reference:** [PML Version](https://docs.google.com/document/d/1VurgqAe_qZlMieK8pA4S2yJjWBd7cnoO8cuvh4zmNZs/edit) · [OCL Version](https://docs.google.com/document/d/1Y23tu2ePPexkBhh_G0RCK1fNio_NQ3EZuTbgWa_UyPA/edit)

**Repo:** `Eval-Ai` eval portfolio  
**Last verified:** 2026-06-20  
**Commands:** `make eval` · `make eval-full` · `make test` · `make eval-reset-config`

---

## Summary

| Layer | Tasks | Deliverables | Auto-verify | PML rubric |
|-------|------:|-------------|-------------|------------|
| Beginner (B1–B6) | 6 | 6/6 ✅ | 4/6 | **6 PASS** |
| Intermediate (I1–I6) | 6 | 6/6 ✅ | 2/6 (+ I5 Docker) | **6 PASS** |
| Advanced (A1–A6) | 6 | 6/6 ✅ | 2/6 | **6 PASS** |
| DevOps (D1–D6) | 6 | 6/6 ✅ | 6/6 | **6 PASS** |
| **Total** | **24** | **24/24** | **14/24** | **24 PASS** |

Analysis/report tasks have no `verify_command` — artifact review only. Code/infra tasks auto-verify via `make eval-full` (Docker required for I5, D2, D6 stack).

---

## Self-eval basics (10 questions)

| Question | Answer | Evidence |
|----------|--------|----------|
| Repo discovery in 30 min | **Yes** | B1 — 242 rows incl. tests, config, docs |
| ER diagram in 45 min | **Yes** | I1 — D2 `transactions` + Mermaid |
| API mapping in 30 min | **Yes** | B2 — 26 routes |
| Flow trace in 45 min | **Yes** | I2 `FLOW_TRACE.md` |
| Test discovery in 30 min | **Yes** | B3 `TEST_REPORT.md`, `make test` |
| FastAPI greenfield in 60 min | **Yes** | B4 — 8 tests |
| Node.js build in 60 min | **Yes** | B5 — API + CLI, 9 tests |
| Rust CLI in 60 min | **Yes** | B6 — 17 tests |
| Parallel work safely | **Yes** | A1 + A2 |
| Separate agent vs verified | **Yes** | Agent submit + `make eval` / `make test` |

---

## Per-task status (all PASS)

| ID | Key deliverable | Verify |
|----|-----------------|--------|
| B1 | `inventory.csv` (242 rows), `REPORT.md` | Manual |
| B2 | `API_MAP.md`, `endpoints.csv` | Manual |
| B3 | `TEST_REPORT.md` | `make test` |
| B4 | FastAPI + 8 tests | `pytest` |
| B5 | Express API + CLI + 9 tests | `npm test` |
| B6 | Rust CLI + 17 tests | `cargo test` |
| I1 | ER diagram + D2 table | Manual |
| I2 | Flow trace + sequence | Manual |
| I3 | Safe change report | Manual |
| I4 | FastAPI + Node pair | `pytest` + `npm test` |
| I5 | Dockerfile + docker verify | `verify-docker.sh` |
| I6 | Bug diagnosis | Manual |
| A1–A6 | Plans, polyglot, perf | A3/A6 scripts |
| D1–D6 | Terraform → observability | Per-task scripts |

---

## Commands

```bash
make bootstrap
make test              # full suite
make eval              # 24/24 deliverables
make eval-full         # + automated verify (Docker)
make eval-reset-config # fix bad local B3 output_map
make eval-api          # dashboard :8788
```

---

## External API note

Register **UserManagement** (`:8090`) for your own project artifacts — not for Eval-Ai B2/B4 transaction routes. Use `make eval-orch-config API_ID=user-api API_BASE_URL=http://127.0.0.1:8090`.

---

## Maintenance scripts

| Script | Purpose |
|--------|---------|
| `scripts/b1-refresh-inventory.py` | Re-scan tests/config/docs into B1 CSV |
| `intermediate/I5-dockerize/scripts/verify-docker.sh` | I5 Docker proof |
| `devops/D6-observability/scripts/export-dashboard-panel.sh` | Live Grafana panel JSON |
| `scripts/eval/reset-orchestrator-config.sh` | Clean `.eval/orchestrator-config.json` |
