#!/usr/bin/env bash
# I5 — build image, run container, curl health (requires Docker)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
I4_CTX="$ROOT/intermediate/I4-fastapi-node-pair/fastapi-service"
IMAGE="eval-service-i5-verify"
CONTAINER="eval-service-i5-verify"

cleanup() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

command -v docker >/dev/null || { echo "docker not found"; exit 1; }

docker build -f "$ROOT/intermediate/I5-dockerize/Dockerfile" -t "$IMAGE" "$I4_CTX"
docker run -d --name "$CONTAINER" -p 18005:8000 "$IMAGE"

for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:18005/health" | grep -q UP; then
    echo "I5 docker verify: health OK"
    curl -sf "http://127.0.0.1:18005/docs" >/dev/null && echo "I5 docker verify: /docs OK"
    exit 0
  fi
  sleep 1
done

echo "I5 docker verify: health check timed out"
exit 1
