# Broken Change

This document records **deliberate** failures used to prove the pipeline fails fast and surfaces the correct stage. No production code was left broken.

Fixtures live under `devops/D3-ci-pipeline/fixtures/` and are exercised only by `scripts/demo-failure.sh`.

---

# Failure Trigger

Three independent failure modes were demonstrated:

| Mode | Trigger | Failing stage |
|------|---------|---------------|
| Lint | `fixtures/broken_lint.py` — unused imports, style violations | **Lint** (blocks test/build/docker) |
| Test | `fixtures/broken_test.py` — `assert 1 == 2` | **Test** (blocks build/docker) |
| Build | Temp file with `SyntaxError` | **Build** (blocks docker) |

---

# Pipeline Failure Output

## Lint failure

**Command:**

```bash
bash devops/D3-ci-pipeline/scripts/demo-failure.sh lint
```

**Exit code:** `1`

**Output (excerpt):**

```text
==> FAILURE DEMO: lint violation (broken_lint.py)
E401 Multiple imports on one line
 --> devops/D3-ci-pipeline/fixtures/broken_lint.py:4:1
F401 `os` imported but unused
F401 `sys` imported but unused
F841 Local variable `unused` is assigned to but never used
Found 4 errors.
EXIT_CODE: 1
```

**Stage that failed:** Lint (`ruff check`)

**Reason:** E401/F401/F841 rule violations in intentional fixture.

---

## Test failure

**Command:**

```bash
bash devops/D3-ci-pipeline/scripts/demo-failure.sh test
```

**Exit code:** `1`

**Output (excerpt):**

```text
devops/D3-ci-pipeline/fixtures/broken_test.py::test_intentional_failure FAILED

AssertionError: deliberate failure for CI pipeline demo
assert 1 == 2

FAILED devops/D3-ci-pipeline/fixtures/broken_test.py::test_intentional_failure
============================== 1 failed in 0.06s ===============================
EXIT_CODE: 1
```

**Stage that failed:** Test (`pytest`)

**Reason:** Deliberate assertion failure.

---

## Build failure

**Command:**

```bash
bash devops/D3-ci-pipeline/scripts/demo-failure.sh build
```

**Exit code:** `1`

**Output:**

```text
File ".../bad.py", line 1
    def broken( -> None: pass
                ^
SyntaxError: invalid syntax
EXIT_CODE: 1
```

**Stage that failed:** Build (`python -m py_compile` / compileall equivalent)

**Reason:** Invalid Python syntax prevents compilation.

---

# Expected Failure

In GitHub Actions, when lint fails on `main`:

1. **Lint** job exits non-zero.
2. **Test**, **Build**, and **Docker** jobs are skipped (`needs: lint`).
3. The workflow run is marked **failed** with the lint step highlighted in red.

The same gating applies for test → build → docker.

---

# Recovery

| Failure type | Recovery action |
|--------------|-----------------|
| Lint | Fix ruff violations; run `ruff check --fix .` and `ruff format .` |
| Test | Fix failing assertion or application bug; re-run `pytest -v` |
| Build | Fix syntax/import errors; verify `python -m compileall app` |
| Docker | Fix `Dockerfile` / context; run `docker build` locally |

After recovery, re-run:

```bash
bash devops/D3-ci-pipeline/scripts/run-pipeline-local.sh
```

Expected exit code: **0**.
