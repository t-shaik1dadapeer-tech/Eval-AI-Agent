# Evil-Ai — Setup (24-task pipeline)

Aligned with [Repo-Analyser](https://github.com/harshitverma69/Repo-Analyser) PML/OCL eval: **24 agents**, **blueprints**, **pipeline UI**, **Cursor skills**.

## Quick start

```bash
git clone <repo-url> Evil-Ai
cd Evil-Ai
make setup
make eval-api    # http://127.0.0.1:8788
```

**Restart Cursor** after setup. Type `/` and search `evil-ai` for slash commands.

## What you get

| Path | Purpose |
|------|---------|
| `docs/task-registry.json` | 24 tasks + `depends_on` + required files |
| `eval_blueprints/` | One blueprint `.md` per task (what to deliver) |
| `skills/` | Cursor skill specs (built from registry) |
| `docs/AGENT_PROMPTS.md` | Full copy-paste prompts per task |
| `frontend/` | Pipeline wizard UI (no score dashboard) |
| `beginner/` … `devops/` | Completed task folders (reference) |

## Daily workflow

1. **Portfolio dashboard** — `make eval-api` then open http://127.0.0.1:8788 → 24-task grid with scores.
2. **Cursor** — run `/evil-ai-repo-inventory` (or prompt from `AGENT_PROMPTS.md`) on your target repo.
3. **Verify** — `make run-all` or `make eval` checks all required files and writes `docs/eval-status.json`.

## Commands

```bash
make setup              # build skills + blueprints + validate DAG
make build-skills       # regenerate skills/ from registry
make install-cursor-skills
make validate-dag       # check depends_on graph
make eval-api           # Evil-Ai portfolio dashboard :8788
make run-all            # verify all 24 pipeline tasks
make eval               # verify 24 deliverables → eval-status.json
make eval-full          # + run tests (Docker for some tasks)
make run-pipeline       # print pipeline JSON
```

## Pipeline order (24)

B1 → B2 → B3 → B4 → B5 → B6 → I1 → I2 → I3 → I4 → I5 → I6 → A1 → A2 → A3 → A4 → A5 → A6 → D1 → D2 → D3 → D4 → D5 → D6

Dependencies (examples): B2 needs B1, I2 needs B2, D2 needs I5. See `eval_blueprints/*_blueprint.md`.

## Target repo

The pipeline UI asks for a **target path** (e.g. your UserManagement project). In Cursor, attach it with `@/path/to/repo` when running a skill.

Evil-Ai itself is both the **eval framework** and the **golden reference** (all 24 folders filled in).

## Troubleshooting

| Problem | Fix |
|---------|-----|
| UI not loading | `make eval-api` |
| Slash commands missing | `make install-cursor-skills` + restart Cursor |
| Files missing on eval | Open blueprint for that task; create listed `.md` files |
| DAG error | `make validate-dag` |

See also: `docs/PML_VERIFICATION.md`, `docs/TASK_REGISTRY.md`.
