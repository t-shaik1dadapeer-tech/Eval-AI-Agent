# Passing Run Evidence

**Date:** 2026-06-17  
**Environment:** macOS, Python 3.9.6 (local); workflow targets 3.11/3.12 on `ubuntu-latest`  
**Command:**

```bash
bash devops/D3-ci-pipeline/scripts/run-pipeline-local.sh
```

**Overall exit code:** `0`

---

## Stage 1: Lint

### Commands

```bash
pip install ruff
ruff check .
ruff format --check .
```

### Output

```text
All checks passed!
14 files already formatted
```

### Result

| Step | Exit code |
|------|-----------|
| `ruff check` | 0 |
| `ruff format --check` | 0 |

---

## Stage 2: Test

### Command

```bash
pip install -r requirements.txt
pytest -v
```

### Output (excerpt)

```text
collected 8 items

tests/test_transaction_lookup.py::test_get_transaction_by_id PASSED
tests/test_transaction_lookup.py::test_get_transaction_not_found PASSED
tests/test_transaction_lookup.py::test_get_transaction_invalid_uuid PASSED
tests/test_transactions.py::test_create_transaction PASSED
tests/test_transactions.py::test_get_transactions PASSED
tests/test_transactions.py::test_get_balance PASSED
tests/test_transactions.py::test_invalid_transaction_validation PASSED
tests/test_transactions.py::test_debit_balance_calculation PASSED

======================== 8 passed, 4 warnings in 0.05s =========================
```

### Result

| Metric | Value |
|--------|-------|
| Tests passed | 8 |
| Tests failed | 0 |
| Exit code | 0 |

JUnit XML is uploaded in GitHub Actions as `pytest-results-py{version}` artifacts.

---

## Stage 3: Build

### Commands

```bash
python -m compileall -q app
python -c "from app.main import app; print(f'build_ok title={app.title!r}')"
```

### Output

```text
build_ok title='Transaction Service'
```

### Result

| Step | Exit code |
|------|-----------|
| compileall | 0 |
| import verify | 0 |

---

## Stage 4: Docker Build

### Command (GitHub Actions / local with Docker)

```bash
docker build \
  -t b4-transaction-api:677d449aa9bf07a26e9d579c84830ddae8e71e6d \
  -t b4-transaction-api:latest \
  beginner/B4-fastapi-service
```

### Local result

Docker CLI was not installed in the verification environment. The Dockerfile was validated on disk; the **docker** job in `.github/workflows/d3-ci.yml` runs on `ubuntu-latest` where Docker is pre-installed.

### Expected GitHub Actions evidence

Workflow step **Capture image metadata** writes to the job summary:

```text
Image: b4-transaction-api:<commit-sha>
Image: b4-transaction-api:latest
REPOSITORY           TAG        SIZE
b4-transaction-api   <sha>      ~150MB
b4-transaction-api   latest     ~150MB
```

---

## Workflow YAML validation

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/d3-ci.yml'))"
# YAML valid — exit 0
```
