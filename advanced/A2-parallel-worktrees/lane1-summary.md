# A2 — Lane 1 Summary

**Branch:** `feature/A2-lane1`  
**Worktree:** `/Users/shaikdadapeer/Eval-Ai-A2-lane1`  
**Owner:** API / service layer

---

## Scope

Implement `GET /transactions/{transaction_id}` for the B4 FastAPI transaction service:

- Add `get_transaction_by_id()` to `TransactionService`
- Add route handler with HTTP 404 when ID not found
- Return `TransactionResponse` on success

## Why this lane

Lane 1 owns production code only (service + routes). No test or documentation files — avoids overlap with Lane 2.

## Files changed

| File | Change |
|------|--------|
| `beginner/B4-fastapi-service/app/services/transaction_service.py` | Added `get_transaction_by_id(UUID) -> Transaction \| None` |
| `beginner/B4-fastapi-service/app/routes/transactions.py` | Added `GET /transactions/{transaction_id}` with 404 handling |

## Commit

| Field | Value |
|-------|-------|
| **Hash** | `1ab2d3447b64ea91a82145e4c5b51088002c771c` |
| **Message** | `A2-lane1: add GET /transactions/{id} endpoint` |

## Independent verification

**Command:**

```bash
cd /Users/shaikdadapeer/Eval-Ai-A2-lane1/beginner/B4-fastapi-service
pytest -v
```

**Output:**

```
collected 5 items
tests/test_transactions.py::test_create_transaction PASSED
tests/test_transactions.py::test_get_transactions PASSED
tests/test_transactions.py::test_get_balance PASSED
tests/test_transactions.py::test_invalid_transaction_validation PASSED
tests/test_transactions.py::test_debit_balance_calculation PASSED
======================== 5 passed, 3 warnings in 0.05s =========================
```

| Metric | Value |
|--------|-------|
| Exit code | `0` |
| Passed | 5 |
| Failed | 0 |
| Notes | Lookup tests not present on this branch (Lane 2 scope) |

## Out of scope (honored)

- No changes to `tests/`
- No changes to `README.md`
