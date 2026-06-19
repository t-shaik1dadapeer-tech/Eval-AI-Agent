# Orchestrator — 24 Live Bots

Run **one task bot** or **all 24 bots** automatically: guide → submit `.md` → optional external API compare → dashboard update.

**No default external API** is stored in the repo. Register your dev APIs when they are ready.

## Quick start

```bash
make eval-api    # http://127.0.0.1:8788
```

Dashboard: register APIs, then **Run all 24 bots** or per-row **run bot**.

---

## 1. Register one or more external APIs

When your service is running (e.g. home API at `:9000`, billing at `:9001`):

```bash
curl -X POST http://127.0.0.1:8788/api/external/register \
  -H 'Content-Type: application/json' \
  -d '{"id":"home-api","name":"Home API","api_base_url":"http://127.0.0.1:9000","default":true}'

curl -X POST http://127.0.0.1:8788/api/external/register \
  -H 'Content-Type: application/json' \
  -d '{"id":"billing-api","name":"Billing API","api_base_url":"http://127.0.0.1:9001"}'
```

List registered APIs:

```bash
curl http://127.0.0.1:8788/api/external/apis
```

Stored in `.eval/external-apis.json` (gitignored).

---

## 2. Map tasks to APIs (optional)

Different tasks can use different APIs:

```bash
curl -X POST http://127.0.0.1:8788/api/orchestrator/config \
  -H 'Content-Type: application/json' \
  -d '{
    "default_api_id": "home-api",
    "task_api_map": {
      "B2": "home-api",
      "B3": "billing-api"
    },
    "use_api_for_all_tasks": false
  }'
```

Or copy [`orchestrator-config.example.json`](orchestrator-config.example.json) to `.eval/orchestrator-config.json` and edit.

Per-task submit file override (only if you use a non-standard path):

```json
"output_map": {
  "B3": "beginner/B3-test-discovery/MY_CUSTOM_REPORT.md"
}
```

---

## 3. Single bot (one task)

**HTTP:**

```bash
curl -X POST http://127.0.0.1:8788/api/orchestrator/run \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"B3","api_id":"billing-api"}'
```

**CLI:**

```bash
make eval-bot TASK=B3 API_ID=billing-api
# or one-off URL (not saved):
make eval-bot TASK=B3 API_BASE_URL=http://127.0.0.1:9001
```

Resolution order for API URL: run `api_id` → `task_api_map[task]` → `default_api_id` → none (repo-only eval).

---

## 4. All 24 bots

**HTTP:**

```bash
curl -X POST http://127.0.0.1:8788/api/orchestrator/run \
  -H 'Content-Type: application/json' \
  -d '{"mode":"all"}'
```

Uses `task_api_map` per task; tasks without a mapping skip API probe unless `use_api_for_all_tasks` is true.

**CLI:**

```bash
make eval-bots-all API_ID=home-api
```

Runs B1→B6, I1→I6, A1→A6, D1→D6 in order.

---

## 5. Check status

```bash
curl http://127.0.0.1:8788/api/orchestrator/status
```

Dashboard shows **Bot** column per task (`running` / `done` / `skipped` / `failed`).

---

## What each bot does

1. Load task from `docs/task-registry.json`
2. Pick submit file (required `.md`/`.csv`, or `output_map` override)
3. `POST` equivalent of `/api/agent/submit` with resolved `api_id` / URL
4. Optional: run `verify_command` if `run_tests: true`
5. Save result to `.eval/orchestrator-state.json`

Bots **verify and compare** existing deliverables — they do not invoke a full LLM agent to write new code.

---

## Config fields

| Field | Description |
|-------|-------------|
| `default_api_id` | Fallback registered API id |
| `task_api_map` | Per-task API id, e.g. `{"B2":"home-api"}` |
| `use_api_for_all_tasks` | If true, use `default_api_id` for every task |
| `output_map` | Per-task submit path overrides |
| `run_tests` | Run registry `verify_command` after submit |

Registered APIs live in `.eval/external-apis.json`, not in orchestrator config.

---

## Clear all APIs

```bash
curl -X POST http://127.0.0.1:8788/api/external/clear
```

---

## Makefile

| Target | Action |
|--------|--------|
| `make eval-api` | Start dashboard + API |
| `make eval-stop` | Stop port 8788 |
| `make eval-bot TASK=B3 API_ID=home-api` | Single bot |
| `make eval-bots-all` | All 24 bots |
| `make eval-orch-config API_ID=home-api API_BASE_URL=http://127.0.0.1:9000` | Register + show config |

---

## Related

- [`EXTERNAL_EVAL.md`](EXTERNAL_EVAL.md) — external API + `.md` compare
- [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) — human/LLM prompts per task
- [`ORCHESTRATOR_DESIGN.md`](ORCHESTRATOR_DESIGN.md) — architecture notes
