#!/usr/bin/env python3
"""Add depends_on, blueprint, primary_output to task-registry.json (Repo-Analyser aligned)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "task-registry.json"

DEPENDS: dict[str, list[str]] = {
    "B1": [],
    "B2": ["B1"],
    "B3": [],
    "B4": [],
    "B5": ["B4"],
    "B6": [],
    "I1": ["B1"],
    "I2": ["B2"],
    "I3": ["B3"],
    "I4": ["B4", "B5"],
    "I5": [],
    "I6": ["I2"],
    "A1": [],
    "A2": ["A1"],
    "A3": ["B4", "B5", "B6", "I4"],
    "A4": ["B1", "B3"],
    "A5": [],
    "A6": [],
    "D1": [],
    "D2": ["I5"],
    "D3": ["B3", "I5"],
    "D4": ["I5"],
    "D5": ["B3"],
    "D6": ["I5"],
}

SKILL_SLUG: dict[str, str] = {
    "B1": "eval-ai-repo-inventory",
    "B2": "eval-ai-api-endpoint-map",
    "B3": "eval-ai-test-discovery",
    "B4": "eval-ai-fastapi-service",
    "B5": "eval-ai-nodejs-api",
    "B6": "eval-ai-rust-cli",
    "I1": "eval-ai-er-diagram",
    "I2": "eval-ai-flow-trace",
    "I3": "eval-ai-safe-change",
    "I4": "eval-ai-fastapi-node-pair",
    "I5": "eval-ai-dockerize",
    "I6": "eval-ai-bug-diagnosis",
    "A1": "eval-ai-parallel-plan",
    "A2": "eval-ai-parallel-worktrees",
    "A3": "eval-ai-polyglot-system",
    "A4": "eval-ai-modernization",
    "A5": "eval-ai-agent-review",
    "A6": "eval-ai-performance",
    "D1": "eval-ai-terraform",
    "D2": "eval-ai-docker-compose",
    "D3": "eval-ai-ci-pipeline",
    "D4": "eval-ai-kubernetes",
    "D5": "eval-ai-dev-environment",
    "D6": "eval-ai-observability",
}


def primary_output(task: dict) -> str:
    folder = task["folder"]
    for name in task.get("required_files", []):
        if name.endswith(".md"):
            return f"{folder}/{name}"
    for name in task.get("required_files", []):
        return f"{folder}/{name}"
    return f"{folder}/README.md"


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for task in data["tasks"]:
        tid = task["id"]
        task["depends_on"] = DEPENDS.get(tid, [])
        task["blueprint"] = f"eval_blueprints/{tid}_blueprint.md"
        task["skill_slug"] = SKILL_SLUG.get(tid, f"eval-ai-{tid.lower()}")
        task["primary_output"] = primary_output(task)
    data["pipeline_order"] = [
        "B1", "B2", "B3", "B4", "B5", "B6",
        "I1", "I2", "I3", "I4", "I5", "I6",
        "A1", "A2", "A3", "A4", "A5", "A6",
        "D1", "D2", "D3", "D4", "D5", "D6",
    ]
    REGISTRY.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {REGISTRY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
