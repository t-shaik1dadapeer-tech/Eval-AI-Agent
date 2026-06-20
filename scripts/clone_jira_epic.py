#!/usr/bin/env python3
"""
Clone a Jira parent issue and all its sub-tasks into another project.

Example:
  python3 scripts/clone_jira_epic.py --source PM4-6626 --target-project PMINFRA --dry-run
  python3 scripts/clone_jira_epic.py --source PM4-6626 --target-project PMINFRA
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CURSOR_SCRIPTS = Path.home() / ".cursor" / "scripts"
sys.path.insert(0, str(CURSOR_SCRIPTS))

import create_jira_ticket as cjt  # noqa: E402


def _run_json(cmd: list[str]) -> dict | list:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout)


def _search_subtasks(parent_key: str) -> list[str]:
    data = _run_json([
        "python3",
        str(CURSOR_SCRIPTS / "search_jira_jql.py"),
        "--jql",
        f"parent = {parent_key} ORDER BY key ASC",
        "--max-results",
        "100",
        "--fields",
        "summary",
    ])
    return [issue["key"] for issue in data.get("issues", [])]


def _fetch_issues(keys: list[str]) -> list[dict]:
    if not keys:
        return []
    cmd = ["python3", str(CURSOR_SCRIPTS / "fetch_jira_batch.py"), *keys]
    return _run_json(cmd)


def _rewrite_description(description: str, source_parent: str, target_parent: str) -> str:
    if not description:
        return description
    out = description.replace(source_parent, target_parent)
    out = re.sub(
        r"Part of PM4-\d+ https://paytmmoney\.atlassian\.net/browse/PM4-\d+",
        f"Part of {target_parent} https://paytmmoney.atlassian.net/browse/{target_parent}",
        out,
    )
    return out


def clone_epic(
    source_parent: str,
    target_project: str,
    parent_issue_type: str = "Story",
    subtask_issue_type: str = "Sub-task",
    priority: str = "Medium",
    labels: list[str] | None = None,
    parent_extra_fields: dict | None = None,
    subtask_extra_fields: dict | None = None,
    dry_run: bool = False,
) -> dict:
    cjt._load_credentials()
    verify_ssl = os.environ.get("REQUEST_VERIFY_SSL", "true").lower() not in ("false", "0", "no")

    subtask_keys = _search_subtasks(source_parent)
    parent_data = _fetch_issues([source_parent])[0]
    if parent_data.get("error"):
        raise RuntimeError(parent_data["error"])
    subtasks = _fetch_issues(subtask_keys)

    plan = {
        "source_parent": source_parent,
        "target_project": target_project,
        "parent_summary": parent_data["summary"],
        "subtask_count": len(subtasks),
        "subtasks": [{"source_key": s["key"], "summary": s["summary"]} for s in subtasks],
        "dry_run": dry_run,
    }

    if dry_run:
        return plan

    parent_result = cjt.create_jira_ticket(
        project=target_project,
        summary=parent_data["summary"],
        description=parent_data.get("description") or "",
        issue_type=parent_issue_type,
        priority=priority,
        labels=labels,
        verify_ssl=verify_ssl,
        extra_fields=parent_extra_fields,
    )
    if parent_result.get("error"):
        raise RuntimeError(parent_result["error"])

    target_parent = parent_result["issue_key"]
    created = [{"key": target_parent, "summary": parent_data["summary"], "role": "parent"}]

    for sub in subtasks:
        if sub.get("error"):
            raise RuntimeError(f"{sub.get('key')}: {sub['error']}")
        description = _rewrite_description(
            sub.get("description") or "",
            source_parent,
            target_parent,
        )
        extra_fields = {"parent": {"key": target_parent}}
        if subtask_extra_fields:
            extra_fields.update(subtask_extra_fields)
        result = cjt.create_jira_ticket(
            project=target_project,
            summary=sub["summary"],
            description=description,
            issue_type=subtask_issue_type,
            priority=priority,
            labels=labels,
            verify_ssl=verify_ssl,
            extra_fields=extra_fields,
        )
        if result.get("error"):
            raise RuntimeError(f"{sub['key']} -> {result['error']}")
        created.append(
            {
                "source_key": sub["key"],
                "key": result["issue_key"],
                "url": result["issue_url"],
                "summary": sub["summary"],
                "role": "sub-task",
            }
        )

    return {
        **plan,
        "target_parent": target_parent,
        "target_parent_url": parent_result["issue_url"],
        "created": created,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Clone a Jira epic/story and all sub-tasks")
    parser.add_argument("--source", required=True, help="Source parent issue key, e.g. PM4-6626")
    parser.add_argument("--target-project", required=True, help="Target project key, e.g. PMINFRA")
    parser.add_argument("--parent-issue-type", default="Story")
    parser.add_argument("--subtask-issue-type", default="Sub-task")
    parser.add_argument("--priority", default="Medium")
    parser.add_argument("--labels", help="Comma-separated labels to apply to all created issues")
    parser.add_argument("--parent-fields-file", help="JSON file of extra fields for the parent issue")
    parser.add_argument("--subtask-fields-file", help="JSON file of extra fields for each sub-task")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    labels = [x.strip() for x in args.labels.split(",")] if args.labels else None
    parent_extra_fields = None
    subtask_extra_fields = None
    if args.parent_fields_file:
        with open(args.parent_fields_file, encoding="utf-8") as f:
            parent_extra_fields = json.load(f)
    if args.subtask_fields_file:
        with open(args.subtask_fields_file, encoding="utf-8") as f:
            subtask_extra_fields = json.load(f)
    try:
        result = clone_epic(
            source_parent=args.source.upper(),
            target_project=args.target_project.upper(),
            parent_issue_type=args.parent_issue_type,
            subtask_issue_type=args.subtask_issue_type,
            priority=args.priority,
            labels=labels,
            parent_extra_fields=parent_extra_fields,
            subtask_extra_fields=subtask_extra_fields,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1

    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
