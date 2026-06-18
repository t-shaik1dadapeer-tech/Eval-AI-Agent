#!/usr/bin/env python3
"""
Eval AI Agent — portfolio verification, compare API, and dashboard generator.

Usage:
  portfolio.py verify [--run-tests] [--run-docker]
  portfolio.py compare TASK_ID [--agent-output PATH]
  portfolio.py dashboard
  portfolio.py serve [--port 8787]
  portfolio.py metrics   # Prometheus text for Grafana
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "task-registry.json"
STATUS_PATH = ROOT / "docs" / "eval-status.json"
DASHBOARD_PATH = ROOT / "docs" / "eval-dashboard.html"


def load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def task_by_id(registry: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    tid = task_id.upper()
    for task in registry["tasks"]:
        if task["id"] == tid:
            return task
    return None


def has_tool(name: str) -> bool:
    if name == "docker":
        return (
            subprocess.run(
                ["bash", "-lc", "command -v docker && docker info >/dev/null 2>&1"],
                cwd=ROOT,
                capture_output=True,
            ).returncode
            == 0
        )
    if name == "terraform":
        return (
            subprocess.run(
                ["bash", "-lc", "command -v mise >/dev/null && mise exec -- terraform version"],
                cwd=ROOT,
                capture_output=True,
            ).returncode
            == 0
        )
    return shutil_which(name)


def shutil_which(cmd: str) -> bool:
    from shutil import which

    return which(cmd) is not None


def check_deliverables(task: dict[str, Any]) -> tuple[bool, list[str]]:
    folder = ROOT / task["folder"]
    missing = []
    for rel in task.get("required_files", []):
        if not (folder / rel).exists():
            missing.append(str(folder / rel))
    return len(missing) == 0, missing


def check_executable(task: dict[str, Any]) -> tuple[bool, str | None]:
    requires = task.get("verify_requires", [])
    for req in requires:
        if not has_tool(req):
            return False, f"requires {req} (not available)"
    if task.get("verify_command") or task.get("type") in ("code", "analysis"):
        return True, None
    if task.get("required_files"):
        return True, None
    return False, "no verify command defined"


def run_verify_command(task: dict[str, Any], timeout: int = 600) -> tuple[bool, str]:
    cmd = task.get("verify_command")
    if not cmd:
        return True, "deliverables only (no command)"
    env = os.environ.copy()
    env["PATH"] = f"{Path.home()}/.local/bin:{Path.home()}/.local/lima/bin:{env.get('PATH', '')}"
    result = subprocess.run(
        ["bash", "-lc", cmd],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    output = (result.stdout or "") + (result.stderr or "")
    tail = output.strip()[-2000:] if output else ""
    return result.returncode == 0, tail or f"exit {result.returncode}"


def score_agent_output(task: dict[str, Any], agent_path: Path | None) -> dict[str, Any]:
    folder = ROOT / task["folder"]
    refs = [folder / r for r in task.get("reference_files", []) if (folder / r).exists()]
    if not refs and task.get("agent_prompt_file"):
        ap = folder / task["agent_prompt_file"]
        if ap.exists():
            refs.append(ap)

    if agent_path is None:
        return {
            "verdict": "reference_only",
            "match_score": None,
            "message": "No agent output provided. Use reference files as ground truth.",
            "reference_files": [str(p.relative_to(ROOT)) for p in refs],
            "suggestion": task.get("compare_hint", ""),
        }

    if not agent_path.exists():
        return {
            "verdict": "error",
            "match_score": 0.0,
            "message": f"Agent output not found: {agent_path}",
            "reference_files": [str(p.relative_to(ROOT)) for p in refs],
            "suggestion": f"Provide output file or align with: {', '.join(task.get('reference_files', [])[:3])}",
        }

    content = agent_path.read_text(encoding="utf-8", errors="replace")
    score = 0.0
    checks: list[str] = []

    if len(content.strip()) > 50:
        score += 0.25
        checks.append("non-empty output")
    if task["id"].lower() in content.lower() or task["name"].lower()[:12] in content.lower():
        score += 0.15
        checks.append("mentions task")

    ref_hits = 0
    for ref in refs:
        name = ref.name
        if name in content or ref.stem.lower() in content.lower():
            ref_hits += 1
    if refs:
        score += 0.3 * min(1.0, ref_hits / len(refs))
        checks.append(f"reference overlap {ref_hits}/{len(refs)}")

    # CSV row count heuristic for B1/B2
    if agent_path.suffix == ".csv" and refs:
        for ref in refs:
            if ref.suffix == ".csv" and ref.exists():
                agent_lines = max(0, len(content.strip().splitlines()) - 1)
                ref_lines = max(0, len(ref.read_text(encoding="utf-8").strip().splitlines()) - 1)
                if ref_lines > 0:
                    ratio = min(agent_lines, ref_lines) / max(agent_lines, ref_lines)
                    score += 0.3 * ratio
                    checks.append(f"csv rows agent={agent_lines} ref={ref_lines}")
                break

    score = min(1.0, score)
    if score >= 0.75:
        verdict = "ok"
        msg = "Agent output aligns reasonably with reference deliverables."
    elif score >= 0.45:
        verdict = "partial"
        msg = "Partial match. Compare against reference files below."
    else:
        verdict = "mismatch"
        msg = "Low similarity to expected deliverables."

    primary = task.get("reference_files", ["README.md"])[0]
    suggestion = (
        f"For exact expected output on {task['id']}, read `{task['folder']}/{primary}` "
        f"and related files: {', '.join(task.get('reference_files', [])[:4])}. "
        f"{task.get('compare_hint', '')}"
    )

    return {
        "verdict": verdict,
        "match_score": round(score, 2),
        "message": msg,
        "checks": checks,
        "reference_files": [str(p.relative_to(ROOT)) for p in refs],
        "suggestion": suggestion.strip(),
    }


def evaluate_task(
    task: dict[str, Any],
    *,
    run_tests: bool = False,
    run_docker: bool = False,
) -> dict[str, Any]:
    deliverables_ok, missing = check_deliverables(task)
    executable, exec_reason = check_executable(task)
    verified = False
    verify_note = "not run"

    if deliverables_ok and run_tests and task.get("verify_command"):
        requires = task.get("verify_requires", [])
        if "docker" in requires and not run_docker:
            verify_note = "skipped (docker tasks need --run-docker)"
        elif not executable:
            verify_note = exec_reason or "not executable"
        else:
            ok, verify_note = run_verify_command(task)
            verified = ok

    status = "completed" if deliverables_ok else "incomplete"
    if deliverables_ok and verified:
        status = "verified"

    return {
        "id": task["id"],
        "name": task["name"],
        "category": task["category"],
        "folder": task["folder"],
        "type": task["type"],
        "status": status,
        "deliverables_ok": deliverables_ok,
        "missing_files": missing,
        "executable": executable,
        "executable_note": exec_reason,
        "verified": verified,
        "verify_note": verify_note,
        "reference_files": [f"{task['folder']}/{r}" for r in task.get("reference_files", [])],
        "agent_prompt_file": (
            f"{task['folder']}/{task['agent_prompt_file']}" if task.get("agent_prompt_file") else None
        ),
    }


def cmd_verify(args: argparse.Namespace) -> int:
    registry = load_registry()
    results = []
    for task in registry["tasks"]:
        results.append(
            evaluate_task(task, run_tests=args.run_tests, run_docker=args.run_docker)
        )

    total = len(results)
    deliverables_ok = sum(1 for r in results if r["deliverables_ok"])
    executable = sum(1 for r in results if r["executable"])
    verified = sum(1 for r in results if r["verified"])

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": total,
            "deliverables_ok": deliverables_ok,
            "executable": executable,
            "verified": verified,
            "completion_pct": round(100 * deliverables_ok / total, 1),
        },
        "tasks": results,
    }
    STATUS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload["summary"], indent=2))
    print(f"\nWrote {STATUS_PATH.relative_to(ROOT)}")
    for r in results:
        if not r["deliverables_ok"]:
            print(f"  MISSING {r['id']}: {r['missing_files']}")
    return 0 if deliverables_ok == total else 1


def cmd_compare(args: argparse.Namespace) -> int:
    registry = load_registry()
    task = task_by_id(registry, args.task_id)
    if not task:
        print(f"Unknown task: {args.task_id}", file=sys.stderr)
        return 1
    agent_path = Path(args.agent_output).resolve() if args.agent_output else None
    result = score_agent_output(task, agent_path)
    out = {
        "task": task["id"],
        "task_name": task["name"],
        "folder": task["folder"],
        **result,
    }
    print(json.dumps(out, indent=2))
    return 0 if result.get("verdict") in ("ok", "reference_only") else 1


def cmd_dashboard(args: argparse.Namespace) -> int:
    if not STATUS_PATH.exists() or args.refresh:
        ns = argparse.Namespace(run_tests=False, run_docker=False)
        cmd_verify(ns)

    data = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    summary = data["summary"]
    tasks = data["tasks"]

    rows = ""
    for t in tasks:
        badge = t["status"]
        color = {"verified": "#22c55e", "completed": "#3b82f6", "incomplete": "#ef4444"}.get(
            badge, "#94a3b8"
        )
        refs = ", ".join(t["reference_files"][:2])
        rows += f"""
        <tr>
          <td><strong>{t['id']}</strong></td>
          <td>{t['name']}</td>
          <td>{t['category']}</td>
          <td><span class="badge" style="background:{color}">{badge}</span></td>
          <td>{'yes' if t['executable'] else 'no'}</td>
          <td>{'yes' if t['deliverables_ok'] else 'no'}</td>
          <td><code>{refs}</code></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Eval AI Agent — Portfolio Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
    h1 {{ color: #f8fafc; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
    .card {{ background: #1e293b; padding: 1rem; border-radius: 8px; text-align: center; }}
    .card .num {{ font-size: 2rem; font-weight: bold; color: #38bdf8; }}
    table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid #334155; }}
    th {{ background: #334155; }}
    code {{ font-size: 0.85em; }}
    .badge {{ padding: 0.2rem 0.5rem; border-radius: 4px; color: #fff; font-size: 0.8rem; }}
    .hint {{ color: #94a3b8; margin-top: 1rem; }}
  </style>
</head>
<body>
  <h1>Eval AI Agent — 24 Task Portfolio</h1>
  <p>Generated: {data.get('generated_at', '')}</p>
  <div class="cards">
    <div class="card"><div class="num">{summary['total']}</div><div>Total tasks</div></div>
    <div class="card"><div class="num">{summary['deliverables_ok']}</div><div>Deliverables OK</div></div>
    <div class="card"><div class="num">{summary['executable']}</div><div>Executable</div></div>
    <div class="card"><div class="num">{summary['verified']}</div><div>Verified (run)</div></div>
    <div class="card"><div class="num">{summary['completion_pct']}%</div><div>Completion</div></div>
  </div>
  <table>
    <thead><tr><th>ID</th><th>Name</th><th>Track</th><th>Status</th><th>Executable</th><th>Deliverables</th><th>Reference docs</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="hint">
    Compare agent output: <code>make eval-compare TASK=I2 AGENT_OUTPUT=./my-trace.md</code><br/>
    Refresh: <code>make eval-dashboard</code> · API: <code>make eval-api</code> ·
    Grafana (D6 service metrics): <code>devops/D6-observability/scripts/start-stack.sh</code>
  </p>
</body>
</html>"""
    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {DASHBOARD_PATH.relative_to(ROOT)}")
    print(f"Open: file://{DASHBOARD_PATH}")
    return 0


def cmd_metrics(_: argparse.Namespace) -> int:
    if not STATUS_PATH.exists():
        cmd_verify(argparse.Namespace(run_tests=False, run_docker=False))
    data = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    s = data["summary"]
    lines = [
        "# HELP eval_tasks_total Total evaluation tasks",
        "# TYPE eval_tasks_total gauge",
        f"eval_tasks_total {s['total']}",
        "# HELP eval_tasks_deliverables_ok Tasks with all required deliverables",
        "# TYPE eval_tasks_deliverables_ok gauge",
        f"eval_tasks_deliverables_ok {s['deliverables_ok']}",
        "# HELP eval_tasks_executable Tasks that can run a verify command",
        "# TYPE eval_tasks_executable gauge",
        f"eval_tasks_executable {s['executable']}",
        "# HELP eval_tasks_verified Tasks verified by last run",
        "# TYPE eval_tasks_verified gauge",
        f"eval_tasks_verified {s['verified']}",
        "# HELP eval_completion_percentage Portfolio completion percent",
        "# TYPE eval_completion_percentage gauge",
        f"eval_completion_percentage {s['completion_pct']}",
    ]
    for t in data["tasks"]:
        val = 1 if t["deliverables_ok"] else 0
        lines.append(f'eval_task_deliverables_ok{{task="{t["id"]}"}} {val}')
    print("\n".join(lines))
    return 0


class EvalAPIHandler(BaseHTTPRequestHandler):
    registry = load_registry()

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path)
        if path.path == "/api/health":
            self._json(200, {"status": "ok"})
            return
        if path.path == "/api/portfolio":
            if STATUS_PATH.exists():
                self._json(200, json.loads(STATUS_PATH.read_text(encoding="utf-8")))
            else:
                self._json(404, {"error": "Run make eval first"})
            return
        if path.path == "/api/tasks":
            self._json(200, {"tasks": self.registry["tasks"]})
            return
        m = re.match(r"^/api/tasks/([A-Za-z0-9]+)$", path.path)
        if m:
            task = task_by_id(self.registry, m.group(1))
            if not task:
                self._json(404, {"error": "unknown task"})
                return
            self._json(200, evaluate_task(task))
            return
        if path.path == "/api/dashboard":
            if DASHBOARD_PATH.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(DASHBOARD_PATH.read_bytes())
            else:
                self._json(404, {"error": "Run make eval-dashboard first"})
            return
        self._json(404, {"error": "not found", "paths": ["/api/portfolio", "/api/tasks", "/api/tasks/B4", "/api/compare/B2?agent_output=path"]})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path)
        m = re.match(r"^/api/compare/([A-Za-z0-9]+)$", path.path)
        if not m:
            self._json(404, {"error": "POST /api/compare/{TASK_ID}?agent_output=..."})
            return
        task = task_by_id(self.registry, m.group(1))
        if not task:
            self._json(404, {"error": "unknown task"})
            return
        qs = parse_qs(path.query)
        agent_out = qs.get("agent_output", [None])[0]
        agent_path = Path(agent_out).resolve() if agent_out else None
        result = score_agent_output(task, agent_path)
        self._json(200, {"task": task["id"], **result})

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"[eval-api] {self.address_string()} - {fmt % args}\n")


def cmd_serve(args: argparse.Namespace) -> int:
    if not STATUS_PATH.exists():
        cmd_verify(argparse.Namespace(run_tests=False, run_docker=False))
    if not DASHBOARD_PATH.exists():
        cmd_dashboard(argparse.Namespace(refresh=False))
    server = HTTPServer((args.host, args.port), EvalAPIHandler)
    print(f"Eval API http://{args.host}:{args.port}")
    print("  GET  /api/portfolio")
    print("  GET  /api/tasks/{id}")
    print("  POST /api/compare/{id}?agent_output=/path/to/file")
    print("  GET  /api/dashboard")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval AI Agent portfolio tools")
    sub = parser.add_subparsers(dest="command", required=True)

    p_verify = sub.add_parser("verify", help="Check deliverables; optional test runs")
    p_verify.add_argument("--run-tests", action="store_true", help="Run verify_command per task")
    p_verify.add_argument("--run-docker", action="store_true", help="Include Docker tasks in --run-tests")

    p_compare = sub.add_parser("compare", help="Compare agent output to reference docs")
    p_compare.add_argument("task_id", help="Task ID e.g. I2, B4")
    p_compare.add_argument("--agent-output", help="Path to agent-produced file")

    p_dash = sub.add_parser("dashboard", help="Generate eval-dashboard.html")
    p_dash.add_argument("--refresh", action="store_true", help="Re-run verify first")

    sub.add_parser("metrics", help="Prometheus metrics text")

    p_serve = sub.add_parser("serve", help="HTTP eval API")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8787)

    args = parser.parse_args()
    handlers = {
        "verify": cmd_verify,
        "compare": cmd_compare,
        "dashboard": cmd_dashboard,
        "metrics": cmd_metrics,
        "serve": cmd_serve,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
