#!/usr/bin/env bash
# Validate docker-compose.yml syntax without Docker daemon
set -euo pipefail
python3 - <<'PY'
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML not installed; skipping YAML parse")
    sys.exit(0)

path = Path("docker-compose.yml").resolve()
data = yaml.safe_load(path.read_text())
assert "services" in data
for name in ("postgres", "api", "worker"):
    assert name in data["services"], f"missing service: {name}"
print("docker-compose.yml: syntax OK")
print("services:", ", ".join(data["services"].keys()))
PY
