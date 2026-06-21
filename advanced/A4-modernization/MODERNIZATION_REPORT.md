# A4 — Modernization Report

**Repository:** `Eval-Ai`  
**Assessment date:** 2026-06-17  
**First improvement implemented:** GitHub Actions CI pipeline

---

# Executive Summary

The repository is a **multi-track evaluation scaffold** (beginner, intermediate, advanced, devops) with **working polyglot services** (Python FastAPI, Node.js, Rust) and **automated CI/CD** via GitHub Actions (`.github/workflows/ci.yml`, `devops/D3-ci-pipeline/`). Tests run via root `make test` / `scripts/ci-verify.sh`. The **devops track (D1–D6)** is fully implemented — Terraform, Docker Compose stack, CI pipeline, Kubernetes manifests, bootstrap Makefile/mise, and Prometheus/Grafana observability. This assessment identified **8 modernization opportunities**; **Priority 1 — add a GitHub Actions CI workflow** — was implemented as a minimal, low-risk, high-value first step. Local verification via `scripts/ci-verify.sh` passed all tests across service directories (exit code `0`).

---

# Repository Overview

| Attribute | Evidence |
|-----------|----------|
| **Type** | Hands-on AI agent evaluation exercises (24 PML/OCL tasks) |
| **Languages** | Python, JavaScript, Rust, HCL (Terraform) |
| **Services with tests** | B4, B5, B6, I4 (×2), A3 (×3), D6 service |
| **CI/CD** | `.github/workflows/ci.yml`; local mirror `devops/D3-ci-pipeline/scripts/run-pipeline-local.sh` |
| **Containerization** | I5 Dockerfile; D2 multi-service compose; D6 observability stack |
| **DevOps track** | D1 Terraform, D2 compose+e2e, D3 CI, D4 K8s, D5 bootstrap, D6 metrics |
| **Root docs** | `README.md`, `docs/TASK_REGISTRY.md`, `docs/PML_VERIFICATION.md` |

No `pom.xml`, `build.gradle`, or monorepo build tool exists. Each task folder is self-contained.

---

# Findings

## F1 — No CI/CD pipeline

| Field | Detail |
|-------|--------|
| **Description** | ~~No GitHub Actions~~ **Resolved:** root CI workflow and D3 local pipeline mirror exist |
| **Evidence** | `.github/workflows/ci.yml`; `devops/D3-ci-pipeline/scripts/run-pipeline-local.sh` |
| **File path** | `.github/workflows/ci.yml`, `devops/D3-ci-pipeline/` |
| **Impact** | PR gate available; `make test` runs full suite locally |
| **Risk of inaction** | Low — maintain workflow as new tasks are added |

## F2 — Manual-only test execution

| Field | Detail |
|-------|--------|
| **Description** | Each service documents `pytest`, `npm test`, or `cargo test` in its own README; no root orchestration before A4 |
| **Evidence** | Root `README.md` lines 51–60 show only `git add` / `git commit` workflow |
| **File path** | `README.md` |
| **Impact** | Developers must discover and run 8+ test suites individually |
| **Risk** | Medium — easy to skip suites after changes |

## F3 — Inconsistent Python dependency pinning

| Field | Detail |
|-------|--------|
| **Description** | B4/I4 use upper-bound pins; A3 uses open lower bounds only |
| **Evidence** | `beginner/B4-fastapi-service/requirements.txt`: `fastapi>=0.115.0,<1.0.0`; `advanced/A3-polyglot-system/fastapi-service/requirements.txt`: `fastapi>=0.115.0` (no upper bound) |
| **File path** | `beginner/B4-fastapi-service/requirements.txt`, `advanced/A3-polyglot-system/fastapi-service/requirements.txt` |
| **Impact** | Non-reproducible builds across services and over time |
| **Risk** | Medium — surprise breakages on `pip install` |

## F4 — Missing Python lint/format tooling

| Field | Detail |
|-------|--------|
| **Description** | No `ruff`, `flake8`, `black`, or `pyproject.toml` lint config at repo or service level |
| **Evidence** | Root `.gitignore` line 29 lists `.ruff_cache/` but no `ruff.toml` or `[tool.ruff]` exists; `find` returns no `pyproject.toml` |
| **File path** | `.gitignore` (anticipates ruff); no config files |
| **Impact** | No automated style or static analysis for Python services |
| **Risk** | Low–medium — quality drift |

## F5 — Missing Node.js lint scripts

| Field | Detail |
|-------|--------|
| **Description** | Node packages define `test` but no `lint` script |
| **Evidence** | `beginner/B5-nodejs-api-cli/package.json` scripts: `"start"`, `"test"` only; no `eslint` devDependency |
| **File path** | `beginner/B5-nodejs-api-cli/package.json`, `advanced/A3-polyglot-system/node-worker/package.json` |
| **Impact** | No JS static analysis |
| **Risk** | Low |

## F6 — Health endpoint response inconsistency

| Field | Detail |
|-------|--------|
| **Description** | B4/B5 return `{"status":"ok"}`; I4/A3/I5 spec use `{"status":"UP"}` |
| **Evidence** | `beginner/B4-fastapi-service/app/main.py` line 30: `return {"status": "ok"}`; `intermediate/I4-fastapi-node-pair/fastapi-service/app/main.py`: `{"status": "UP"}` |
| **File path** | `beginner/B4-fastapi-service/app/main.py`, `beginner/B5-nodejs-api-cli/src/app.js` |
| **Impact** | Inconsistent ops/monitoring contracts across services |
| **Risk** | Low — functional but confusing for container health checks |

## F7 — Limited containerization coverage

| Field | Detail |
|-------|--------|
| **Description** | Only I4 FastAPI service has a Dockerfile; B4, B5, A3 lack container builds |
| **Evidence** | `find` returns single `intermediate/I5-dockerize/Dockerfile`; `devops/D2-docker-compose/` is `.gitkeep` only |
| **File path** | `intermediate/I5-dockerize/Dockerfile`, `devops/D2-docker-compose/.gitkeep` |
| **Impact** | Most services not deployable via containers without new work |
| **Risk** | Medium for deployment; low for eval scaffold |

## F8 — No structured logging or observability

| Field | Detail |
|-------|--------|
| **Description** | Services use `console.log` (Node) or no request logging (FastAPI); no metrics/tracing |
| **Evidence** | `advanced/A3-polyglot-system/node-worker/src/worker.js` uses `console.log`; FastAPI apps have no logging middleware; `devops/D6-observability/.gitkeep` empty |
| **File path** | `advanced/A3-polyglot-system/node-worker/src/worker.js`, `devops/D6-observability/.gitkeep` |
| **Impact** | Hard to debug production-like failures |
| **Risk** | Medium at scale; low for local eval |

---

# Modernization Opportunities

| # | Opportunity | Business Value | Technical Value | Risk | Effort | Priority |
|---|-------------|:--------------:|:---------------:|:----:|:------:|:--------:|
| 1 | **Add GitHub Actions CI** | 5 | 5 | 1 | 2 | **P1** |
| 2 | Standardize health endpoint responses | 3 | 3 | 2 | 2 | P2 |
| 3 | Add Python linting (ruff) | 3 | 4 | 2 | 2 | P3 |
| 4 | Pin Python deps consistently | 3 | 4 | 2 | 2 | P4 |
| 5 | Add docker-compose for polyglot stack | 4 | 4 | 3 | 4 | P5 |
| 6 | Add Node.js ESLint | 2 | 3 | 2 | 2 | P6 |
| 7 | Add structured logging | 3 | 4 | 3 | 3 | P7 |
| 8 | Add security scanning (pip-audit, npm audit) | 4 | 4 | 2 | 2 | P8 |

See `PRIORITIZATION_MATRIX.md` for full ranking and rationale.

---

# Recommendation Summary

**Implement now (done):** GitHub Actions CI — `.github/workflows/ci.yml` + local mirror `scripts/ci-verify.sh`

**Next recommended:**
1. Standardize `/health` to `{"status":"UP"}` across B4/B5
2. Add `ruff` to Python services with CI lint job
3. Align `requirements.txt` pinning across A3/B4/I4

**Defer:** Full docker-compose, observability stack — higher effort, planned for devops track (D2, D6).

---

# Priority 1 Selection Rationale

| Criterion | CI pipeline assessment |
|-----------|------------------------|
| Highest value | Validates all existing tests on every push/PR |
| Lowest risk | Additive only — no application code changed |
| Smallest effort | One workflow file + verify script |
| Easily verifiable | `bash scripts/ci-verify.sh` mirrors workflow |

---

# Implemented Improvement (Summary)

| Item | Detail |
|------|--------|
| **Files added** | `.github/workflows/ci.yml`, `scripts/ci-verify.sh` |
| **Scope** | Matrix jobs for Python (3), Node (3), Rust (2) services |
| **Verification** | `bash scripts/ci-verify.sh` → exit `0`, 47 tests passed |

Full implementation details in `IMPLEMENTATION_SUMMARY.md`.
