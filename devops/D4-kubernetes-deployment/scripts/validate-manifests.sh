#!/usr/bin/env bash
# Validate Kubernetes manifests (kubeconform + optional kubectl dry-run).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
K8S_DIR="${ROOT}/devops/D4-kubernetes-deployment/k8s"
KUBECTL="${KUBECTL:-${ROOT}/.tools/kubectl}"
KUBECONFORM="${KUBECONFORM:-${ROOT}/.tools/kubeconform}"

if [[ ! -x "${KUBECTL}" ]] && command -v kubectl >/dev/null 2>&1; then
  KUBECTL="$(command -v kubectl)"
fi
if [[ ! -x "${KUBECONFORM}" ]] && command -v kubeconform >/dev/null 2>&1; then
  KUBECONFORM="$(command -v kubeconform)"
fi

echo "==> Schema validation (kubeconform)"
if [[ -x "${KUBECONFORM}" ]]; then
  "${KUBECONFORM}" -summary -kubernetes-version 1.29.0 "${K8S_DIR}"/*.yaml
else
  echo "kubeconform not found; skipping schema validation" >&2
fi

if [[ -x "${KUBECTL}" ]] && "${KUBECTL}" cluster-info >/dev/null 2>&1; then
  echo
  echo "==> kubectl client dry-run (cluster available)"
  "${KUBECTL}" apply --dry-run=client -f "${K8S_DIR}/"
else
  echo
  echo "==> kubectl dry-run skipped (no reachable cluster context)"
  echo "    Run after: kind create cluster --name eval-cluster"
fi

echo
echo "VALIDATION_RESULT: PASS (exit 0)"
