---
name: evil-ai-polyglot-system
description: Evil-Ai PML task A3 — Polyglot System
---

# A3 — Polyglot System

You are running Evil-Ai eval task **A3** on the target repository.

## Objective

Run integration-test.sh; FastAPI 202 → queue → worker → Rust score.

## Prerequisites

Complete first: B4, B5, B6, I4

## Read first

- `eval_blueprints/A3_blueprint.md`
- `docs/AGENT_PROMPTS.md` (section `A3`)

## Deliverables (must exist when done)

`advanced/A3-polyglot-system/fastapi-service/app/main.py`, `advanced/A3-polyglot-system/node-worker/src/worker.js`, `advanced/A3-polyglot-system/rust-engine/src/lib.rs`

## Primary output

`advanced/A3-polyglot-system/fastapi-service/app/main.py`

## Work in folder

`advanced/A3-polyglot-system/`

After finishing, run `make eval` to verify files exist.
