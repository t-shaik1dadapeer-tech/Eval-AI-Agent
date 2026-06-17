#!/usr/bin/env bash
# Demonstrate deliberate CI failure modes for D3 documentation.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SERVICE_DIR="${ROOT}/beginner/B4-fastapi-service"
FIXTURES="${ROOT}/devops/D3-ci-pipeline/fixtures"
MODE="${1:-lint}"

log() { printf '\n==> %s\n' "$*"; }

case "${MODE}" in
  lint)
    log "FAILURE DEMO: lint violation (broken_lint.py)"
    pip install -q ruff
    set +e
    ruff check "${FIXTURES}/broken_lint.py"
    CODE=$?
    set -e
    echo "EXIT_CODE: ${CODE}"
    exit "${CODE}"
    ;;
  test)
    log "FAILURE DEMO: failing pytest (broken_test.py)"
    pip install -q pytest
    set +e
    pytest -v "${FIXTURES}/broken_test.py"
    CODE=$?
    set -e
    echo "EXIT_CODE: ${CODE}"
    exit "${CODE}"
    ;;
  build)
    log "FAILURE DEMO: import error (syntax error in temp module)"
    TMP="$(mktemp -d)"
    trap 'rm -rf "${TMP}"' EXIT
    echo 'def broken( -> None: pass' > "${TMP}/bad.py"
    set +e
    python3 -m py_compile "${TMP}/bad.py"
    CODE=$?
    set -e
    echo "EXIT_CODE: ${CODE}"
    exit "${CODE}"
    ;;
  *)
    echo "Usage: $0 [lint|test|build]" >&2
    exit 2
    ;;
esac
