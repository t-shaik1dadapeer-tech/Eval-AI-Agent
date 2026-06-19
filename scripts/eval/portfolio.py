#!/usr/bin/env python3
"""
Eval AI Agent — portfolio verification, agent compare API, live dashboard.

After clone:  make eval-api  →  http://127.0.0.1:8787

Agents call:
  GET  /api/agent/guide/{TASK}
  POST /api/agent/submit  {"task_id","agent_name","output_path"|"content"}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "task-registry.json"
STATUS_PATH = ROOT / "docs" / "eval-status.json"
DASHBOARD_STATIC = Path(__file__).resolve().parent / "dashboard.html"
EVAL_DIR = ROOT / ".eval"
AGENT_RUNS_PATH = EVAL_DIR / "agent-runs.json"
SUBMISSIONS_DIR = EVAL_DIR / "submissions"
EXTERNAL_TARGET_PATH = EVAL_DIR / "external-target.json"
EXTERNAL_APIS_PATH = EVAL_DIR / "external-apis.json"

# Orchestrator (lazy import in handlers to avoid circular load at CLI startup)
def _orch():
    import orchestrator as orch  # noqa: PLC0415

    return orch

# Related .md files from other tasks when agent/API match fails (suggest on dashboard).
RELATED_MD: dict[str, list[str]] = {
    "B1": ["beginner/B2-api-endpoint-map/API_MAP.md", "beginner/B3-test-discovery/TEST_REPORT.md"],
    "B2": ["beginner/B4-fastapi-service/README.md", "beginner/B5-nodejs-api-cli/README.md"],
    "B3": ["beginner/B4-fastapi-service/tests/", "devops/D5-dev-environment/docs/BOOTSTRAP_VERIFICATION.md"],
    "B4": ["beginner/B2-api-endpoint-map/endpoints.csv", "beginner/B5-nodejs-api-cli/README.md"],
    "B5": ["beginner/B2-api-endpoint-map/endpoints.csv", "beginner/B4-fastapi-service/README.md"],
    "B6": ["beginner/B3-test-discovery/TEST_REPORT.md"],
    "I1": ["beginner/B4-fastapi-service/README.md", "advanced/A3-polyglot-system/docs/ARCHITECTURE.md"],
    "I2": ["beginner/B2-api-endpoint-map/API_MAP.md", "intermediate/I2-end-to-end-trace/FLOW_TRACE.md"],
    "I3": ["intermediate/I6-bug-diagnosis/ROOT_CAUSE_ANALYSIS.md"],
    "I4": ["beginner/B4-fastapi-service/README.md", "beginner/B5-nodejs-api-cli/README.md"],
    "I5": ["devops/D2-docker-compose/docs/STACK_REPORT.md"],
    "I6": ["intermediate/I3-safe-change/CHANGE_REPORT.md"],
    "D6": ["beginner/B2-api-endpoint-map/endpoints.csv", "devops/D6-observability/docs/METRICS_REPORT.md"],
}

DEFAULT_API_PROBE_PATHS = ["/health", "/api/health", "/", "/docs", "/openapi.json"]


def load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def task_by_id(registry: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    tid = task_id.upper()
    for task in registry["tasks"]:
        if task["id"] == tid:
            return task
    return None


def ensure_eval_dir() -> None:
    EVAL_DIR.mkdir(exist_ok=True)
    SUBMISSIONS_DIR.mkdir(exist_ok=True)
    if not AGENT_RUNS_PATH.exists():
        AGENT_RUNS_PATH.write_text('{"runs": []}\n', encoding="utf-8")


def load_agent_runs() -> dict[str, Any]:
    ensure_eval_dir()
    return json.loads(AGENT_RUNS_PATH.read_text(encoding="utf-8"))


def save_agent_run(entry: dict[str, Any]) -> None:
    ensure_eval_dir()
    data = load_agent_runs()
    data["runs"].append(entry)
    AGENT_RUNS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def latest_agent_results() -> dict[str, dict[str, Any]]:
    data = load_agent_runs()
    latest: dict[str, dict[str, Any]] = {}
    for run in data.get("runs", []):
        latest[run["task_id"]] = run
    return latest


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
    from shutil import which

    return which(name) is not None


def check_deliverables(task: dict[str, Any]) -> tuple[bool, list[str]]:
    folder = ROOT / task["folder"]
    missing = []
    for rel in task.get("required_files", []):
        if not (folder / rel).exists():
            missing.append(str((folder / rel).relative_to(ROOT)))
    return len(missing) == 0, missing


def check_executable(task: dict[str, Any]) -> tuple[bool, str | None]:
    requires = task.get("verify_requires", [])
    for req in requires:
        if not has_tool(req):
            return False, f"requires {req} (not available)"
    if task.get("verify_command") or task.get("type") in ("code", "analysis", "report", "infra"):
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


def _rel_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_external_target() -> dict[str, Any]:
    """Legacy single-target read; prefer load_external_apis()."""
    apis = load_external_apis()
    if apis.get("apis"):
        first = apis["apis"][0]
        return {
            "api_base_url": first.get("api_base_url"),
            "project_name": first.get("name"),
            "id": first.get("id"),
            "apis": apis["apis"],
            "default_api_id": apis.get("default_api_id"),
        }
    ensure_eval_dir()
    if EXTERNAL_TARGET_PATH.exists():
        legacy = json.loads(EXTERNAL_TARGET_PATH.read_text(encoding="utf-8"))
        if legacy.get("api_base_url"):
            return legacy
    return {}


def default_external_apis() -> dict[str, Any]:
    return {"apis": [], "default_api_id": None, "updated_at": None}


def load_external_apis() -> dict[str, Any]:
    ensure_eval_dir()
    if EXTERNAL_APIS_PATH.exists():
        data = json.loads(EXTERNAL_APIS_PATH.read_text(encoding="utf-8"))
        data.setdefault("apis", [])
        return data
    if EXTERNAL_TARGET_PATH.exists():
        legacy = json.loads(EXTERNAL_TARGET_PATH.read_text(encoding="utf-8"))
        if legacy.get("api_base_url"):
            migrated = {
                "apis": [
                    {
                        "id": legacy.get("project_name", "default").lower().replace(" ", "-")[:32],
                        "name": legacy.get("project_name") or "external",
                        "api_base_url": legacy["api_base_url"].rstrip("/"),
                    }
                ],
                "default_api_id": None,
                "updated_at": legacy.get("updated_at"),
            }
            save_external_apis(migrated)
            return migrated
    return default_external_apis()


def save_external_apis(data: dict[str, Any]) -> dict[str, Any]:
    ensure_eval_dir()
    data = {**default_external_apis(), **data}
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    for api in data.get("apis", []):
        if api.get("api_base_url"):
            api["api_base_url"] = str(api["api_base_url"]).rstrip("/")
    EXTERNAL_APIS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def save_external_target(data: dict[str, Any]) -> None:
    """Legacy: register as one API in the multi-api store."""
    if data.get("api_base_url"):
        register_external_api(
            data.get("id") or data.get("project_name", "default"),
            data.get("project_name") or "external",
            data["api_base_url"],
        )


def register_external_api(api_id: str, name: str, api_base_url: str) -> dict[str, Any]:
    store = load_external_apis()
    api_id = api_id.strip().lower().replace(" ", "-")
    entry = {"id": api_id, "name": name.strip() or api_id, "api_base_url": api_base_url.rstrip("/")}
    apis = [a for a in store.get("apis", []) if a.get("id") != api_id]
    apis.append(entry)
    store["apis"] = apis
    return save_external_apis(store)


def remove_external_api(api_id: str) -> dict[str, Any]:
    store = load_external_apis()
    api_id = api_id.strip().lower()
    store["apis"] = [a for a in store.get("apis", []) if a.get("id") != api_id]
    if store.get("default_api_id") == api_id:
        store["default_api_id"] = None
    return save_external_apis(store)


def clear_external_apis() -> dict[str, Any]:
    if EXTERNAL_TARGET_PATH.exists():
        EXTERNAL_TARGET_PATH.unlink()
    return save_external_apis(default_external_apis())


def get_external_api(api_id: str) -> dict[str, Any] | None:
    api_id = api_id.strip().lower()
    for api in load_external_apis().get("apis", []):
        if api.get("id") == api_id:
            return api
    return None


def resolve_api_base_url(
    *,
    api_base_url: str | None = None,
    api_id: str | None = None,
    task_id: str | None = None,
    orch_config: dict[str, Any] | None = None,
) -> str | None:
    if api_base_url:
        return api_base_url.rstrip("/")
    store = load_external_apis()
    if api_id:
        found = get_external_api(api_id)
        return found["api_base_url"] if found else None
    cfg = orch_config or {}
    if task_id and cfg.get("task_api_map", {}).get(task_id.upper()):
        found = get_external_api(cfg["task_api_map"][task_id.upper()])
        if found:
            return found["api_base_url"]
    if cfg.get("use_api_for_all_tasks") and cfg.get("default_api_id"):
        found = get_external_api(cfg["default_api_id"])
        if found:
            return found["api_base_url"]
    if cfg.get("default_api_id"):
        found = get_external_api(cfg["default_api_id"])
        if found:
            return found["api_base_url"]
    if store.get("default_api_id"):
        found = get_external_api(store["default_api_id"])
        if found:
            return found["api_base_url"]
    return None


def resolve_md_path(md_path: str | None, task: dict[str, Any] | None) -> Path | None:
    if md_path:
        p = Path(md_path)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        return p if p.exists() else None
    if task:
        folder = ROOT / task["folder"]
        for name in task.get("reference_files", []):
            if name.endswith(".md"):
                candidate = folder / name
                if candidate.exists():
                    return candidate
    return None


def parse_md_api_expectations(content: str, api_base_url: str | None = None) -> list[dict[str, Any]]:
    """Extract HTTP methods/paths and curl targets from markdown text."""
    seen: set[tuple[str, str]] = set()
    endpoints: list[dict[str, Any]] = []

    def add(method: str, path: str, source: str) -> None:
        path = path.split("?")[0].strip()
        if not path.startswith("/") or "*" in path or ".." in path or len(path) > 120:
            return
        key = (method.upper(), path)
        if key in seen:
            return
        seen.add(key)
        endpoints.append({"method": method.upper(), "path": path, "source": source})

    for m in re.finditer(
        r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[\w./\-{}:]+)",
        content,
        re.IGNORECASE,
    ):
        add(m.group(1), m.group(2), "md-method-path")

    for m in re.finditer(r"`(/[\w./\-{}:]+)`", content):
        add("GET", m.group(1), "md-backtick-path")

    for m in re.finditer(r"curl\s+(?:-[A-Za-z]+\s+)*['\"]?(https?://[^\s'\"]+)", content, re.IGNORECASE):
        url = m.group(1).rstrip("'\"")
        parsed = urlparse(url)
        if parsed.path:
            add("GET", parsed.path, "md-curl-url")

    if api_base_url:
        base = urlparse(api_base_url.rstrip("/"))
        for m in re.finditer(r"https?://[^\s`'\"<>]+", content):
            url = m.group(0).rstrip(".,)")
            parsed = urlparse(url)
            if parsed.netloc == base.netloc and parsed.path:
                add("GET", parsed.path, "md-same-host-url")

    if not endpoints:
        for path in DEFAULT_API_PROBE_PATHS:
            add("GET", path, "default-probe")

    return endpoints[:20]


def probe_http_endpoint(
    api_base_url: str,
    method: str,
    path: str,
    timeout: float = 5.0,
) -> dict[str, Any]:
    base = api_base_url.rstrip("/") + "/"
    url = urljoin(base, path.lstrip("/"))
    req = Request(url, method=method.upper(), headers={"Accept": "application/json, */*"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
            return {
                "url": url,
                "method": method.upper(),
                "path": path,
                "status": resp.status,
                "ok": 200 <= resp.status < 300,
                "body_preview": body[:200],
            }
    except HTTPError as exc:
        return {
            "url": url,
            "method": method.upper(),
            "path": path,
            "status": exc.code,
            "ok": 200 <= exc.code < 300,
            "error": str(exc.reason),
        }
    except URLError as exc:
        return {
            "url": url,
            "method": method.upper(),
            "path": path,
            "status": None,
            "ok": False,
            "error": str(exc.reason),
        }


def compare_api_to_md(
    md_content: str,
    api_base_url: str,
    *,
    task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    expectations = parse_md_api_expectations(md_content, api_base_url)
    if task:
        for probe in task.get("api_probes", []):
            expectations.append(
                {
                    "method": probe.get("method", "GET").upper(),
                    "path": probe["path"],
                    "source": "task-registry",
                    "expected_status": probe.get("expected_status"),
                }
            )

    dedup: dict[tuple[str, str], dict[str, Any]] = {}
    for item in expectations:
        dedup[(item["method"], item["path"])] = item
    expectations = list(dedup.values())[:25]

    results = []
    ok_count = 0
    for exp in expectations:
        result = probe_http_endpoint(api_base_url, exp["method"], exp["path"])
        expected = exp.get("expected_status")
        if expected is not None:
            result["ok"] = result.get("status") == expected
        if result["ok"]:
            ok_count += 1
        result["source"] = exp.get("source")
        results.append(result)

    total = len(results) or 1
    score = round(ok_count / total, 2)
    if score >= 0.75:
        verdict, msg = "ok", f"Live API matches {ok_count}/{total} endpoints from .md expectations."
    elif score >= 0.4:
        verdict, msg = "partial", f"Live API partially matches ({ok_count}/{total} endpoints OK)."
    elif ok_count == 0 and all(r.get("status") is None for r in results):
        verdict, msg = "unreachable", f"Could not reach API at {api_base_url}."
    else:
        verdict, msg = "mismatch", f"Live API mismatch ({ok_count}/{total} endpoints OK)."

    md_paths_in_text = re.findall(r"`(/[\w./\-{}:]+)`", md_content)
    tested_paths = {r["path"] for r in results}
    missing_in_api = [p for p in md_paths_in_text if p not in tested_paths][:10]

    return {
        "verdict": verdict,
        "match_score": score,
        "message": msg,
        "api_base_url": api_base_url,
        "endpoints_tested": total,
        "endpoints_ok": ok_count,
        "probes": results,
        "md_endpoints_found": len(parse_md_api_expectations(md_content, api_base_url)),
        "missing_in_api": missing_in_api,
    }


def analyze_md_file(
    md_path: Path,
    api_base_url: str | None,
    task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    content = md_path.read_text(encoding="utf-8", errors="replace")
    out: dict[str, Any] = {
        "md_path": _rel_path(md_path),
        "md_size": len(content),
        "endpoints_in_md": parse_md_api_expectations(content, api_base_url),
        "headings": re.findall(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)[:15],
    }
    if api_base_url:
        out["api_match"] = compare_api_to_md(content, api_base_url, task=task)
    else:
        out["api_match"] = {
            "verdict": "skipped",
            "message": "Provide api_base_url to compare live API against this .md file.",
        }
    if task:
        out["task_id"] = task["id"]
        out["related_md_on_mismatch"] = RELATED_MD.get(task["id"], [])
    return out


def related_suggestions(task: dict[str, Any], md_verdict: str, api_verdict: str | None) -> list[str]:
    if md_verdict in ("ok", "reference_only") and (api_verdict in (None, "ok", "skipped")):
        return []
    related = list(RELATED_MD.get(task["id"], []))
    for ref in task.get("reference_files", []):
        p = f"{task['folder']}/{ref}"
        if p not in related:
            related.insert(0, p)
    return related[:8]


def combine_verdicts(md_result: dict[str, Any], api_result: dict[str, Any] | None) -> dict[str, Any]:
    if not api_result or api_result.get("verdict") in (None, "skipped"):
        return {
            "verdict": md_result.get("verdict"),
            "match_score": md_result.get("match_score"),
            "message": md_result.get("message"),
        }
    md_score = md_result.get("match_score") or 0.0
    api_score = api_result.get("match_score") or 0.0
    combined = round((md_score + api_score) / 2, 2)
    md_v = md_result.get("verdict")
    api_v = api_result.get("verdict")
    if md_v == "ok" and api_v == "ok":
        verdict, msg = "ok", "Agent .md output and live API both match expectations."
    elif md_v in ("ok", "partial") and api_v in ("ok", "partial"):
        verdict, msg = "partial", "Partial match on .md and/or live API — see details and related .md files."
    elif api_v == "unreachable":
        verdict, msg = "partial", "Could not reach live API; .md comparison still available."
    else:
        verdict, msg = "mismatch", "Agent output or live API does not match .md expectations."
    return {"verdict": verdict, "match_score": combined, "message": msg}


def score_agent_output(task: dict[str, Any], agent_path: Path | None) -> dict[str, Any]:
    folder = ROOT / task["folder"]
    refs = [folder / r for r in task.get("reference_files", []) if (folder / r).exists()]
    if task.get("agent_prompt_file"):
        ap = folder / task["agent_prompt_file"]
        if ap.exists() and ap not in refs:
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
            "suggestion": _suggestion_text(task),
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
        if ref.name in content or ref.stem.lower() in content.lower():
            ref_hits += 1
    if refs:
        score += 0.3 * min(1.0, ref_hits / len(refs))
        checks.append(f"reference overlap {ref_hits}/{len(refs)}")

    if agent_path.suffix == ".csv":
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
        verdict, msg = "ok", "Agent output aligns reasonably with reference deliverables."
    elif score >= 0.45:
        verdict, msg = "partial", "Partial match. Compare against reference files below."
    else:
        verdict, msg = "mismatch", "Low similarity to expected deliverables."

    return {
        "verdict": verdict,
        "match_score": round(score, 2),
        "message": msg,
        "checks": checks,
        "reference_files": [str(p.relative_to(ROOT)) for p in refs],
        "suggestion": _suggestion_text(task),
    }


def _suggestion_text(task: dict[str, Any]) -> str:
    primary = task.get("reference_files", ["README.md"])[0]
    refs = ", ".join(f"`{task['folder']}/{r}`" for r in task.get("reference_files", [])[:4])
    return (
        f"For exact expected output on {task['id']}, read `{task['folder']}/{primary}` "
        f"and: {refs}. {task.get('compare_hint', '')}"
    ).strip()


def agent_guide(task: dict[str, Any]) -> dict[str, Any]:
    folder = ROOT / task["folder"]
    refs = [f"{task['folder']}/{r}" for r in task.get("reference_files", [])]
    return {
        "task_id": task["id"],
        "name": task["name"],
        "category": task["category"],
        "folder": task["folder"],
        "type": task["type"],
        "objective": task.get("compare_hint", task["name"]),
        "reference_files": refs,
        "required_files": [f"{task['folder']}/{r}" for r in task.get("required_files", [])],
        "agent_prompt_file": (
            f"{task['folder']}/{task['agent_prompt_file']}" if task.get("agent_prompt_file") else None
        ),
        "verify_command": task.get("verify_command"),
        "verify_requires": task.get("verify_requires", []),
        "instructions": [
            f"1. Read reference files in `{task['folder']}/` (especially {refs[0] if refs else 'README.md'}).",
            f"2. Complete work for task {task['id']} in `{task['folder']}/` (or your external project).",
            "3. POST to /api/agent/submit with task_id, output_path or content.",
            "4. Optional: add api_base_url (your running API, e.g. http://127.0.0.1:3000) to compare .md vs live API.",
            "5. Open dashboard / to see agent + API match columns.",
        ],
        "external_api": {
            "analyze": "POST /api/external/analyze  {md_path, api_base_url, task_id?}",
            "set_target": "POST /api/external/target  {api_base_url, project_name?}",
            "submit_with_api": {
                "task_id": task["id"],
                "agent_name": "cursor",
                "output_path": f"{task['folder']}/{task.get('reference_files', ['README.md'])[0]}",
                "api_base_url": "http://127.0.0.1:YOUR_PORT",
            },
        },
        "related_md_on_mismatch": RELATED_MD.get(task["id"], []),
    }


def evaluate_task(
    task: dict[str, Any],
    *,
    run_tests: bool = False,
    run_docker: bool = False,
    agent_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    deliverables_ok, missing = check_deliverables(task)
    executable, exec_reason = check_executable(task)
    verified = False
    verify_note = "not run"

    if deliverables_ok and run_tests and task.get("verify_command"):
        requires = task.get("verify_requires", [])
        if "docker" in requires and not run_docker:
            verify_note = "skipped (docker tasks need run_tests + docker available)"
        elif not executable:
            verify_note = exec_reason or "not executable"
        else:
            ok, verify_note = run_verify_command(task)
            verified = ok

    status = "completed" if deliverables_ok else "incomplete"
    if deliverables_ok and verified:
        status = "verified"

    out = {
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
    if agent_result:
        out["agent_result"] = {
            "verdict": agent_result.get("verdict"),
            "match_score": agent_result.get("match_score"),
            "message": agent_result.get("message"),
            "suggestion": agent_result.get("suggestion"),
            "agent_name": agent_result.get("agent_name"),
            "submitted_at": agent_result.get("submitted_at"),
            "output_path": agent_result.get("output_path"),
            "md_verdict": agent_result.get("md_verdict"),
            "api_match": agent_result.get("api_match"),
            "api_base_url": agent_result.get("api_base_url"),
            "related_md": agent_result.get("related_md"),
            "combined_verdict": agent_result.get("combined_verdict"),
        }
    bot = _orch().bot_status_for_task(task["id"])
    if bot:
        out["bot"] = bot
    return out


def build_portfolio(*, run_tests: bool = False, run_docker: bool = False) -> dict[str, Any]:
    registry = load_registry()
    latest = latest_agent_results()
    results = []
    for task in registry["tasks"]:
        ar = latest.get(task["id"])
        results.append(
            evaluate_task(task, run_tests=run_tests, run_docker=run_docker, agent_result=ar)
        )

    total = len(results)
    deliverables_ok = sum(1 for r in results if r["deliverables_ok"])
    executable = sum(1 for r in results if r["executable"])
    verified = sum(1 for r in results if r["verified"])
    agent_evaluated = sum(1 for r in results if r.get("agent_result", {}).get("verdict") not in (None, "reference_only"))
    agent_ok = sum(1 for r in results if r.get("agent_result", {}).get("verdict") == "ok")
    api_checked = sum(
        1
        for r in results
        if ((r.get("agent_result") or {}).get("api_match") or {}).get("verdict") not in (None, "skipped")
    )
    api_ok = sum(1 for r in results if ((r.get("agent_result") or {}).get("api_match") or {}).get("verdict") == "ok")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "external_apis": load_external_apis(),
        "external_target": load_external_target(),
        "orchestrator": _orch().orchestrator_status(),
        "summary": {
            "total": total,
            "deliverables_ok": deliverables_ok,
            "executable": executable,
            "verified": verified,
            "agent_evaluated": agent_evaluated,
            "agent_ok": agent_ok,
            "api_checked": api_checked,
            "api_ok": api_ok,
            "completion_pct": round(100 * deliverables_ok / total, 1),
        },
        "tasks": results,
    }


def resolve_output_path(task: dict[str, Any], output_path: str | None, content: str | None) -> Path:
    if content is not None:
        ensure_eval_dir()
        fname = SUBMISSIONS_DIR / f"{task['id']}-{uuid.uuid4().hex[:8]}.txt"
        fname.write_text(content, encoding="utf-8")
        return fname
    if not output_path:
        raise ValueError("Provide output_path or content")
    p = Path(output_path)
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    return p


def submit_agent_output(
    task: dict[str, Any],
    *,
    agent_name: str | None,
    output_path: str | None,
    content: str | None,
    api_base_url: str | None = None,
    md_path: str | None = None,
    api_id: str | None = None,
) -> dict[str, Any]:
    path = resolve_output_path(task, output_path, content)
    md_result = score_agent_output(task, path)

    try:
        orch_cfg = _orch().load_config()
    except Exception:
        orch_cfg = {}
    base = resolve_api_base_url(
        api_base_url=api_base_url,
        api_id=api_id,
        task_id=task["id"],
        orch_config=orch_cfg,
    )

    api_result: dict[str, Any] | None = None
    md_for_api = resolve_md_path(md_path, task)
    if base:
        chunks: list[str] = []
        if md_for_api and md_for_api.exists():
            chunks.append(md_for_api.read_text(encoding="utf-8", errors="replace"))
        if path.exists() and path.suffix == ".md":
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        folder = ROOT / task["folder"]
        for ref in task.get("reference_files", []):
            if ref.endswith(".md"):
                rp = folder / ref
                if rp.exists():
                    chunks.append(rp.read_text(encoding="utf-8", errors="replace"))
        merged_md = "\n\n".join(chunks) if chunks else ""
        if merged_md.strip():
            api_result = compare_api_to_md(merged_md, base.rstrip("/"), task=task)
        else:
            api_result = {
                "verdict": "skipped",
                "message": "No .md content found to compare against API.",
                "api_base_url": base,
            }

    combined = combine_verdicts(md_result, api_result)
    related = related_suggestions(
        task,
        md_result.get("verdict", "mismatch"),
        api_result.get("verdict") if api_result else None,
    )
    suggestion = md_result.get("suggestion", "")
    if related and combined["verdict"] != "ok":
        suggestion += " Related .md files: " + ", ".join(f"`{r}`" for r in related)

    result = {
        **md_result,
        "md_verdict": md_result.get("verdict"),
        "md_match_score": md_result.get("match_score"),
        "verdict": combined["verdict"],
        "match_score": combined["match_score"],
        "message": combined["message"],
        "api_match": api_result,
        "api_base_url": base,
        "related_md": related,
        "combined_verdict": combined["verdict"],
        "suggestion": suggestion.strip(),
    }
    entry = {
        "task_id": task["id"],
        "agent_name": agent_name or "unknown",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "output_path": _rel_path(path),
        **result,
    }
    save_agent_run(entry)
    return {"task": task["id"], "task_name": task["name"], "folder": task["folder"], **result}


def api_docs() -> dict[str, Any]:
    return {
        "title": "Eval AI Agent API",
        "dashboard": "/",
        "workflow": [
            "1. git clone repo && cd Evil-Ai",
            "2. python3 scripts/eval/portfolio.py serve --port 8788",
            "3. Start YOUR API (any project) e.g. http://127.0.0.1:3000",
            "4. POST /api/external/target  {api_base_url}  — save your API for this session",
            "5. GET /api/agent/guide/{TASK}  — read reference .md before working",
            "6. POST /api/agent/submit  — include api_base_url to compare .md + live API",
            "7. POST /api/external/analyze  — analyze any .md file vs your API",
            "8. Open /  — dashboard shows agent eval + API match + related .md suggestions",
            "9. POST /api/orchestrator/run  {task_id} or {mode:all}  — run verify bots",
            "10. GET /api/orchestrator/status  — bot run state for all 24",
        ],
        "endpoints": [
            "GET  /",
            "GET  /api/health",
            "GET  /api/docs",
            "GET  /api/portfolio",
            "GET  /api/tasks",
            "GET  /api/tasks/{id}",
            "GET  /api/agent/guide/{id}",
            "GET  /api/external/apis",
            "GET  /api/external/target",
            "POST /api/external/register",
            "POST /api/external/target",
            "POST /api/external/clear",
            "DELETE /api/external/apis/{id}",
            "POST /api/external/analyze",
            "POST /api/agent/submit",
            "POST /api/agent/compare/{id}",
            "POST /api/portfolio/refresh",
            "GET  /api/orchestrator/status",
            "GET  /api/orchestrator/config",
            "POST /api/orchestrator/config",
            "POST /api/orchestrator/run",
            "GET  /api/metrics",
        ],
        "submit_example": {
            "task_id": "B3",
            "agent_name": "cursor",
            "output_path": "beginner/B3-test-discovery/TEST_REPORT.md",
            "api_base_url": "http://127.0.0.1:3000",
        },
        "analyze_example": {
            "md_path": "docs/AGENT_PROMPTS.md",
            "api_base_url": "http://127.0.0.1:3000",
            "task_id": "B3",
        },
        "docs_files": ["docs/AGENT_API.md", "docs/EXTERNAL_EVAL.md", "docs/ORCHESTRATOR.md", "docs/AGENT_PROMPTS.md"],
        "orchestrator_run_single": {"task_id": "B3", "api_id": "my-dev-api"},
        "orchestrator_run_all": {"mode": "all", "default_api_id": "my-dev-api"},
        "register_api_example": {"id": "my-dev-api", "name": "My Dev API", "api_base_url": "http://127.0.0.1:9000"},
        "multi_api_config_example": {
            "apis": [
                {"id": "home-api", "name": "Home API", "api_base_url": "http://127.0.0.1:9000"},
                {"id": "billing-api", "name": "Billing API", "api_base_url": "http://127.0.0.1:9001"},
            ],
            "default_api_id": "home-api",
            "task_api_map": {"B2": "home-api", "B3": "billing-api"},
            "use_api_for_all_tasks": False,
        },
    }


def cmd_verify(args: argparse.Namespace) -> int:
    payload = build_portfolio(run_tests=args.run_tests, run_docker=args.run_docker)
    STATUS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print(f"\nWrote {STATUS_PATH.relative_to(ROOT)}")
    for r in payload["tasks"]:
        if not r["deliverables_ok"]:
            print(f"  MISSING {r['id']}: {r['missing_files']}")
    return 0 if payload["summary"]["deliverables_ok"] == payload["summary"]["total"] else 1


def cmd_compare(args: argparse.Namespace) -> int:
    registry = load_registry()
    task = task_by_id(registry, args.task_id)
    if not task:
        print(f"Unknown task: {args.task_id}", file=sys.stderr)
        return 1
    if args.agent_output:
        out = submit_agent_output(
            task,
            agent_name=args.agent_name,
            output_path=args.agent_output,
            content=None,
            api_base_url=getattr(args, "api_base_url", None),
        )
    else:
        out = score_agent_output(task, None)
        out = {"task": task["id"], "task_name": task["name"], "folder": task["folder"], **out}
    print(json.dumps(out, indent=2))
    return 0 if out.get("verdict") in ("ok", "reference_only") else 1


def cmd_bot(args: argparse.Namespace) -> int:
    orch = _orch()
    overrides: dict[str, Any] = {}
    if getattr(args, "api_id", None):
        overrides["api_id"] = args.api_id
    if getattr(args, "api_base_url", None):
        overrides["api_base_url"] = args.api_base_url
    if getattr(args, "run_tests", False):
        overrides["run_tests"] = True
    result = orch.run_orchestrator(task_id=args.task_id, config_overrides=overrides or None)
    print(json.dumps(result, indent=2))
    return 0 if result["summary"].get("failed", 0) == 0 else 1


def cmd_bots_all(args: argparse.Namespace) -> int:
    orch = _orch()
    overrides: dict[str, Any] = {}
    if getattr(args, "api_id", None):
        overrides["default_api_id"] = args.api_id
        overrides["use_api_for_all_tasks"] = True
    if getattr(args, "api_base_url", None):
        overrides["api_base_url"] = args.api_base_url
    if getattr(args, "run_tests", False):
        overrides["run_tests"] = True
    result = orch.run_orchestrator(mode="all", config_overrides=overrides or None)
    print(json.dumps(result, indent=2))
    s = result["summary"]
    print(f"\nBots done: {s['done']}/{s['total']}  verdict_ok: {s['verdict_ok']}")
    return 0 if s.get("failed", 0) == 0 else 1


def cmd_orchestrator_config(args: argparse.Namespace) -> int:
    orch = _orch()
    if args.api_base_url or args.api_id:
        payload: dict[str, Any] = {}
        if args.api_id and args.api_base_url:
            payload["apis"] = [
                {
                    "id": args.api_id,
                    "name": args.project_name or args.api_id,
                    "api_base_url": args.api_base_url,
                }
            ]
            payload["default_api_id"] = args.api_id
        elif args.api_base_url:
            payload["apis"] = [
                {
                    "id": (args.project_name or "my-api").lower().replace(" ", "-"),
                    "name": args.project_name or "my-api",
                    "api_base_url": args.api_base_url,
                }
            ]
            payload["default_api_id"] = payload["apis"][0]["id"]
        cfg = orch.save_config(payload)
    else:
        cfg = orch.load_config()
    apis = load_external_apis()
    print(json.dumps({**cfg, "registered_apis": apis.get("apis", [])}, indent=2))
    return 0


def cmd_dashboard(_: argparse.Namespace) -> int:
    print("Live dashboard is served by: make eval-api")
    print("Static template: scripts/eval/dashboard.html")
    print("Open: http://127.0.0.1:8788/")
    return 0


def cmd_metrics(_: argparse.Namespace) -> int:
    payload = build_portfolio()
    s = payload["summary"]
    lines = [
        "# HELP eval_tasks_total Total evaluation tasks",
        "# TYPE eval_tasks_total gauge",
        f"eval_tasks_total {s['total']}",
        "# HELP eval_tasks_deliverables_ok Tasks with deliverables present",
        "# TYPE eval_tasks_deliverables_ok gauge",
        f"eval_tasks_deliverables_ok {s['deliverables_ok']}",
        "# HELP eval_tasks_agent_ok Agent submissions scored ok",
        "# TYPE eval_tasks_agent_ok gauge",
        f"eval_tasks_agent_ok {s.get('agent_ok', 0)}",
        "# HELP eval_completion_percentage Repo completion percent",
        "# TYPE eval_completion_percentage gauge",
        f"eval_completion_percentage {s['completion_pct']}",
    ]
    print("\n".join(lines))
    return 0


class EvalAPIHandler(BaseHTTPRequestHandler):
    registry = load_registry()

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw.strip() else {}

    def _html_file(self, path: Path) -> None:
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path)
        qs = parse_qs(path.query)

        if path.path in ("/", "/dashboard"):
            self._html_file(DASHBOARD_STATIC)
            return
        if path.path == "/api/health":
            self._json(200, {"status": "ok", "repo": str(ROOT)})
            return
        if path.path == "/api/docs":
            self._json(200, api_docs())
            return
        if path.path == "/api/portfolio":
            run_tests = qs.get("run_tests", ["0"])[0] in ("1", "true", "yes")
            payload = build_portfolio(run_tests=run_tests, run_docker=run_tests)
            self._json(200, payload)
            return
        if path.path == "/api/tasks":
            self._json(200, {"tasks": self.registry["tasks"]})
            return
        if path.path == "/api/metrics":
            import io
            from contextlib import redirect_stdout

            buf = io.StringIO()
            with redirect_stdout(buf):
                cmd_metrics(argparse.Namespace())
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self._cors()
            self.end_headers()
            self.wfile.write(buf.getvalue().encode("utf-8"))
            return

        if path.path in ("/api/external/target", "/api/external/apis"):
            self._json(200, load_external_apis())
            return

        if path.path == "/api/orchestrator/status":
            self._json(200, _orch().orchestrator_status())
            return

        if path.path == "/api/orchestrator/config":
            self._json(200, _orch().load_config())
            return

        m = re.match(r"^/api/tasks/([A-Za-z0-9]+)$", path.path)
        if m:
            task = task_by_id(self.registry, m.group(1))
            if not task:
                self._json(404, {"error": "unknown task"})
                return
            latest = latest_agent_results().get(task["id"])
            self._json(200, evaluate_task(task, agent_result=latest))
            return

        m = re.match(r"^/api/agent/guide/([A-Za-z0-9]+)$", path.path)
        if m:
            task = task_by_id(self.registry, m.group(1))
            if not task:
                self._json(404, {"error": "unknown task", "hint": "Use B1-D6, I1-I6, A1-A6"})
                return
            self._json(200, agent_guide(task))
            return

        self._json(404, {"error": "not found", "see": "/api/docs"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path)
        qs = parse_qs(path.query)

        if path.path == "/api/portfolio/refresh":
            payload = build_portfolio()
            STATUS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            self._json(200, payload)
            return

        if path.path == "/api/agent/submit":
            try:
                body = self._read_json_body()
                task = task_by_id(self.registry, body.get("task_id", ""))
                if not task:
                    self._json(400, {"error": "unknown task_id", "example": api_docs()["submit_example"]})
                    return
                result = submit_agent_output(
                    task,
                    agent_name=body.get("agent_name"),
                    output_path=body.get("output_path"),
                    content=body.get("content"),
                    api_base_url=body.get("api_base_url"),
                    api_id=body.get("api_id"),
                    md_path=body.get("md_path"),
                )
                self._json(200, result)
            except (json.JSONDecodeError, ValueError) as exc:
                self._json(400, {"error": str(exc)})
            return

        if path.path == "/api/external/target":
            try:
                body = self._read_json_body()
                url = body.get("api_base_url", "").strip()
                if not url:
                    self._json(400, {"error": "api_base_url required"})
                    return
                api_id = body.get("id") or body.get("project_name", "default")
                name = body.get("name") or body.get("project_name") or api_id
                data = register_external_api(api_id, name, url)
                self._json(200, data)
            except json.JSONDecodeError as exc:
                self._json(400, {"error": str(exc)})
            return

        if path.path == "/api/external/register":
            try:
                body = self._read_json_body()
                api_id = body.get("id", "").strip()
                url = body.get("api_base_url", "").strip()
                if not api_id or not url:
                    self._json(400, {"error": "id and api_base_url required"})
                    return
                data = register_external_api(api_id, body.get("name", api_id), url)
                if body.get("default"):
                    store = load_external_apis()
                    store["default_api_id"] = api_id.lower()
                    data = save_external_apis(store)
                self._json(200, data)
            except json.JSONDecodeError as exc:
                self._json(400, {"error": str(exc)})
            return

        if path.path == "/api/external/clear":
            self._json(200, clear_external_apis())
            return

        if path.path == "/api/external/analyze":
            try:
                body = self._read_json_body()
                md_raw = body.get("md_path", "").strip()
                if not md_raw:
                    self._json(400, {"error": "md_path required"})
                    return
                md_p = Path(md_raw)
                if not md_p.is_absolute():
                    md_p = (ROOT / md_p).resolve()
                if not md_p.exists():
                    self._json(404, {"error": f"md file not found: {md_raw}"})
                    return
                task = None
                if body.get("task_id"):
                    task = task_by_id(self.registry, body["task_id"])
                try:
                    orch_cfg = _orch().load_config()
                except Exception:
                    orch_cfg = {}
                url = resolve_api_base_url(
                    api_base_url=body.get("api_base_url"),
                    api_id=body.get("api_id"),
                    task_id=body.get("task_id"),
                    orch_config=orch_cfg,
                )
                result = analyze_md_file(md_p, url, task=task)
                if task and result.get("api_match", {}).get("verdict") not in ("ok", "skipped"):
                    result["related_md"] = related_suggestions(
                        task,
                        "partial",
                        result.get("api_match", {}).get("verdict"),
                    )
                self._json(200, result)
            except json.JSONDecodeError as exc:
                self._json(400, {"error": str(exc)})
            return

        if path.path == "/api/orchestrator/config":
            try:
                body = self._read_json_body()
                cfg = _orch().save_config(body)
                self._json(200, cfg)
            except json.JSONDecodeError as exc:
                self._json(400, {"error": str(exc)})
            return

        if path.path == "/api/orchestrator/run":
            try:
                body = self._read_json_body()
                overrides: dict[str, Any] = {}
                if body.get("api_base_url"):
                    overrides["api_base_url"] = body["api_base_url"]
                if body.get("project_name"):
                    overrides["project_name"] = body["project_name"]
                if "run_tests" in body:
                    overrides["run_tests"] = bool(body["run_tests"])
                if body.get("output_map"):
                    overrides["output_map"] = body["output_map"]
                if body.get("task_api_map"):
                    overrides["task_api_map"] = body["task_api_map"]
                if body.get("default_api_id"):
                    overrides["default_api_id"] = body["default_api_id"]
                if body.get("apis"):
                    overrides["apis"] = body["apis"]
                if body.get("api_id"):
                    overrides["api_id"] = body["api_id"]
                if body.get("api_base_url"):
                    overrides["api_base_url"] = body["api_base_url"]
                if body.get("mode") == "all":
                    result = _orch().run_orchestrator(mode="all", config_overrides=overrides or None)
                elif body.get("task_id"):
                    result = _orch().run_orchestrator(
                        task_id=body["task_id"],
                        config_overrides=overrides or None,
                    )
                else:
                    self._json(400, {"error": "Provide task_id or mode=all", "examples": api_docs()["orchestrator_run_all"]})
                    return
                self._json(200, result)
            except (json.JSONDecodeError, ValueError) as exc:
                self._json(400, {"error": str(exc)})
            return

        m = re.match(r"^/api/agent/compare/([A-Za-z0-9]+)$", path.path)
        if m:
            task = task_by_id(self.registry, m.group(1))
            if not task:
                self._json(404, {"error": "unknown task"})
                return
            try:
                body = self._read_json_body()
                agent_out = body.get("output_path") or qs.get("agent_output", [None])[0]
                content = body.get("content")
                if agent_out or content:
                    result = submit_agent_output(
                        task,
                        agent_name=body.get("agent_name"),
                        output_path=agent_out,
                        content=content,
                        api_base_url=body.get("api_base_url"),
                        md_path=body.get("md_path"),
                    )
                else:
                    result = score_agent_output(task, None)
                    result = {"task": task["id"], **result}
                self._json(200, result)
            except (json.JSONDecodeError, ValueError) as exc:
                self._json(400, {"error": str(exc)})
            return

        self._json(404, {"error": "POST /api/agent/submit, /api/orchestrator/run, /api/external/register"})

    def do_DELETE(self) -> None:  # noqa: N802
        path = urlparse(self.path)
        m = re.match(r"^/api/external/apis/([A-Za-z0-9_-]+)$", path.path)
        if m:
            self._json(200, remove_external_api(m.group(1)))
            return
        self._json(404, {"error": "DELETE /api/external/apis/{id}"})

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"[eval-api] {fmt % args}\n")


def cmd_serve(args: argparse.Namespace) -> int:
    ensure_eval_dir()
    build_portfolio()  # warm cache / create status file
    server = HTTPServer((args.host, args.port), EvalAPIHandler)
    base = f"http://{args.host}:{args.port}"
    print(f"\nEval AI Agent — live eval service")
    print(f"  Dashboard:       {base}/")
    print(f"  External analyze:  POST {base}/api/external/analyze")
    print(f"  Set your API:      POST {base}/api/external/target")
    print(f"  Agent submit:      POST {base}/api/agent/submit  (+ api_base_url)")
    print(f"  Portfolio JSON:    {base}/api/portfolio")
    print(f"  Orchestrator:    POST {base}/api/orchestrator/run")
    print(f"  Bot status:      {base}/api/orchestrator/status")
    print(f"  Docs:              docs/ORCHESTRATOR.md\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Eval AI Agent portfolio tools")
    sub = parser.add_subparsers(dest="command", required=True)

    p_verify = sub.add_parser("verify", help="Check deliverables")
    p_verify.add_argument("--run-tests", action="store_true")
    p_verify.add_argument("--run-docker", action="store_true")

    p_compare = sub.add_parser("compare", help="Compare agent output")
    p_compare.add_argument("task_id")
    p_compare.add_argument("--agent-output")
    p_compare.add_argument("--agent-name", default="cli")
    p_compare.add_argument("--api-base-url", help="Your running API e.g. http://127.0.0.1:3000")

    sub.add_parser("dashboard", help="Print dashboard URL (use serve)")
    sub.add_parser("metrics", help="Prometheus metrics")

    p_serve = sub.add_parser("serve", help="Live eval API + dashboard")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8788)

    p_bot = sub.add_parser("bot", help="Run orchestrator bot for one task")
    p_bot.add_argument("task_id")
    p_bot.add_argument("--api-id", help="Registered API id from /api/external/register")
    p_bot.add_argument("--api-base-url", help="One-off API URL (not saved)")
    p_bot.add_argument("--run-tests", action="store_true")

    p_all = sub.add_parser("bots-all", help="Run orchestrator bots for all 24 tasks")
    p_all.add_argument("--api-id", help="Use this registered API for all tasks")
    p_all.add_argument("--api-base-url", help="One-off API URL for all tasks")
    p_all.add_argument("--run-tests", action="store_true")

    p_ocfg = sub.add_parser("orch-config", help="Show or set orchestrator config")
    p_ocfg.add_argument("--api-id", help="Register/update API id")
    p_ocfg.add_argument("--api-base-url", help="API base URL to register")
    p_ocfg.add_argument("--project-name", help="Display name for registered API")

    args = parser.parse_args()
    handlers = {
        "verify": cmd_verify,
        "compare": cmd_compare,
        "dashboard": cmd_dashboard,
        "metrics": cmd_metrics,
        "serve": cmd_serve,
        "bot": cmd_bot,
        "bots-all": cmd_bots_all,
        "orch-config": cmd_orchestrator_config,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
