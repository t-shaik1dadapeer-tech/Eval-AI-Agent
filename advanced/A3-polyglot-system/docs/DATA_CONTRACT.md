# A3 Data Contract

## Overview

All three components communicate through **JSON files** and a **Rust CLI JSON protocol**. Schemas are documented in `shared/` and enforced at runtime by FastAPI (Pydantic) and Node (manual validation).

---

## Transaction ingestion (`transaction-schema.json`)

### Request — `POST /transactions`

```json
{
  "transaction_id": "txn-001",
  "user_id": "user-123",
  "amount": 15000,
  "merchant": "electronics",
  "country": "IN"
}
```

### Required fields

| Field | Type | Rules |
|-------|------|-------|
| `transaction_id` | string | Non-empty |
| `user_id` | string | Non-empty |
| `amount` | number | Must be > 0 |
| `merchant` | string | Non-empty |
| `country` | string | ISO 3166-1 alpha-2 (2 chars) |

### API response — `202 Accepted`

```json
{
  "status": "accepted",
  "transaction_id": "txn-001"
}
```

### Queue record (written by FastAPI)

Same fields plus `status: "pending"`:

```json
{
  "transaction_id": "txn-001",
  "user_id": "user-123",
  "amount": 15000,
  "merchant": "electronics",
  "country": "IN",
  "status": "pending"
}
```

### Validation errors — `422 Unprocessable Entity`

FastAPI returns standard Pydantic `detail` array for invalid payloads (e.g. negative amount).

---

## Fraud score output (`score-schema.json`)

### Rust CLI input (subset of transaction)

```json
{
  "amount": 15000,
  "merchant": "electronics",
  "country": "IN"
}
```

### Rust CLI output

```json
{
  "risk_score": 82,
  "risk_level": "HIGH"
}
```

| Field | Type | Values |
|-------|------|--------|
| `risk_score` | integer | ≥ 0 |
| `risk_level` | string | `LOW`, `MEDIUM`, `HIGH` |

### Scoring rules

| Condition | Points |
|-----------|--------|
| `amount > 10000` | +50 |
| `merchant` is `electronics` (case-insensitive) | +20 |
| `country` is not `IN` (foreign) | +30 |
| `amount >= 15000` | +12 |

| Score range | Level |
|-------------|-------|
| 0–30 | LOW |
| 31–70 | MEDIUM |
| 71+ | HIGH |

**Example:** `15000`, `electronics`, `IN` → 50 + 20 + 12 = **82 HIGH**

---

## Processed record (written by Node worker)

```json
{
  "transaction_id": "txn-001",
  "user_id": "user-123",
  "amount": 15000,
  "merchant": "electronics",
  "country": "IN",
  "risk_score": 82,
  "risk_level": "HIGH",
  "processed_at": "2026-06-17T10:13:54.478Z"
}
```

---

## Health check

### `GET /health`

```json
{
  "status": "UP"
}
```

---

## Environment configuration

| Variable | Default |
|----------|---------|
| `FRAUD_SYSTEM_ROOT` | A3 project root |
| `TRANSACTIONS_QUEUE_FILE` | `{root}/shared/data/transactions.json` |
| `PROCESSED_TRANSACTIONS_FILE` | `{root}/shared/data/processed_transactions.json` |
| `RUST_ENGINE_BIN` | `{root}/rust-engine/target/release/fraud-engine` |
