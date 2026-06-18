# Eval AI Agent

Hands-on exercises for evaluating AI coding agents across beginner, intermediate, advanced, and DevOps tracks.

Each subfolder is a self-contained task. Put all deliverables (reports, code, configs) directly in that task folder — not under a separate `docs/` mirror. Then commit and push when ready.

The top-level `docs/` directory holds **evaluation framework** documentation (task registry, mapping, agent usage, future dashboard/orchestrator design). See [`docs/TASK_REGISTRY.md`](docs/TASK_REGISTRY.md) for status of all 24 tasks.

## Fresh clone setup

From a clean machine with `git`, `curl`, and `make`:

```bash
git clone <repo-url> Evil-Ai
cd Evil-Ai
make bootstrap
```

This installs pinned runtimes via [mise](https://mise.jdx.dev) and runs the full test suite. See [`devops/D5-dev-environment/README.md`](devops/D5-dev-environment/README.md) for details.

```bash
make test    # run tests only
make lint    # ruff + cargo fmt/clippy
make help    # all targets
```

## Structure

```
Eval-ai-agent/
├── docs/                    ← task registry, mapping, agent usage (see below)
├── beginner/
│   ├── B1-repo-artifact-inventory/
│   ├── B2-api-endpoint-map/
│   ├── B3-test-discovery/
│   ├── B4-fastapi-service/
│   ├── B5-nodejs-api-cli/
│   └── B6-rust-cli/
├── intermediate/
│   ├── I1-er-diagram/
│   ├── I2-end-to-end-trace/
│   ├── I3-safe-change/
│   ├── I4-fastapi-node-pair/
│   ├── I5-dockerize/
│   └── I6-bug-diagnosis/
├── advanced/
│   ├── A1-parallel-plan/
│   ├── A2-parallel-worktrees/
│   ├── A3-polyglot-system/
│   ├── A4-modernization/
│   ├── A5-agent-review/
│   └── A6-performance/
└── devops/
    ├── D1-terraform/
    ├── D2-docker-compose/
    ├── D3-ci-pipeline/
    ├── D4-kubernetes/
    ├── D5-dev-environment/
    └── D6-observability/
```

## Evaluation framework (`docs/`)

| Document | Purpose |
| -------- | ------- |
| [`docs/TASK_REGISTRY.md`](docs/TASK_REGISTRY.md) | Status of all 24 tasks (B1–D6) |
| [`docs/TASK_MAPPING.md`](docs/TASK_MAPPING.md) | Task ID → name, purpose, folder |
| [`docs/AGENT_USAGE.md`](docs/AGENT_USAGE.md) | How to use Cursor/agents + verify work |
| [`docs/DASHBOARD_VISION.md`](docs/DASHBOARD_VISION.md) | Future eval dashboard (design only) |
| [`docs/ORCHESTRATOR_DESIGN.md`](docs/ORCHESTRATOR_DESIGN.md) | Future task orchestrator (design only) |

## Tracks

| Track | Tasks | Focus |
|-------|-------|-------|
| **beginner** | B1–B6 | Repo exploration, APIs, tests, FastAPI, Node.js CLI, Rust CLI |
| **intermediate** | I1–I6 | ER diagrams, tracing, safe changes, polyglot pairs, Docker, debugging |
| **advanced** | A1–A6 | Parallel planning, worktrees, polyglot systems, modernization, agent review, performance |
| **devops** | D1–D6 | Terraform, Compose, CI, Kubernetes, dev environments, observability |

## Workflow

1. Pick a task folder (e.g. `beginner/B4-fastapi-service/`).
2. Add your code and any notes for that exercise.
3. Commit from the repo root:

   ```bash
   git add beginner/B4-fastapi-service/
   git commit -m "B4: add FastAPI service"
   ```

4. Push when your remote is configured.
