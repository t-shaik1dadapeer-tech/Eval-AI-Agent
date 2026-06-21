# A1 — Multi-Worktree Parallel Execution Plan

**Repository:** `Eval-Ai`  
**Task output:** `advanced/A1-parallel-plan/`  
**Date:** 2026-06-17  
**Type:** Executable plan (no implementation in A1)

---

# Executive Summary

This plan decomposes **B4 FastAPI Transaction Service persistence upgrade** into **4 parallel workstreams** that can execute in separate git worktrees with minimal merge conflict risk. A parent integration branch establishes shared contracts first; lanes then implement data, service, API, and quality layers independently before sequential merge.

| Metric | Value |
|--------|-------|
| Selected feature | B4 SQLite persistence + transaction lookup |
| Workstreams | 4 |
| Parent branch | `feature/A1-parent` |
| Estimated parallel duration | 2–4 hours per lane (agent-dependent) |
| Merge strategy | Sequential: parent → data → service → api → quality |

---

# Selected Feature

## Feature: B4 Transaction Service — SQLite Persistence & Lookup

**Base path:** `beginner/B4-fastapi-service/`

**Scope:**

1. Replace in-memory `list` storage with SQLite persistence
2. Add `GET /transactions/{id}` — fetch single transaction by UUID
3. Add optional filter on `GET /transactions?type=credit|debit`
4. Preserve existing `POST /transactions`, `GET /transactions`, `GET /balance` behavior
5. Add tests and documentation

### Why this feature is suitable for parallel execution

| Criterion | Assessment |
|-----------|------------|
| Existing layered architecture | B4 already has `routes/`, `services/`, `schemas/`, `models/` |
| Clear ownership boundaries | DB, service, API, and tests touch mostly disjoint files |
| Medium complexity | Large enough for 4 lanes; not a trivial one-file change |
| Contract-driven integration | Repository `Protocol` enables parallel work against interface |
| Low cross-repo blast radius | Contained to `beginner/B4-fastapi-service/` |
| Existing test harness | pytest + TestClient already in place |

### Why not other candidates

| Alternative | Reason rejected |
|-------------|-----------------|
| I4 currency converter extension | Smaller surface; fewer independent lanes |
| New greenfield service | Higher integration uncertainty |
| B6 log analyzer feature | CLI-only; limited parallel API/test/doc split |
| Cross-cutting observability | High conflict risk on `main.py` across services |

---

# Task Decomposition

## Phase 0 — Parent setup (sequential, ~30 min)

Create `feature/A1-parent` from `main` with **contracts only**:

| File | Purpose |
|------|---------|
| `app/contracts/transaction_repository.py` | `Protocol` defining `save`, `find_all`, `find_by_id`, `count` |
| `app/contracts/__init__.py` | Package init |
| `docs/A1-INTERFACE.md` | Frozen interface spec for all lanes |

**No implementation** on parent branch — only interfaces and acceptance criteria.

---

# Parallel Workstreams

## Lane 1 — Data Layer (`feature/A1-data`)

| Field | Value |
|-------|-------|
| **Scope** | SQLite schema, connection management, `SqliteTransactionRepository` |
| **Owner** | Agent/Data |
| **Dependencies** | `feature/A1-parent` merged or rebased |
| **Duration** | ~2–3 hours |

**Deliverables:**

- `app/db/connection.py` — SQLite connection factory (`DATABASE_URL` env)
- `app/db/schema.sql` — `transactions` table DDL
- `app/repositories/sqlite_transaction_repository.py` — implements `TransactionRepository` protocol
- `app/repositories/__init__.py`
- Unit tests: `tests/test_sqlite_repository.py`

**Does not touch:** routes, `transaction_service.py`, existing tests (except new repo tests)

---

## Lane 2 — Service Layer (`feature/A1-service`)

| Field | Value |
|-------|-------|
| **Scope** | Refactor `TransactionService` to use `TransactionRepository` |
| **Owner** | Agent/Service |
| **Dependencies** | Lane 1 protocol (parent); can use in-memory mock until Lane 1 merges |
| **Duration** | ~2 hours |

**Deliverables:**

- Modified `app/services/transaction_service.py` — inject repository
- `app/services/dependencies.py` — DI wiring for repository singleton
- `tests/test_transaction_service.py` — service tests with mock repository

**Does not touch:** SQLite files, route handlers, OpenAPI docs

---

## Lane 3 — API Layer (`feature/A1-api`)

| Field | Value |
|-------|-------|
| **Scope** | New endpoints, query params, 404 handling |
| **Owner** | Agent/API |
| **Dependencies** | Service method signatures from parent contract doc |
| **Duration** | ~2 hours |

**Deliverables:**

- `GET /transactions/{transaction_id}` in `app/routes/transactions.py`
- Query param `type` filter on `GET /transactions`
- `app/schemas/transaction.py` — `TransactionListParams` if needed
- HTTP 404 for unknown ID

**Does not touch:** repository implementation, SQLite schema, test files (except optional route unit tests in lane 4)

---

## Lane 4 — Quality Layer (`feature/A1-quality`)

| Field | Value |
|-------|-------|
| **Scope** | Integration tests, README, migration notes |
| **Owner** | Agent/QA |
| **Dependencies** | API contract from parent; can stub service |
| **Duration** | ~2–3 hours |

**Deliverables:**

- `tests/test_api_integration.py` — end-to-end with temp SQLite file
- Updated `beginner/B4-fastapi-service/README.md`
- `advanced/A1-parallel-plan/INTEGRATION_REPORT.md` (post-merge validation template)
- `requirements.txt` — add `aiosqlite` or stdlib `sqlite3` only (no upgrade spree)

**Does not touch:** repository internals, service logic (except test fixtures)

---

# Branch Structure

```
main
 └── feature/A1-parent          # contracts + interface doc
      ├── feature/A1-data       # Lane 1
      ├── feature/A1-service    # Lane 2
      ├── feature/A1-api        # Lane 3
      └── feature/A1-quality    # Lane 4
           └── (merge back to feature/A1-parent → main)
```

See `branch-strategy.md` for ownership and merge order details.

---

# Merge Strategy

| Order | Branch | Into | Prerequisites | Validation |
|------:|--------|------|---------------|------------|
| 0 | `feature/A1-parent` | `main` | Plan approved | Contract files exist; CI green on main |
| 1 | `feature/A1-data` | `feature/A1-parent` | Parent on branch | `pytest tests/test_sqlite_repository.py` |
| 2 | `feature/A1-service` | `feature/A1-parent` | Lane 1 merged | `pytest tests/test_transaction_service.py` |
| 3 | `feature/A1-api` | `feature/A1-parent` | Lane 2 merged | Manual curl / OpenAPI check |
| 4 | `feature/A1-quality` | `feature/A1-parent` | Lane 3 merged | Full `pytest -v` |
| 5 | `feature/A1-parent` | `main` | All lanes merged | Full regression + B4 backward compat |

### Expected conflicts

| Merge | Conflict risk | Likely files |
|-------|---------------|--------------|
| Data → Parent | **Low** | New files only |
| Service → Parent | **Medium** | `transaction_service.py`, `conftest.py` |
| API → Parent | **Medium** | `routes/transactions.py`, `schemas/transaction.py` |
| Quality → Parent | **Low–Medium** | `tests/conftest.py`, `README.md`, `requirements.txt` |

**Resolution rule:** Parent contract wins; implementer rebases and adapts.

---

# Verification Plan

## Build verification

```bash
cd beginner/B4-fastapi-service
pip install -r requirements.txt
python -c "from app.main import app"
```

## Testing verification

```bash
pytest -v
# Expected: all existing B4 tests + new persistence tests pass
```

## API verification

```bash
uvicorn app.main:app --port 8000
curl -X POST http://localhost:8000/transactions -H "Content-Type: application/json" \
  -d '{"type":"credit","amount":100}'
curl http://localhost:8000/transactions/{id}
curl http://localhost:8000/balance
```

## Merge verification

- [ ] No conflict markers in merged files
- [ ] `git log --oneline` shows lane commits in order
- [ ] In-memory behavior replaced; restart persists data
- [ ] I2 flow trace updated if endpoints changed (optional follow-up)

## Code review verification

- [ ] Repository protocol not broken
- [ ] No unrelated file changes
- [ ] No dependency version bumps without approval
- [ ] 404/422 error shapes consistent with B4 patterns

---

# Worktree Commands (executable)

```bash
# From repo root
git checkout -b feature/A1-parent main

# Lane 1
git worktree add ../Eval-Ai-A1-data feature/A1-data
# Agent works in ../Eval-Ai-A1-data

# Lane 2
git worktree add ../Eval-Ai-A1-service feature/A1-service

# Lane 3
git worktree add ../Eval-Ai-A1-api feature/A1-api

# Lane 4
git worktree add ../Eval-Ai-A1-quality feature/A1-quality

# After all lanes merge to parent
git worktree remove ../Eval-Ai-A1-data
# ... repeat for each worktree
```

---

# Shared Constraints

See `agent-prompts.md` and `risk-analysis.md` for lane-specific constraints and conflict mitigation.

**Repository-wide rules:**

- No force push to `main`
- No formatting-only commits
- No dependency upgrades beyond `sqlite3` (stdlib) or explicit `aiosqlite` if approved
- No changes outside `beginner/B4-fastapi-service/` except `advanced/A1-parallel-plan/INTEGRATION_REPORT.md`
- No schema changes outside `app/db/schema.sql`
- Preserve existing API response shapes for current endpoints

---

# Final Summary

| Field | Value |
|-------|-------|
| Selected task | B4 SQLite persistence + lookup/filter API |
| Workstreams | 4 |
| Branch names | `feature/A1-parent`, `A1-data`, `A1-service`, `A1-api`, `A1-quality` |
| Merge order | parent → data → service → api → quality → main |
| Major risks | `conftest.py`, `transaction_service.py`, `requirements.txt` conflicts |
| Verification | pytest full suite + curl smoke tests |
