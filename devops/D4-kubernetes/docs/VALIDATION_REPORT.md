# Manifest Validation

**Date:** 2026-06-17  
**Tool:** kubeconform v0.7.0  
**Kubernetes schema version:** 1.29.0

## Command

```bash
bash devops/D4-kubernetes/scripts/validate-manifests.sh
```

## Output

```text
==> Schema validation (kubeconform)
Summary: 5 resources found in 5 files - Valid: 5, Invalid: 0, Errors: 0, Skipped: 0

==> kubectl dry-run skipped (no reachable cluster context)
    Run after: kind create cluster --name eval-cluster

VALIDATION_RESULT: PASS (exit 0)
```

## Result

| File | Resource | Valid |
|------|----------|-------|
| `namespace.yaml` | Namespace | Yes |
| `configmap.yaml` | ConfigMap | Yes |
| `deployment.yaml` | Deployment | Yes |
| `service.yaml` | Service | Yes |
| `ingress.yaml` | Ingress | Yes |

**Exit code:** `0`

## kubectl dry-run (client)

**Command:**

```bash
kubectl apply --dry-run=client -f devops/D4-kubernetes/k8s/
```

**Status:** Not run — requires reachable cluster API (blocked: Docker/kind unavailable).

---

# Cluster Validation

## kind cluster creation

**Command:**

```bash
kind create cluster --name eval-cluster \
  --config devops/D4-kubernetes/kind-config.yaml
```

**Output:**

```text
ERROR: failed to create cluster: failed to get docker info: command "docker info --format '{{json .}}'" failed with error: exec: "docker": executable file not found in $PATH
```

**Exit code:** `1`

**Cluster state:** Not created

**Next step:** Install Docker Desktop → re-run `deploy-and-verify.sh`

---

# Pod Validation

**Status:** Not executed (no cluster).

**Expected checks after deploy:**

```bash
kubectl get pods -n eval-ai-agent
kubectl describe pod -n eval-ai-agent -l app=b4-transaction-api
```

| Check | Expected |
|-------|----------|
| Phase | `Running` |
| Ready | `1/1` per pod |
| Readiness probe | Success on `/health` |
| Liveness probe | Success on `/health` |
| ConfigMap env | `ENVIRONMENT=production` visible in `kubectl describe pod` |

---

# Service Validation

**Status:** Not executed (no cluster).

**Expected:**

```bash
kubectl get svc app-service -n eval-ai-agent
```

| Field | Expected |
|-------|----------|
| Type | `ClusterIP` |
| Port | `80/TCP` |
| Target | Pod port `8000` |
| Selector | `app=b4-transaction-api` |

**Endpoints:** 2 pod IPs when deployment is healthy.

---

# Curl Verification

## Cluster path (not executed)

```bash
kubectl port-forward svc/app-service 8080:80 -n eval-ai-agent
curl -i http://localhost:8080/health
```

**Expected:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"status":"UP"}
```

## Local ConfigMap simulation (executed)

**Command:**

```bash
bash devops/D4-kubernetes/scripts/verify-health-local.sh
```

**Output:**

```text
HTTP_STATUS: 200
RESPONSE: {"status":"UP"}
EXIT_CODE: 0
```

| Metric | Value |
|--------|-------|
| HTTP status | 200 |
| Body | `{"status":"UP"}` |
| Exit code | 0 |

**Environment injected (mirrors ConfigMap):**

| Variable | Value |
|----------|-------|
| `APP_NAME` | `b4-transaction-api` |
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `info` |

---

# Summary

| Validation step | Status | Evidence |
|-----------------|--------|----------|
| Manifest schema (kubeconform) | PASS | 5/5 valid |
| kubectl dry-run | Skipped | No cluster |
| kind cluster | BLOCKED | Docker not installed |
| Pod running | Skipped | No cluster |
| Service created | Skipped | No cluster |
| Curl `/health` | PASS (local) | HTTP 200, `{"status":"UP"}` |
