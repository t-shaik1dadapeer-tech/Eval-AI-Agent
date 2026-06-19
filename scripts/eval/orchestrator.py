#!/usr/bin/env python3
"""Task bot orchestrator — run one task or all 24 with multi-API config."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVAL_SCRIPTS = Path(__file__).resolve().parent
if str(EVAL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EVAL_SCRIPTS))

import portfolio as p  # noqa: E402

ROOT = p.ROOT
ORCH_CONFIG_PATH = p.EVAL_DIR / "orchestrator-config.json"
ORCH_STATE_PATH = p.EVAL_DIR / "orchestrator-state.json"

TASK_ORDER = (
    [f"B{i}" for i in range(1, 7)]
    + [f"I{i}" for i in range(1, 7)]
    + [f"A{i}" for i in range(1, 7)]
    + [f"D{i}" for i in range(1, 7)]
)


def default_config() -> dict[str, Any]:
    """No project/API defaults — configure after your APIs are ready."""
    return {
        "agent_name": "orchestrator-bot",
        "run_tests": False,
        "use_api_for_all_tasks": False,
        "default_api_id": None,
        "task_api_map": {},
        "output_map": {},
    }


def load_config() -> dict[str, Any]:
    p.ensure_eval_dir()
    cfg = default_config()
    if ORCH_CONFIG_PATH.exists():
        cfg.update(json.loads(ORCH_CONFIG_PATH.read_text(encoding="utf-8")))
    for legacy_key in ("api_base_url", "project_name"):
        cfg.pop(legacy_key, None)
    store = p.load_external_apis()
    if cfg.get("default_api_id") is None and store.get("default_api_id"):
        cfg["default_api_id"] = store["default_api_id"]
    return cfg


def save_config(data: dict[str, Any]) -> dict[str, Any]:
    p.ensure_eval_dir()
    cfg = load_config()
    if data.get("api_base_url") and not data.get("apis"):
        api_id = data.get("id") or data.get("project_name") or "my-api"
        p.register_external_api(api_id, data.get("project_name") or api_id, data["api_base_url"])
        if data.get("default") or data.get("set_default", True):
            store = p.load_external_apis()
            store["default_api_id"] = api_id.strip().lower().replace(" ", "-")
            p.save_external_apis(store)
        data = {
            k: v
            for k, v in data.items()
            if k not in ("api_base_url", "project_name", "id", "default", "set_default")
        }
    cfg.update(data)
    if "apis" in data and isinstance(data["apis"], list):
        for item in data["apis"]:
            if item.get("id") and item.get("api_base_url"):
                p.register_external_api(item["id"], item.get("name", item["id"]), item["api_base_url"])
        if data.get("default_api_id") is not None:
            store = p.load_external_apis()
            store["default_api_id"] = data["default_api_id"]
            p.save_external_apis(store)
        cfg.pop("apis", None)
    if cfg.get("default_api_id") is not None:
        store = p.load_external_apis()
        store["default_api_id"] = cfg["default_api_id"]
        p.save_external_apis(store)
    ORCH_CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return cfg


def resolve_submit_path(task: dict[str, Any], config: dict[str, Any]) -> str | None:
    tid = task["id"]
    overrides = config.get("output_map") or {}
    if tid in overrides:
        rel = overrides[tid]
        if not rel.startswith(task["folder"]):
            rel = f"{task['folder']}/{rel.lstrip('/')}"
        if (ROOT / rel).exists():
            return rel

    for name in task.get("required_files", []):
        if name.endswith((".md", ".csv")):
            rel = f"{task['folder']}/{name}"
            if (ROOT / rel).exists():
                return rel
    for name in task.get("reference_files", []):
        if name.endswith(".md"):
            rel = f"{task['folder']}/{name}"
            if (ROOT / rel).exists():
                return rel
    return None


def resolve_task_api(
    task_id: str,
    config: dict[str, Any],
    run_override: dict[str, Any] | None = None,
) -> tuple[str | None, str | None]:
    """Return (api_base_url, api_id) for a task."""
    ov = run_override or {}
    if ov.get("api_base_url"):
        return ov["api_base_url"].rstrip("/"), ov.get("api_id")
    merged = {**config, **ov}
    url = p.resolve_api_base_url(task_id=task_id, orch_config=merged)
    api_id = merged.get("task_api_map", {}).get(task_id.upper())
    if not api_id and merged.get("use_api_for_all_tasks"):
        api_id = merged.get("default_api_id")
    if not api_id and url:
        for api in p.load_external_apis().get("apis", []):
            if api.get("api_base_url") == url:
                api_id = api.get("id")
                break
    return url, api_id


def _update_run_in_state(run_record: dict[str, Any]) -> None:
    state = load_state()
    for i, run in enumerate(state.get("runs", [])):
        if run.get("run_id") == run_record.get("run_id"):
            state["runs"][i] = run_record
            break
    state["current_run_id"] = run_record.get("run_id")
    save_state(state)


def load_state() -> dict[str, Any]:
    p.ensure_eval_dir()
    if not ORCH_STATE_PATH.exists():
        return {"current_run_id": None, "runs": []}
    return json.loads(ORCH_STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    p.ensure_eval_dir()
    ORCH_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def run_task_bot(
    task: dict[str, Any],
    config: dict[str, Any],
    *,
    run_record: dict[str, Any],
    run_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tid = task["id"]
    run_record["tasks"][tid] = {
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    _update_run_in_state(run_record)

    result: dict[str, Any] = {"task_id": tid, "status": "failed"}
    try:
        guide = p.agent_guide(task)
        output_path = resolve_submit_path(task, config)
        if not output_path:
            result = {
                "task_id": tid,
                "status": "skipped",
                "reason": "no submit .md/.csv found",
                "guide": guide.get("reference_files", []),
            }
        else:
            api_url, api_id = resolve_task_api(tid, config, run_override)
            submit = p.submit_agent_output(
                task,
                agent_name=config.get("agent_name", "orchestrator-bot"),
                output_path=output_path,
                content=None,
                api_base_url=api_url,
                api_id=api_id,
            )
            verified = False
            verify_note = "not run"
            if config.get("run_tests") and task.get("verify_command"):
                ok, verify_note = p.run_verify_command(task)
                verified = ok
            result = {
                "task_id": tid,
                "status": "done",
                "output_path": output_path,
                "api_base_url": api_url,
                "api_id": api_id,
                "verdict": submit.get("verdict"),
                "match_score": submit.get("match_score"),
                "api_match": submit.get("api_match", {}).get("verdict") if submit.get("api_match") else None,
                "verified": verified,
                "verify_note": verify_note,
                "related_md": submit.get("related_md", []),
            }
    except Exception as exc:  # noqa: BLE001
        result = {"task_id": tid, "status": "failed", "error": str(exc)}

    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    run_record["tasks"][tid] = result
    _update_run_in_state(run_record)
    return result


def run_orchestrator(
    *,
    task_id: str | None = None,
    mode: str | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = p.load_registry()
    config = load_config()
    run_override = dict(config_overrides or {})

    if mode == "all":
        task_ids = TASK_ORDER
    elif task_id:
        task_ids = [task_id.upper()]
    else:
        raise ValueError("Provide task_id or mode=all")

    if run_override.get("apis"):
        for item in run_override["apis"]:
            if item.get("id") and item.get("api_base_url"):
                p.register_external_api(item["id"], item.get("name", item["id"]), item["api_base_url"])
        run_override.pop("apis", None)

    if run_override.get("default_api_id") is not None:
        save_config({"default_api_id": run_override["default_api_id"]})
        config = load_config()

    run_id = uuid.uuid4().hex[:12]
    apis_snapshot = p.load_external_apis()
    run_record: dict[str, Any] = {
        "run_id": run_id,
        "mode": "all" if mode == "all" else "single",
        "task_ids": task_ids,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config_snapshot": {
            "apis_count": len(apis_snapshot.get("apis", [])),
            "default_api_id": config.get("default_api_id"),
            "task_api_map": config.get("task_api_map", {}),
            "run_tests": config.get("run_tests"),
        },
        "tasks": {},
    }

    state = load_state()
    state["current_run_id"] = run_id
    state["runs"].append(run_record)
    save_state(state)

    results = []
    for tid in task_ids:
        task = p.task_by_id(registry, tid)
        if not task:
            entry = {"task_id": tid, "status": "failed", "error": "unknown task"}
            run_record["tasks"][tid] = entry
            results.append(entry)
            continue
        results.append(run_task_bot(task, config, run_record=run_record, run_override=run_override))

    done = sum(1 for r in results if r.get("status") == "done")
    ok = sum(1 for r in results if r.get("verdict") == "ok")
    run_record["completed_at"] = datetime.now(timezone.utc).isoformat()
    run_record["summary"] = {
        "total": len(task_ids),
        "done": done,
        "skipped": sum(1 for r in results if r.get("status") == "skipped"),
        "failed": sum(1 for r in results if r.get("status") == "failed"),
        "verdict_ok": ok,
    }
    _update_run_in_state(run_record)

    return {
        "run_id": run_id,
        "mode": run_record["mode"],
        "summary": run_record["summary"],
        "results": results,
        "registered_apis": p.load_external_apis().get("apis", []),
        "dashboard": "/",
    }


def orchestrator_status() -> dict[str, Any]:
    config = load_config()
    state = load_state()
    current = None
    if state.get("runs"):
        for run in reversed(state["runs"]):
            if run.get("run_id") == state.get("current_run_id"):
                current = run
                break
        if current is None:
            current = state["runs"][-1]

    return {
        "config": config,
        "config_path": str(ORCH_CONFIG_PATH.relative_to(ROOT)),
        "external_apis": p.load_external_apis(),
        "current_run": current,
        "task_order": list(TASK_ORDER),
        "bots": current.get("tasks", {}) if current else {},
    }


def bot_status_for_task(task_id: str) -> dict[str, Any] | None:
    return orchestrator_status().get("bots", {}).get(task_id.upper())
