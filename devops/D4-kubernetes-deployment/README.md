# Overview

Evaluation task **D4** deploys the **B4 FastAPI transaction service** to Kubernetes using plain manifests (no Helm). Resources live in the `eval-ai-agent` namespace and include Namespace, ConfigMap, Deployment (2 replicas), Service (`ClusterIP`), and optional Ingress.

**Manifests:** `devops/D4-kubernetes-deployment/k8s/`  
**Full deploy script:** `scripts/deploy-and-verify.sh` (requires Docker + kind + kubectl)

# Prerequisites

Install:

| Tool | Purpose | Install (macOS) |
|------|---------|-----------------|
| **Docker** | Build image + kind node runtime | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **kubectl** | Apply and inspect manifests | `brew install kubectl` |
| **kind** | Local Kubernetes cluster | `brew install kind` |

Optional offline validators (used in this eval):

```bash
# Repo-local binaries (gitignored under .tools/)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"
curl -LO https://github.com/yannh/kubeconform/releases/download/v0.7.0/kubeconform-darwin-arm64.tar.gz
```

# Validate Manifests

```bash
bash devops/D4-kubernetes-deployment/scripts/validate-manifests.sh
```

Uses **kubeconform** for schema validation. When a cluster context is reachable, also runs `kubectl apply --dry-run=client`.

# Create Cluster

```bash
kind create cluster --name eval-cluster \
  --config devops/D4-kubernetes-deployment/kind-config.yaml
```

# Build and Load Image

```bash
docker build -t b4-transaction-api:d4 beginner/B4-fastapi-service
kind load docker-image b4-transaction-api:d4 --name eval-cluster
```

# Deploy

```bash
kubectl apply -f devops/D4-kubernetes-deployment/k8s/
```

Or run the full automated flow:

```bash
bash devops/D4-kubernetes-deployment/scripts/deploy-and-verify.sh
```

# Verify

```bash
kubectl get all -n eval-ai-agent
kubectl get pods -n eval-ai-agent
kubectl get svc -n eval-ai-agent
kubectl get deployments -n eval-ai-agent
kubectl describe pod -n eval-ai-agent -l app=b4-transaction-api
```

# Port Forward

```bash
kubectl port-forward svc/app-service 8080:80 -n eval-ai-agent
```

# Test

```bash
curl http://localhost:8080/health
```

Expected response (ConfigMap sets `ENVIRONMENT=production`):

```json
{"status":"UP"}
```

**Fallback without cluster** (ConfigMap env simulation):

```bash
bash devops/D4-kubernetes-deployment/scripts/verify-health-local.sh
```

# Cleanup

```bash
kubectl delete -f devops/D4-kubernetes-deployment/k8s/
kind delete cluster --name eval-cluster
```

# Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `ImagePullBackOff` | Image not loaded into kind | `kind load docker-image b4-transaction-api:d4` |
| Probes failing | App not ready | `kubectl logs -n eval-ai-agent -l app=b4-transaction-api` |
| `kind create` fails | Docker not running | Start Docker Desktop |
| `curl` connection refused | Port-forward not running | Re-run `kubectl port-forward` |
| Health returns `ok` not `UP` | `ENVIRONMENT` not set | Verify ConfigMap mounted via `envFrom` |
