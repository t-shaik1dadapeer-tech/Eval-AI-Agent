#!/usr/bin/env python3
"""
Eval AI Agent — portfolio verification, agent compare API, live dashboard.

After clone:  make eval-api  →  http://127.0.0.1:8788

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
FRONTEND_STATIC = DASHBOARD_STATIC  # alias — live UI is the eval dashboard
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

    def _is_likely_api_path(path: str) -> bool:
        if re.search(r"/Users/|/home/|/var/|/tmp/|/private/", path, re.IGNORECASE):
            return False
        segments = [s for s in path.split("/") if s]
        if len(segments) > 8:
            return False
        for seg in segments:
            if seg.startswith("{") and seg.endswith("}"):
                continue
            if "." in seg and not seg.startswith("."):
                return False
            if seg and seg[0].isupper() and not seg.isupper():
                return False
        return True

    def add(method: str, path: str, source: str) -> None:
        path = path.split("?")[0].strip()
        if (
            not path.startswith("/")
            or "*" in path
            or ".." in path
            or len(path) > 120
            or not _is_likely_api_path(path)
        ):
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
    timeout: float = 2.0,
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
    except Exception as exc:  # noqa: BLE001 — timeout, connection reset, etc.
        return {
            "url": url,
            "method": method.upper(),
            "path": path,
            "status": None,
            "ok": False,
            "error": str(exc),
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


def collect_task_md_content(task: dict[str, Any], extra_path: str | Path | None = None) -> tuple[str, list[str]]:
    """Gather .md text from task references for API expectation parsing."""
    folder = ROOT / task["folder"]
    chunks: list[str] = []
    sources: list[str] = []
    seen: set[str] = set()

    def add_path(path: Path) -> None:
        if not path.exists() or path.suffix != ".md":
            return
        rel = _rel_path(path)
        if rel in seen:
            return
        seen.add(rel)
        chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        sources.append(rel)

    for name in list(task.get("reference_files", [])) + list(task.get("required_files", [])):
        add_path(folder / name)
    for rel in RELATED_MD.get(task["id"], []):
        add_path(ROOT / rel)
    if extra_path:
        p = Path(extra_path)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        add_path(p)
    return "\n\n".join(chunks), sources


def summarize_api_match(api_match: dict[str, Any] | None) -> dict[str, Any]:
    if not api_match or api_match.get("verdict") == "skipped":
        return {
            "matching": [],
            "not_matching": [],
            "summary": (api_match or {}).get("message", "No API comparison run."),
        }
    matching: list[dict[str, Any]] = []
    not_matching: list[dict[str, Any]] = []
    for probe in api_match.get("probes") or []:
        item = {
            "method": probe.get("method", "GET"),
            "path": probe.get("path"),
            "status": probe.get("status"),
            "ok": probe.get("ok"),
            "error": probe.get("error"),
        }
        if probe.get("ok"):
            matching.append(item)
        else:
            not_matching.append(item)
    parts: list[str] = []
    if matching:
        parts.append(
            "Matching on your API: "
            + ", ".join(f"{m['method']} {m['path']} ({m['status']})" for m in matching[:12])
        )
    if not_matching:
        parts.append(
            "Not matching: "
            + ", ".join(
                f"{n['method']} {n['path']} ({n.get('status') or n.get('error') or '?'})"
                for n in not_matching[:12]
            )
        )
    if not parts:
        parts.append(api_match.get("message", ""))
    return {"matching": matching, "not_matching": not_matching, "summary": " | ".join(parts)}


def _task_primary_md_path(task: dict[str, Any]) -> Path | None:
    folder = ROOT / task["folder"]
    for name in list(task.get("reference_files", [])) + list(task.get("required_files", [])):
        path = folder / name
        if path.exists() and path.suffix == ".md":
            return path
    readme = folder / "README.md"
    return readme if readme.exists() else None


def suggest_alternate_tasks(
    current_id: str,
    api_base_url: str,
    registry: dict[str, Any],
    current_api_match: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """When current task poorly fits the user's API, rank other agent tasks by endpoint overlap."""
    current_pct = round((current_api_match or {}).get("match_score", 0) * 100)
    if current_pct >= 80:
        return []

    ranked: list[dict[str, Any]] = []
    for other in registry.get("tasks", []):
        if other["id"] == current_id:
            continue
        md_content, sources = collect_task_md_content(other)
        if not md_content.strip():
            continue
        match = compare_api_to_md(md_content, api_base_url, task=other)
        fit = round((match.get("match_score") or 0) * 100)
        if fit <= current_pct:
            continue
        ranked.append(
            {
                "id": other["id"],
                "name": other["name"],
                "category": other.get("category"),
                "fit_score": fit,
                "verdict": match.get("verdict"),
                "md_sources": sources[:3],
                "reason": f"{fit}% endpoint match vs your API (better fit than {current_id}).",
            }
        )
    ranked.sort(key=lambda x: x["fit_score"], reverse=True)
    if ranked:
        return ranked[:4]

    # Fallback hints when nothing scores higher — common analysis tasks for unknown APIs
    fallbacks = []
    for fid in ("B2", "B1", "I2", "B3"):
        other = task_by_id(registry, fid)
        if other and other["id"] != current_id:
            fallbacks.append(
                {
                    "id": other["id"],
                    "name": other["name"],
                    "category": other.get("category"),
                    "fit_score": None,
                    "verdict": None,
                    "md_sources": [f"{other['folder']}/{other.get('reference_files', ['README.md'])[0]}"],
                    "reason": f"Try {other['id']} — {other['name']} for mapping or documenting your API.",
                }
            )
    return fallbacks[:3]


def build_verification_note(
    task: dict[str, Any],
    *,
    verdict: str | None,
    has_api: bool,
    alternate_tasks: list[dict[str, Any]],
    matching: list[dict[str, Any]],
    not_matching: list[dict[str, Any]],
) -> str:
    if not has_api:
        return "Register your API in the panel above, then click Check to compare this task's .md files against it."
    if verdict == "ok":
        return (
            f"Task {task['id']} ({task['name']}) fully matches your API — "
            f"{len(matching)} endpoint(s) verified."
        )
    if verdict == "partial":
        base = (
            f"Task {task['id']} partially matches your API — "
            f"{len(matching)} matching, {len(not_matching)} not matching."
        )
    else:
        base = f"Task {task['id']} is not a complete match for your API."
    if alternate_tasks:
        alts = ", ".join(f"{a['id']} ({a['name']})" for a in alternate_tasks[:3])
        return f"{base} This agent is not fully verifiable for your API — try: {alts}."
    return f"{base} Consider B2 (API Endpoint Map) or B1 (Repository Inventory) for your API."


def run_task_check(
    task: dict[str, Any],
    registry: dict[str, Any],
    *,
    api_base_url: str | None = None,
    api_id: str | None = None,
) -> dict[str, Any]:
    """Dashboard check: compare task .md files vs registered API; score + alternate task hints."""
    try:
        orch_cfg = _orch().load_config()
    except Exception:
        orch_cfg = {}

    url = resolve_api_base_url(
        api_base_url=api_base_url,
        api_id=api_id,
        task_id=task["id"],
        orch_config=orch_cfg,
    )

    md_result: dict[str, Any] | None = None
    primary = _task_primary_md_path(task)
    if primary:
        md_result = score_agent_output(task, primary)

    api_match: dict[str, Any] | None = None
    md_sources: list[str] = []
    if url:
        md_content, md_sources = collect_task_md_content(task)
        api_match = compare_api_to_md(md_content, url, task=task)

    endpoint_summary = summarize_api_match(api_match)
    matching = endpoint_summary["matching"]
    not_matching = endpoint_summary["not_matching"]

    alternate_tasks: list[dict[str, Any]] = []
    if url and api_match and api_match.get("verdict") not in ("ok", "skipped"):
        alternate_tasks = suggest_alternate_tasks(task["id"], url, registry, api_match)

    if url and api_match and api_match.get("verdict") != "skipped":
        verdict = api_match.get("verdict")
        check_type = "api_analyze"
        match_score = api_match.get("match_score")
        message = api_match.get("message")
    elif md_result:
        verdict = md_result.get("verdict")
        check_type = "repo_check"
        match_score = md_result.get("match_score")
        message = md_result.get("message")
    else:
        verdict = "error"
        check_type = "repo_check"
        match_score = 0.0
        message = "No .md deliverable found for this task."

    verification_note = build_verification_note(
        task,
        verdict=str(verdict),
        has_api=bool(url),
        alternate_tasks=alternate_tasks,
        matching=matching,
        not_matching=not_matching,
    )

    checked_at = datetime.now(timezone.utc).isoformat()
    entry: dict[str, Any] = {
        "task_id": task["id"],
        "agent_name": "dashboard_check",
        "submitted_at": checked_at,
        "checked_at": checked_at,
        "check_type": check_type,
        "output_path": _rel_path(primary) if primary else None,
        "md_verdict": md_result.get("verdict") if md_result else None,
        "verdict": verdict,
        "match_score": match_score,
        "message": message,
        "api_base_url": url,
        "api_match": api_match or {"verdict": "skipped", "message": "No API registered."},
        "matching_summary": endpoint_summary["summary"],
        "matching_endpoints": matching,
        "not_matching_endpoints": not_matching,
        "alternate_tasks": alternate_tasks,
        "verification_note": verification_note,
        "md_sources": md_sources,
    }
    entry["completion_score"] = score_from_check(entry)
    save_agent_run(entry)

    evaluated = evaluate_task(task, agent_result=entry)
    evaluated["check_result"] = {
        "verdict": verdict,
        "completion_score": entry["completion_score"],
        "matching_endpoints": matching,
        "not_matching_endpoints": not_matching,
        "alternate_tasks": alternate_tasks,
        "verification_note": verification_note,
    }
    return evaluated


def resolve_task_remote(task_id: str, orch_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Per-task registered remote API (from task_api_map or default) — no live probe."""
    cfg = orch_config or _orch().load_config()
    url = resolve_api_base_url(task_id=task_id, orch_config=cfg)
    api_id = cfg.get("task_api_map", {}).get(task_id.upper())
    if not api_id and cfg.get("use_api_for_all_tasks"):
        api_id = cfg.get("default_api_id")
    if not api_id and url:
        for api in load_external_apis().get("apis", []):
            if api.get("api_base_url") == url:
                api_id = api.get("id")
                break
    if not api_id and not url and cfg.get("default_api_id"):
        found = get_external_api(cfg["default_api_id"])
        if found and not cfg.get("task_api_map"):
            api_id = found.get("id")
            url = found.get("api_base_url")
    return {
        "api_id": api_id,
        "api_base_url": url,
        "registered": bool(url),
    }


def task_was_checked(agent_result: dict[str, Any] | None) -> bool:
    return bool(agent_result and agent_result.get("checked_at"))


def score_from_check(agent_result: dict[str, Any]) -> int:
    """Derive 0–100 score from an explicit check record."""
    if agent_result.get("completion_score") is not None:
        return min(100, max(0, int(agent_result["completion_score"])))
    check_type = agent_result.get("check_type")
    if check_type == "api_analyze":
        api = agent_result.get("api_match") or {}
        ms = api.get("match_score")
        if ms is not None:
            return round(float(ms) * 100)
    ms = agent_result.get("match_score")
    if ms is not None:
        return round(float(ms) * 100)
    verdict = agent_result.get("md_verdict") or agent_result.get("verdict")
    return {"ok": 100, "partial": 50, "mismatch": 15, "unreachable": 10}.get(str(verdict), 0)


def compute_task_score(agent_result: dict[str, Any] | None = None) -> int:
    """0 until POST /api/agent/submit or POST /api/external/analyze (with task_id)."""
    if not task_was_checked(agent_result):
        return 0
    return score_from_check(agent_result)


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
    """Plain summary for a task (used by tools; dashboard shows this inline)."""
    primary = task.get("required_files", task.get("reference_files", ["README.md"]))[0]
    return {
        "task_id": task["id"],
        "name": task["name"],
        "folder": task["folder"],
        "what_to_do": task.get("compare_hint", task["name"]),
        "files_to_create": [f"{task['folder']}/{r}" for r in task.get("required_files", [])],
        "main_file": f"{task['folder']}/{primary}",
        "cursor_prompt": f"Open docs/AGENT_PROMPTS.md and find section ## {task['id']} —",
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
        "summary": task.get("compare_hint", task["name"]),
        "required_files": [f"{task['folder']}/{r}" for r in task.get("required_files", [])],
    }
    if agent_result and task_was_checked(agent_result):
        out["agent_result"] = {
            "verdict": agent_result.get("verdict"),
            "match_score": agent_result.get("match_score"),
            "message": agent_result.get("message"),
            "suggestion": agent_result.get("suggestion"),
            "agent_name": agent_result.get("agent_name"),
            "submitted_at": agent_result.get("submitted_at"),
            "checked_at": agent_result.get("checked_at"),
            "check_type": agent_result.get("check_type"),
            "output_path": agent_result.get("output_path"),
            "md_verdict": agent_result.get("md_verdict"),
            "api_match": agent_result.get("api_match"),
            "api_base_url": agent_result.get("api_base_url"),
            "related_md": agent_result.get("related_md"),
            "combined_verdict": agent_result.get("combined_verdict"),
            "matching_summary": agent_result.get("matching_summary"),
            "matching_endpoints": agent_result.get("matching_endpoints") or [],
            "not_matching_endpoints": agent_result.get("not_matching_endpoints") or [],
            "alternate_tasks": agent_result.get("alternate_tasks") or [],
            "verification_note": agent_result.get("verification_note"),
            "md_sources": agent_result.get("md_sources") or [],
        }
    ar = agent_result if task_was_checked(agent_result) else None
    orch_cfg = _orch().load_config()
    remote = resolve_task_remote(task["id"], orch_cfg)
    completion_score = compute_task_score(agent_result=ar)
    out["remote_api"] = remote
    out["completion_score"] = completion_score
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
    verified = sum(1 for r in results if r.get("verified"))
    agent_evaluated = sum(1 for r in results if task_was_checked(r.get("agent_result")))
    agent_ok = sum(
        1
        for r in results
        if task_was_checked(r.get("agent_result"))
        and (r.get("agent_result", {}).get("md_verdict") or r.get("agent_result", {}).get("verdict")) == "ok"
    )
    complete_count = sum(1 for r in results if r.get("completion_score", 0) >= 80)

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
            "complete_count": complete_count,
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
    """Score agent deliverable against repo references. API registration does not affect verdict/score."""
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

    related = related_suggestions(task, md_result.get("verdict", "mismatch"), None)
    suggestion = md_result.get("suggestion", "")
    if related and md_result.get("verdict") != "ok":
        suggestion += " Related .md files: " + ", ".join(f"`{r}`" for r in related)

    checked_at = datetime.now(timezone.utc).isoformat()
    result = {
        **md_result,
        "md_verdict": md_result.get("verdict"),
        "verdict": md_result.get("verdict"),
        "match_score": md_result.get("match_score"),
        "message": md_result.get("message"),
        "api_base_url": base,
        "api_match": {
            "verdict": "skipped",
            "message": "Agent submit checks .md vs repo only; use POST /api/external/analyze for live API.",
        },
        "related_md": related,
        "combined_verdict": md_result.get("verdict"),
        "suggestion": suggestion.strip(),
        "check_type": "agent_submit",
        "checked_at": checked_at,
    }
    result["completion_score"] = score_from_check(result)
    entry = {
        "task_id": task["id"],
        "agent_name": agent_name or "unknown",
        "submitted_at": checked_at,
        "output_path": _rel_path(path),
        **result,
    }
    save_agent_run(entry)
    return {"task": task["id"], "task_name": task["name"], "folder": task["folder"], **result}


def save_api_check(
    task: dict[str, Any],
    md_path: Path,
    analyze_result: dict[str, Any],
) -> dict[str, Any]:
    """Persist live API vs .md check so dashboard score updates for this task."""
    api_match = analyze_result.get("api_match") or {}
    checked_at = datetime.now(timezone.utc).isoformat()
    entry: dict[str, Any] = {
        "task_id": task["id"],
        "agent_name": "api_analyze",
        "submitted_at": checked_at,
        "checked_at": checked_at,
        "check_type": "api_analyze",
        "output_path": _rel_path(md_path),
        "verdict": api_match.get("verdict"),
        "match_score": api_match.get("match_score"),
        "message": api_match.get("message"),
        "api_match": api_match,
        "api_base_url": api_match.get("api_base_url"),
        "related_md": analyze_result.get("related_md", []),
    }
    entry["completion_score"] = score_from_check(entry)
    endpoint_summary = summarize_api_match(api_match)
    entry["matching_summary"] = endpoint_summary["summary"]
    entry["matching_endpoints"] = endpoint_summary["matching"]
    entry["not_matching_endpoints"] = endpoint_summary["not_matching"]
    if api_match.get("verdict") not in ("ok", "skipped") and api_match.get("api_base_url"):
        registry = load_registry()
        entry["alternate_tasks"] = suggest_alternate_tasks(
            task["id"], api_match["api_base_url"], registry, api_match
        )
        entry["verification_note"] = build_verification_note(
            task,
            verdict=str(api_match.get("verdict")),
            has_api=True,
            alternate_tasks=entry["alternate_tasks"],
            matching=entry["matching_endpoints"],
            not_matching=entry["not_matching_endpoints"],
        )
    save_agent_run(entry)
    return entry


def run_pipeline_task_verify(
    task: dict[str, Any],
    *,
    run_tests: bool = False,
) -> dict[str, Any]:
    """Verify one pipeline task: required files (+ optional verify_command)."""
    deliverables_ok, missing = check_deliverables(task)
    verified = False
    verify_note = ""
    if run_tests and task.get("verify_command"):
        requires_ok = all(has_tool(r) for r in task.get("verify_requires", []))
        if requires_ok or not task.get("verify_requires"):
            verified, verify_note = run_verify_command(task)
        else:
            verify_note = f"skipped: needs {task.get('verify_requires')}"

    primary = _task_primary_md_path(task)
    if deliverables_ok and verified:
        verdict, completion_score = "ok", 100
        message = "Deliverables present and verify command passed."
    elif deliverables_ok:
        verdict, completion_score = "ok", 100
        message = "All required deliverables present."
    else:
        verdict, completion_score = "mismatch", 0
        message = f"Missing: {', '.join(missing)}"

    checked_at = datetime.now(timezone.utc).isoformat()
    entry: dict[str, Any] = {
        "task_id": task["id"],
        "agent_name": "pipeline_run",
        "submitted_at": checked_at,
        "checked_at": checked_at,
        "check_type": "pipeline_verify",
        "output_path": _rel_path(primary) if primary else None,
        "verdict": verdict,
        "md_verdict": verdict,
        "match_score": 1.0 if deliverables_ok else 0.0,
        "completion_score": completion_score,
        "message": message,
        "deliverables_ok": deliverables_ok,
        "missing_files": missing,
        "verified": verified,
        "verify_note": verify_note,
    }
    save_agent_run(entry)
    out = evaluate_task(task, agent_result=entry)
    out["pipeline_status"] = verdict
    return out


def run_all_pipeline(*, run_tests: bool = False) -> dict[str, Any]:
    registry = load_registry()
    order = registry.get("pipeline_order") or [t["id"] for t in registry["tasks"]]
    results: list[dict[str, Any]] = []
    for tid in order:
        task = task_by_id(registry, tid)
        if task:
            results.append(run_pipeline_task_verify(task, run_tests=run_tests))
    payload = build_portfolio()
    ok = sum(1 for r in results if r.get("deliverables_ok"))
    verified = sum(1 for r in results if r.get("verified"))
    return {
        "run": "pipeline_all",
        "total": len(results),
        "deliverables_ok": ok,
        "verified": verified,
        "all_complete": ok == len(results),
        "tasks": results,
        "portfolio": payload,
    }


def build_pipeline_plan(target_repo: str | None = None) -> dict[str, Any]:
    registry = load_registry()
    order = registry.get("pipeline_order") or [t["id"] for t in registry["tasks"]]
    by_id = {t["id"]: t for t in registry["tasks"]}
    steps: list[dict[str, Any]] = []
    for tid in order:
        task = by_id.get(tid)
        if not task:
            continue
        ok, missing = check_deliverables(task)
        steps.append(
            {
                "id": task["id"],
                "name": task["name"],
                "category": task.get("category"),
                "folder": task["folder"],
                "depends_on": task.get("depends_on") or [],
                "blueprint": task.get("blueprint", f"eval_blueprints/{tid}_blueprint.md"),
                "primary_output": task.get("primary_output"),
                "skill_slug": task.get("skill_slug"),
                "required_files": [f"{task['folder']}/{r}" for r in task.get("required_files", [])],
                "summary": task.get("compare_hint", task["name"]),
                "deliverables_ok": ok,
                "missing_files": missing,
            }
        )
    root = Path(target_repo).resolve() if target_repo else ROOT
    return {
        "target_repo": str(root),
        "repo_root": str(ROOT),
        "total": len(steps),
        "steps": steps,
    }


def api_docs() -> dict[str, Any]:
    return {
        "title": "Evil-Ai Portfolio API",
        "ui": "/",
        "workflow": [
            "1. make setup",
            "2. make eval-api",
            "3. Open dashboard / — 24-task grid with scores",
            "4. GET /api/agent/guide/{id} → work in Cursor → POST /api/agent/submit",
            "5. make run-all — verify all deliverables",
        ],
        "endpoints": [
            "GET  /",
            "GET  /api/health",
            "GET  /api/docs",
            "GET  /api/pipeline/plan",
            "POST /api/pipeline/run-all",
            "GET  /api/portfolio",
            "GET  /api/tasks",
            "GET  /api/tasks/{id}",
            "GET  /api/agent/guide/{id}",
            "POST /api/agent/submit",
            "POST /api/portfolio/refresh",
        ],
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


def cmd_orch_config(args: argparse.Namespace) -> int:
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


def cmd_run_all(args: argparse.Namespace) -> int:
    payload = run_all_pipeline(run_tests=getattr(args, "run_tests", False))
    STATUS_PATH.write_text(json.dumps(payload["portfolio"], indent=2) + "\n", encoding="utf-8")
    s = payload["portfolio"]["summary"]
    print(json.dumps({
        "total": payload["total"],
        "deliverables_ok": payload["deliverables_ok"],
        "verified": payload["verified"],
        "all_complete": payload["all_complete"],
        "complete_count": s.get("complete_count"),
    }, indent=2))
    for r in payload["tasks"]:
        if not r.get("deliverables_ok"):
            print(f"  FAIL {r['id']}: {r.get('missing_files')}")
    return 0 if payload["all_complete"] else 1


def cmd_pipeline(_: argparse.Namespace) -> int:
    print(json.dumps(build_pipeline_plan(), indent=2))
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
        if path.path == "/api/pipeline/plan":
            target = qs.get("target", [""])[0].strip()
            self._json(200, build_pipeline_plan(target or None))
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

        if path.path == "/api/pipeline/run-all":
            try:
                body = self._read_json_body()
                run_tests = body.get("run_tests") in (True, "true", "1", 1)
                payload = run_all_pipeline(run_tests=run_tests)
                STATUS_PATH.write_text(
                    json.dumps(payload["portfolio"], indent=2) + "\n", encoding="utf-8"
                )
                self._json(200, payload)
            except Exception as exc:
                self._json(500, {"error": str(exc)})
            return

        if path.path == "/api/check-all":
            try:
                body = self._read_json_body()
                results = []
                for task in self.registry["tasks"]:
                    results.append(
                        run_task_check(
                            task,
                            self.registry,
                            api_base_url=body.get("api_base_url"),
                            api_id=body.get("api_id"),
                        )
                    )
                payload = build_portfolio()
                self._json(200, {"checked": len(results), "tasks": results, "portfolio": payload})
            except Exception as exc:
                self._json(500, {"error": str(exc)})
            return

        m_check = re.match(r"^/api/tasks/([A-Za-z0-9]+)/check$", path.path)
        if m_check:
            task = task_by_id(self.registry, m_check.group(1))
            if not task:
                self._json(404, {"error": "unknown task"})
                return
            try:
                body = self._read_json_body()
                result = run_task_check(
                    task,
                    self.registry,
                    api_base_url=body.get("api_base_url"),
                    api_id=body.get("api_id"),
                )
                self._json(200, result)
            except Exception as exc:
                self._json(500, {"error": str(exc)})
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
                if task and url:
                    saved = save_api_check(task, md_p, result)
                    result["task_id"] = task["id"]
                    result["check_type"] = saved["check_type"]
                    result["checked_at"] = saved["checked_at"]
                    result["completion_score"] = saved["completion_score"]
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

        self._json(404, {"error": "POST /api/agent/submit, /api/external/register"})

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
    print(f"\nEvil-Ai portfolio")
    print(f"  Live dashboard:  {base}/")
    print(f"  Portfolio API:   {base}/api/portfolio")
    print(f"  Agent guide:     {base}/api/agent/guide/B1")
    print(f"  Verify files:    make eval")
    print(f"  Stop server:     make eval-stop\n")
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

    sub.add_parser("pipeline", help="Print pipeline plan JSON")
    p_run_all = sub.add_parser("run-all", help="Verify all 24 pipeline tasks")
    p_run_all.add_argument("--run-tests", action="store_true")
    p_serve = sub.add_parser("serve", help="Evil-Ai portfolio — live eval API + dashboard")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8788)

    p_ocfg = sub.add_parser("orch-config", help="Show or set eval config (API map)")
    p_ocfg.add_argument("--api-id", help="Register/update API id")
    p_ocfg.add_argument("--api-base-url", help="API base URL to register")
    p_ocfg.add_argument("--project-name", help="Display name for registered API")

    args = parser.parse_args()
    handlers = {
        "verify": cmd_verify,
        "compare": cmd_compare,
        "pipeline": cmd_pipeline,
        "run-all": cmd_run_all,
        "metrics": cmd_metrics,
        "serve": cmd_serve,
        "orch-config": cmd_orch_config,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
