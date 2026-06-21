#!/usr/bin/env python3
"""Install Eval-Ai skills from skills/ into ~/.cursor/skills/."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_SRC = ROOT.parent / "skills"
DEST = Path.home() / ".cursor" / "skills"


def main() -> int:
    if not SKILLS_SRC.exists():
        print("Run: make build-skills first")
        return 1
    DEST.mkdir(parents=True, exist_ok=True)
    count = 0
    for src in sorted(SKILLS_SRC.glob("*.skill.md")):
        # eval-ai-b1: B1_eval-ai-repo-inventory.skill.md -> eval-ai-repo-inventory/SKILL.md
        parts = src.stem.split("_", 1)
        slug = parts[1] if len(parts) > 1 else src.stem
        target_dir = DEST / slug
        target_dir.mkdir(exist_ok=True)
        shutil.copy2(src, target_dir / "SKILL.md")
        count += 1
    print(f"Installed {count} skills to {DEST}")
    print("Restart Cursor, then type / and search eval-ai")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
