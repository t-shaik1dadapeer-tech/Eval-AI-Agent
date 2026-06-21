# D3 — CI Pipeline

## What to do

Local pipeline mirrors GitHub Actions; see PIPELINE_REPORT.md.

## Depends on

B3, I5

## Required deliverables

- `devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md`
- `devops/D3-ci-pipeline/scripts/run-pipeline-local.sh`

## Reference files (golden examples in this repo)

- `devops/D3-ci-pipeline/README.md`
- `devops/D3-ci-pipeline/docs/PIPELINE_REPORT.md`
- `devops/D3-ci-pipeline/scripts/run-pipeline-local.sh`

## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## D3 —**

Or run slash command: `/eval-ai-ci-pipeline`

## Verify (optional)

```bash
bash devops/D3-ci-pipeline/scripts/run-pipeline-local.sh
```
