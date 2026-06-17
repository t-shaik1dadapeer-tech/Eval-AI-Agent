# A2 — Lane 2 Summary

**Branch:** `feature/A2-lane2`  
**Worktree:** `/Users/shaikdadapeer/Evil-Ai-A2-lane2`  
**Owner:** Tests + documentation

---

## Scope

Add test coverage and user documentation for transaction lookup by ID:

- New pytest module for lookup success, 404, and invalid UUID cases
- README endpoint table and curl examples
- Update expected test count (5 → 8)

## Why this lane

Lane 2 owns quality artifacts only. No production route or service edits — zero file overlap with Lane 1.

## Files changed

| File | Change |
|------|--------|
| `beginner/B4-fastapi-service/tests/test_transaction_lookup.py` | **New** — 3 test cases |
| `beginner/B4-fastapi-service/README.md` | Endpoint table, curl example, test count |

## Commit

| Field | Value |
|-------|-------|
| **Hash** | `957723203ec4f2db2f25d37e1844072a4120fb39` |
| **Message** | `A2-lane2: add transaction lookup tests and README docs` |

## Independent verification

**Command:**

```bash
cd /Users/shaikdadapeer/Evil-Ai-A2-lane2/beginner/B4-fastapi-service
pytest -v
```

**Output:**

```
collected 8 items
tests/test_transaction_lookup.py::test_get_transaction_by_id FAILED
tests/test_transaction_lookup.py::test_get_transaction_not_found FAILED
tests/test_transaction_lookup.py::test_get_transaction_invalid_uuid FAILED
tests/test_transactions.py::test_create_transaction PASSED
tests/test_transactions.py::test_get_transactions PASSED
tests/test_transactions.py::test_get_balance PASSED
tests/test_transactions.py::test_invalid_transaction_validation PASSED
tests/test_transactions.py::test_debit_balance_calculation PASSED
=================== 3 failed, 5 passed, 3 warnings in 0.14s ====================
```

| Metric | Value |
|--------|-------|
| Exit code | `1` |
| Passed | 5 (existing suite) |
| Failed | 3 (lookup tests — endpoint not on this branch) |
| Expected | **Yes** — Lane 2 tests require Lane 1 API; failures confirm isolation |

### Failure analysis (pre-merge)

| Test | Got | Expected after merge |
|------|-----|----------------------|
| `test_get_transaction_by_id` | 404 (route missing) | 200 |
| `test_get_transaction_not_found` | `{"detail": "Not Found"}` | `{"detail": "Transaction not found"}` |
| `test_get_transaction_invalid_uuid` | 404 | 422 |

## Out of scope (honored)

- No changes to `app/services/`
- No changes to `app/routes/`
