# A3 — Polyglot System

## What to do

Run integration-test.sh; FastAPI 202 → queue → worker → Rust score.

## Depends on

B4, B5, B6, I4

## Required deliverables

- `advanced/A3-polyglot-system/fastapi-service/app/main.py`
- `advanced/A3-polyglot-system/node-worker/src/worker.js`
- `advanced/A3-polyglot-system/rust-engine/src/lib.rs`

## Reference files (golden examples in this repo)

- `advanced/A3-polyglot-system/README.md`
- `advanced/A3-polyglot-system/docs/ARCHITECTURE.md`
- `advanced/A3-polyglot-system/docs/REPORT.md`
- `advanced/A3-polyglot-system/scripts/integration-test.sh`

## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## A3 —**

Or run slash command: `/evil-ai-polyglot-system`

## Verify (optional)

```bash
bash advanced/A3-polyglot-system/scripts/integration-test.sh
```
