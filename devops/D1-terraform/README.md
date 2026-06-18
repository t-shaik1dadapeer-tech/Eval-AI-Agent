# Task

D1 — Terraform

# Objective

Define AWS infrastructure as code (Lambda and supporting resources).

# Deliverables

- `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, `backend.tf`
- `lambda/` — Python handler
- `docs/TERRAFORM_REPORT.md` — design and usage report

# Status

Completed

# Verification

```bash
cd devops/D1-terraform
terraform init -backend=false
terraform validate
```
