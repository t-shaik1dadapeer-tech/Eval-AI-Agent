# Eval AI Agent

Hands-on exercises for evaluating AI coding agents across beginner, intermediate, advanced, and DevOps tracks.

Each subfolder is a self-contained task. Put all deliverables (reports, code, configs) directly in that task folder — not under a separate `docs/` mirror. Then commit and push when ready.

The top-level `docs/` directory holds **evaluation framework** docs. Start with [`docs/SETUP.md`](docs/SETUP.md).

## Fresh clone setup

From a clean machine with `git`, `curl`, and `make`:

```bash
git clone git@github.com:t-shaik1dadapeer-tech/Eval-AI-Agent.git
cd Eval-AI-Agent
make setup
make eval-api          # portfolio dashboard → http://127.0.0.1:8788
```

See [`docs/SETUP.md`](docs/SETUP.md) for the full 24-task pipeline workflow.

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
| [`docs/AGENT_PROMPTS.md`](docs/AGENT_PROMPTS.md) | **Copy-paste prompts for all 24 tasks** |
| [`docs/PM4_JIRA_SUBTASK_PROMPTS.md`](docs/PM4_JIRA_SUBTASK_PROMPTS.md) | **All 24 prompts + Jira links (PM4-6626 subtasks)** |
| [`docs/JIRA_TASK_MAP.md`](docs/JIRA_TASK_MAP.md) | Task ID → Jira key → folder → deliverable |
| [`docs/AGENT_API.md`](docs/AGENT_API.md) | **Clone + agent eval API** (guide, submit, live dashboard) |
| [`docs/AGENT_USAGE.md`](docs/AGENT_USAGE.md) | How to use Cursor/agents + verify work |
| [`docs/DASHBOARD_VISION.md`](docs/DASHBOARD_VISION.md) | Eval dashboard design + implemented tooling |
| [`docs/ORCHESTRATOR_DESIGN.md`](docs/ORCHESTRATOR_DESIGN.md) | Future task router/executor (design only) |
| [`docs/task-registry.json`](docs/task-registry.json) | Machine-readable task profiles + eval API |

## Eval portfolio (24 tasks)

```bash
make eval-api          # Evil-Ai portfolio — live dashboard + agent API → http://127.0.0.1:8788
make eval              # verify deliverables
make eval-compare TASK=B2 AGENT_OUTPUT=./out.csv
```

See [`docs/AGENT_PROMPTS.md`](docs/AGENT_PROMPTS.md) for copy-paste prompts per task, or [`docs/AGENT_API.md`](docs/AGENT_API.md) for the full API reference.

## Eval API usage (after clone)

Start the server once, then use the HTTP API or dashboard. Base URL: **http://127.0.0.1:8788**

```bash
make eval-api    # keep this terminal open
```

### Procedure for reviewers / agents

| Step | Action | Command or URL |
|------|--------|----------------|
| 1 | Start eval server | `make eval-api` |
| 2 | Open live dashboard | http://127.0.0.1:8788 |
| 3 | Health check | `curl http://127.0.0.1:8788/api/health` |
| 4 | Get task instructions | `curl http://127.0.0.1:8788/api/agent/guide/B4` |
| 5 | Do work in task folder | e.g. `beginner/B4-fastapi-service/` |
| 6 | Submit deliverable | `POST /api/agent/submit` (see below) |
| 7 | View all 24 task results | `curl http://127.0.0.1:8788/api/portfolio` |

Replace `B4` with any task ID: `B1`–`B6`, `I1`–`I6`, `A1`–`A6`, `D1`–`D6`.

### Get task guide (step 4)

```bash
curl http://127.0.0.1:8788/api/agent/guide/B4
```

Returns `objective`, `reference_files`, `required_files`, `compare_hint`, and optional `verify_command`.

### Submit work (step 6)

**By file path** (report or code already saved in the repo):

```bash
curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id": "B2",
    "agent_name": "cursor",
    "output_path": "beginner/B2-api-endpoint-map/API_MAP.md"
  }'
```

**By inline markdown** (agent pasted content):

```bash
curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id": "I2",
    "agent_name": "claude",
    "content": "# Flow trace\n..."
  }'
```

Response fields: `verdict` (`ok` | `partial` | `mismatch`), `match_score`, `reference_files`, `suggestion`.

### Main endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Live dashboard (HTML) |
| GET | `/api/health` | Server health check |
| GET | `/api/docs` | Workflow + endpoint list |
| GET | `/api/portfolio` | All 24 tasks + scores (JSON) |
| GET | `/api/tasks` | Task registry |
| GET | `/api/tasks/{id}` | One task status |
| GET | `/api/agent/guide/{id}` | Task instructions (read first) |
| POST | `/api/agent/submit` | Submit output for comparison |
| POST | `/api/portfolio/refresh` | Re-scan repo deliverables |

### CLI equivalents (no curl)

```bash
make eval                              # verify all deliverables
make eval-compare TASK=B2              # show reference files for B2
make eval-compare TASK=B2 AGENT_OUTPUT=./out.md
```

Prompts per task (including Jira PM4-6626 links): [`docs/PM4_JIRA_SUBTASK_PROMPTS.md`](docs/PM4_JIRA_SUBTASK_PROMPTS.md).

External live API vs `.md` comparison: [`docs/EXTERNAL_EVAL.md`](docs/EXTERNAL_EVAL.md) (`POST /api/external/register`, `POST /api/external/analyze`).

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
