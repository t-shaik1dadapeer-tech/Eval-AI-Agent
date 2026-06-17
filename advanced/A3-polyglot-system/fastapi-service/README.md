# A3 FastAPI Ingestion Service

Transaction ingestion API for the polyglot fraud scoring system.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/transactions` | Validate and enqueue a transaction |
| `GET` | `/health` | Health check |

## Setup

```bash
cd advanced/A3-polyglot-system/fastapi-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
export FRAUD_SYSTEM_ROOT=/path/to/advanced/A3-polyglot-system
uvicorn app.main:app --reload --port 8100
```

## Test

```bash
pytest -v
```

## Example

```bash
curl -X POST http://localhost:8100/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn-001",
    "user_id": "user-123",
    "amount": 15000,
    "merchant": "electronics",
    "country": "IN"
  }'
```

Response:

```json
{"status": "accepted", "transaction_id": "txn-001"}
```

Transactions are appended to `shared/data/transactions.json`.
