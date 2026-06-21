# I4 — FastAPI + Node Pair

## What to do

POST /convert on FastAPI; Node client tests in node-client/tests/.

## Depends on

B4, B5

## Required deliverables

- `intermediate/I4-fastapi-node-pair/fastapi-service/app/main.py`
- `intermediate/I4-fastapi-node-pair/node-client/src/cli.js`

## Reference files (golden examples in this repo)

- `intermediate/I4-fastapi-node-pair/README.md`
- `intermediate/I4-fastapi-node-pair/docs/REPORT.md`
- `intermediate/I4-fastapi-node-pair/fastapi-service/README.md`
- `intermediate/I4-fastapi-node-pair/node-client/README.md`

## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## I4 —**

Or run slash command: `/eval-ai-fastapi-node-pair`

## Verify (optional)

```bash
cd intermediate/I4-fastapi-node-pair/fastapi-service && mise exec -- pytest -q && cd ../node-client && mise exec -- npm test
```
