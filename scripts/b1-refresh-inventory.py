#!/usr/bin/env python3
"""Append test, config, and documentation artifacts to B1 inventory.csv."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "beginner/B1-repo-artifact-inventory/inventory.csv"
SKIP_DIRS = {".git", "node_modules", "target", ".venv", "__pycache__", ".ruff_cache", ".eval", ".tools", ".pytest_cache"}

TEST_PATTERNS = (
    re.compile(r"tests/.+\.py$"),
    re.compile(r"test_.+\.py$"),
    re.compile(r".+\.test\.js$"),
    re.compile(r"tests/.+\.rs$"),
    re.compile(r"conftest\.py$"),
)
CONFIG_PATTERNS = (
    re.compile(r"Makefile$"),
    re.compile(r"mise\.toml$"),
    re.compile(r"pyproject\.toml$"),
    re.compile(r"pytest\.ini$"),
    re.compile(r"requirements\.txt$"),
    re.compile(r"package\.json$"),
    re.compile(r"Cargo\.toml$"),
    re.compile(r"docker-compose\.yml$"),
    re.compile(r"Dockerfile$"),
    re.compile(r"\.github/workflows/.+\.ya?ml$"),
    re.compile(r"\.tf$"),
    re.compile(r"k8s/.+\.ya?ml$"),
    re.compile(r"monitoring/.+\.(ya?ml|json)$"),
)
DOC_PATTERNS = (
    re.compile(r"README\.md$"),
    re.compile(r"REPORT\.md$"),
    re.compile(r".+_REPORT\.md$"),
    re.compile(r"docs/.+\.md$"),
    re.compile(r".+\.mmd$"),
    re.compile(r"AGENT_.+\.md$"),
    re.compile(r"TASK_.+\.md$"),
)


def category_for(path: Path) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    if any(part in SKIP_DIRS for part in path.parts):
        return None
    for pat in TEST_PATTERNS:
        if pat.search(rel):
            return "Tests"
    for pat in CONFIG_PATTERNS:
        if pat.search(rel):
            return "Configuration"
    for pat in DOC_PATTERNS:
        if pat.search(rel):
            return "Documentation"
    return None


def main() -> None:
    existing: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    with OUT.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or [
            "Name",
            "Category",
            "File Path",
            "Purpose",
            "Key Dependencies",
            "Confidence Level",
        ]
        for row in reader:
            existing.append(row)
            seen_paths.add(row["File Path"])

    added = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in seen_paths:
            continue
        cat = category_for(path)
        if not cat:
            continue
        name = path.stem if path.suffix else path.name
        purpose = {
            "Tests": f"Automated test file ({path.suffix or 'file'})",
            "Configuration": "Build, runtime, or infrastructure configuration",
            "Documentation": "Task or project documentation / diagram",
        }[cat]
        existing.append(
            {
                "Name": name,
                "Category": cat,
                "File Path": rel,
                "Purpose": purpose,
                "Key Dependencies": "—",
                "Confidence Level": "Confirmed",
            }
        )
        seen_paths.add(rel)
        added += 1

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing)

    print(f"inventory.csv: {len(existing)} rows (+{added} test/config/doc)")


if __name__ == "__main__":
    main()
