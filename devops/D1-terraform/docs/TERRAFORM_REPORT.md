# D1 — Terraform Report

**Date:** 2026-06-17  
**Location:** `devops/D1-terraform/`  
**Architecture selected:** **Option A** — API Gateway → Lambda → S3  
**Backend:** Local (`terraform.tfstate`)

---

# Executive Summary

Created a runnable Terraform project for a small AWS serverless health API. All verification commands passed:

| Command | Exit code | Result |
|---------|-----------|--------|
| `terraform fmt -check` | `0` | Formatted |
| `terraform init` | `0` | Initialized |
| `terraform validate` | `0` | Valid |
| `terraform plan` | `0` | **14 resources** to add |

**Terraform version used:** `1.9.8`  
**Primary provider:** `hashicorp/aws` v5.100.0

---

# Architecture

**Option A (AWS Preferred)** selected with **local backend** for state:

```
HTTP Client
    ↓
aws_apigatewayv2_api (GET /health)
    ↓
aws_lambda_function (Python 3.11)
    ↓
aws_s3_bucket (data + Lambda artifacts)
```

**Why Option A:** Matches task recommendation; demonstrates realistic serverless pattern with IAM, S3 hardening, and API Gateway wiring.

**Why local backend:** Enables offline `terraform plan` and evaluation without remote state infrastructure.

---

# Terraform Files

## providers.tf

- `required_version = ">= 1.5.0"`
- Providers: `aws` (~> 5.0), `archive` (~> 2.4), `random` (~> 3.6)
- AWS provider configured with credential skip flags for local `plan`/`validate`

## backend.tf

```hcl
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
```

## variables.tf

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `project_name` | string | — | Project identifier |
| `environment` | string | — | dev/staging/prod/test |
| `region` | string | `us-east-1` | AWS region |
| `lambda_runtime` | string | `python3.11` | Lambda runtime |
| `lambda_handler` | string | `index.handler` | Handler |
| `tags` | map(string) | `{}` | Extra tags |

## outputs.tf

| Output | Description |
|--------|-------------|
| `bucket_name` | S3 bucket name |
| `lambda_name` | Lambda function name |
| `lambda_arn` | Lambda ARN |
| `api_url` | API Gateway invoke URL |
| `api_id` | API Gateway ID |
| `iam_role_name` | Lambda IAM role name |

## main.tf

Defines:

- `random_id` for unique S3 bucket suffix
- S3 bucket with versioning, SSE, public access block
- Lambda package upload (`archive_file` + `aws_s3_object`)
- IAM role and inline policy (S3 + CloudWatch Logs)
- Lambda function (S3-based deployment)
- API Gateway HTTP API, integration, `GET /health` route, stage
- Lambda permission for API Gateway invoke

---

# Validation Results

## terraform fmt -check

**Command:**

```bash
terraform fmt -check -recursive
```

**Output:**

```
(no output — all files formatted)
```

**Exit code:** `0`

---

## terraform init

**Command:**

```bash
terraform init -input=false
```

**Output (excerpt):**

```
Successfully configured the backend "local"!
Initializing provider plugins...
- Installing hashicorp/archive v2.8.0...
- Installing hashicorp/aws v5.100.0...
- Installing hashicorp/random v3.x.x...
Terraform has been successfully initialized!
```

**Exit code:** `0`

---

## terraform validate

**Command:**

```bash
terraform validate
```

**Output:**

```
Success! The configuration is valid.
```

**Exit code:** `0`

---

# Plan Results

**Command:**

```bash
terraform plan -var-file=terraform.tfvars.example -input=false -no-color
```

**Output (summary):**

```
Plan: 14 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + api_id        = (known after apply)
  + api_url       = (known after apply)
  + bucket_name   = (known after apply)
  + iam_role_name = "eval-service-dev-lambda-role"
  + lambda_arn    = (known after apply)
  + lambda_name   = "eval-service-dev-api"
```

**Exit code:** `0`

---

# Resources Planned

| # | Resource type | Name / purpose |
|---|---------------|----------------|
| 1 | `random_id` | `bucket_suffix` |
| 2 | `aws_s3_bucket` | `service_data` |
| 3 | `aws_s3_bucket_versioning` | `service_data` |
| 4 | `aws_s3_bucket_server_side_encryption_configuration` | `service_data` |
| 5 | `aws_s3_bucket_public_access_block` | `service_data` |
| 6 | `aws_s3_object` | `lambda_package` |
| 7 | `aws_iam_role` | `lambda_exec` |
| 8 | `aws_iam_role_policy` | `lambda_exec` |
| 9 | `aws_lambda_function` | `api` |
| 10 | `aws_apigatewayv2_api` | `http` |
| 11 | `aws_apigatewayv2_integration` | `lambda` |
| 12 | `aws_apigatewayv2_route` | `default` (`GET /health`) |
| 13 | `aws_apigatewayv2_stage` | `default` |
| 14 | `aws_lambda_permission` | `apigw` |

**Data sources:** `archive_file.lambda_zip`, `aws_iam_policy_document` (assume role, permissions)

---

# Variables

See `variables.tf` and `terraform.tfvars.example`:

```hcl
project_name = "eval-service"
environment  = "dev"
region       = "us-east-1"
```

---

# Outputs

See `outputs.tf` — six outputs including `bucket_name`, `lambda_name`, `api_url`.

---

# Risk Considerations

| Risk | Mitigation in project |
|------|----------------------|
| **Cost** | Serverless pay-per-use; destroy with `terraform destroy` when done |
| **Security** | S3 public access blocked; SSE enabled; IAM scoped to bucket + logs |
| **State management** | Local state for eval only — document migration to S3 + DynamoDB lock for production |
| **Credentials** | `apply` requires real AWS creds; plan uses skip flags for local verification |
| **Bucket naming** | `random_id` suffix avoids collisions without STS caller identity |

---

# Reproduce verification

```bash
cd devops/D1-terraform
terraform fmt -check -recursive
terraform init -input=false
terraform validate
terraform plan -var-file=terraform.tfvars.example
```

All commands verified on **2026-06-17** with Terraform **v1.9.8**.
