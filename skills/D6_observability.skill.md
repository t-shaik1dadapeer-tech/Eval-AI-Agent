---
name: eval-ai-observability
description: Eval-Ai PML task D6 — Observability
---

# D6 — Observability

You are running Eval-Ai eval task **D6** on the target repository.

## Objective

pytest for service; full stack via start-stack.sh + verify_metrics.sh (Docker).

## Prerequisites

Complete first: I5

## Read first

- `eval_blueprints/D6_blueprint.md`
- `docs/AGENT_PROMPTS.md` (section `D6`)

## Deliverables (must exist when done)

`devops/D6-observability/docker-compose.yml`, `devops/D6-observability/service/app/main.py`, `devops/D6-observability/service/tests/test_metrics.py`

## Primary output

`devops/D6-observability/docker-compose.yml`

## Work in folder

`devops/D6-observability/`

After finishing, run `make eval` to verify files exist.
