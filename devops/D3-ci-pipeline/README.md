# Task

D3 — CI Pipeline

# Objective

Document and reproduce CI stages: lint, test, build, Docker image.

# Deliverables

- `docs/PIPELINE_REPORT.md`, `PASSING_RUN.md`, `FAILING_RUN.md`
- `scripts/run-pipeline-local.sh` — local pipeline mirror
- Root `.github/workflows/d3-ci.yml` — GitHub Actions workflow

# Status

Completed

# Verification

```bash
bash devops/D3-ci-pipeline/scripts/run-pipeline-local.sh
```

Also covered by root `make test` and `make lint`.
