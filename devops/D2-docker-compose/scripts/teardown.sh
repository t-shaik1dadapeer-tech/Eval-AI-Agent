#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE="${COMPOSE_CMD:-docker compose}"

echo "[teardown] stopping stack and removing volumes"
$COMPOSE down -v --remove-orphans

echo "[teardown] remaining containers (should be none for d2-*)"
docker ps -a --filter "name=d2-" || true

echo "[teardown] complete"
