# A1 — Agent Prompts

Copy each prompt into a separate agent session or worktree. All agents work from `beginner/B4-fastapi-service/` unless noted.

**Shared context for all lanes:**

- Base branch: `feature/A1-parent` (contains `app/contracts/transaction_repository.py`)
- Read `docs/A1-INTERFACE.md` before coding
- Do not modify files outside your lane ownership (see `branch-strategy.md`)
- Run `pytest` for your lane's tests before marking complete

---

## Agent Lane 1 — Data Layer

### Objective

Implement SQLite persistence for transactions behind the `TransactionRepository` protocol defined on `feature/A1-parent`.

### Scope

- Create `app/db/connection.py` with configurable `DATABASE_URL` (default `sqlite:///./transactions.db`)
- Create `app/db/schema.sql` with `transactions` table matching existing `Transaction` model fields
- Implement `app/repositories/sqlite_transaction_repository.py` satisfying the protocol:
  - `save(transaction: Transaction) -> Transaction`
  - `find_all(type_filter: str | None = None) -> list[Transaction]`
  - `find_by_id(transaction_id: UUID) -> Transaction | None`
  - `count() -> int`
- Add `tests/test_sqlite_repository.py` with tempfile database

### Constraints

- Use Python stdlib `sqlite3` unless parent branch explicitly approves `aiosqlite`
- UUID stored as TEXT; timestamps as ISO-8601 UTC strings
- Repository must be stateless aside from connection config
- Table creation runs on first connection (idempotent `CREATE TABLE IF NOT EXISTS`)

### Deliverables

- [ ] `app/db/connection.py`
- [ ] `app/db/schema.sql`
- [ ] `app/db/__init__.py`
- [ ] `app/repositories/sqlite_transaction_repository.py`
- [ ] `app/repositories/__init__.py`
- [ ] `tests/test_sqlite_repository.py` (≥4 test cases)

### Out of scope

- Do **not** modify:
  - `app/services/transaction_service.py`
  - `app/routes/transactions.py`
  - `app/schemas/transaction.py`
  - `app/main.py`
  - Existing test files (`tests/test_transactions.py`, etc.)
  - `README.md`
  - `requirements.txt` (Lane 4 owns dependency manifest)

### Validation before handoff

```bash
cd beginner/B4-fastapi-service
pytest tests/test_sqlite_repository.py -v
```

---

## Agent Lane 2 — Service Layer

### Objective

Refactor `TransactionService` to delegate storage to `TransactionRepository` via dependency injection while preserving public method signatures used by routes.

### Scope

- Modify `app/services/transaction_service.py`:
  - Accept `TransactionRepository` in constructor (default: `SqliteTransactionRepository`)
  - `create_transaction` → `repository.save`
  - `list_transactions` → `repository.find_all`
  - Add `get_transaction_by_id(id: UUID) -> Transaction | None`
  - `get_balance` → compute from `repository.find_all()` or dedicated query
  - Keep `clear()` for tests (truncate table or swap in-memory mock)
- Create `app/services/dependencies.py` with `get_transaction_service()` factory
- Add `tests/test_transaction_service.py` using `unittest.mock` or in-memory fake repository

### Constraints

- Do not import SQLite directly in service layer — only the protocol
- Preserve existing return types (`Transaction`, `list[Transaction]`, `tuple[float, int]`)
- Module-level `transaction_service` singleton must remain for backward compatibility with routes until Lane 3 wires DI
- Fake repository for unit tests lives in test file, not production code

### Deliverables

- [ ] Updated `app/services/transaction_service.py`
- [ ] `app/services/dependencies.py`
- [ ] `tests/test_transaction_service.py` (≥5 test cases)

### Out of scope

- Do **not** modify:
  - `app/db/` or `app/repositories/` (Lane 1)
  - Route handlers or HTTP status codes (Lane 3)
  - `app/schemas/transaction.py`
  - Integration tests against real HTTP (Lane 4)
  - Documentation

### Validation before handoff

```bash
pytest tests/test_transaction_service.py -v
# Existing route tests may fail until Lane 3 — that is expected
```

---

## Agent Lane 3 — API Layer

### Objective

Expose persistence-backed lookup and filtering through new and extended HTTP endpoints.

### Scope

- Add `GET /transactions/{transaction_id}`:
  - 200 + `TransactionResponse` when found
  - 404 `{"detail": "Transaction not found"}` when missing
  - 422 for invalid UUID format (FastAPI default)
- Extend `GET /transactions`:
  - Optional query param `type: credit | debit` (enum validation)
  - Pass filter to `transaction_service.list_transactions(type_filter=...)`
- Update `app/schemas/transaction.py` only if new response/request models needed
- Ensure OpenAPI docs reflect new endpoints

### Constraints

- Reuse existing `TransactionResponse` schema
- Do not change `POST /transactions` or `GET /balance` response shapes
- HTTP status codes must match B4 conventions (422 for validation errors)
- Minimal changes to `app/main.py` — prefer editing `routes/transactions.py` only

### Deliverables

- [ ] Updated `app/routes/transactions.py`
- [ ] Schema updates in `app/schemas/transaction.py` (if required)
- [ ] Service method `list_transactions` signature extended (coordinate with Lane 2 via parent rebase)

### Out of scope

- Do **not** modify:
  - SQLite or repository implementation
  - `transaction_service.py` internals (request new method via rebase if missing)
  - Test files (Lane 4)
  - `README.md`
  - Docker or deployment configs

### Validation before handoff

```bash
# After rebasing onto parent with Lanes 1+2 merged:
uvicorn app.main:app --port 8000 &
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/transactions/00000000-0000-0000-0000-000000000001
# Expect 404
```

---

## Agent Lane 4 — Quality Layer

### Objective

Add integration test coverage, update documentation, and produce post-merge validation artifacts.

### Scope

- `tests/test_api_integration.py`:
  - Full flow: POST → GET by id → GET list with filter → GET balance
  - Persistence across service restart (new TestClient with same DB file)
  - 404 case for unknown ID
- Update `tests/conftest.py`:
  - Temp SQLite DB fixture shared across integration tests
  - Reset DB between tests
- Update `beginner/B4-fastapi-service/README.md`:
  - Persistence behavior
  - New endpoints with curl examples
  - `DATABASE_URL` configuration
- Add `advanced/A1-parallel-plan/INTEGRATION_REPORT.md` template filled after merge
- Update `requirements.txt` only if new dependency required (document reason)

### Constraints

- All existing B4 tests must pass after full integration
- No changes to production logic except test fixtures
- README changes limited to B4 service folder
- Do not refactor unrelated code

### Deliverables

- [ ] `tests/test_api_integration.py` (≥6 test cases)
- [ ] Updated `tests/conftest.py`
- [ ] Updated `README.md`
- [ ] `advanced/A1-parallel-plan/INTEGRATION_REPORT.md`
- [ ] `requirements.txt` (if needed)

### Out of scope

- Do **not** modify:
  - `app/repositories/` implementation
  - `app/services/transaction_service.py` business logic
  - Route handler implementation (file edits for test imports only)
  - Other tracks (`intermediate/`, `beginner/B5-*`, etc.)

### Validation before handoff

```bash
pytest -v
ruff check .   # if ruff configured
```

---

## Orchestrator Agent — Parent Branch Setup

### Objective

Create frozen contracts so parallel lanes can proceed without blocking on each other.

### Scope

- Branch `feature/A1-parent` from `main`
- Add `app/contracts/transaction_repository.py`:

```python
from typing import Protocol
from uuid import UUID
from app.models.transaction import Transaction

class TransactionRepository(Protocol):
    def save(self, transaction: Transaction) -> Transaction: ...
    def find_all(self, type_filter: str | None = None) -> list[Transaction]: ...
    def find_by_id(self, transaction_id: UUID) -> Transaction | None: ...
    def count(self) -> int: ...
```

- Add `docs/A1-INTERFACE.md` documenting method semantics and acceptance criteria
- Create all four lane branches pointing at parent

### Out of scope

- No feature implementation on parent branch
