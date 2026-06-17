# A1 — Risk Analysis

**Feature:** B4 SQLite persistence & lookup  
**Lanes:** 4 parallel workstreams  
**Integration branch:** `feature/A1-parent`

---

## Conflict Analysis

### High-risk areas

| Area | Files | Risk | Lanes involved | Why |
|------|-------|:----:|----------------|-----|
| Service singleton wiring | `app/services/transaction_service.py` | **High** | 2, 3 | Lane 3 may need new methods; Lane 2 owns file |
| Test fixtures | `tests/conftest.py` | **High** | 1, 2, 4 | Multiple lanes add DB fixtures |
| Route + service coupling | `app/routes/transactions.py` | **Medium** | 2, 3 | Signature changes propagate |
| Schema extensions | `app/schemas/transaction.py` | **Medium** | 3, 4 | Query param models vs docs |
| Dependency manifest | `requirements.txt` | **Medium** | 1, 4 | Lane 1 may want `aiosqlite`; Lane 4 owns file |
| Application entry | `app/main.py` | **Low–Medium** | 2, 3 | Lifespan DB init, router includes |
| README | `beginner/B4-fastapi-service/README.md` | **Low** | 4 only | Single owner |

### Medium-risk areas

| Area | Files | Risk | Prevention |
|------|-------|:----:|------------|
| Model field drift | `app/models/transaction.py` | **Medium** | Freeze model on parent; no lane edits without approval |
| Existing API tests | `tests/test_transactions.py` | **Medium** | Lane 4 updates after all merges; lanes 1–3 read-only |
| Package init files | `app/__init__.py`, `app/services/__init__.py` | **Low** | Avoid unless required |

### Low-risk areas

| Area | Files | Risk | Notes |
|------|-------|:----:|-------|
| New DB module | `app/db/*` | **Low** | Lane 1 exclusive |
| New repository | `app/repositories/*` | **Low** | Lane 1 exclusive |
| New service tests | `tests/test_transaction_service.py` | **Low** | Lane 2 exclusive |
| New repo tests | `tests/test_sqlite_repository.py` | **Low** | Lane 1 exclusive |
| Integration tests | `tests/test_api_integration.py` | **Low** | Lane 4 exclusive (new file) |
| Root README | `README.md` | **None** | Out of scope |

---

## Mitigation Plan

### 1. Contract-first development

**Strategy:** Parent branch publishes `TransactionRepository` protocol and `docs/A1-INTERFACE.md` before any lane starts.

**Effect:** Lanes 2–4 can mock the protocol without waiting for Lane 1's SQLite code.

### 2. Strict file ownership

**Strategy:** Enforce ownership matrix from `branch-strategy.md`. Cross-lane needs → rebase onto parent, request orchestrator merge of prerequisite lane.

**Effect:** Eliminates simultaneous edits to `transaction_service.py`.

### 3. Sequential merge with rebase

**Strategy:** Merge order data → service → api → quality. Each lane rebases onto updated parent before PR.

**Effect:** Later lanes always see prior lanes' changes; conflicts resolved once per lane.

### 4. `conftest.py` coordination

**Strategy:**

- Lane 1: add `sqlite_repo` fixture in `tests/test_sqlite_repository.py` (local conftest or inline)
- Lane 2: mock fixtures in `tests/test_transaction_service.py` only
- Lane 4: **sole owner** of shared `tests/conftest.py` — merges last

**Effect:** Avoids three-way fixture conflicts.

### 5. `requirements.txt` single owner

**Strategy:** Only Lane 4 modifies `requirements.txt`. Lane 1 uses stdlib `sqlite3` by default.

**Effect:** No dependency manifest conflicts.

### 6. Feature flags / compatibility shim (optional)

**Strategy:** If Lane 3 starts before Lane 2 merges, stub `get_transaction_by_id` raising `NotImplementedError` on parent contract tests only.

**Effect:** Parallel start without broken imports.

---

## Conflict Resolution Playbook

| Conflict file | Owner wins | Resolver action |
|---------------|------------|-----------------|
| `app/contracts/*` | Parent / orchestrator | Lanes adapt to contract |
| `app/db/*`, `app/repositories/*` | Lane 1 | Others must not edit |
| `app/services/transaction_service.py` | Lane 2 | Lane 3 rebases; adds only call-site needs via PR comment |
| `app/routes/transactions.py` | Lane 3 | — |
| `tests/conftest.py` | Lane 4 (final) | Lanes 1–2 keep fixtures local until Lane 4 merges |
| `requirements.txt` | Lane 4 | Lane 1 documents deps in PR description |
| `README.md` | Lane 4 | — |

### Resolution procedure

1. Identify owning lane from table above
2. Non-owner discards their version of conflicted hunk
3. Re-run lane-specific `pytest` subset
4. Re-run full `pytest -v` on parent after merge
5. Document resolution in merge commit message

---

## Rollback Strategy

### Per-lane rollback

If a lane fails validation after merge to parent:

```bash
git checkout feature/A1-parent
git revert -m 1 <merge-commit-sha>   # revert bad lane merge
git push origin feature/A1-parent
```

Re-open lane branch, fix, re-merge.

### Full feature rollback

If integrated feature must be removed from `main`:

```bash
git checkout main
git revert -m 1 <parent-to-main-merge-sha>
git push origin main
```

**Data note:** SQLite file `transactions.db` is gitignored; rollback does not affect local DB files.

### Worktree cleanup rollback

```bash
git worktree remove ../Evil-Ai-A1-data --force
git branch -D feature/A1-data   # only if lane abandoned
```

### Rollback triggers

| Trigger | Action |
|---------|--------|
| `pytest` failure on parent after lane merge | Revert that lane; do not proceed |
| Breaking change to existing B4 API contract | Halt merge; fix Lane 3 |
| Data loss in persistence layer | Revert Lane 1+2; investigate schema |
| Dependency vulnerability introduced | Revert Lane 4 requirements change |

---

## Risk Register Summary

| ID | Risk | Likelihood | Impact | Mitigation | Residual |
|----|------|:----------:|:------:|------------|:--------:|
| R1 | `conftest.py` merge conflict | High | Medium | Lane 4 owns final conftest | Low |
| R2 | Service/API signature mismatch | Medium | High | Contract on parent; sequential merge | Low |
| R3 | Parallel edit of `transaction_service.py` | Medium | High | Lane 2 sole owner | Low |
| R4 | Persistence breaks existing tests | Medium | Medium | Lane 4 full regression | Low |
| R5 | UUID format inconsistency DB vs API | Low | Medium | Schema review on Lane 1 PR | Low |
| R6 | Agent modifies wrong files | Medium | Medium | Ownership matrix in prompts | Medium |
| R7 | Force push to main | Low | Critical | Explicit ban in shared constraints | Low |

---

## Pre-merge checklist (orchestrator)

- [ ] All four lane branches rebased on latest `feature/A1-parent`
- [ ] No conflict markers in any file
- [ ] Ownership violations reviewed (unexpected file changes reverted)
- [ ] `pytest -v` green on parent
- [ ] API smoke test documented in `INTEGRATION_REPORT.md`
- [ ] Rollback SHA recorded in integration report
