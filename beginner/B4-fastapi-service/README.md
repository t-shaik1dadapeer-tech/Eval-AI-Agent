# B4 — FastAPI Transaction Service

Production-quality in-memory transaction API built with FastAPI. Create credit/debit transactions, list them, and compute the running balance.

## Project overview

| Component | Description |
|-----------|-------------|
| Framework | FastAPI |
| Validation | Pydantic v2 |
| Storage | In-memory (singleton service) |
| Tests | pytest + FastAPI `TestClient` |

## Folder structure

```
B4-fastapi-service/
├── app/
│   ├── main.py              # FastAPI app, validation error handler
│   ├── routes/
│   │   └── transactions.py  # HTTP endpoints
│   ├── models/
│   │   └── transaction.py   # Domain model + TransactionType enum
│   ├── services/
│   │   └── transaction_service.py  # Business logic + in-memory store
│   └── schemas/
│       └── transaction.py   # Request/response Pydantic models
├── tests/
│   ├── conftest.py
│   └── test_transactions.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

```bash
cd beginner/B4-fastapi-service
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the service

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`.

Interactive docs: `http://127.0.0.1:8000/docs`

## Run tests

```bash
source .venv/bin/activate
pytest -v
```

Expected: **8 passed** (5 original + 3 lookup tests).

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/transactions` | Create a transaction |
| `GET` | `/transactions` | List all transactions |
| `GET` | `/transactions/{id}` | Get a single transaction by UUID |
| `GET` | `/balance` | Current balance + transaction count |
| `GET` | `/health` | Health check |

### Transaction model

| Field | Type | Rules |
|-------|------|-------|
| `id` | UUID | Auto-generated |
| `type` | string | `credit` or `debit` |
| `amount` | number | Must be > 0 |
| `description` | string | Optional, max 500 chars |
| `created_at` | datetime | Auto-generated (UTC) |

### Balance calculation

- `credit` adds to balance
- `debit` subtracts from balance

## API examples

### Create a credit transaction

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"credit","amount":150.0,"description":"Initial deposit"}'
```

**Expected response (201):**

```json
{
  "id": "e0e53338-8cc3-4dbb-8ef8-66a6428a71eb",
  "type": "credit",
  "amount": 150.0,
  "description": "Initial deposit",
  "created_at": "2026-06-17T09:22:09.054827Z"
}
```

### Create a debit transaction

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"debit","amount":50.0,"description":"Purchase"}'
```

### List all transactions

```bash
curl http://localhost:8000/transactions
```

### Get transaction by ID

```bash
curl http://localhost:8000/transactions/{transaction_id}
```

**Expected response (200):** single transaction object (same shape as create response).

**Expected response (404):** `{"detail": "Transaction not found"}` when the ID does not exist.

**Expected response (200):**

```json
[
  {
    "id": "e0e53338-8cc3-4dbb-8ef8-66a6428a71eb",
    "type": "credit",
    "amount": 150.0,
    "description": "Initial deposit",
    "created_at": "2026-06-17T09:22:09.054827Z"
  },
  {
    "id": "7ddb9063-8a31-497d-9576-f21d25fea4d3",
    "type": "debit",
    "amount": 50.0,
    "description": "Purchase",
    "created_at": "2026-06-17T09:22:09.070294Z"
  }
]
```

### Get balance

```bash
curl http://localhost:8000/balance
```

**Expected response (200):**

```json
{
  "balance": 100.0,
  "transaction_count": 2
}
```

### Invalid payload (validation error)

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"credit","amount":-5}'
```

**Expected response (422):**

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "amount"],
      "msg": "Input should be greater than 0",
      "input": -5,
      "ctx": {"gt": 0.0}
    }
  ]
}
```
