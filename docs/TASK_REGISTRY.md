# Task Registry

Master index of all 24 evaluation tasks in this repository. Status reflects the current deliverables in each task folder (not future roadmap items).

| Category     | Task | Folder                              | Status        | Primary deliverables                          |
| ------------ | ---- | ----------------------------------- | ------------- | --------------------------------------------- |
| Beginner     | B1   | `beginner/B1-repo-artifact-inventory/` | Completed     | `REPORT.md`, `inventory.csv`                  |
| Beginner     | B2   | `beginner/B2-api-endpoint-map/`        | Completed     | `API_MAP.md`, `endpoints.csv` (25 routes)     |
| Beginner     | B3   | `beginner/B3-test-discovery/`          | Completed     | `TEST_REPORT.md` (`make test` — 47 pass)      |
| Beginner     | B4   | `beginner/B4-fastapi-service/`         | Completed     | FastAPI service, tests, `REPORT.md`           |
| Beginner     | B5   | `beginner/B5-nodejs-api-cli/`          | Completed     | Express API, tests, `REPORT.md`               |
| Beginner     | B6   | `beginner/B6-rust-cli/`                | Completed     | Rust CLI, tests, `REPORT.md`                  |
| Intermediate | I1   | `intermediate/I1-er-diagram/`          | Completed     | `ER_REPORT.md`, diagrams, CSV exports         |
| Intermediate | I2   | `intermediate/I2-end-to-end-trace/`    | Completed     | `FLOW_TRACE.md`, sequence diagram             |
| Intermediate | I3   | `intermediate/I3-safe-change/`         | Completed     | `CHANGE_REPORT.md`, risk assessment           |
| Intermediate | I4   | `intermediate/I4-fastapi-node-pair/`   | Completed     | FastAPI + Node client, tests, report          |
| Intermediate | I5   | `intermediate/I5-dockerize/`           | Completed     | `Dockerfile`, `docs/DOCKER_REPORT.md`         |
| Intermediate | I6   | `intermediate/I6-bug-diagnosis/`       | Completed     | Bug report, root cause, fix summary           |
| Advanced     | A1   | `advanced/A1-parallel-plan/`           | Completed     | Parallel execution plan, branch strategy      |
| Advanced     | A2   | `advanced/A2-parallel-worktrees/`      | Completed     | Worktree execution report, merge log          |
| Advanced     | A3   | `advanced/A3-polyglot-system/`         | Completed     | FastAPI + Node + Rust, integration test       |
| Advanced     | A4   | `advanced/A4-modernization/`           | Completed     | Modernization report, prioritization matrix   |
| Advanced     | A5   | `advanced/A5-agent-review/`              | Completed     | Review report, findings matrix                |
| Advanced     | A6   | `advanced/A6-performance/`             | Completed     | Performance report, benchmark script          |
| DevOps       | D1   | `devops/D1-terraform/`                 | Completed     | Terraform modules, Lambda, report             |
| DevOps       | D2   | `devops/D2-docker-compose/`              | Completed     | Compose stack, e2e script, report             |
| DevOps       | D3   | `devops/D3-ci-pipeline/`                 | Completed     | CI workflow docs, local pipeline script       |
| DevOps       | D4   | `devops/D4-kubernetes/`                  | Completed     | K8s manifests, validation scripts, report       |
| DevOps       | D5   | `devops/D5-dev-environment/`             | Completed     | Makefile, mise, bootstrap verification        |
| DevOps       | D6   | `devops/D6-observability/`                 | Completed     | Metrics, Prometheus, Grafana, compose stack   |

## Summary

| Status        | Count |
| ------------- | ----: |
| Completed     |    24 |
| Needs refresh |     0 |
| Planned       |     0 |

## Verification entry point

From a fresh clone:

```bash
make bootstrap   # install toolchains + run automated tests
make lint        # optional linters
```

See [`TASK_MAPPING.md`](TASK_MAPPING.md) for task descriptions and [`AGENT_USAGE.md`](AGENT_USAGE.md) for evaluation workflow.

## Eval tooling

```bash
make eval              # deliverables check for all 24 tasks
make eval-dashboard    # HTML portfolio dashboard
make eval-api          # compare API on :8787
```

Machine-readable registry: [`task-registry.json`](task-registry.json).
