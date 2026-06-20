#!/usr/bin/env python3
"""Validate task depends_on graph (no cycles, valid ids)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "task-registry.json"


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids = {t["id"] for t in data["tasks"]}
    graph: dict[str, list[str]] = {t["id"]: list(t.get("depends_on") or []) for t in data["tasks"]}

    errors: list[str] = []
    for tid, deps in graph.items():
        for d in deps:
            if d not in ids:
                errors.append(f"{tid}: unknown dependency {d}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(n: str) -> bool:
        if n in visiting:
            errors.append(f"cycle involving {n}")
            return True
        if n in visited:
            return False
        visiting.add(n)
        for d in graph.get(n, []):
            dfs(d)
        visiting.remove(n)
        visited.add(n)
        return False

    for tid in ids:
        dfs(tid)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    order = data.get("pipeline_order") or sorted(ids)
    print(json.dumps({"valid": True, "task_count": len(ids), "pipeline_order": order}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
