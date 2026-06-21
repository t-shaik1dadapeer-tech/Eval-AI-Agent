# D6 — Observability

## What to do

pytest for service; full stack via start-stack.sh + verify_metrics.sh (Docker).

## Depends on

I5

## Required deliverables

- `devops/D6-observability/docker-compose.yml`
- `devops/D6-observability/service/app/main.py`
- `devops/D6-observability/service/tests/test_metrics.py`

## Reference files (golden examples in this repo)

- `devops/D6-observability/README.md`
- `devops/D6-observability/docs/OBSERVABILITY_REPORT.md`
- `devops/D6-observability/docs/METRICS_REPORT.md`
- `devops/D6-observability/docs/DASHBOARD_PANEL.json`
- `devops/D6-observability/scripts/start-stack.sh`

## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## D6 —**

Or run slash command: `/eval-ai-observability`

## Verify (optional)

```bash
cd devops/D6-observability/service && mise exec -- pytest -q
```
