#!/usr/bin/env python3
"""Generate docs/PM4_JIRA_SUBTASK_PROMPTS.md from AGENT_PROMPTS + Jira map."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "docs" / "AGENT_PROMPTS.md"
OUTPUT = ROOT / "docs" / "PM4_JIRA_SUBTASK_PROMPTS.md"

JIRA_BASE = "https://paytmmoney.atlassian.net/browse"
GITHUB = "https://github.com/t-shaik1dadapeer-tech/Eval-AI-Agent"
EVAL_PORT = 8788

# Task ID -> Jira subtask under PM4-6626
JIRA_KEYS: dict[str, str] = {
    "B1": "PM4-6627",
    "B2": "PM4-6629",
    "B3": "PM4-6628",
    "B4": "PM4-6630",
    "B5": "PM4-6631",
    "B6": "PM4-6632",
    "I1": "PM4-6633",
    "I2": "PM4-6634",
    "I3": "PM4-6635",
    "I4": "PM4-6636",
    "I5": "PM4-6637",
    "I6": "PM4-6638",
    "A1": "PM4-6640",
    "A2": "PM4-6639",
    "A3": "PM4-6642",
    "A4": "PM4-6641",
    "A5": "PM4-6643",
    "A6": "PM4-6645",
    "D1": "PM4-6644",
    "D2": "PM4-6646",
    "D3": "PM4-6649",
    "D4": "PM4-6647",
    "D5": "PM4-6648",
    "D6": "PM4-6650",
}

JIRA_TITLES: dict[str, str] = {
    "B1": "B1 — Repo Artifact Inventory",
    "B2": "B2 — API Endpoint Map",
    "B3": "B3 — Test Discovery and Execution",
    "B4": "B4 — FastAPI Greenfield Service",
    "B5": "B5 — Node.js Greenfield API or CLI",
    "B6": "B6 — Rust Greenfield",
    "I1": "I1 — ER Diagram from Repo",
    "I2": "I2 — End-to-End Flow Trace",
    "I3": "I3 — Small Safe Change in Unfamiliar Repo",
    "I4": "I4 — Polyglot Service Pair: FastAPI plus Node Client",
    "I5": "I5 — Dockerize and Run",
    "I6": "I6 — Bug Diagnosis with Agent",
    "A1": "A1 — Multi-worktree Parallel Plan",
    "A2": "A2 — Execute Two Parallel Worktrees",
    "A3": "A3 — Polyglot Mini-System: FastAPI, Node Worker, Rust Engine",
    "A4": "A4 — Repository Modernization Plan with Executable First Step",
    "A5": "A5 — Agent Code Review and Adversarial Verification",
    "A6": "A6 — Performance Profiling and Targeted Improvement",
    "D1": "D1 — Terraform Plan for a Small Service",
    "D2": "D2 — docker-compose Stack with End-to-End Tests",
    "D3": "D3 — CI Pipeline that Lints, Tests, and Builds an Image",
    "D4": "D4 — Kubernetes Manifests Verified on a Local Cluster",
    "D5": "D5 — Reproducible Dev Environment from a Fresh Clone",
    "D6": "D6 — Observability Bolt-on with Metrics and a Dashboard",
}

PIPELINE = [
    "B1", "B2", "B3", "B4", "B5", "B6",
    "I1", "I2", "I3", "I4", "I5", "I6",
    "A1", "A2", "A3", "A4", "A5", "A6",
    "D1", "D2", "D3", "D4", "D5", "D6",
]


def extract_task_sections(text: str) -> dict[str, str]:
    """Return task_id -> full markdown section from AGENT_PROMPTS."""
    pattern = re.compile(r"^## ([BIAD][0-9]) — .+$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections: dict[str, str] = {}
    for i, m in enumerate(matches):
        task_id = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else text.find("\n## Quick reference table")
        sections[task_id] = text[start:end].rstrip()
    return sections


def normalize_ports(section: str) -> str:
    return section.replace("127.0.0.1:8787", f"127.0.0.1:{EVAL_PORT}")


def build() -> str:
    source = PROMPTS.read_text(encoding="utf-8")
    sections = extract_task_sections(source)

    lines = [
        "# PM4-6626 — All 24 Jira Subtask Prompts",
        "",
        "Single reference for the **Coding Agent Skill Self-Evaluation** epic and every subtask prompt.",
        "",
        "| Link | URL |",
        "|------|-----|",
        f"| **Jira epic** | [{JIRA_BASE}/PM4-6626]({JIRA_BASE}/PM4-6626) |",
        f"| **GitHub repo** | [{GITHUB}]({GITHUB}) |",
        f"| **Eval dashboard** | `make eval-api` → http://127.0.0.1:{EVAL_PORT} |",
        f"| **Task map** | [`JIRA_TASK_MAP.md`](JIRA_TASK_MAP.md) |",
        f"| **Agent API** | [`AGENT_API.md`](AGENT_API.md) |",
        "",
        "## Pipeline order",
        "",
        " → ".join(PIPELINE),
        "",
        "## Subtask index",
        "",
        "| Task | Jira | Jira title |",
        "|------|------|------------|",
    ]

    for task_id in PIPELINE:
        key = JIRA_KEYS[task_id]
        lines.append(f"| {task_id} | [{key}]({JIRA_BASE}/{key}) | {JIRA_TITLES[task_id]} |")

    lines.extend([
        "",
        "## How to use",
        "",
        "1. Open the Jira subtask for the task you are working on.",
        "2. Copy the **Copy-paste prompt** block from that task section below.",
        "3. Paste into Cursor (or your coding agent) with the repo open.",
        "4. Submit output via eval API or attach the deliverable `.md` to Jira.",
        "",
        "```bash",
        "make eval-api",
        f"curl http://127.0.0.1:{EVAL_PORT}/api/agent/guide/B4",
        "```",
        "",
        "---",
        "",
    ])

    for task_id in PIPELINE:
        key = JIRA_KEYS[task_id]
        section = sections.get(task_id, f"## {task_id} — (missing from AGENT_PROMPTS.md)")
        section = normalize_ports(section)
        lines.append(f"<!-- Jira: {key} -->")
        lines.append("")
        lines.append(f"**Jira:** [{key}]({JIRA_BASE}/{key}) — {JIRA_TITLES[task_id]}  ")
        lines.append(f"**GitHub folder:** `{GITHUB}/tree/main/` + folder from section below")
        lines.append("")
        lines.append(section)
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.extend([
        "## Full portfolio prompt (all 24 tasks)",
        "",
        "Run every subtask in pipeline order:",
        "",
        "```",
        "You are evaluating the Eval-AI-Agent portfolio (24 tasks: B1–B6, I1–I6, A1–A6, D1–D6).",
        "",
        "Setup:",
        f"1. From repo root: make eval-api → http://127.0.0.1:{EVAL_PORT}/",
        "2. For EACH task in order:",
        f"   - GET http://127.0.0.1:{EVAL_PORT}/api/agent/guide/{{TASK_ID}}",
        "   - Complete work in that task folder",
        f"   - POST http://127.0.0.1:{EVAL_PORT}/api/agent/submit with task_id and output_path",
        f"3. Final: GET http://127.0.0.1:{EVAL_PORT}/api/portfolio — report deliverables_ok/24",
        "```",
        "",
        "See also [`AGENT_PROMPTS.md`](AGENT_PROMPTS.md) for the extended version with mismatch hints.",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
