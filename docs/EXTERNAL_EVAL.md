# External API Eval — Any Project + .md Prompts

Use the Evil-Ai eval server to compare **your running API** (UserManagement, Library API, or any service) against **`.md` prompt files** — and see results on the **live dashboard**.

Evil-Ai stays the **eval host**; your API is the **target under test**.

---

## Quick start

**Terminal 1 — eval dashboard (Evil-Ai)**

```bash
cd /path/to/Evil-Ai
python3 scripts/eval/portfolio.py serve --port 8788
```

Open **http://127.0.0.1:8788/**

**Terminal 2 — your API (any project)**

```bash
cd /path/to/UserManagement   # or any project
# start your API — note the URL, e.g. http://127.0.0.1:3000
```

---

## Step 1 — Register your API URL

```bash
curl -X POST http://127.0.0.1:8788/api/external/target \
  -H 'Content-Type: application/json' \
  -d '{
    "api_base_url": "http://127.0.0.1:3000",
    "project_name": "UserManagement"
  }'
```

Dashboard header shows your API URL after this.

---

## Step 2 — Analyze any .md file vs your API

```bash
curl -X POST http://127.0.0.1:8788/api/external/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "md_path": "docs/AGENT_PROMPTS.md",
    "api_base_url": "http://127.0.0.1:3000",
    "task_id": "B3"
  }'
```

The eval server:

1. Reads the `.md` file
2. Finds endpoints (`GET /users`, `curl http://...`, paths in backticks)
3. Calls your live API
4. Returns **api_match** verdict + **related_md** if mismatch

---

## Step 3 — Submit agent work (.md output + API check)

Paste a prompt from [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) in Cursor, then submit:

```bash
curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id": "B3",
    "agent_name": "cursor",
    "output_path": "beginner/B3-test-discovery/TEST_REPORT.md",
    "api_base_url": "http://127.0.0.1:3000"
  }'
```

Response includes:

| Field | Meaning |
|-------|---------|
| `md_verdict` | Agent `.md` vs repo reference files |
| `api_match` | Live API vs endpoints found in `.md` |
| `verdict` | Combined score |
| `related_md` | Other task `.md` files to read if mismatch |

---

## Step 4 — Dashboard

**http://127.0.0.1:8788/**

| Column | Meaning |
|--------|---------|
| **Agent** | `.md` / deliverable compare |
| **API match** | Your running API vs `.md` expectations |
| **Related .md** | Suggested files from other tasks when fail |

Summary cards: **API checked / API OK** out of 24.

---

## Universal Cursor prompt (any external API)

Copy into a new chat (change ports and task):

```
You are evaluating task B3 using Evil-Ai eval + my external API.

1. Eval API: http://127.0.0.1:8788 (already running)
2. My API: http://127.0.0.1:3000 (UserManagement — start if needed)
3. POST http://127.0.0.1:8788/api/external/target with my API URL
4. GET http://127.0.0.1:8788/api/agent/guide/B3
5. Read reference .md files from the guide response
6. Compare my API responses with what the .md expects (curl my endpoints)
7. POST http://127.0.0.1:8788/api/agent/submit with task_id, output_path, api_base_url
8. If verdict is partial/mismatch, open related_md from the response
9. Show me dashboard summary from GET /api/portfolio
```

---

## How .md → API matching works

From markdown text the eval server extracts:

- `GET /api/users`, `POST /convert`
- `` `/health` `` paths in backticks
- `curl http://127.0.0.1:3000/...` lines

If none found, it probes defaults: `/health`, `/api/health`, `/`, `/docs`.

Each path is called on **your** `api_base_url`. Score = endpoints returning 2xx / total tested.

---

## CLI

```bash
make eval-compare TASK=B3 AGENT_OUTPUT=./out.md API_BASE_URL=http://127.0.0.1:3000
```

---

## Related

- [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) — copy-paste prompts for all 24 tasks
- [`AGENT_API.md`](AGENT_API.md) — full HTTP API reference
