# D1 — Terraform

## What to do

terraform validate must pass; see TERRAFORM_REPORT.md.

## Depends on

None — start here

## Required deliverables

- `devops/D1-terraform/main.tf`
- `devops/D1-terraform/lambda/index.py`

## Reference files (golden examples in this repo)

- `devops/D1-terraform/README.md`
- `devops/D1-terraform/docs/TERRAFORM_REPORT.md`
- `devops/D1-terraform/main.tf`

## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## D1 —**

Or run slash command: `/eval-ai-terraform`

## Verify (optional)

```bash
cd devops/D1-terraform && mise exec -- terraform init -backend=false -input=false && mise exec -- terraform validate
```
