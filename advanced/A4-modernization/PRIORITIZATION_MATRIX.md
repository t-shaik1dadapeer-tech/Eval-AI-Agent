# A4 — Prioritization Matrix

Scoring scale: **1** (low) to **5** (high).  
**Priority** = lower number = implement sooner.

---

## Full scoring table

| Opportunity | Business Value | Technical Value | Risk | Effort | Priority |
|-------------|:--------------:|:---------------:|:----:|:------:|:--------:|
| Add GitHub Actions CI pipeline | 5 | 5 | 1 | 2 | **P1** |
| Standardize `/health` responses (`ok` → `UP`) | 3 | 3 | 2 | 2 | **P2** |
| Add Python linting (ruff + CI job) | 3 | 4 | 2 | 2 | **P3** |
| Consistent Python dependency pinning | 3 | 4 | 2 | 2 | **P4** |
| Docker Compose for A3 polyglot stack | 4 | 4 | 3 | 4 | **P5** |
| Add Node.js ESLint | 2 | 3 | 2 | 2 | **P6** |
| Structured logging (JSON logs) | 3 | 4 | 3 | 3 | **P7** |
| Security scanning in CI | 4 | 4 | 2 | 2 | **P8** |

---

## Ranked opportunities

### Priority 1 — Add GitHub Actions CI pipeline ✅ IMPLEMENTED

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 5 / 5 | Automates regression detection for 8 service test suites |
| Risk | 1 / 5 | No production code changes |
| Effort | 2 / 5 | Single workflow + verify script |

**Evidence gap:** No `.github/` directory; `devops/D3-ci-pipeline/.gitkeep` empty.

---

### Priority 2 — Standardize health endpoint responses

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 3 / 5 | Aligns ops contracts; I5 Dockerfile expects `UP` |
| Risk | 2 / 5 | Test updates required in B4/B5 |
| Effort | 2 / 5 | 2–4 file edits |

**Evidence:** `beginner/B4-fastapi-service/app/main.py` returns `"ok"`; I4/A3 return `"UP"`.

---

### Priority 3 — Add Python linting (ruff)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 4 / 5 (technical) | Catches bugs, enforces style |
| Risk | 2 / 5 | May surface existing violations |
| Effort | 2 / 5 | `pyproject.toml` + CI step |

**Evidence:** `.gitignore` has `.ruff_cache/` but no ruff config exists.

---

### Priority 4 — Consistent Python dependency pinning

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 4 / 5 (technical) | Reproducible installs |
| Risk | 2 / 5 | Pin updates may need testing |
| Effort | 2 / 5 | Edit 3 `requirements.txt` files |

**Evidence:** A3 uses open bounds; B4/I4 use `<major` upper caps.

---

### Priority 5 — Docker Compose for polyglot stack

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 4 / 5 | One-command full stack |
| Risk | 3 / 5 | Networking, volume mounts |
| Effort | 4 / 5 | Compose file + Dockerfiles for A3 |

**Evidence:** Only `intermediate/I5-dockerize/Dockerfile` exists; `devops/D2-docker-compose/` empty.

---

### Priority 6 — Node.js ESLint

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 3 / 5 | JS quality gate |
| Risk | 2 / 5 | Initial lint debt |
| Effort | 2 / 5 | Config + 3 packages |

**Evidence:** `package.json` files lack `lint` script and eslint dep.

---

### Priority 7 — Structured logging

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 4 / 5 (technical) | Debuggability |
| Risk | 3 / 5 | Touches runtime code |
| Effort | 3 / 5 | Per-service logging setup |

**Evidence:** `console.log` in A3 worker; no FastAPI logging middleware.

---

### Priority 8 — Security scanning in CI

| Dimension | Score | Notes |
|-----------|-------|-------|
| Value | 4 / 5 | Catches known CVEs |
| Risk | 2 / 5 | May report unfixable advisories |
| Effort | 2 / 5 | `pip audit` + `npm audit` steps |

**Evidence:** No security steps in CI (before A4); hub rules mention `pip audit` as standard but not configured.

---

## Selection decision

**P1 selected** because it:

1. Addresses the largest evidenced gap (no CI at all)
2. Leverages **existing** test suites without modifying them
3. Has **near-zero regression risk** (additive infrastructure)
4. Is **immediately verifiable** locally via `scripts/ci-verify.sh`
5. Unblocks future P3/P8 improvements (lint and security as CI jobs)
