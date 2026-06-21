# External API Eval — Any Project + .md Prompts

Use the Eval-Ai eval server to compare **your running APIs** against **`.md` prompt files** — and see results on the **live dashboard**.

Eval-Ai stays the **eval host**; your APIs are **targets under test**. There is **no built-in default API** — register each service when it is ready.

---

## Quick start

**Terminal 1 — eval dashboard (Eval-Ai)**

```bash
cd /path/to/Eval-Ai
python3 scripts/eval/portfolio.py serve --port 8788
```

Open **http://127.0.0.1:8788/**

**Terminal 2 — your API(s) (any project)**

```bash
cd /path/to/your-project
# start your API — note the URL, e.g. http://127.0.0.1:9000
```

---

## Step 1 — Register your API(s)

Register one or more APIs (dashboard or curl):

```bash
curl -X POST http://127.0.0.1:8788/api/external/register \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "my-dev-api",
    "name": "My Dev API",
    "api_base_url": "http://127.0.0.1:9000",
    "default": true
  }'
```

List / remove:

```bash
curl http://127.0.0.1:8788/api/external/apis
curl -X DELETE http://127.0.0.1:8788/api/external/apis/my-dev-api
curl -X POST http://127.0.0.1:8788/api/external/clear
```

Legacy single-target endpoint still works (`POST /api/external/target`) — it registers into the multi-API store.

---

## Step 2 — Map tasks to APIs (optional)

When you have multiple services:

```bash
curl -X POST http://127.0.0.1:8788/api/orchestrator/config \
  -H 'Content-Type: application/json' \
  -d '{
    "task_api_map": {"B2": "home-api", "B3": "billing-api"},
    "default_api_id": "home-api"
  }'
```

---

## Step 3 — Analyze any .md file vs an API

```bash
curl -X POST http://127.0.0.1:8788/api/external/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "md_path": "beginner/B2-api-endpoint-map/API_MAP.md",
    "api_id": "my-dev-api",
    "task_id": "B2"
  }'
```

The eval server:

1. Reads the `.md` file
2. Finds endpoints (`GET /users`, `curl http://...`, paths in backticks)
3. Calls your live API
4. Returns **api_match** verdict + **related_md** if mismatch

---

## Step 4 — Submit agent work (.md output)

Paste a prompt from [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) in Cursor, then submit:

```bash
curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id": "B3",
    "agent_name": "cursor",
    "output_path": "beginner/B3-test-discovery/TEST_REPORT.md"
  }'
```

Submit scores **agent `.md` vs repo reference files only**. Optional `api_id` / `api_base_url` on submit are ignored for scoring (stored for display if provided).

Response includes:

| Field | Meaning |
|-------|---------|
| `md_verdict` | Agent `.md` vs repo reference files |
| `verdict` | Same as `md_verdict` (no API blend on submit) |
| `api_match` | Always `skipped` on submit — use `/api/external/analyze` for live API check |
| `related_md` | Other task `.md` files to read if mismatch |

---

## Step 5 — Dashboard

**http://127.0.0.1:8788/**

| Column | Meaning |
|--------|---------|
| **Repo** | Required deliverable files present |
| **Agent work** | Latest agent submit verdict (`ok` / `partial` / …) |
| **Remote API** | Optional registered URL (display only) |
| **Score** | **0% until checked** — updates after submit or `/api/external/analyze` (with `task_id`) |

Use **POST /api/external/analyze** with `task_id` to score your live API vs a `.md` file.

---

## Universal Cursor prompt (any external API)

Copy into a new chat (change ids, ports, and task):

```
You are evaluating task B3 using Eval-Ai eval + my external API.

1. Eval API: http://127.0.0.1:8788 (already running)
2. My API: http://127.0.0.1:9000 — register when running:
   POST /api/external/register {"id":"my-dev-api","name":"My Dev API","api_base_url":"http://127.0.0.1:9000","default":true}
3. GET http://127.0.0.1:8788/api/agent/guide/B3
4. Read reference .md files from the guide response
5. Compare my API responses with what the .md expects (curl my endpoints)
6. POST http://127.0.0.1:8788/api/agent/submit with task_id, output_path, api_id
7. If verdict is partial/mismatch, open related_md from the response
8. Show me dashboard summary from GET /api/portfolio
```

---

## How .md → API matching works

From markdown text the eval server extracts:

- `GET /api/users`, `POST /convert`
- `` `/health` `` paths in backticks
- `curl http://127.0.0.1:9000/...` lines

If none found, it probes defaults: `/health`, `/api/health`, `/`, `/docs`.

Each path is called on **your** resolved API URL. Score = endpoints returning 2xx / total tested.

---

## CLI

```bash
make eval-compare TASK=B3 AGENT_OUTPUT=./out.md API_BASE_URL=http://127.0.0.1:9000
make eval-orch-config API_ID=my-dev-api API_BASE_URL=http://127.0.0.1:9000
```

---

## Related

- [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) — copy-paste prompts for all 24 tasks
- [`AGENT_API.md`](AGENT_API.md) — full HTTP API reference
- [`ORCHESTRATOR.md`](ORCHESTRATOR.md) — per-task API config
