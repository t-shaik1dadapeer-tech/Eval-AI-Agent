# I4 — Polyglot Service Pair

FastAPI currency conversion service + Node.js CLI client.

## Architecture

```
┌─────────────┐     POST /convert      ┌──────────────────┐
│  Node CLI   │ ─────────────────────► │  FastAPI Service │
│  (axios)    │ ◄───────────────────── │  (hardcoded rates)│
└─────────────┘     JSON response      └──────────────────┘
```

## Folder structure

```
I4-polyglot-service-pair/
├── fastapi-service/     # Currency conversion API
├── node-client/         # CLI HTTP client
├── docs/REPORT.md       # Verification report
└── README.md
```

## Quick start

### Terminal 1 — FastAPI service

```bash
cd fastapi-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Node.js CLI

```bash
cd node-client
npm install
node src/cli.js 100 USD INR
```

Expected output:

```
Converting 100 USD -> INR
Converted Amount: 8300
```

## Supported conversions

| From | To | Rate |
|------|-----|------|
| USD | INR | 83 |
| INR | USD | 0.012 |
| USD | EUR | 0.92 |
| EUR | USD | 1.08 |

Currencies: `USD`, `INR`, `EUR`. Other pairs return HTTP 400.

## Testing

```bash
# FastAPI
cd fastapi-service && source .venv/bin/activate && pytest -v

# Node client
cd node-client && npm test
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONVERTER_API_URL` | `http://127.0.0.1:8000` | FastAPI base URL for CLI |

See component READMEs for details.
