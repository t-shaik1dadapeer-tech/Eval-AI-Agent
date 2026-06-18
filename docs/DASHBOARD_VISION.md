# Dashboard Vision

**Status:** Partially implemented — see **Eval tooling** below. Service metrics remain in **D6 Grafana**.

This document describes the evaluation dashboard for tracking AI agent exercise completion across all 24 tasks. It complements the existing **D6 Grafana** stack (`devops/D6-observability/`), which monitors API request metrics only.

## Implemented today

| Component | Command | Output |
| --------- | ------- | ------ |
| Portfolio verify | `make eval` | `docs/eval-status.json` |
| HTML dashboard | `make eval-dashboard` | `docs/eval-dashboard.html` (24-task grid, completion %) |
| Compare API | `make eval-api` | `http://127.0.0.1:8787/api/compare/{TASK}` |
| Agent compare CLI | `make eval-compare TASK=…` | JSON verdict + suggested `.md` files |
| Prometheus eval metrics | `make eval-metrics` | Text format for optional Grafana panel |
| Registry | `docs/task-registry.json` | Per-task reference files, verify commands |

## Goals (full vision)

Provide evaluators and developers a single view of:

- Task coverage across beginner, intermediate, advanced, and DevOps tracks
- Per-task execution status (Planned, In progress, Completed, Needs refresh)
- Agent execution history (which tool ran which task, when, outcome)
- Success rate and completion percentage across the portfolio
- Health of runnable services (APIs, Docker stacks, CI)
- Actionable recommendations for next tasks or fixes

## Planned capabilities

### Task coverage panel

- Grid or table of B1–B6, I1–I6, A1–A6, D1–D6
- Color-coded status synced from `docs/TASK_REGISTRY.md` (or a future machine-readable registry)
- Drill-down link to each task folder and primary deliverable

### Execution status

- Last verified timestamp per task (e.g. from `make test`, e2e scripts, manual sign-off)
- Failed vs passed verification runs
- Stale deliverable warnings (e.g. B2 endpoint map out of date vs B4/B5 routes)

### Agent execution history

- Agent name (Cursor, Claude, ChatGPT, etc.)
- Task ID, prompt summary, commits produced
- Duration and token/cost estimates (optional)
- Links to PRs, Jira, or Confluence if integrated later

### Success metrics

- **Completion percentage:** completed tasks / 24
- **Automated test pass rate:** from CI and `make bootstrap`
- **Cross-task consistency score:** B1 artifacts vs B2 routes vs B3 test counts

### Grafana integration

- Extend D6 provisioning with an **Eval Portfolio** dashboard folder
- Panels fed by:
  - Prometheus (service health, request rates) — already in D6
  - Future custom exporter reading task registry JSON
  - Optional Loki/log aggregation for agent run logs

### Health monitoring

- Service probes: B4/B5 local APIs, D2 Compose stack, D6 stack, A3 integration script
- Docker/Colima availability indicator
- `make bootstrap` last-run status

### Recommendation engine (future)

- Suggest next task based on gaps (e.g. “Refresh B2 after B4/B5 changes”)
- Flag inconsistent reports before submission
- Propose re-run commands (`make test`, `./scripts/e2e_test.sh`, etc.)

## Non-goals (current phase)

- No dashboard UI code in this repo yet
- No changes to existing API behavior or D6 metrics schema
- No replacement of per-task markdown/CSV deliverables

## Related documents

- [`TASK_REGISTRY.md`](TASK_REGISTRY.md) — current task statuses
- [`ORCHESTRATOR_DESIGN.md`](ORCHESTRATOR_DESIGN.md) — future task routing architecture
- `devops/D6-observability/` — operational Grafana/Prometheus stack today
