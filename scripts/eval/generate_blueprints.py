#!/usr/bin/env python3
"""Generate eval_blueprints/*.md from task-registry.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "task-registry.json"
OUT = ROOT / "eval_blueprints"


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    for task in data["tasks"]:
        tid = task["id"]
        deps = task.get("depends_on") or []
        required = [f"{task['folder']}/{r}" for r in task.get("required_files", [])]
        refs = [f"{task['folder']}/{r}" for r in task.get("reference_files", [])]
        body = f"""# {tid} — {task['name']}

## What to do

{task.get('compare_hint', task['name'])}

## Depends on

{', '.join(deps) if deps else 'None — start here'}

## Required deliverables

"""
        for p in required:
            body += f"- `{p}`\n"
        body += f"""
## Reference files (golden examples in this repo)

"""
        for p in refs[:6]:
            body += f"- `{p}`\n"
        body += f"""
## Cursor prompt

Open **docs/AGENT_PROMPTS.md** → section **## {tid} —**

Or run slash command: `/{task.get('skill_slug', tid)}`

## Verify (optional)

"""
        if task.get("verify_command"):
            body += f"```bash\n{task['verify_command']}\n```\n"
        else:
            body += "Review deliverable files manually.\n"
        (OUT / f"{tid}_blueprint.md").write_text(body, encoding="utf-8")
    print(f"Wrote {len(data['tasks'])} blueprints to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
