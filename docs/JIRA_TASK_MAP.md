# Jira Task Map — Eval-Ai (24 Tasks)

**Epic / Parent:** [PM4-6626](https://paytmmoney.atlassian.net/browse/PM4-6626) — Coding Agent Skill Self-Evaluation  
**GitHub:** [t-shaik1dadapeer-tech/Eval-AI-Agent](https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent)  
**Eval API:** `make eval-api` → http://127.0.0.1:8788

This file maps each repo task (B1–D6) to its Jira subtask, folder, primary deliverable, and git commit.

---

## Beginner (B1–B6)

| Task | Jira | Folder | Primary deliverable | Git commit message |
|------|------|--------|---------------------|-------------------|
| B1 | [PM4-6627](https://paytmmoney.atlassian.net/browse/PM4-6627) | `beginner/B1-repo-artifact-inventory/` | `REPORT.md`, `inventory.csv` | B1: Repository artifact inventory |
| B2 | [PM4-6629](https://paytmmoney.atlassian.net/browse/PM4-6629) | `beginner/B2-api-endpoint-map/` | `API_MAP.md`, `endpoints.csv` | B2: API endpoint map |
| B3 | [PM4-6628](https://paytmmoney.atlassian.net/browse/PM4-6628) | `beginner/B3-test-discovery/` | `TEST_REPORT.md` | B3: Test discovery and execution |
| B4 | [PM4-6630](https://paytmmoney.atlassian.net/browse/PM4-6630) | `beginner/B4-fastapi-service/` | `app/main.py`, tests | B4: FastAPI transaction service |
| B5 | [PM4-6631](https://paytmmoney.atlassian.net/browse/PM4-6631) | `beginner/B5-nodejs-api-cli/` | `src/app.js`, tests | B5: Node.js transaction API |
| B6 | [PM4-6632](https://paytmmoney.atlassian.net/browse/PM4-6632) | `beginner/B6-rust-cli/` | `src/main.rs`, tests | B6: Rust log analyzer CLI |

## Intermediate (I1–I6)

| Task | Jira | Folder | Primary deliverable | Git commit message |
|------|------|--------|---------------------|-------------------|
| I1 | [PM4-6633](https://paytmmoney.atlassian.net/browse/PM4-6633) | `intermediate/I1-er-diagram/` | `ER_REPORT.md`, `er-diagram.mmd` | I1: Repository ER diagram and entity mapping |
| I2 | [PM4-6634](https://paytmmoney.atlassian.net/browse/PM4-6634) | `intermediate/I2-end-to-end-trace/` | `FLOW_TRACE.md`, `sequence-diagram.mmd` | I2: End-to-end flow trace and sequence diagram |
| I3 | [PM4-6635](https://paytmmoney.atlassian.net/browse/PM4-6635) | `intermediate/I3-safe-change/` | `CHANGE_REPORT.md`, `risk-assessment.md` | I3: Small safe change with test coverage |
| I4 | [PM4-6636](https://paytmmoney.atlassian.net/browse/PM4-6636) | `intermediate/I4-fastapi-node-pair/` | FastAPI + Node client | I4: FastAPI service and Node.js CLI client |
| I5 | [PM4-6637](https://paytmmoney.atlassian.net/browse/PM4-6637) | `intermediate/I5-dockerize/` | `Dockerfile`, `DOCKER_REPORT.md` | I5: Dockerize service and verify runtime |
| I6 | [PM4-6638](https://paytmmoney.atlassian.net/browse/PM4-6638) | `intermediate/I6-bug-diagnosis/` | `BUG_REPORT.md`, `ROOT_CAUSE_ANALYSIS.md` | I6: Diagnose and fix seeded bug with verification |

## Advanced (A1–A6)

| Task | Jira | Folder | Primary deliverable | Git commit message |
|------|------|--------|---------------------|-------------------|
| A1 | [PM4-6640](https://paytmmoney.atlassian.net/browse/PM4-6640) | `advanced/A1-parallel-plan/` | `PARALLEL_EXECUTION_PLAN.md` | A1: Multi-worktree parallel execution plan |
| A2 | [PM4-6639](https://paytmmoney.atlassian.net/browse/PM4-6639) | `advanced/A2-parallel-worktrees/` | `WORKTREE_EXECUTION_REPORT.md` | A2: Execute parallel worktrees and reconcile changes |
| A3 | [PM4-6642](https://paytmmoney.atlassian.net/browse/PM4-6642) | `advanced/A3-polyglot-system/` | FastAPI + Node + Rust | A3: Polyglot fraud scoring system |
| A4 | [PM4-6641](https://paytmmoney.atlassian.net/browse/PM4-6641) | `advanced/A4-modernization/` | `MODERNIZATION_REPORT.md` | A4: Repository modernization assessment |
| A5 | [PM4-6643](https://paytmmoney.atlassian.net/browse/PM4-6643) | `advanced/A5-agent-review/` | `REVIEW_REPORT.md` | A5: Agent code review and adversarial verification |
| A6 | [PM4-6645](https://paytmmoney.atlassian.net/browse/PM4-6645) | `advanced/A6-performance/` | `PERFORMANCE_REPORT.md` | A6: Profile and optimize performance bottleneck |

## DevOps (D1–D6)

| Task | Jira | Folder | Primary deliverable | Git commit message |
|------|------|--------|---------------------|-------------------|
| D1 | [PM4-6644](https://paytmmoney.atlassian.net/browse/PM4-6644) | `devops/D1-terraform/` | `main.tf`, `lambda/index.py` | D1: Terraform infrastructure plan and validation |
| D2 | [PM4-6646](https://paytmmoney.atlassian.net/browse/PM4-6646) | `devops/D2-docker-compose/` | `docker-compose.yml`, `e2e_test.sh` | D2: Multi-service docker-compose stack |
| D3 | [PM4-6649](https://paytmmoney.atlassian.net/browse/PM4-6649) | `devops/D3-ci-pipeline/` | `PIPELINE_REPORT.md` | D3: CI pipeline with lint, test, build |
| D4 | [PM4-6647](https://paytmmoney.atlassian.net/browse/PM4-6647) | `devops/D4-kubernetes/` | `k8s/deployment.yaml` | D4: Kubernetes deployment with local verification |
| D5 | [PM4-6648](https://paytmmoney.atlassian.net/browse/PM4-6648) | `devops/D5-dev-environment/` | `README.md`, bootstrap docs | D5: Reproducible development environment bootstrap |
| D6 | [PM4-6650](https://paytmmoney.atlassian.net/browse/PM4-6650) | `devops/D6-observability/` | `docker-compose.yml`, `/metrics` | D6: Observability stack with Prometheus and Grafana |

---

## Pipeline order

`B1 → B2 → B3 → B4 → B5 → B6 → I1 → I2 → I3 → I4 → I5 → I6 → A1 → A2 → A3 → A4 → A5 → A6 → D1 → D2 → D3 → D4 → D5 → D6`

## How to verify a task

```bash
# Get instructions
curl http://127.0.0.1:8788/api/agent/guide/B4

# Submit deliverable
curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"B4","output_path":"beginner/B4-fastapi-service/app/main.py"}'
```

## Related docs

- [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) — copy-paste prompt per task
- [`PM4_JIRA_SUBTASK_PROMPTS.md`](PM4_JIRA_SUBTASK_PROMPTS.md) — all 24 prompts with PM4 Jira subtask links
- [`AGENT_API.md`](AGENT_API.md) — eval server API reference
- [`EVAL_AI_TASK_NOTES.pdf`](EVAL_AI_TASK_NOTES.pdf) — printable 24-task cheat sheet
- [`task-registry.json`](task-registry.json) — machine-readable task config
