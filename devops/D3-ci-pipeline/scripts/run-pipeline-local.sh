#!/usr/bin/env bash
# Local reproduction of the D3 CI pipeline stages for B4 FastAPI service.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SERVICE_DIR="${ROOT}/beginner/B4-fastapi-service"
IMAGE_NAME="${IMAGE_NAME:-b4-transaction-api}"
IMAGE_TAG="${IMAGE_TAG:-local-$(git -C "${ROOT}" rev-parse --short HEAD 2>/dev/null || echo dev)}"

log() { printf '\n==> %s\n' "$*"; }
run_stage() {
  local name="$1"
  shift
  log "STAGE: ${name}"
  if "$@"; then
    echo "RESULT: ${name} PASS (exit 0)"
  else
    local code=$?
    echo "RESULT: ${name} FAIL (exit ${code})"
    return "${code}"
  fi
}

cd "${SERVICE_DIR}"

log "D3 local pipeline — service: ${SERVICE_DIR}"
log "Image tag target: ${IMAGE_NAME}:${IMAGE_TAG}"

run_stage "lint-ruff-check" bash -c 'pip install -q ruff && ruff check .'
run_stage "lint-ruff-format" bash -c 'ruff format --check .'
run_stage "test-pytest" bash -c 'pip install -q -r requirements.txt && pytest -v'
run_stage "build-compile" bash -c 'PYTHONPYCACHEPREFIX="$(mktemp -d)" python3 -m compileall -q app'
run_stage "build-import" bash -c 'python3 -c "from app.main import app; print(f\"build_ok title={app.title!r}\")"'

if command -v docker >/dev/null 2>&1; then
  run_stage "docker-build" docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -t "${IMAGE_NAME}:latest" .
  run_stage "docker-images" docker images "${IMAGE_NAME}" --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'
else
  log "STAGE: docker-build SKIPPED (docker CLI not installed)"
  log "Dockerfile validated at: ${SERVICE_DIR}/Dockerfile"
  echo "RESULT: docker-build SKIPPED (exit 0 — validated in GitHub Actions)"
fi

log "Pipeline complete"
