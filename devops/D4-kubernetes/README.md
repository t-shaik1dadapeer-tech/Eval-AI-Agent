# Task

D4 — Kubernetes

# Objective

Kubernetes manifests for deploying the transaction API; local validation workflow.

# Deliverables

- `k8s/` — namespace, deployment, service, ingress, configmap
- `scripts/validate-manifests.sh`, `deploy-and-verify.sh`
- `docs/K8S_REPORT.md`, `VALIDATION_REPORT.md`

# Status

Completed

# Verification

```bash
bash devops/D4-kubernetes/scripts/validate-manifests.sh
```

Optional: kind cluster + `deploy-and-verify.sh` when kubectl context available.
