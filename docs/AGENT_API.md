# Agent Eval API

Use this after cloning the repo so any AI agent can discover tasks, get reference docs, submit output, and see results on the **live dashboard**.

## Quick start (any clone)

```bash
git clone <repo-url> Evil-Ai
cd Evil-Ai
make bootstrap          # optional: install + run tests
make eval-api           # starts http://127.0.0.1:8788
```

Open **http://127.0.0.1:8788** — live dashboard (all 24 tasks).

---

## Workflow for an AI agent

### 1. Get task instructions + reference files

```bash
curl http://127.0.0.1:8788/api/agent/guide/B4
curl http://127.0.0.1:8788/api/agent/guide/I2
curl http://127.0.0.1:8788/api/agent/guide/A1
```

Response includes:

- `objective` — what the task is for
- `reference_files` — ground-truth `.md` / `.csv` to read in the repo
- `required_files` — what must exist when done
- `compare_hint` — how eval compares your work
- `verify_command` — optional command to prove it works

### 2. Do the work in the task folder

Example: implement or write report under `beginner/B4-fastapi-service/`.

## External APIs (register when your services are ready)

No default API is stored. Register one or more — see [`EXTERNAL_EVAL.md`](EXTERNAL_EVAL.md).

```bash
curl -X POST http://127.0.0.1:8788/api/external/register \
  -H 'Content-Type: application/json' \
  -d '{"id":"my-dev-api","name":"My Dev API","api_base_url":"http://127.0.0.1:9000","default":true}'

curl http://127.0.0.1:8788/api/external/apis

curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"B3","output_path":"beginner/B3-test-discovery/TEST_REPORT.md"}'
```

Submit compares agent output to repo references only. For live API vs `.md`, use **POST /api/external/analyze** (see [`EXTERNAL_EVAL.md`](EXTERNAL_EVAL.md)).

---

**By file path** (agent saved a report in the repo):

```bash
curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id": "I2",
    "agent_name": "cursor",
    "output_path": "intermediate/I2-end-to-end-trace/FLOW_TRACE.md"
  }'
```

**By inline content** (agent pasted markdown):

```bash
curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id": "B2",
    "agent_name": "claude",
    "content": "# API Map\n..."
  }'
```

Response:

```json
{
  "task": "I2",
  "verdict": "ok|partial|mismatch",
  "match_score": 0.82,
  "reference_files": ["intermediate/I2-end-to-end-trace/FLOW_TRACE.md", "..."],
  "suggestion": "For exact output read FLOW_TRACE.md ..."
}
```

### 4. View portfolio on dashboard

- **http://127.0.0.1:8788/** — live UI (auto-refresh)
- **http://127.0.0.1:8788/api/portfolio** — JSON for all 24 tasks + agent results

---

## API reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Live dashboard (HTML) |
| GET | `/api/health` | Health check |
| GET | `/api/docs` | Agent workflow + endpoint list |
| GET | `/api/portfolio` | Scan repo + agent history (`?run_tests=1` optional) |
| GET | `/api/tasks` | Raw task registry (24 tasks) |
| GET | `/api/tasks/{id}` | One task status |
| GET | `/api/agent/guide/{id}` | **Agent:** read this before working on task |
| POST | `/api/agent/submit` | **Agent:** submit output for compare |
| POST | `/api/agent/compare/{id}` | Compare (query `?agent_output=` or JSON body) |
| POST | `/api/portfolio/refresh` | Re-scan deliverables |
| GET | `/api/metrics` | Prometheus text metrics |

### POST `/api/agent/submit` body

| Field | Required | Description |
|-------|----------|-------------|
| `task_id` | yes | e.g. `B4`, `I2`, `D6` |
| `agent_name` | no | e.g. `cursor`, `claude`, `chatgpt` |
| `output_path` | one of | Path to file (relative to repo root) |
| `content` | one of | Inline text (saved under `.eval/submissions/`) |

---

## CLI equivalents

```bash
make eval-compare TASK=I2
make eval-compare TASK=I2 AGENT_OUTPUT=./my-file.md
make eval
```

---

## Grafana (service metrics, separate)

D6 observability stack monitors **HTTP API metrics**, not agent eval:

```bash
cd devops/D6-observability && ./scripts/start-stack.sh
```

Optional: scrape `http://127.0.0.1:8787/api/metrics` for portfolio gauges.

---

## Related

- [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) — copy-paste prompt per task (B1–D6)
- [`task-registry.json`](task-registry.json) — machine-readable 24-task config
- [`AGENT_USAGE.md`](AGENT_USAGE.md) — human + agent process
- [`TASK_REGISTRY.md`](TASK_REGISTRY.md) — task status table
