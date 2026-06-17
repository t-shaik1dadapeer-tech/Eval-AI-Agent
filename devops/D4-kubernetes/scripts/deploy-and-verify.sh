#!/usr/bin/env bash
# Full D4 flow: kind cluster, image build/load, deploy, verify, curl.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
D4="${ROOT}/devops/D4-kubernetes"
K8S_DIR="${D4}/k8s"
NS="eval-ai-agent"
CLUSTER="eval-cluster"
IMAGE="b4-transaction-api:d4"
SERVICE_DIR="${ROOT}/beginner/B4-fastapi-service"

KUBECTL="${KUBECTL:-${ROOT}/.tools/kubectl}"
KIND="${KIND:-${ROOT}/.tools/kind}"
DOCKER="${DOCKER:-docker}"

log() { printf '\n==> %s\n' "$*"; }

require() {
  if ! command -v "$1" >/dev/null 2>&1 && [[ ! -x "${!2:-}" ]]; then
    echo "Missing required tool: $1" >&2
    exit 1
  fi
}

require docker DOCKER
require kubectl KUBECTL
require kind KIND
require curl

log "Step 1: Validate manifests"
bash "${D4}/scripts/validate-manifests.sh"

log "Step 2: Create kind cluster (if missing)"
if ! "${KIND}" get clusters 2>/dev/null | grep -qx "${CLUSTER}"; then
  "${KIND}" create cluster --name "${CLUSTER}" --config "${D4}/kind-config.yaml"
else
  echo "Cluster ${CLUSTER} already exists"
fi

log "Step 3: Build Docker image"
"${DOCKER}" build -t "${IMAGE}" "${SERVICE_DIR}"

log "Step 4: Load image into kind"
"${KIND}" load docker-image "${IMAGE}" --name "${CLUSTER}"

log "Step 5: Deploy manifests"
"${KUBECTL}" apply -f "${K8S_DIR}/"

log "Step 6: Wait for rollout"
"${KUBECTL}" rollout status deployment/b4-transaction-api -n "${NS}" --timeout=120s

log "Step 7: Resource verification"
"${KUBECTL}" get pods,svc,deployments,configmap -n "${NS}"

POD="$("${KUBECTL}" get pods -n "${NS}" -l app=b4-transaction-api -o jsonpath='{.items[0].metadata.name}')"
log "Step 8: Describe pod ${POD}"
"${KUBECTL}" describe pod "${POD}" -n "${NS}"

log "Step 9: Port-forward and curl /health"
PF_LOG="$(mktemp)"
"${KUBECTL}" port-forward "svc/app-service" 8080:80 -n "${NS}" >"${PF_LOG}" 2>&1 &
PF_PID=$!
trap 'kill ${PF_PID} 2>/dev/null || true' EXIT
sleep 3

HTTP_CODE="$(curl -s -o /tmp/d4-health.json -w '%{http_code}' http://localhost:8080/health)"
BODY="$(cat /tmp/d4-health.json)"
echo "HTTP_STATUS: ${HTTP_CODE}"
echo "RESPONSE: ${BODY}"

if [[ "${HTTP_CODE}" != "200" ]] || [[ "${BODY}" != *'"status":"UP"'* && "${BODY}" != *'"status": "UP"'* ]]; then
  echo "Health check failed" >&2
  exit 1
fi

log "D4 deployment verification complete"
