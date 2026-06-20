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
    "B1": "evil-ai-repo-inventory",
    "B2": "evil-ai-api-endpoint-map",
    "B3": "evil-ai-test-discovery",
    "B4": "evil-ai-fastapi-service",
    "B5": "evil-ai-nodejs-api",
    "B6": "evil-ai-rust-cli",
    "I1": "evil-ai-er-diagram",
    "I2": "evil-ai-flow-trace",
    "I3": "evil-ai-safe-change",
    "I4": "evil-ai-fastapi-node-pair",
    "I5": "evil-ai-dockerize",
    "I6": "evil-ai-bug-diagnosis",
    "A1": "evil-ai-parallel-plan",
    "A2": "evil-ai-parallel-worktrees",
    "A3": "evil-ai-polyglot-system",
    "A4": "evil-ai-modernization",
    "A5": "evil-ai-agent-review",
    "A6": "evil-ai-performance",
    "D1": "evil-ai-terraform",
    "D2": "evil-ai-docker-compose",
    "D3": "evil-ai-ci-pipeline",
    "D4": "evil-ai-kubernetes",
    "D5": "evil-ai-dev-environment",
    "D6": "evil-ai-observability",
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
        task["skill_slug"] = SKILL_SLUG.get(tid, f"evil-ai-{tid.lower()}")
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
