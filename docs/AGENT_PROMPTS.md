# Agent Prompts — All 24 Tasks

Copy-paste prompts for each PML/OCL task. Start the portfolio with **`make eval-api`** or see **`docs/SETUP.md`**.

## Before you start

```bash
cd Evil-Ai
make setup
make eval-api    # http://127.0.0.1:8788 — Evil-Ai portfolio dashboard
make install-cursor-skills   # optional: /evil-ai-* slash commands in Cursor
```

Each task also has **`eval_blueprints/{ID}_blueprint.md`** listing required `.md` files.

---

## Universal prompt — any target repo

```
You are running Evil-Ai task {TASK_ID} on my repository.

1. Read eval_blueprints/{TASK_ID}_blueprint.md
2. Read docs/AGENT_PROMPTS.md section {TASK_ID}
3. Do the work — create the required .md files listed in the blueprint
4. Run make eval to verify files exist
```

Replace `{TASK_ID}`. Attach repo in Cursor with `@/path/to/repo` if analyzing another project.

---

## Full portfolio prompt (all 24)

Copy everything inside the block below for a full portfolio run:

```
You are evaluating the Evil-Ai portfolio (24 tasks: B1–B6, I1–I6, A1–A6, D1–D6).

Setup:
1. From repo root run: make eval-api (if not already running).
2. Open http://127.0.0.1:8787/ for the live dashboard.

For EACH task in order (B1, B2, B3, B4, B5, B6, I1, I2, I3, I4, I5, I6, A1, A2, A3, A4, A5, A6, D1, D2, D3, D4, D5, D6):
1. GET http://127.0.0.1:8787/api/agent/guide/{TASK_ID}
2. Read every file listed in reference_files from the repo.
3. Complete or verify work in that task's folder only.
4. POST http://127.0.0.1:8787/api/agent/submit with JSON: {"task_id":"{TASK_ID}","agent_name":"cursor","output_path":"<primary deliverable path>"}
5. If verdict is partial or mismatch, read reference_files AND the "If mismatch" related files from docs/AGENT_PROMPTS.md for that task.
6. Run verify_command from the guide response when present.

Final report:
- GET http://127.0.0.1:8787/api/portfolio
- Summarize: deliverables_ok/24, agent_ok/24, agent_evaluated/24
- List any failed tasks with suggested .md files to read.
```

---

## B1 — Repository Artifact Inventory

**Folder:** `beginner/B1-repo-artifact-inventory`  
**Submit file:** `beginner/B1-repo-artifact-inventory/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`, `inventory.csv`

### Copy-paste prompt

```
Evaluate Evil-Ai task B1 (Repository Artifact Inventory).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/B1
3. Read beginner/B1-repo-artifact-inventory/README.md, REPORT.md, and inventory.csv.
4. Scan the repo and ensure inventory.csv lists artifacts by category (controllers, services, tests, configs, docs) with correct paths. Update REPORT.md with counts and summary.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"B1","agent_name":"cursor","output_path":"beginner/B1-repo-artifact-inventory/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/API_MAP.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

## B2 — API Endpoint Map

**Folder:** `beginner/B2-api-endpoint-map`  
**Submit file:** `beginner/B2-api-endpoint-map/API_MAP.md` (or `endpoints.csv`)  
**Reference:** `README.md`, `API_MAP.md`, `endpoints.csv`

### Copy-paste prompt

```
Evaluate Evil-Ai task B2 (API Endpoint Map).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/B2
3. Read beginner/B2-api-endpoint-map/README.md, API_MAP.md, endpoints.csv.
4. Scan HTTP routes in B4, B5, I4, A3, D2, D6 services. Update endpoints.csv and API_MAP.md so every route matches actual handlers.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"B2","agent_name":"cursor","output_path":"beginner/B2-api-endpoint-map/endpoints.csv"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/README.md
- beginner/B5-nodejs-api-cli/README.md
- devops/D6-observability/README.md
- beginner/B1-repo-artifact-inventory/inventory.csv
```

---

## B3 — Test Discovery

**Folder:** `beginner/B3-test-discovery`  
**Submit file:** `beginner/B3-test-discovery/TEST_REPORT.md`  
**Reference:** `README.md`, `TEST_REPORT.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task B3 (Test Discovery).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/B3
3. Read beginner/B3-test-discovery/README.md and TEST_REPORT.md.
4. Run make test from repo root. Update TEST_REPORT.md with frameworks found (pytest, Jest, Cargo), test counts, and pass/fail summary.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"B3","agent_name":"cursor","output_path":"beginner/B3-test-discovery/TEST_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/tests/
- beginner/B5-nodejs-api-cli/tests/
- beginner/B6-rust-cli/tests/
- devops/D5-dev-environment/docs/BOOTSTRAP_VERIFICATION.md
```

---

## B4 — FastAPI Transaction Service

**Folder:** `beginner/B4-fastapi-service`  
**Submit file:** `beginner/B4-fastapi-service/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task B4 (FastAPI Transaction Service).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/B4
3. Read beginner/B4-fastapi-service/README.md and REPORT.md.
4. Ensure app/main.py, app/routes/transactions.py, and tests/test_transactions.py implement the in-memory transaction REST API per README. Run: cd beginner/B4-fastapi-service && mise exec -- pytest -q
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"B4","agent_name":"cursor","output_path":"beginner/B4-fastapi-service/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/endpoints.csv
- beginner/B5-nodejs-api-cli/README.md
- devops/D6-observability/service/app/main.py
```

---

## B5 — Node.js Transaction API

**Folder:** `beginner/B5-nodejs-api-cli`  
**Submit file:** `beginner/B5-nodejs-api-cli/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task B5 (Node.js Transaction API).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/B5
3. Read beginner/B5-nodejs-api-cli/README.md and REPORT.md.
4. Ensure src/app.js, src/routes/transactionRoutes.js, and tests/transactions.test.js mirror B4 endpoints. Run: cd beginner/B5-nodejs-api-cli && mise exec -- npm test
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"B5","agent_name":"cursor","output_path":"beginner/B5-nodejs-api-cli/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/endpoints.csv
- beginner/B4-fastapi-service/README.md
```

---

## B6 — Rust Log Analyzer CLI

**Folder:** `beginner/B6-rust-cli`  
**Submit file:** `beginner/B6-rust-cli/REPORT.md`  
**Reference:** `README.md`, `REPORT.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task B6 (Rust Log Analyzer CLI).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/B6
3. Read beginner/B6-rust-cli/README.md and REPORT.md.
4. Ensure src/main.rs, src/analyzer.rs, and tests/log_analyzer_test.rs count INFO/WARN/ERROR lines per README. Run: cd beginner/B6-rust-cli && mise exec -- cargo test -q
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"B6","agent_name":"cursor","output_path":"beginner/B6-rust-cli/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B3-test-discovery/TEST_REPORT.md
- beginner/B1-repo-artifact-inventory/inventory.csv
```

---

## I1 — ER Diagram

**Folder:** `intermediate/I1-er-diagram`  
**Submit file:** `intermediate/I1-er-diagram/ER_REPORT.md`  
**Reference:** `README.md`, `ER_REPORT.md`, `er-diagram.mmd`, `entities.csv`

### Copy-paste prompt

```
Evaluate Evil-Ai task I1 (ER Diagram).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/I1
3. Read intermediate/I1-er-diagram/README.md, ER_REPORT.md, er-diagram.mmd, entities.csv.
4. Document entities and relationships from B4, D2, and A3 data models. Update ER_REPORT.md and er-diagram.mmd.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"I1","agent_name":"cursor","output_path":"intermediate/I1-er-diagram/ER_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/app/models/
- devops/D2-docker-compose/
- advanced/A3-polyglot-system/docs/ARCHITECTURE.md
```

---

## I2 — End-to-End Trace

**Folder:** `intermediate/I2-end-to-end-trace`  
**Submit file:** `intermediate/I2-end-to-end-trace/FLOW_TRACE.md`  
**Reference:** `README.md`, `FLOW_TRACE.md`, `sequence-diagram.mmd`, `flow-summary.csv`

### Copy-paste prompt

```
Evaluate Evil-Ai task I2 (End-to-End Trace).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/I2
3. Read intermediate/I2-end-to-end-trace/README.md, FLOW_TRACE.md, sequence-diagram.mmd, flow-summary.csv.
4. Document request flow across B4/B5 (or chosen service): client → API → handler → response. Update FLOW_TRACE.md and sequence-diagram.mmd.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"I2","agent_name":"cursor","output_path":"intermediate/I2-end-to-end-trace/FLOW_TRACE.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/API_MAP.md
- beginner/B4-fastapi-service/README.md
- devops/D6-observability/docs/OBSERVABILITY_REPORT.md
```

---

## I3 — Safe Change

**Folder:** `intermediate/I3-safe-change`  
**Submit file:** `intermediate/I3-safe-change/CHANGE_REPORT.md`  
**Reference:** `README.md`, `CHANGE_REPORT.md`, `risk-assessment.md`, `diff-summary.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task I3 (Safe Change).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/I3
3. Read intermediate/I3-safe-change/README.md, CHANGE_REPORT.md, risk-assessment.md, diff-summary.md.
4. Assess a scoped change (e.g. adding a field to transaction DTO). Document scope, risks, rollback, and test plan in CHANGE_REPORT.md and risk-assessment.md.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"I3","agent_name":"cursor","output_path":"intermediate/I3-safe-change/CHANGE_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/REPORT.md
- intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md
```

---

## I4 — FastAPI + Node Pair

**Folder:** `intermediate/I4-fastapi-node-pair`  
**Submit file:** `intermediate/I4-fastapi-node-pair/docs/REPORT.md`  
**Reference:** `README.md`, `docs/REPORT.md`, `fastapi-service/README.md`, `node-client/README.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task I4 (FastAPI + Node Pair).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/I4
3. Read intermediate/I4-fastapi-node-pair/README.md, docs/REPORT.md, fastapi-service/README.md, node-client/README.md.
4. Ensure FastAPI POST /convert and Node CLI client work. Run pytest in fastapi-service and npm test in node-client.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"I4","agent_name":"cursor","output_path":"intermediate/I4-fastapi-node-pair/docs/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B4-fastapi-service/README.md
- beginner/B5-nodejs-api-cli/README.md
- beginner/B2-api-endpoint-map/endpoints.csv
```

---

## I5 — Dockerize

**Folder:** `intermediate/I5-dockerize`  
**Submit file:** `intermediate/I5-dockerize/docs/DOCKER_REPORT.md`  
**Reference:** `README.md`, `docs/DOCKER_REPORT.md`, `Dockerfile`

### Copy-paste prompt

```
Evaluate Evil-Ai task I5 (Dockerize).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/I5
3. Read intermediate/I5-dockerize/README.md, docs/DOCKER_REPORT.md, Dockerfile.
4. Document build/run steps. Verify docker build and container run per DOCKER_REPORT.md (Docker required).
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"I5","agent_name":"cursor","output_path":"intermediate/I5-dockerize/docs/DOCKER_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D2-docker-compose/docs/STACK_REPORT.md
- intermediate/I4-fastapi-node-pair/fastapi-service/
```

---

## I6 — Bug Diagnosis

**Folder:** `intermediate/I6-bug-diagnosis`  
**Submit file:** `intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md`  
**Reference:** `README.md`, `BUG_REPORT.md`, `ROOT_CAUSE_ANALYSIS.md`, `FIX_SUMMARY.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task I6 (Bug Diagnosis).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/I6
3. Read intermediate/I6-bug-diagnosis/README.md, BUG_REPORT.md, ROOT_CAUSE_ANALYSIS.md, FIX_SUMMARY.md.
4. Document bug symptoms, root cause, fix, and verification in the three report files following the repo structure.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"I6","agent_name":"cursor","output_path":"intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- intermediate/I3-safe-change/CHANGE_REPORT.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

## A1 — Parallel Planning

**Folder:** `advanced/A1-parallel-plan`  
**Submit file:** `advanced/A1-parallel-plan/PARALLEL_EXECUTION_PLAN.md`  
**Reference:** `README.md`, `PARALLEL_EXECUTION_PLAN.md`, `agent-prompts.md`, `branch-strategy.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task A1 (Parallel Planning).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/A1
3. Read advanced/A1-parallel-plan/README.md, PARALLEL_EXECUTION_PLAN.md, agent-prompts.md, branch-strategy.md.
4. Ensure multi-lane parallel plan and per-agent prompts are complete for B4 extension work. Lane prompts live in agent-prompts.md.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"A1","agent_name":"cursor","output_path":"advanced/A1-parallel-plan/PARALLEL_EXECUTION_PLAN.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A1-parallel-plan/agent-prompts.md
- advanced/A2-parallel-worktrees/WORKTREE_EXECUTION_REPORT.md
- beginner/B4-fastapi-service/README.md
```

---

## A2 — Parallel Worktrees

**Folder:** `advanced/A2-parallel-worktrees`  
**Submit file:** `advanced/A2-parallel-worktrees/WORKTREE_EXECUTION_REPORT.md`  
**Reference:** `README.md`, `WORKTREE_EXECUTION_REPORT.md`, `merge-log.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task A2 (Parallel Worktrees).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/A2
3. Read advanced/A2-parallel-worktrees/README.md, WORKTREE_EXECUTION_REPORT.md, merge-log.md.
4. Document git worktree workflow: create worktrees, parallel branches, merge order, and conflicts in WORKTREE_EXECUTION_REPORT.md and merge-log.md.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"A2","agent_name":"cursor","output_path":"advanced/A2-parallel-worktrees/WORKTREE_EXECUTION_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A1-parallel-plan/branch-strategy.md
- advanced/A1-parallel-plan/PARALLEL_EXECUTION_PLAN.md
```

---

## A3 — Polyglot System

**Folder:** `advanced/A3-polyglot-system`  
**Submit file:** `advanced/A3-polyglot-system/docs/REPORT.md`  
**Reference:** `README.md`, `docs/ARCHITECTURE.md`, `docs/REPORT.md`, `scripts/integration-test.sh`

### Copy-paste prompt

```
Evaluate Evil-Ai task A3 (Polyglot System).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/A3
3. Read advanced/A3-polyglot-system/README.md, docs/ARCHITECTURE.md, docs/REPORT.md.
4. Ensure FastAPI → queue → Node worker → Rust scorer flow works. Run: bash advanced/A3-polyglot-system/scripts/integration-test.sh
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"A3","agent_name":"cursor","output_path":"advanced/A3-polyglot-system/docs/REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A3-polyglot-system/docs/ARCHITECTURE.md
- beginner/B2-api-endpoint-map/endpoints.csv
- intermediate/I1-er-diagram/ER_REPORT.md
```

---

## A4 — Modernization

**Folder:** `advanced/A4-modernization`  
**Submit file:** `advanced/A4-modernization/MODERNIZATION_REPORT.md`  
**Reference:** `README.md`, `MODERNIZATION_REPORT.md`, `PRIORITIZATION_MATRIX.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task A4 (Modernization).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/A4
3. Read advanced/A4-modernization/README.md, MODERNIZATION_REPORT.md, PRIORITIZATION_MATRIX.md.
4. Analyze legacy patterns across the repo. Update MODERNIZATION_REPORT.md and PRIORITIZATION_MATRIX.md with ranked upgrade items.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"A4","agent_name":"cursor","output_path":"advanced/A4-modernization/MODERNIZATION_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A4-modernization/PRIORITIZATION_MATRIX.md
- beginner/B1-repo-artifact-inventory/REPORT.md
- devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md
```

---

## A5 — Agent Review

**Folder:** `advanced/A5-agent-review`  
**Submit file:** `advanced/A5-agent-review/REVIEW_REPORT.md`  
**Reference:** `README.md`, `REVIEW_REPORT.md`, `FINDINGS_MATRIX.md`, `VERIFICATION_PLAN.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task A5 (Agent Review).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/A5
3. Read advanced/A5-agent-review/README.md, REVIEW_REPORT.md, FINDINGS_MATRIX.md, VERIFICATION_PLAN.md.
4. Perform structured code/agent review. Categorize findings in FINDINGS_MATRIX.md format. Summarize in REVIEW_REPORT.md.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"A5","agent_name":"cursor","output_path":"advanced/A5-agent-review/REVIEW_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A5-agent-review/FINDINGS_MATRIX.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

## A6 — Performance

**Folder:** `advanced/A6-performance`  
**Submit file:** `advanced/A6-performance/PERFORMANCE_REPORT.md`  
**Reference:** `README.md`, `PERFORMANCE_REPORT.md`, `run-benchmark.sh`, `benchmark-results.csv`

### Copy-paste prompt

```
Evaluate Evil-Ai task A6 (Performance).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/A6
3. Read advanced/A6-performance/README.md, PERFORMANCE_REPORT.md, run-benchmark.sh, benchmark-results.csv.
4. Run benchmarks: BENCH_LINES=100000 BENCH_RUNS=2 bash advanced/A6-performance/run-benchmark.sh. Update PERFORMANCE_REPORT.md with results.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"A6","agent_name":"cursor","output_path":"advanced/A6-performance/PERFORMANCE_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- advanced/A6-performance/benchmark-results.csv
- devops/D6-observability/docs/METRICS_REPORT.md
```

---

## D1 — Terraform

**Folder:** `devops/D1-terraform`  
**Submit file:** `devops/D1-terraform/docs/TERRAFORM_REPORT.md`  
**Reference:** `README.md`, `docs/TERRAFORM_REPORT.md`, `main.tf`

### Copy-paste prompt

```
Evaluate Evil-Ai task D1 (Terraform).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/D1
3. Read devops/D1-terraform/README.md, docs/TERRAFORM_REPORT.md, main.tf.
4. Ensure main.tf and lambda/index.py are valid. Run: cd devops/D1-terraform && mise exec -- terraform init -backend=false -input=false && mise exec -- terraform validate
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"D1","agent_name":"cursor","output_path":"devops/D1-terraform/docs/TERRAFORM_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D1-terraform/main.tf
- devops/D4-kubernetes/docs/K8S_REPORT.md
```

---

## D2 — Docker Compose

**Folder:** `devops/D2-docker-compose`  
**Submit file:** `devops/D2-docker-compose/docs/STACK_REPORT.md`  
**Reference:** `README.md`, `docs/STACK_REPORT.md`, `docker-compose.yml`

### Copy-paste prompt

```
Evaluate Evil-Ai task D2 (Docker Compose).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/D2
3. Read devops/D2-docker-compose/README.md, docs/STACK_REPORT.md, docker-compose.yml.
4. Ensure multi-service stack (Postgres + API + worker) works. Run: bash devops/D2-docker-compose/scripts/e2e_test.sh (Docker required, API port 8200).
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"D2","agent_name":"cursor","output_path":"devops/D2-docker-compose/docs/STACK_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- beginner/B2-api-endpoint-map/endpoints.csv
- intermediate/I1-er-diagram/ER_REPORT.md
- devops/D6-observability/docker-compose.yml
```

---

## D3 — CI Pipeline

**Folder:** `devops/D3-ci-pipeline`  
**Submit file:** `devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md`  
**Reference:** `README.md`, `docs/PIPELINE_REPORT.md`, `scripts/run-pipeline-local.sh`

### Copy-paste prompt

```
Evaluate Evil-Ai task D3 (CI Pipeline).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/D3
3. Read devops/D3-ci-pipeline/README.md, docs/PIPELINE_REPORT.md, scripts/run-pipeline-local.sh.
4. Run local pipeline: bash devops/D3-ci-pipeline/scripts/run-pipeline-local.sh. Document lint, test, build stages in PIPELINE_REPORT.md.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"D3","agent_name":"cursor","output_path":"devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D5-dev-environment/docs/BOOTSTRAP_VERIFICATION.md
- beginner/B3-test-discovery/TEST_REPORT.md
```

---

## D4 — Kubernetes

**Folder:** `devops/D4-kubernetes`  
**Submit file:** `devops/D4-kubernetes/docs/K8S_REPORT.md`  
**Reference:** `README.md`, `docs/K8S_REPORT.md`, `k8s/deployment.yaml`

### Copy-paste prompt

```
Evaluate Evil-Ai task D4 (Kubernetes).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/D4
3. Read devops/D4-kubernetes/README.md, docs/K8S_REPORT.md, k8s/deployment.yaml.
4. Validate manifests: bash devops/D4-kubernetes/scripts/validate-manifests.sh
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"D4","agent_name":"cursor","output_path":"devops/D4-kubernetes/docs/K8S_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D2-docker-compose/docs/STACK_REPORT.md
- devops/D1-terraform/docs/TERRAFORM_REPORT.md
```

---

## D5 — Dev Environment

**Folder:** `devops/D5-dev-environment`  
**Submit file:** `devops/D5-dev-environment/docs/DEV_ENVIRONMENT_REPORT.md`  
**Reference:** `README.md`, `docs/DEV_ENVIRONMENT_REPORT.md`, `docs/BOOTSTRAP_VERIFICATION.md`

### Copy-paste prompt

```
Evaluate Evil-Ai task D5 (Dev Environment).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/D5
3. Read devops/D5-dev-environment/README.md, docs/DEV_ENVIRONMENT_REPORT.md, docs/BOOTSTRAP_VERIFICATION.md.
4. Verify make bootstrap and make test work from repo root with mise-pinned runtimes. Document setup in DEV_ENVIRONMENT_REPORT.md.
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"D5","agent_name":"cursor","output_path":"devops/D5-dev-environment/docs/DEV_ENVIRONMENT_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D5-dev-environment/docs/BOOTSTRAP_VERIFICATION.md
- beginner/B3-test-discovery/TEST_REPORT.md
- Root Makefile and .mise.toml
```

---

## D6 — Observability

**Folder:** `devops/D6-observability`  
**Submit file:** `devops/D6-observability/docs/METRICS_REPORT.md`  
**Reference:** `README.md`, `docs/OBSERVABILITY_REPORT.md`, `docs/METRICS_REPORT.md`, `scripts/start-stack.sh`

### Copy-paste prompt

```
Evaluate Evil-Ai task D6 (Observability).

1. Run make eval-api if not running. Open http://127.0.0.1:8787/
2. GET http://127.0.0.1:8787/api/agent/guide/D6
3. Read devops/D6-observability/README.md, docs/OBSERVABILITY_REPORT.md, docs/METRICS_REPORT.md.
4. Run service tests: cd devops/D6-observability/service && mise exec -- pytest -q. For full stack: ./scripts/start-stack.sh and ./scripts/verify_metrics.sh (Docker, Grafana on port 3002).
5. POST http://127.0.0.1:8787/api/agent/submit with:
   {"task_id":"D6","agent_name":"cursor","output_path":"devops/D6-observability/docs/METRICS_REPORT.md"}
6. Run `make eval` to confirm required files exist for this task.

If mismatch, also read:
- devops/D6-observability/docs/OBSERVABILITY_REPORT.md
- beginner/B4-fastapi-service/README.md
- beginner/B2-api-endpoint-map/endpoints.csv
- docs/DASHBOARD_VISION.md
```

---

## Quick reference table

| ID | Submit this file | Verify (optional) |
|----|------------------|-------------------|
| B1 | `beginner/B1-repo-artifact-inventory/REPORT.md` | — |
| B2 | `beginner/B2-api-endpoint-map/endpoints.csv` | — |
| B3 | `beginner/B3-test-discovery/TEST_REPORT.md` | `make test` |
| B4 | `beginner/B4-fastapi-service/REPORT.md` | `pytest` in B4 |
| B5 | `beginner/B5-nodejs-api-cli/REPORT.md` | `npm test` in B5 |
| B6 | `beginner/B6-rust-cli/REPORT.md` | `cargo test` in B6 |
| I1 | `intermediate/I1-er-diagram/ER_REPORT.md` | — |
| I2 | `intermediate/I2-end-to-end-trace/FLOW_TRACE.md` | — |
| I3 | `intermediate/I3-safe-change/CHANGE_REPORT.md` | — |
| I4 | `intermediate/I4-fastapi-node-pair/docs/REPORT.md` | pytest + npm test |
| I5 | `intermediate/I5-dockerize/docs/DOCKER_REPORT.md` | Docker build |
| I6 | `intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md` | — |
| A1 | `advanced/A1-parallel-plan/PARALLEL_EXECUTION_PLAN.md` | — |
| A2 | `advanced/A2-parallel-worktrees/WORKTREE_EXECUTION_REPORT.md` | — |
| A3 | `advanced/A3-polyglot-system/docs/REPORT.md` | `integration-test.sh` |
| A4 | `advanced/A4-modernization/MODERNIZATION_REPORT.md` | — |
| A5 | `advanced/A5-agent-review/REVIEW_REPORT.md` | — |
| A6 | `advanced/A6-performance/PERFORMANCE_REPORT.md` | `run-benchmark.sh` |
| D1 | `devops/D1-terraform/docs/TERRAFORM_REPORT.md` | `terraform validate` |
| D2 | `devops/D2-docker-compose/docs/STACK_REPORT.md` | `e2e_test.sh` |
| D3 | `devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md` | `run-pipeline-local.sh` |
| D4 | `devops/D4-kubernetes/docs/K8S_REPORT.md` | `validate-manifests.sh` |
| D5 | `devops/D5-dev-environment/docs/DEV_ENVIRONMENT_REPORT.md` | `make test` |
| D6 | `devops/D6-observability/docs/METRICS_REPORT.md` | `pytest` in D6 service |

---

## CLI alternative (no HTTP)

```bash
make eval-compare TASK=I2 AGENT_OUTPUT=intermediate/I2-end-to-end-trace/FLOW_TRACE.md
make eval    # scan all 24 deliverables
```

---

## Related documents

- [`AGENT_API.md`](AGENT_API.md) — HTTP API reference
- [`AGENT_USAGE.md`](AGENT_USAGE.md) — human workflow
- [`TASK_REGISTRY.md`](TASK_REGISTRY.md) — task status table
- [`TASK_MAPPING.md`](TASK_MAPPING.md) — task descriptions
