# I2 — End-to-End Flow Trace

**Repository:** `Eval-Ai`  
**Scan date:** 2026-06-17  
**Task output:** `intermediate/I2-end-to-end-trace/`  
**Evidence policy:** Repository source code only

---

# Executive Summary

| Field | Value |
|-------|-------|
| **Flow selected** | `POST /transactions` — create transaction (B4 FastAPI service) |
| **Business purpose** | Accept a credit/debit transaction payload, validate it, store it in memory, and return the created transaction |
| **Entry point** | HTTP `POST /transactions` handled by FastAPI ASGI app |
| **Final side effect** | `Transaction` appended to in-memory `TransactionService._transactions` list |

**Why this flow:** The repository contains no Kafka consumers, schedulers, cron jobs, webhooks, or queue listeners. The only traceable asynchronous/event flows are absent. B4 (`beginner/B4-fastapi-service/`) provides the clearest layered REST flow: route → service → domain model → in-memory store.

---

# Entry Point

| Attribute | Value |
|-----------|-------|
| **File path** | `beginner/B4-fastapi-service/app/routes/transactions.py` |
| **Class / callable** | Module-level function `create_transaction` (FastAPI route handler) |
| **Method name** | `create_transaction` |
| **Trigger mechanism** | **HTTP** — `POST /transactions` |
| **App registration** | `beginner/B4-fastapi-service/app/main.py` — `app.include_router(transactions_router)` |

**Evidence — route definition:**

```13:21:beginner/B4-fastapi-service/app/routes/transactions.py
@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transaction",
)
def create_transaction(payload: TransactionCreate) -> TransactionResponse:
    transaction = transaction_service.create_transaction(payload)
    return TransactionResponse.model_validate(transaction)
```

**Evidence — router mounted on app:**

```15:15:beginner/B4-fastapi-service/app/main.py
app.include_router(transactions_router)
```

---

# Step-by-Step Trace

## Step 1 — HTTP request received by FastAPI application

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/main.py` |
| **Class** | `FastAPI` instance (`app`) |
| **Method** | ASGI request dispatch (framework-internal) + `include_router` registration |
| **Purpose** | Receive HTTP request and route to matching handler |
| **Input** | HTTP `POST /transactions` with JSON body |
| **Output** | Matched route: `create_transaction` |

---

## Step 2 — Request body validation (Pydantic)

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/schemas/transaction.py` |
| **Class** | `TransactionCreate` |
| **Method** | Pydantic model validation (invoked by FastAPI before handler) |
| **Purpose** | Validate `type`, `amount > 0`, optional `description` |
| **Input** | Raw JSON body fields: `type`, `amount`, `description` |
| **Output** | `TransactionCreate` instance, or `RequestValidationError` |

**Evidence:**

```12:15:beginner/B4-fastapi-service/app/schemas/transaction.py
class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0, description="Transaction amount; must be greater than zero")
    description: Optional[str] = Field(default=None, max_length=500)
```

---

## Step 3 — Route handler delegates to service

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/routes/transactions.py` |
| **Class** | N/A (module function) |
| **Method** | `create_transaction` |
| **Purpose** | Orchestrate service call and map result to response DTO |
| **Input** | `TransactionCreate` |
| **Output** | `TransactionResponse` |

**Evidence:**

```19:21:beginner/B4-fastapi-service/app/routes/transactions.py
def create_transaction(payload: TransactionCreate) -> TransactionResponse:
    transaction = transaction_service.create_transaction(payload)
    return TransactionResponse.model_validate(transaction)
```

---

## Step 4 — Service creates domain transaction

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/services/transaction_service.py` |
| **Class** | `TransactionService` |
| **Method** | `create_transaction` |
| **Purpose** | Generate ID/timestamp, build domain object, persist in memory |
| **Input** | `TransactionCreate` |
| **Output** | `Transaction` |

**Evidence:**

```16:25:beginner/B4-fastapi-service/app/services/transaction_service.py
    def create_transaction(self, payload: TransactionCreate) -> Transaction:
        transaction = Transaction(
            id=uuid4(),
            type=payload.type,
            amount=payload.amount,
            description=payload.description,
            created_at=datetime.now(timezone.utc),
        )
        self._transactions.append(transaction)
        return transaction
```

---

## Step 5 — Domain model instantiation

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/models/transaction.py` |
| **Class** | `Transaction` |
| **Method** | Dataclass constructor |
| **Purpose** | Hold persisted transaction fields in process memory |
| **Input** | `id`, `type`, `amount`, `description`, `created_at` |
| **Output** | `Transaction` instance |

**Evidence:**

```15:21:beginner/B4-fastapi-service/app/models/transaction.py
@dataclass
class Transaction:
    id: UUID
    type: TransactionType
    amount: float
    description: Optional[str]
    created_at: datetime
```

---

## Step 6 — Final side effect: in-memory append

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/services/transaction_service.py` |
| **Class** | `TransactionService` |
| **Method** | `create_transaction` → `self._transactions.append(transaction)` |
| **Purpose** | **Final side effect** — store transaction in process-local list |
| **Input** | `Transaction` object |
| **Output** | Mutation of `self._transactions` (no return from `append`) |

**Evidence — store declaration:**

```10:14:beginner/B4-fastapi-service/app/services/transaction_service.py
class TransactionService:
    """In-memory transaction store with balance calculation."""

    def __init__(self) -> None:
        self._transactions: list[Transaction] = []
```

---

## Step 7 — Response DTO mapping

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/routes/transactions.py` |
| **Class** | `TransactionResponse` |
| **Method** | `TransactionResponse.model_validate(transaction)` |
| **Purpose** | Convert domain `Transaction` to API response schema |
| **Input** | `Transaction` |
| **Output** | `TransactionResponse` |

**Evidence:**

```26:31:beginner/B4-fastapi-service/app/schemas/transaction.py
class TransactionResponse(BaseModel):
    id: UUID
    type: TransactionType
    amount: float
    description: Optional[str]
    created_at: datetime
```

---

## Step 8 — HTTP response serialization

| Field | Value |
|-------|-------|
| **File path** | `beginner/B4-fastapi-service/app/main.py` (FastAPI framework) |
| **Class** | `FastAPI` |
| **Method** | Response serialization (framework) |
| **Purpose** | Return `HTTP 201` with JSON body |
| **Input** | `TransactionResponse` |
| **Output** | HTTP `201 Created` JSON response to client |

---

# Repository / Data Layer

| Layer | Status | Evidence |
|-------|--------|----------|
| Repository class | **Not present** | No `*Repository` or DAO in repository |
| Database access | **Not present** | No SQL/ORM calls |
| Data layer substitute | **In-memory list** | `TransactionService._transactions` |

This flow **does not** pass through a repository or database layer. The service layer is the terminal persistence point.

---

# External Dependencies

| Dependency | File path | Purpose | Present in this flow? |
|------------|-----------|---------|----------------------|
| Database (PostgreSQL, MySQL, etc.) | — | Persistent storage | **No** |
| Kafka | — | Event streaming | **No** |
| Redis | — | Cache | **No** |
| External HTTP APIs | — | Third-party calls | **No** |
| S3 / object storage | — | File/blob storage | **No** |
| Message queues | — | Async messaging | **No** |
| **Python stdlib `uuid`** | `transaction_service.py` | `uuid4()` for transaction ID | **Yes** |
| **Python stdlib `datetime`** | `transaction_service.py` | `datetime.now(timezone.utc)` | **Yes** |
| **FastAPI / Pydantic / Starlette** | `main.py`, `schemas/transaction.py` | HTTP + validation + serialization | **Yes** |

---

# Side Effects

| Side effect type | Occurs? | Evidence |
|------------------|---------|----------|
| Database write | **No** | No DB client in codebase |
| Database read | **No** | — |
| Queue publish | **No** | — |
| Queue consumption | **No** | — |
| External API call | **No** | — |
| Cache update | **No** | — |
| File write | **No** | — |
| **In-memory list mutation** | **Yes** | `self._transactions.append(transaction)` |

**Final side effect (confirmed):** Append one `Transaction` to the singleton `transaction_service._transactions` list in process memory.

---

# Data Transformations

```
HTTP JSON body
  → TransactionCreate (Pydantic request DTO)
    → Transaction (domain dataclass)
      → [stored in _transactions list]
    → TransactionResponse (Pydantic response DTO)
  → HTTP JSON response (201)
```

| Stage | Type | File |
|-------|------|------|
| Request | `TransactionCreate` | `app/schemas/transaction.py` |
| Domain | `Transaction` | `app/models/transaction.py` |
| Storage | `list[Transaction]` | `app/services/transaction_service.py` |
| Response | `TransactionResponse` | `app/schemas/transaction.py` |

No entity-to-external-request mapping exists (no external systems).

---

# Error Handling Path

## Validation errors (invalid payload)

| Step | File | Handler | Result |
|------|------|---------|--------|
| 1 | `schemas/transaction.py` | Pydantic `Field(gt=0)`, enum `TransactionType` | Raises `RequestValidationError` |
| 2 | `main.py` | `validation_exception_handler` | Returns HTTP `422` JSON `{"detail": [...]}` |

**Evidence:**

```18:25:beginner/B4-fastapi-service/app/main.py
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )
```

## Other error paths

| Type | Present? | Evidence |
|------|----------|----------|
| Service-layer exceptions | **No** | `create_transaction` has no `try/except` |
| Retry logic | **No** | Not found in flow |
| Fallback logic | **No** | Not found in flow |

---

# Alternative Flows Considered (not selected)

| Flow | Location | Reason not selected |
|------|----------|---------------------|
| `GET /transactions` | B4 | Read-only; no mutating side effect |
| `GET /balance` | B4 | Computation only; no persistence write |
| `POST /transactions` | B5 Node.js | Valid alternative; B4 chosen for clearer layer separation |
| B6 log analyzer CLI | B6 | File read only; not REST/event/scheduler per task options |
| Kafka / cron / webhook | — | **Not present** in repository |

---

# Known Uncertainties

| # | Item | Classification |
|---|------|----------------|
| 1 | Exact ASGI middleware order inside FastAPI | **Inferred** — framework-internal; entry routing confirmed via route registration |
| 2 | Whether `transaction_service` singleton is shared across workers | **Uncertain at runtime** — code uses module-level singleton; multi-worker uvicorn would have separate memory per process (not stated in code) |
| 3 | Repository layer omission | **Confirmed** — no repository class exists; not an inference |
| 4 | Persistence survival after process exit | **Confirmed absent** — in-memory only; data lost on restart |

---

# Validation Checklist

| # | Check | Result |
|---|-------|--------|
| 1 | Every step exists in code | **Yes** — 8 steps traced |
| 2 | Every method is real | **Yes** — all cited functions/classes verified |
| 3 | Side effects traceable | **Yes** — `list.append` on `_transactions` |
| 4 | Inferred sections marked | **Yes** — see Known Uncertainties |
| 5 | Mermaid syntax valid | **Yes** — `sequence-diagram.mmd` |

---

# Verification Summary

| Field | Value |
|-------|-------|
| Flow selected | `POST /transactions` (B4 FastAPI) |
| Files analyzed | 30 application source files (full repo scan) |
| Files in trace path | 5 (`main.py`, `transactions.py`, `transaction.py` ×2, `transaction_service.py`) |
| Steps documented | 8 |
| External dependencies (infrastructure) | 0 |
| Stdlib/framework dependencies | `uuid`, `datetime`, FastAPI/Pydantic |
| Side effects | 1 — in-memory list append |
| Repository layer | Absent |
| Confidence | **Confirmed** (for traced path) |

---

# Appendix — Files Analyzed

**B4 FastAPI (trace path):** `app/main.py`, `app/routes/transactions.py`, `app/schemas/transaction.py`, `app/models/transaction.py`, `app/services/transaction_service.py`

**B4 FastAPI (other):** `tests/*`, remaining `app/**`

**B5 Node.js:** `src/**/*.js` — parallel REST API, in-memory, not traced

**B6 Rust:** `src/**/*.rs` — CLI file read, not a task-listed entry type

**Not found:** Kafka consumers, schedulers, cron, webhooks, queue listeners, database repositories
