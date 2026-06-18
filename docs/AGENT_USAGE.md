# Agent Usage

How to use AI coding agents (and manual verification) when working on Eval AI Agent tasks. This repo is designed for hands-on evaluation of agent quality across 24 exercises.

## Supported tools

| Tool    | Typical use                                      |
| ------- | ------------------------------------------------ |
| Cursor  | Primary IDE agent; rules/skills in `.cursor/`   |
| Claude  | Architecture, reports, long-context analysis    |
| ChatGPT | Explaining tasks, comparing deliverables        |
| Manual  | Final sign-off, Docker/infra, spot-checks       |

## Recommended workflow

1. **Pick a task** from [`TASK_REGISTRY.md`](TASK_REGISTRY.md).
2. **Read the mapping** in [`TASK_MAPPING.md`](TASK_MAPPING.md) for scope.
3. **Work in the task folder only** — deliverables live under `beginner/`, `intermediate/`, `advanced/`, or `devops/` (not a separate mirror under root `docs/` except registry files).
4. **Run verification** before marking complete (see below).
5. **Update registry status** if you refresh a task (e.g. B2, B3).

## Eval compare API (agent output vs reference `.md`)

**Start the eval server first** (works on any fresh clone):

```bash
make eval-api    # http://127.0.0.1:8787 — live dashboard + all endpoints below
```

Full API reference: [`AGENT_API.md`](AGENT_API.md).  
Copy-paste prompts per task: [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md).

When an agent finishes a task, compare its output to the repo ground truth:

```bash
# Show reference files and hint (no agent file)
make eval-compare TASK=I2

# Compare agent-produced file
make eval-compare TASK=I2 AGENT_OUTPUT=./agent-flow.md
```

The response includes:

- `verdict`: `ok` | `partial` | `mismatch` | `reference_only`
- `reference_files`: which `.md` / `.csv` files define expected output
- `suggestion`: e.g. “Read `intermediate/I2-end-to-end-trace/FLOW_TRACE.md`…”

HTTP API (after `make eval-api`):

```bash
curl http://127.0.0.1:8787/api/portfolio
curl http://127.0.0.1:8787/api/agent/guide/I2
curl -X POST http://127.0.0.1:8787/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"I2","agent_name":"cursor","output_path":"intermediate/I2-end-to-end-trace/FLOW_TRACE.md"}'
open http://127.0.0.1:8787/
```

Registry source: [`task-registry.json`](task-registry.json).

## Portfolio dashboard (24 tasks)

Open **http://127.0.0.1:8787/** after `make eval-api`. The page auto-refreshes and shows:

- **Total / deliverables OK / executable / agent compared / agent OK** out of 24
- Per-task agent eval status when submissions are posted via `/api/agent/submit`

For A1, drill into `advanced/A1-parallel-plan/agent-prompts.md` for per-lane agent prompts.

## Verification by task type

### Analysis tasks (B1–B3)

- Re-scan the repo; update CSV/report deliverables.
- Cross-check: B1 controllers should appear in B2 routes; B3 should list frameworks found in B4–B6.
- Another agent can compare output to repo: “List gaps vs `inventory.csv`.”

### Implementation tasks (B4–B6, I4, A3, etc.)

```bash
make test                    # from repo root
make lint                    # optional
```

### DevOps tasks

```bash
make bootstrap                              # D5 full suite
cd devops/D1-terraform && terraform validate
cd devops/D2-docker-compose && ./scripts/e2e_test.sh   # requires Docker
cd devops/D4-kubernetes && ./scripts/validate-manifests.sh
cd devops/D6-observability && ./scripts/start-stack.sh
eval "$(bash scripts/docker-setup.sh --print-env)"      # Colima Docker if needed
```

### Report-only tasks (I1–I3, A1–A2, A4–A6, etc.)

- Confirm required markdown/diagram/CSV files exist.
- Peer or agent review for completeness and accuracy.

## Agent guardrails

When prompting agents on this repo:

- **Do not** change API contracts, DTOs, DB schema, or business logic unless the task explicitly requires it.
- **Do not** rename existing packages or move working code without a structure task.
- **Prefer** `make test` over ad-hoc checks.
- **Commit** per task with clear messages (e.g. `B4: add FastAPI service`).

## Future evidence collection (planned)

For formal evaluation submissions, capture:

| Evidence            | Description                                      |
| ------------------- | ------------------------------------------------ |
| Prompt log          | Task ID, agent, date, full prompt                |
| Diff summary        | Files changed, lines added/removed               |
| Test output         | `make test` or task-specific script exit code    |
| Deliverable paths   | Links to REPORT.md, CSV, code folders            |
| Cross-task check    | Agent comparison output (optional)               |
| Manual notes        | Docker issues, port conflicts, environment quirks |

Store evidence outside git or in a future `docs/evidence/` convention — not required today.

## Comparing agent outputs

Useful prompts for a second agent:

- “Compare `beginner/B1-repo-artifact-inventory/inventory.csv` to a fresh repo scan.”
- “Do B4 and B5 expose the same transaction endpoints?”
- “Does `TEST_REPORT.md` match `make test` results?”

## Related documents

- [`TASK_REGISTRY.md`](TASK_REGISTRY.md) — status of all 24 tasks
- [`TASK_MAPPING.md`](TASK_MAPPING.md) — task descriptions
- [`DASHBOARD_VISION.md`](DASHBOARD_VISION.md) — future unified dashboard
- [`ORCHESTRATOR_DESIGN.md`](ORCHESTRATOR_DESIGN.md) — future automation architecture
- Root [`README.md`](../README.md) — clone and `make bootstrap`
