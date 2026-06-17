# Overview

Evaluation task **D3** delivers a reproducible GitHub Actions CI pipeline for the **B4 FastAPI transaction service** (`beginner/B4-fastapi-service`).

The pipeline runs on every **push** and **pull_request** to `main` and executes four gated stages:

1. **Lint** — `ruff check` + `ruff format --check`
2. **Test** — `pytest` (Python 3.11 and 3.12 matrix)
3. **Build** — bytecode compile + import verification
4. **Docker** — build and tag `b4-transaction-api:${{ github.sha }}` and `b4-transaction-api:latest`

**Active workflow (GitHub):** [`.github/workflows/d3-ci.yml`](../../.github/workflows/d3-ci.yml)  
**Deliverable copy:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

# CI Workflow

```text
push / pull_request
        │
        ▼
    ┌───────┐
    │ Lint  │
    └───┬───┘
        ▼
    ┌───────┐
    │ Test  │  matrix: Python 3.11, 3.12
    └───┬───┘
        ▼
    ┌───────┐
    │ Build │
    └───┬───┘
        ▼
    ┌────────┐
    │ Docker │
    └────────┘
```

Jobs use `needs:` so a failure in an earlier stage blocks downstream work.

# Running Locally

## Pipeline simulator (recommended)

```bash
bash devops/D3-ci-pipeline/scripts/run-pipeline-local.sh
```

Runs lint → test → build → docker (if Docker CLI is installed).

## Using act

[nektos/act](https://github.com/nektos/act) replays GitHub Actions locally:

```bash
# Install act (macOS)
brew install act

# Run the D3 workflow on a synthetic push event
act push -W .github/workflows/d3-ci.yml
```

`act` requires Docker. If Docker is unavailable, use the simulator script above.

## Individual stages

```bash
cd beginner/B4-fastapi-service
pip install ruff && ruff check . && ruff format --check .
pip install -r requirements.txt && pytest -v
python -m compileall -q app
python -c "from app.main import app; print(app.title)"
docker build -t b4-transaction-api:local .
```

# Workflow Stages

| Stage | Tooling | Pass criteria |
|-------|---------|---------------|
| Lint | ruff | Zero lint/format violations |
| Test | pytest | All tests pass; JUnit XML uploaded |
| Build | compileall + import | App compiles and imports cleanly |
| Docker | buildx | Image built with SHA + `latest` tags |

# Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ruff check` fails | Style/import/line-length issues | Run `ruff check --fix .` and `ruff format .` |
| `pytest` fails | Regression in transaction logic | Fix tests or application code |
| Docker build fails | Missing `Dockerfile` or bad `requirements.txt` | Verify `beginner/B4-fastapi-service/Dockerfile` |
| Cache stale deps | requirements.txt changed but cache hit | Bump cache key or clear Actions cache |
| `act` fails | No Docker daemon | Start Docker Desktop or use local script |

# Failure Scenarios

Deliberate failures are demonstrated with fixtures (not wired into production code):

```bash
# Lint failure (exit 1)
bash devops/D3-ci-pipeline/scripts/demo-failure.sh lint

# Test failure (exit 1)
bash devops/D3-ci-pipeline/scripts/demo-failure.sh test

# Build failure (exit 1)
bash devops/D3-ci-pipeline/scripts/demo-failure.sh build
```

See [docs/FAILING_RUN.md](docs/FAILING_RUN.md) for captured logs and recovery steps.
