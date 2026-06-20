# Eval config — per-task API mapping

Optional config for linking **your external APIs** to tasks (Remote API column on dashboard).

---

## Quick start

```bash
make eval-api    # http://127.0.0.1:8788
```

---

## Agent workflow (primary)

```bash
curl http://127.0.0.1:8788/api/agent/guide/B1
# Copy prompt from docs/AGENT_PROMPTS.md → do work in Cursor → submit:

curl -X POST http://127.0.0.1:8788/api/agent/submit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"B1","agent_name":"cursor","output_path":"beginner/B1-repo-artifact-inventory/REPORT.md"}'
```

---

## Register external API (optional)

```bash
curl -X POST http://127.0.0.1:8788/api/external/register \
  -H 'Content-Type: application/json' \
  -d '{"id":"user-api","name":"UserManagement","api_base_url":"http://127.0.0.1:8090","default":true}'
```

Per-task mapping:

```bash
curl -X POST http://127.0.0.1:8788/api/orchestrator/config \
  -H 'Content-Type: application/json' \
  -d '{"task_api_map":{"B2":"user-api","B4":"user-api"}}'
```

Or CLI:

```bash
make eval-orch-config API_ID=user-api API_BASE_URL=http://127.0.0.1:8090
```

---

## Makefile

| Command | Purpose |
|---------|---------|
| `make eval-api` | Dashboard + API server |
| `make eval` | Check all 24 deliverables |
| `make eval-compare TASK=B1 AGENT_OUTPUT=...` | Score agent output |
| `make eval-orch-config` | Register API + show config |
| `make eval-reset-config` | Reset `.eval/eval-config.json` |

---

## Related

- [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) — prompts for all 24 tasks
- [`AGENT_API.md`](AGENT_API.md) — API reference
- [`AGENT_USAGE.md`](AGENT_USAGE.md) — workflow guide
