# Orchestrator Design

**Status:** Future architecture — not implemented in this repository yet.

This document outlines a planned orchestrator for running and tracking evaluation tasks with AI coding agents. Existing task implementations and `make bootstrap` remain the source of truth until this is built.

## High-level flow

```text
User Request
     ↓
Task Router        ← parses intent (“run B4”, “refresh B2”, “full basics eval”)
     ↓
Task Registry      ← docs/TASK_REGISTRY.md (+ future JSON)
     ↓
Task Executor      ← runs scripts/tests per task; no silent code changes
     ↓
Dashboard          ← see DASHBOARD_VISION.md
     ↓
Metrics            ← D6 Prometheus + future eval metrics
     ↓
Recommendations    ← stale reports, failing tests, next task suggestions
```

## Components (planned)

### User request

- Natural language or slash-style commands (e.g. “verify all DevOps tasks”)
- Scope: single task, track (beginner/intermediate/advanced/devops), or full portfolio

### Task router

- Maps requests to task IDs using `TASK_MAPPING.md`
- Enforces guardrails: analysis-only tasks (B1–B3) vs implementation tasks (B4+)
- Refuses to modify production API contracts without explicit implement mode

### Task registry

- Human-readable: `docs/TASK_REGISTRY.md` (today)
- Future: `docs/task-registry.json` for automation
- Fields: id, folder, status, verify_command, deliverables[], last_verified

### Task executor

Per-task verification hooks (examples already in repo):

| Task type   | Example verify command                                      |
| ----------- | ----------------------------------------------------------- |
| Code + test | `make test`, per-service `pytest` / `npm test` / `cargo test` |
| Compose     | `devops/D2-docker-compose/scripts/e2e_test.sh`              |
| Observability | `devops/D6-observability/scripts/start-stack.sh` + `verify_metrics.sh` |
| Analysis    | Diff deliverable vs repo scan (agent-assisted)              |
| Terraform   | `terraform validate` in `devops/D1-terraform/`              |
| K8s         | `devops/D4-kubernetes/scripts/validate-manifests.sh`        |

Executor collects stdout, exit codes, and artifacts for the dashboard.

### Dashboard

- Visual layer described in `DASHBOARD_VISION.md`
- Read-only view for evaluators; optional write-back to registry status

### Metrics

- **Operational:** D6 `http_requests_total`, Prometheus targets, Grafana health
- **Eval:** task pass/fail counts, duration, agent attribution (future)

### Recommendations

- Rule-based at first (e.g. B2 stale if B4 routes exist but endpoints.csv empty)
- Later: LLM summary over registry + test logs

## Design principles

1. **Non-breaking** — orchestrator invokes existing scripts; does not rewrite services
2. **Explicit verification** — every “Completed” status backed by a command exit 0
3. **Auditable** — agent runs logged with prompts and file diffs
4. **Incremental** — registry and mapping docs first; automation later

## Current state

| Component        | Status   | Location                          |
| ---------------- | -------- | --------------------------------- |
| Task registry    | Done     | `docs/TASK_REGISTRY.md`, `docs/task-registry.json` |
| Task executor    | Partial  | `make test`, per-task `scripts/`, `make eval --run-tests` |
| Compare API      | Done     | `scripts/eval/portfolio.py`, `make eval-api` |
| HTML dashboard   | Done     | `make eval-dashboard` → `docs/eval-dashboard.html` |
| Grafana eval panel | Partial | `make eval-metrics` (Prometheus text); wire into D6 optional |
| Orchestrator CLI | Planned  | —                                 |

## Related documents

- [`TASK_REGISTRY.md`](TASK_REGISTRY.md)
- [`TASK_MAPPING.md`](TASK_MAPPING.md)
- [`AGENT_USAGE.md`](AGENT_USAGE.md)
