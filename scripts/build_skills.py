#!/usr/bin/env python3
"""Build skills/*.skill.md from task-registry + blueprints."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "task-registry.json"
SKILLS = ROOT / "skills"


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    SKILLS.mkdir(exist_ok=True)
    for task in data["tasks"]:
        tid = task["id"]
        slug = task.get("skill_slug", f"eval-ai-{tid.lower()}")
        required = ", ".join(f"`{task['folder']}/{r}`" for r in task.get("required_files", []))
        deps = ", ".join(task.get("depends_on") or []) or "none"
        content = f"""---
name: {slug}
description: Eval-Ai PML task {tid} — {task['name']}
---

# {tid} — {task['name']}

You are running Eval-Ai eval task **{tid}** on the target repository.

## Objective

{task.get('compare_hint', task['name'])}

## Prerequisites

Complete first: {deps}

## Read first

- `{task.get('blueprint', f'eval_blueprints/{tid}_blueprint.md')}`
- `docs/AGENT_PROMPTS.md` (section `{tid}`)

## Deliverables (must exist when done)

{required}

## Primary output

`{task.get('primary_output', task['folder'] + '/README.md')}`

## Work in folder

`{task['folder']}/`

After finishing, run `make eval` to verify files exist.
"""
        path = SKILLS / f"{tid}_{slug.replace('eval-ai-', '')}.skill.md"
        path.write_text(content, encoding="utf-8")
    print(f"Wrote {len(data['tasks'])} skills to {SKILLS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
