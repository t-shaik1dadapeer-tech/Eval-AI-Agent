# A1 — Branch Strategy

**Feature:** B4 Transaction Service — SQLite persistence & lookup  
**Integration branch:** `feature/A1-parent`  
**Base:** `main`

---

## Branch Hierarchy

```
main
│
└── feature/A1-parent                    [Integration / contract branch]
    │
    ├── feature/A1-data                  [Lane 1 — Data layer]
    ├── feature/A1-service               [Lane 2 — Service layer]
    ├── feature/A1-api                 [Lane 3 — API layer]
    └── feature/A1-quality             [Lane 4 — Tests & docs]
```

### Branch creation sequence

```bash
git checkout main
git pull origin main
git checkout -b feature/A1-parent

# Add contract files only, commit, push
git push -u origin feature/A1-parent

# Create lane branches from parent
git checkout feature/A1-parent
git checkout -b feature/A1-data
git push -u origin feature/A1-data

git checkout feature/A1-parent
git checkout -b feature/A1-service
git push -u origin feature/A1-service

git checkout feature/A1-parent
git checkout -b feature/A1-api
git push -u origin feature/A1-api

git checkout feature/A1-parent
git checkout -b feature/A1-quality
git push -u origin feature/A1-quality
```

---

## Branch Details

### `feature/A1-parent`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Frozen repository protocol + integration target for all lanes |
| **Owner** | Tech lead / orchestrator agent |
| **Duration** | ~30 minutes setup; open until all lanes merge |
| **Merge target** | `main` (after all lanes integrated) |
| **Allowed changes** | `app/contracts/*`, `docs/A1-INTERFACE.md` only |

---

### `feature/A1-data`

| Attribute | Value |
|-----------|-------|
| **Purpose** | SQLite schema, connection, repository implementation |
| **Owner** | Agent Lane 1 (Data) |
| **Duration** | 2–3 hours |
| **Merge target** | `feature/A1-parent` |
| **Touch zone** | `app/db/`, `app/repositories/`, `tests/test_sqlite_repository.py` |

---

### `feature/A1-service`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Refactor `TransactionService` to use repository injection |
| **Owner** | Agent Lane 2 (Service) |
| **Duration** | ~2 hours |
| **Merge target** | `feature/A1-parent` (after `A1-data`) |
| **Touch zone** | `app/services/`, `tests/test_transaction_service.py` |

---

### `feature/A1-api`

| Attribute | Value |
|-----------|-------|
| **Purpose** | New `GET /transactions/{id}` and list filtering |
| **Owner** | Agent Lane 3 (API) |
| **Duration** | ~2 hours |
| **Merge target** | `feature/A1-parent` (after `A1-service`) |
| **Touch zone** | `app/routes/transactions.py`, `app/schemas/transaction.py` |

---

### `feature/A1-quality`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Integration tests, README, integration report |
| **Owner** | Agent Lane 4 (QA/Docs) |
| **Duration** | 2–3 hours |
| **Merge target** | `feature/A1-parent` (after `A1-api`) |
| **Touch zone** | `tests/test_api_integration.py`, `tests/conftest.py`, `README.md`, `requirements.txt` |

---

## Ownership Matrix

| Path / artifact | Lane 1 | Lane 2 | Lane 3 | Lane 4 | Shared |
|-----------------|:------:|:------:|:------:|:------:|:------:|
| `app/contracts/` | — | — | — | — | Parent |
| `app/db/` | **own** | — | — | — | — |
| `app/repositories/` | **own** | — | — | — | — |
| `app/services/transaction_service.py` | — | **own** | — | — | — |
| `app/services/dependencies.py` | — | **own** | — | — | — |
| `app/routes/transactions.py` | — | — | **own** | — | — |
| `app/schemas/transaction.py` | — | — | **own** | — | — |
| `app/main.py` | — | — | read | — | Parent approves |
| `tests/conftest.py` | fixture only | fixture only | — | **own** | coordinate |
| `tests/test_*.py` (existing) | — | — | — | **own** | read-only |
| `README.md` | — | — | — | **own** | — |
| `requirements.txt` | — | — | — | **own** | review |

**Rule:** If a lane needs a file outside its zone, open a comment on parent branch — do not edit directly.

---

## Merge Order

| Step | Source branch | Target | Gate |
|-----:|---------------|--------|------|
| 1 | `feature/A1-parent` | `main` | Contracts committed (optional early merge) |
| 2 | `feature/A1-data` | `feature/A1-parent` | `pytest tests/test_sqlite_repository.py` |
| 3 | `feature/A1-service` | `feature/A1-parent` | `pytest tests/test_transaction_service.py` |
| 4 | `feature/A1-api` | `feature/A1-parent` | Route smoke test |
| 5 | `feature/A1-quality` | `feature/A1-parent` | `pytest -v` full suite |
| 6 | `feature/A1-parent` | `main` | Integration checklist complete |

### Rebase policy

Before each merge into parent:

```bash
git checkout feature/A1-<lane>
git fetch origin
git rebase origin/feature/A1-parent
# resolve conflicts per risk-analysis.md
git push --force-with-lease origin feature/A1-<lane>
```

**Allowed:** `--force-with-lease` on lane branches only.  
**Forbidden:** Force push to `main` or `feature/A1-parent`.

---

## Worktree Mapping

| Worktree directory | Branch | Agent |
|--------------------|--------|-------|
| `../Eval-Ai-A1-parent` | `feature/A1-parent` | Orchestrator |
| `../Eval-Ai-A1-data` | `feature/A1-data` | Lane 1 |
| `../Eval-Ai-A1-service` | `feature/A1-service` | Lane 2 |
| `../Eval-Ai-A1-api` | `feature/A1-api` | Lane 3 |
| `../Eval-Ai-A1-quality` | `feature/A1-quality` | Lane 4 |

---

## Commit Message Convention

```
A1-data: add SQLite transaction repository
A1-service: inject repository into TransactionService
A1-api: add GET /transactions/{id} and type filter
A1-quality: add integration tests and README persistence docs
A1: merge lane branches into parent
```
