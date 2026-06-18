# Evaluation Framework Documentation

Central index for the 24-task Eval AI Agent portfolio. Task **deliverables** (code, reports, configs) live in each task folder under `beginner/`, `intermediate/`, `advanced/`, and `devops/`.

## Documents

| File | Description |
| ---- | ----------- |
| [TASK_REGISTRY.md](TASK_REGISTRY.md) | Master table: all tasks and current status |
| [TASK_MAPPING.md](TASK_MAPPING.md) | Task ID → purpose and folder path |
| [task-registry.json](task-registry.json) | Machine-readable registry (verify, compare API) |
| [AGENT_USAGE.md](AGENT_USAGE.md) | Agent tools, workflow, verification commands |
| [DASHBOARD_VISION.md](DASHBOARD_VISION.md) | Dashboard design + implemented tooling |
| [ORCHESTRATOR_DESIGN.md](ORCHESTRATOR_DESIGN.md) | Task router/executor architecture |

## Eval tooling (compare + dashboard)

```bash
make eval              # check all 24 deliverables → docs/eval-status.json
make eval-dashboard    # HTML dashboard → docs/eval-dashboard.html
make eval-api          # HTTP API on http://127.0.0.1:8787
make eval-compare TASK=I2 AGENT_OUTPUT=./my-output.md
make eval-metrics      # Prometheus text (optional Grafana panel)
```

Generated files (`eval-status.json`, `eval-dashboard.html`) are gitignored; regenerate after changes.

## Quick verify

```bash
make bootstrap
```

See [TASK_REGISTRY.md](TASK_REGISTRY.md) for per-task status and deliverable paths.
