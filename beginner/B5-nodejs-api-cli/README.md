# B5 — Node.js Transaction API

Express-based REST API for in-memory transaction management and balance calculation. Mirrors the B4 FastAPI service using Node.js.

## Overview

| Component | Technology |
|-----------|------------|
| Runtime | Node.js |
| Framework | Express.js |
| Storage | In-memory (singleton service) |
| Tests | Jest + Supertest |

## Folder structure

```
B5-nodejs-api-cli/
├── src/
│   ├── app.js
│   ├── server.js
│   ├── routes/
│   │   └── transactionRoutes.js
│   ├── controllers/
│   │   └── transactionController.js
│   ├── services/
│   │   └── transactionService.js
│   ├── models/
│   │   └── transactionTypes.js
│   └── middleware/
│       ├── validateTransaction.js
│       └── errorHandler.js
├── tests/
│   └── transactions.test.js
├── package.json
├── README.md
└── .gitignore
```

## Installation

```bash
cd beginner/B5-nodejs-api-cli
npm install
```

## Run the service

```bash
npm start
```

Server starts at `http://127.0.0.1:3000`.

## Run tests

```bash
npm test
```

Expected: **5 passed**.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/transactions` | Create a transaction |
| `GET` | `/transactions` | List all transactions |
| `GET` | `/balance` | Current balance + count |
| `GET` | `/health` | Health check |

### Transaction schema

| Field | Type | Rules |
|-------|------|-------|
| `id` | string (UUID) | Auto-generated |
| `type` | string | `credit` or `debit` |
| `amount` | number | Must be > 0 |
| `description` | string | Optional |
| `createdAt` | string (ISO-8601) | Auto-generated |

## API examples

### Create a credit transaction

```bash
curl -X POST http://localhost:3000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"credit","amount":150.0,"description":"Initial deposit"}'
```

**Sample response (201):**

```json
{
  "id": "4575fe35-1315-4ffb-8726-017d53c502e2",
  "type": "credit",
  "amount": 150,
  "description": "Initial deposit",
  "createdAt": "2026-06-17T09:27:42.163Z"
}
```

### Create a debit transaction

```bash
curl -X POST http://localhost:3000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"debit","amount":50.0,"description":"Purchase"}'
```

### List transactions

```bash
curl http://localhost:3000/transactions
```

**Sample response (200):**

```json
[
  {
    "id": "4575fe35-1315-4ffb-8726-017d53c502e2",
    "type": "credit",
    "amount": 150,
    "description": "Initial deposit",
    "createdAt": "2026-06-17T09:27:42.163Z"
  },
  {
    "id": "e43496ab-7c62-470b-a562-2ab6b8b2c2e4",
    "type": "debit",
    "amount": 50,
    "description": "Purchase",
    "createdAt": "2026-06-17T09:27:42.179Z"
  }
]
```

### Get balance

```bash
curl http://localhost:3000/balance
```

**Sample response (200):**

```json
{
  "balance": 100,
  "transactionCount": 2
}
```

### Invalid payload

```bash
curl -X POST http://localhost:3000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"credit","amount":-5}'
```

**Sample response (400):**

```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "amount",
      "message": "amount must be greater than 0"
    }
  ]
}
```
