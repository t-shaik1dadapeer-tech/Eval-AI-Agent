# PM4-6626 — All 24 Jira Subtask Prompts

Single reference for the **Coding Agent Skill Self-Evaluation** epic and every subtask prompt.

| Link | URL |
|------|-----|
| **Jira epic** | [https://paytmmoney.atlassian.net/browse/PM4-6626](https://paytmmoney.atlassian.net/browse/PM4-6626) |
| **GitHub repo** | [https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent](https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent) |
| **Eval dashboard** | `make eval-api` → http://127.0.0.1:8788 |
| **Task map** | [`JIRA_TASK_MAP.md`](JIRA_TASK_MAP.md) |
| **Agent API** | [`AGENT_API.md`](AGENT_API.md) |

## Pipeline order

B1 → B2 → B3 → B4 → B5 → B6 → I1 → I2 → I3 → I4 → I5 → I6 → A1 → A2 → A3 → A4 → A5 → A6 → D1 → D2 → D3 → D4 → D5 → D6

## Subtask index

| Task | Jira | Jira title |
|------|------|------------|
| B1 | [PM4-6627](https://paytmmoney.atlassian.net/browse/PM4-6627) | B1 — Repo Artifact Inventory |
| B2 | [PM4-6629](https://paytmmoney.atlassian.net/browse/PM4-6629) | B2 — API Endpoint Map |
| B3 | [PM4-6628](https://paytmmoney.atlassian.net/browse/PM4-6628) | B3 — Test Discovery and Execution |
| B4 | [PM4-6630](https://paytmmoney.atlassian.net/browse/PM4-6630) | B4 — FastAPI Greenfield Service |
| B5 | [PM4-6631](https://paytmmoney.atlassian.net/browse/PM4-6631) | B5 — Node.js Greenfield API or CLI |
| B6 | [PM4-6632](https://paytmmoney.atlassian.net/browse/PM4-6632) | B6 — Rust Greenfield |
| I1 | [PM4-6633](https://paytmmoney.atlassian.net/browse/PM4-6633) | I1 — ER Diagram from Repo |
| I2 | [PM4-6634](https://paytmmoney.atlassian.net/browse/PM4-6634) | I2 — End-to-End Flow Trace |
| I3 | [PM4-6635](https://paytmmoney.atlassian.net/browse/PM4-6635) | I3 — Small Safe Change in Unfamiliar Repo |
| I4 | [PM4-6636](https://paytmmoney.atlassian.net/browse/PM4-6636) | I4 — Polyglot Service Pair: FastAPI plus Node Client |
| I5 | [PM4-6637](https://paytmmoney.atlassian.net/browse/PM4-6637) | I5 — Dockerize and Run |
| I6 | [PM4-6638](https://paytmmoney.atlassian.net/browse/PM4-6638) | I6 — Bug Diagnosis with Agent |
| A1 | [PM4-6640](https://paytmmoney.atlassian.net/browse/PM4-6640) | A1 — Multi-worktree Parallel Plan |
| A2 | [PM4-6639](https://paytmmoney.atlassian.net/browse/PM4-6639) | A2 — Execute Two Parallel Worktrees |
| A3 | [PM4-6642](https://paytmmoney.atlassian.net/browse/PM4-6642) | A3 — Polyglot Mini-System: FastAPI, Node Worker, Rust Engine |
| A4 | [PM4-6641](https://paytmmoney.atlassian.net/browse/PM4-6641) | A4 — Repository Modernization Plan with Executable First Step |
| A5 | [PM4-6643](https://paytmmoney.atlassian.net/browse/PM4-6643) | A5 — Agent Code Review and Adversarial Verification |
| A6 | [PM4-6645](https://paytmmoney.atlassian.net/browse/PM4-6645) | A6 — Performance Profiling and Targeted Improvement |
| D1 | [PM4-6644](https://paytmmoney.atlassian.net/browse/PM4-6644) | D1 — Terraform Plan for a Small Service |
| D2 | [PM4-6646](https://paytmmoney.atlassian.net/browse/PM4-6646) | D2 — docker-compose Stack with End-to-End Tests |
| D3 | [PM4-6649](https://paytmmoney.atlassian.net/browse/PM4-6649) | D3 — CI Pipeline that Lints, Tests, and Builds an Image |
| D4 | [PM4-6647](https://paytmmoney.atlassian.net/browse/PM4-6647) | D4 — Kubernetes Manifests Verified on a Local Cluster |
| D5 | [PM4-6648](https://paytmmoney.atlassian.net/browse/PM4-6648) | D5 — Reproducible Dev Environment from a Fresh Clone |
| D6 | [PM4-6650](https://paytmmoney.atlassian.net/browse/PM4-6650) | D6 — Observability Bolt-on with Metrics and a Dashboard |

## How to use

1. Open the Jira subtask for the task you are working on.
2. Copy the **Copy-paste prompt** block from that task section below.
3. Paste into Cursor (or your coding agent) with the repo open.
4. Submit output via eval API or attach the deliverable `.md` to Jira.

```bash
make eval-api
curl http://127.0.0.1:8788/api/agent/guide/B4
```

---

<!-- Jira: PM4-6627 -->

**Jira:** [PM4-6627](https://paytmmoney.atlassian.net/browse/PM4-6627) — B1 — Repo Artifact Inventory  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## B1 — Repository Artifact Inventory

**Folder:** `beginner/B1-repo-artifact-inventory`  
**Submit file:** `beginner/B1-repo-artifact-inventory/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`, `inventory.csv`

### Copy-paste prompt

```
Evaluate Eval-Ai task B1 (Repository Artifact Inventory).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/B1
3. Read beginner/B1-repo-artifact-inventory/README.md, REPORT.md, and inventory.csv.
4. Scan the repo and ensure inventory.csv lists artifacts by category (controllers, services, tests, configs, docs) with correct paths. Update REPORT.md with counts and summary.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"B1","agent_name":"cursor","output_path":"beginner/B1-repo-artifact-inventory/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/API_MAP.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

---

<!-- Jira: PM4-6629 -->

**Jira:** [PM4-6629](https://paytmmoney.atlassian.net/browse/PM4-6629) — B2 — API Endpoint Map  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## B2 — API Endpoint Map

**Folder:** `beginner/B2-api-endpoint-map`  
**Submit file:** `beginner/B2-api-endpoint-map/API_MAP.md` (or `endpoints.csv`)  
**Reference:** `README.md`, `API_MAP.md`, `endpoints.csv`

### Copy-paste prompt

```
Evaluate Eval-Ai task B2 (API Endpoint Map).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/B2
3. Read beginner/B2-api-endpoint-map/README.md, API_MAP.md, endpoints.csv.
4. Scan HTTP routes in B4, B5, I4, A3, D2, D6 services. Update endpoints.csv and API_MAP.md so every route matches actual handlers.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"B2","agent_name":"cursor","output_path":"beginner/B2-api-endpoint-map/endpoints.csv"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/README.md
- beginner/B5-nodejs-api-cli/README.md
- devops/D6-observability/README.md
- beginner/B1-repo-artifact-inventory/inventory.csv
```

---

---

<!-- Jira: PM4-6628 -->

**Jira:** [PM4-6628](https://paytmmoney.atlassian.net/browse/PM4-6628) — B3 — Test Discovery and Execution  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## B3 — Test Discovery

**Folder:** `beginner/B3-test-discovery`  
**Submit file:** `beginner/B3-test-discovery/TEST_REPORT.md`  
**Reference:** `README.md`, `TEST_REPORT.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task B3 (Test Discovery).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/B3
3. Read beginner/B3-test-discovery/README.md and TEST_REPORT.md.
4. Run make test from repo root. Update TEST_REPORT.md with frameworks found (pytest, Jest, Cargo), test counts, and pass/fail summary.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"B3","agent_name":"cursor","output_path":"beginner/B3-test-discovery/TEST_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/tests/
- beginner/B5-nodejs-api-cli/tests/
- beginner/B6-rust-cli/tests/
- devops/D5-dev-environment/docs/BOOTSTRAP_VERIFICATION.md
```

---

---

<!-- Jira: PM4-6630 -->

**Jira:** [PM4-6630](https://paytmmoney.atlassian.net/browse/PM4-6630) — B4 — FastAPI Greenfield Service  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## B4 — FastAPI Transaction Service

**Folder:** `beginner/B4-fastapi-service`  
**Submit file:** `beginner/B4-fastapi-service/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task B4 (FastAPI Transaction Service).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/B4
3. Read beginner/B4-fastapi-service/README.md and REPORT.md.
4. Ensure app/main.py, app/routes/transactions.py, and tests/test_transactions.py implement the in-memory transaction REST API per README. Run: cd beginner/B4-fastapi-service && mise exec -- pytest -q
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"B4","agent_name":"cursor","output_path":"beginner/B4-fastapi-service/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/endpoints.csv
- beginner/B5-nodejs-api-cli/README.md
- devops/D6-observability/service/app/main.py
```

---

---

<!-- Jira: PM4-6631 -->

**Jira:** [PM4-6631](https://paytmmoney.atlassian.net/browse/PM4-6631) — B5 — Node.js Greenfield API or CLI  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## B5 — Node.js Transaction API

**Folder:** `beginner/B5-nodejs-api-cli`  
**Submit file:** `beginner/B5-nodejs-api-cli/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task B5 (Node.js Transaction API).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/B5
3. Read beginner/B5-nodejs-api-cli/README.md and REPORT.md.
4. Ensure src/app.js, src/routes/transactionRoutes.js, and tests/transactions.test.js mirror B4 endpoints. Run: cd beginner/B5-nodejs-api-cli && mise exec -- npm test
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"B5","agent_name":"cursor","output_path":"beginner/B5-nodejs-api-cli/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/endpoints.csv
- beginner/B4-fastapi-service/README.md
```

---

---

<!-- Jira: PM4-6632 -->

**Jira:** [PM4-6632](https://paytmmoney.atlassian.net/browse/PM4-6632) — B6 — Rust Greenfield  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## B6 — Rust Log Analyzer CLI

**Folder:** `beginner/B6-rust-cli`  
**Submit file:** `beginner/B6-rust-cli/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task B6 (Rust Log Analyzer CLI).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/B6
3. Read beginner/B6-rust-cli/README.md and REPORT.md.
4. Ensure src/main.rs, src/analyzer.rs, and tests/log_analyzer_test.rs count INFO/WARN/ERROR lines per README. Run: cd beginner/B6-rust-cli && mise exec -- cargo test -q
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"B6","agent_name":"cursor","output_path":"beginner/B6-rust-cli/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B3-test-discovery/TEST_REPORT.md
- beginner/B1-repo-artifact-inventory/inventory.csv
```

---

---

<!-- Jira: PM4-6633 -->

**Jira:** [PM4-6633](https://paytmmoney.atlassian.net/browse/PM4-6633) — I1 — ER Diagram from Repo  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## I1 — ER Diagram

**Folder:** `intermediate/I1-er-diagram`  
**Submit file:** `intermediate/I1-er-diagram/ER_REPORT.md`  
**Reference:** `README.md`, `ER_REPORT.md`, `er-diagram.mmd`, `entities.csv`

### Copy-paste prompt

```
Evaluate Eval-Ai task I1 (ER Diagram).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/I1
3. Read intermediate/I1-er-diagram/README.md, ER_REPORT.md, er-diagram.mmd, entities.csv.
4. Document entities and relationships from B4, D2, and A3 data models. Update ER_REPORT.md and er-diagram.mmd.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"I1","agent_name":"cursor","output_path":"intermediate/I1-er-diagram/ER_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/app/models/
- devops/D2-docker-compose/
- advanced/A3-polyglot-system/docs/ARCHITECTURE.md
```

---

---

<!-- Jira: PM4-6634 -->

**Jira:** [PM4-6634](https://paytmmoney.atlassian.net/browse/PM4-6634) — I2 — End-to-End Flow Trace  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## I2 — End-to-End Trace

**Folder:** `intermediate/I2-end-to-end-trace`  
**Submit file:** `intermediate/I2-end-to-end-trace/FLOW_TRACE.md`  
**Reference:** `README.md`, `FLOW_TRACE.md`, `sequence-diagram.mmd`, `flow-summary.csv`

### Copy-paste prompt

```
Evaluate Eval-Ai task I2 (End-to-End Trace).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/I2
3. Read intermediate/I2-end-to-end-trace/README.md, FLOW_TRACE.md, sequence-diagram.mmd, flow-summary.csv.
4. Document request flow across B4/B5 (or chosen service): client → API → handler → response. Update FLOW_TRACE.md and sequence-diagram.mmd.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"I2","agent_name":"cursor","output_path":"intermediate/I2-end-to-end-trace/FLOW_TRACE.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/API_MAP.md
- beginner/B4-fastapi-service/README.md
- devops/D6-observability/docs/OBSERVABILITY_REPORT.md
```

---

---

<!-- Jira: PM4-6635 -->

**Jira:** [PM4-6635](https://paytmmoney.atlassian.net/browse/PM4-6635) — I3 — Small Safe Change in Unfamiliar Repo  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## I3 — Safe Change

**Folder:** `intermediate/I3-safe-change`  
**Submit file:** `intermediate/I3-safe-change/CHANGE_REPORT.md`  
**Reference:** `README.md`, `CHANGE_REPORT.md`, `risk-assessment.md`, `diff-summary.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task I3 (Safe Change).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/I3
3. Read intermediate/I3-safe-change/README.md, CHANGE_REPORT.md, risk-assessment.md, diff-summary.md.
4. Assess a scoped change (e.g. adding a field to transaction DTO). Document scope, risks, rollback, and test plan in CHANGE_REPORT.md and risk-assessment.md.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"I3","agent_name":"cursor","output_path":"intermediate/I3-safe-change/CHANGE_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/REPORT.md
- intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md
```

---

---

<!-- Jira: PM4-6636 -->

**Jira:** [PM4-6636](https://paytmmoney.atlassian.net/browse/PM4-6636) — I4 — Polyglot Service Pair: FastAPI plus Node Client  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## I4 — FastAPI + Node Pair

**Folder:** `intermediate/I4-fastapi-node-pair`  
**Submit file:** `intermediate/I4-fastapi-node-pair/docs/REPORT.md`  
**Reference:** `README.md`, `docs/REPORT.md`, `fastapi-service/README.md`, `node-client/README.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task I4 (FastAPI + Node Pair).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/I4
3. Read intermediate/I4-fastapi-node-pair/README.md, docs/REPORT.md, fastapi-service/README.md, node-client/README.md.
4. Ensure FastAPI POST /convert and Node CLI client work. Run pytest in fastapi-service and npm test in node-client.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"I4","agent_name":"cursor","output_path":"intermediate/I4-fastapi-node-pair/docs/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/README.md
- beginner/B5-nodejs-api-cli/README.md
- beginner/B2-api-endpoint-map/endpoints.csv
```

---

---

<!-- Jira: PM4-6637 -->

**Jira:** [PM4-6637](https://paytmmoney.atlassian.net/browse/PM4-6637) — I5 — Dockerize and Run  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## I5 — Dockerize

**Folder:** `intermediate/I5-dockerize`  
**Submit file:** `intermediate/I5-dockerize/docs/DOCKER_REPORT.md`  
**Reference:** `README.md`, `docs/DOCKER_REPORT.md`, `Dockerfile`

### Copy-paste prompt

```
Evaluate Eval-Ai task I5 (Dockerize).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/I5
3. Read intermediate/I5-dockerize/README.md, docs/DOCKER_REPORT.md, Dockerfile.
4. Document build/run steps. Verify docker build and container run per DOCKER_REPORT.md (Docker required).
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"I5","agent_name":"cursor","output_path":"intermediate/I5-dockerize/docs/DOCKER_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D2-docker-compose/docs/STACK_REPORT.md
- intermediate/I4-fastapi-node-pair/fastapi-service/
```

---

---

<!-- Jira: PM4-6638 -->

**Jira:** [PM4-6638](https://paytmmoney.atlassian.net/browse/PM4-6638) — I6 — Bug Diagnosis with Agent  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## I6 — Bug Diagnosis

**Folder:** `intermediate/I6-bug-diagnosis`  
**Submit file:** `intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md`  
**Reference:** `README.md`, `BUG_REPORT.md`, `ROOT_CAUSE_ANALYSIS.md`, `FIX_SUMMARY.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task I6 (Bug Diagnosis).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/I6
3. Read intermediate/I6-bug-diagnosis/README.md, BUG_REPORT.md, ROOT_CAUSE_ANALYSIS.md, FIX_SUMMARY.md.
4. Document bug symptoms, root cause, fix, and verification in the three report files following the repo structure.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"I6","agent_name":"cursor","output_path":"intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- intermediate/I3-safe-change/CHANGE_REPORT.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

---

<!-- Jira: PM4-6640 -->

**Jira:** [PM4-6640](https://paytmmoney.atlassian.net/browse/PM4-6640) — A1 — Multi-worktree Parallel Plan  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## A1 — Parallel Planning

**Folder:** `advanced/A1-parallel-plan`  
**Submit file:** `advanced/A1-parallel-plan/PARALLEL_EXECUTION_PLAN.md`  
**Reference:** `README.md`, `PARALLEL_EXECUTION_PLAN.md`, `agent-prompts.md`, `branch-strategy.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task A1 (Parallel Planning).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/A1
3. Read advanced/A1-parallel-plan/README.md, PARALLEL_EXECUTION_PLAN.md, agent-prompts.md, branch-strategy.md.
4. Ensure multi-lane parallel plan and per-agent prompts are complete for B4 extension work. Lane prompts live in agent-prompts.md.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"A1","agent_name":"cursor","output_path":"advanced/A1-parallel-plan/PARALLEL_EXECUTION_PLAN.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A1-parallel-plan/agent-prompts.md
- advanced/A2-parallel-worktrees/WORKTREE_EXECUTION_REPORT.md
- beginner/B4-fastapi-service/README.md
```

---

---

<!-- Jira: PM4-6639 -->

**Jira:** [PM4-6639](https://paytmmoney.atlassian.net/browse/PM4-6639) — A2 — Execute Two Parallel Worktrees  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## A2 — Parallel Worktrees

**Folder:** `advanced/A2-parallel-worktrees`  
**Submit file:** `advanced/A2-parallel-worktrees/WORKTREE_EXECUTION_REPORT.md`  
**Reference:** `README.md`, `WORKTREE_EXECUTION_REPORT.md`, `merge-log.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task A2 (Parallel Worktrees).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/A2
3. Read advanced/A2-parallel-worktrees/README.md, WORKTREE_EXECUTION_REPORT.md, merge-log.md.
4. Document git worktree workflow: create worktrees, parallel branches, merge order, and conflicts in WORKTREE_EXECUTION_REPORT.md and merge-log.md.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"A2","agent_name":"cursor","output_path":"advanced/A2-parallel-worktrees/WORKTREE_EXECUTION_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A1-parallel-plan/branch-strategy.md
- advanced/A1-parallel-plan/PARALLEL_EXECUTION_PLAN.md
```

---

---

<!-- Jira: PM4-6642 -->

**Jira:** [PM4-6642](https://paytmmoney.atlassian.net/browse/PM4-6642) — A3 — Polyglot Mini-System: FastAPI, Node Worker, Rust Engine  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## A3 — Polyglot System

**Folder:** `advanced/A3-polyglot-system`  
**Submit file:** `advanced/A3-polyglot-system/docs/REPORT.md`  
**Reference:** `README.md`, `docs/ARCHITECTURE.md`, `docs/REPORT.md`, `scripts/integration-test.sh`

### Copy-paste prompt

```
Evaluate Eval-Ai task A3 (Polyglot System).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/A3
3. Read advanced/A3-polyglot-system/README.md, docs/ARCHITECTURE.md, docs/REPORT.md.
4. Ensure FastAPI → queue → Node worker → Rust scorer flow works. Run: bash advanced/A3-polyglot-system/scripts/integration-test.sh
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"A3","agent_name":"cursor","output_path":"advanced/A3-polyglot-system/docs/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A3-polyglot-system/docs/ARCHITECTURE.md
- beginner/B2-api-endpoint-map/endpoints.csv
- intermediate/I1-er-diagram/ER_REPORT.md
```

---

---

<!-- Jira: PM4-6641 -->

**Jira:** [PM4-6641](https://paytmmoney.atlassian.net/browse/PM4-6641) — A4 — Repository Modernization Plan with Executable First Step  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## A4 — Modernization

**Folder:** `advanced/A4-modernization`  
**Submit file:** `advanced/A4-modernization/MODERNIZATION_REPORT.md`  
**Reference:** `README.md`, `MODERNIZATION_REPORT.md`, `PRIORITIZATION_MATRIX.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task A4 (Modernization).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/A4
3. Read advanced/A4-modernization/README.md, MODERNIZATION_REPORT.md, PRIORITIZATION_MATRIX.md.
4. Analyze legacy patterns across the repo. Update MODERNIZATION_REPORT.md and PRIORITIZATION_MATRIX.md with ranked upgrade items.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"A4","agent_name":"cursor","output_path":"advanced/A4-modernization/MODERNIZATION_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A4-modernization/PRIORITIZATION_MATRIX.md
- beginner/B1-repo-artifact-inventory/REPORT.md
- devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md
```

---

---

<!-- Jira: PM4-6643 -->

**Jira:** [PM4-6643](https://paytmmoney.atlassian.net/browse/PM4-6643) — A5 — Agent Code Review and Adversarial Verification  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## A5 — Agent Review

**Folder:** `advanced/A5-agent-review`  
**Submit file:** `advanced/A5-agent-review/REVIEW_REPORT.md`  
**Reference:** `README.md`, `REVIEW_REPORT.md`, `FINDINGS_MATRIX.md`, `VERIFICATION_PLAN.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task A5 (Agent Review).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/A5
3. Read advanced/A5-agent-review/README.md, REVIEW_REPORT.md, FINDINGS_MATRIX.md, VERIFICATION_PLAN.md.
4. Perform structured code/agent review. Categorize findings in FINDINGS_MATRIX.md format. Summarize in REVIEW_REPORT.md.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"A5","agent_name":"cursor","output_path":"advanced/A5-agent-review/REVIEW_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A5-agent-review/FINDINGS_MATRIX.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

---

<!-- Jira: PM4-6645 -->

**Jira:** [PM4-6645](https://paytmmoney.atlassian.net/browse/PM4-6645) — A6 — Performance Profiling and Targeted Improvement  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## A6 — Performance

**Folder:** `advanced/A6-performance`  
**Submit file:** `advanced/A6-performance/PERFORMANCE_REPORT.md`  
**Reference:** `README.md`, `PERFORMANCE_REPORT.md`, `run-benchmark.sh`, `benchmark-results.csv`

### Copy-paste prompt

```
Evaluate Eval-Ai task A6 (Performance).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/A6
3. Read advanced/A6-performance/README.md, PERFORMANCE_REPORT.md, run-benchmark.sh, benchmark-results.csv.
4. Run benchmarks: BENCH_LINES=100000 BENCH_RUNS=2 bash advanced/A6-performance/run-benchmark.sh. Update PERFORMANCE_REPORT.md with results.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"A6","agent_name":"cursor","output_path":"advanced/A6-performance/PERFORMANCE_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A6-performance/benchmark-results.csv
- devops/D6-observability/docs/METRICS_REPORT.md
```

---

---

<!-- Jira: PM4-6644 -->

**Jira:** [PM4-6644](https://paytmmoney.atlassian.net/browse/PM4-6644) — D1 — Terraform Plan for a Small Service  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## D1 — Terraform

**Folder:** `devops/D1-terraform`  
**Submit file:** `devops/D1-terraform/docs/TERRAFORM_REPORT.md`  
**Reference:** `README.md`, `docs/TERRAFORM_REPORT.md`, `main.tf`

### Copy-paste prompt

```
Evaluate Eval-Ai task D1 (Terraform).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/D1
3. Read devops/D1-terraform/README.md, docs/TERRAFORM_REPORT.md, main.tf.
4. Ensure main.tf and lambda/index.py are valid. Run: cd devops/D1-terraform && mise exec -- terraform init -backend=false -input=false && mise exec -- terraform validate
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"D1","agent_name":"cursor","output_path":"devops/D1-terraform/docs/TERRAFORM_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D1-terraform/main.tf
- devops/D4-kubernetes/docs/K8S_REPORT.md
```

---

---

<!-- Jira: PM4-6646 -->

**Jira:** [PM4-6646](https://paytmmoney.atlassian.net/browse/PM4-6646) — D2 — docker-compose Stack with End-to-End Tests  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## D2 — Docker Compose

**Folder:** `devops/D2-docker-compose`  
**Submit file:** `devops/D2-docker-compose/docs/STACK_REPORT.md`  
**Reference:** `README.md`, `docs/STACK_REPORT.md`, `docker-compose.yml`

### Copy-paste prompt

```
Evaluate Eval-Ai task D2 (Docker Compose).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/D2
3. Read devops/D2-docker-compose/README.md, docs/STACK_REPORT.md, docker-compose.yml.
4. Ensure multi-service stack (Postgres + API + worker) works. Run: bash devops/D2-docker-compose/scripts/e2e_test.sh (Docker required, API port 8200).
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"D2","agent_name":"cursor","output_path":"devops/D2-docker-compose/docs/STACK_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/endpoints.csv
- intermediate/I1-er-diagram/ER_REPORT.md
- devops/D6-observability/docker-compose.yml
```

---

---

<!-- Jira: PM4-6649 -->

**Jira:** [PM4-6649](https://paytmmoney.atlassian.net/browse/PM4-6649) — D3 — CI Pipeline that Lints, Tests, and Builds an Image  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## D3 — CI Pipeline

**Folder:** `devops/D3-ci-pipeline`  
**Submit file:** `devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md`  
**Reference:** `README.md`, `docs/PIPELINE_REPORT.md`, `scripts/run-pipeline-local.sh`

### Copy-paste prompt

```
Evaluate Eval-Ai task D3 (CI Pipeline).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/D3
3. Read devops/D3-ci-pipeline/README.md, docs/PIPELINE_REPORT.md, scripts/run-pipeline-local.sh.
4. Run local pipeline: bash devops/D3-ci-pipeline/scripts/run-pipeline-local.sh. Document lint, test, build stages in PIPELINE_REPORT.md.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"D3","agent_name":"cursor","output_path":"devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D5-dev-environment/docs/BOOTSTRAP_VERIFICATION.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

---

<!-- Jira: PM4-6647 -->

**Jira:** [PM4-6647](https://paytmmoney.atlassian.net/browse/PM4-6647) — D4 — Kubernetes Manifests Verified on a Local Cluster  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## D4 — Kubernetes

**Folder:** `devops/D4-kubernetes`  
**Submit file:** `devops/D4-kubernetes/docs/K8S_REPORT.md`  
**Reference:** `README.md`, `docs/K8S_REPORT.md`, `k8s/deployment.yaml`

### Copy-paste prompt

```
Evaluate Eval-Ai task D4 (Kubernetes).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/D4
3. Read devops/D4-kubernetes/README.md, docs/K8S_REPORT.md, k8s/deployment.yaml.
4. Validate manifests: bash devops/D4-kubernetes/scripts/validate-manifests.sh
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"D4","agent_name":"cursor","output_path":"devops/D4-kubernetes/docs/K8S_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D2-docker-compose/docs/STACK_REPORT.md
- devops/D1-terraform/docs/TERRAFORM_REPORT.md
```

---

---

<!-- Jira: PM4-6648 -->

**Jira:** [PM4-6648](https://paytmmoney.atlassian.net/browse/PM4-6648) — D5 — Reproducible Dev Environment from a Fresh Clone  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## D5 — Dev Environment

**Folder:** `devops/D5-dev-environment`  
**Submit file:** `devops/D5-dev-environment/docs/DEV_ENVIRONMENT_REPORT.md`  
**Reference:** `README.md`, `docs/DEV_ENVIRONMENT_REPORT.md`, `docs/BOOTSTRAP_VERIFICATION.md`

### Copy-paste prompt

```
Evaluate Eval-Ai task D5 (Dev Environment).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/D5
3. Read devops/D5-dev-environment/README.md, docs/DEV_ENVIRONMENT_REPORT.md, docs/BOOTSTRAP_VERIFICATION.md.
4. Verify make bootstrap and make test work from repo root with mise-pinned runtimes. Document setup in DEV_ENVIRONMENT_REPORT.md.
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"D5","agent_name":"cursor","output_path":"devops/D5-dev-environment/docs/DEV_ENVIRONMENT_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D5-dev-environment/docs/BOOTSTRAP_VERIFICATION.md
- beginner/B3-test-discovery/TEST_REPORT.md
- Root Makefile and .mise.toml
```

---

---

<!-- Jira: PM4-6650 -->

**Jira:** [PM4-6650](https://paytmmoney.atlassian.net/browse/PM4-6650) — D6 — Observability Bolt-on with Metrics and a Dashboard  
**GitHub folder:** `https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent/tree/main/` + folder from section below

## D6 — Observability

**Folder:** `devops/D6-observability`  
**Submit file:** `devops/D6-observability/docs/METRICS_REPORT.md`  
**Reference:** `README.md`, `docs/OBSERVABILITY_REPORT.md`, `docs/METRICS_REPORT.md`, `scripts/start-stack.sh`

### Copy-paste prompt

```
Evaluate Eval-Ai task D6 (Observability).

1. Run make eval-api if not running. Open http://127.0.0.1:8788/
2. GET http://127.0.0.1:8788/api/agent/guide/D6
3. Read devops/D6-observability/README.md, docs/OBSERVABILITY_REPORT.md, docs/METRICS_REPORT.md.
4. Run service tests: cd devops/D6-observability/service && mise exec -- pytest -q. For full stack: ./scripts/start-stack.sh and ./scripts/verify_metrics.sh (Docker, Grafana on port 3002).
5. POST http://127.0.0.1:8788/api/agent/submit with:
   {"task_id":"D6","agent_name":"cursor","output_path":"devops/D6-observability/docs/METRICS_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D6-observability/docs/OBSERVABILITY_REPORT.md
- beginner/B4-fastapi-service/README.md
- beginner/B2-api-endpoint-map/endpoints.csv
- docs/DASHBOARD_VISION.md
```

---

---

## Full portfolio prompt (all 24 tasks)

Run every subtask in pipeline order:

```
You are evaluating the Eval-AI-Agent portfolio (24 tasks: B1–B6, I1–I6, A1–A6, D1–D6).

Setup:
1. From repo root: make eval-api → http://127.0.0.1:8788/
2. For EACH task in order:
   - GET http://127.0.0.1:8788/api/agent/guide/{TASK_ID}
   - Complete work in that task folder
   - POST http://127.0.0.1:8788/api/agent/submit with task_id and output_path
3. Final: GET http://127.0.0.1:8788/api/portfolio — report deliverables_ok/24
```

See also [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) for the extended version with mismatch hints.
