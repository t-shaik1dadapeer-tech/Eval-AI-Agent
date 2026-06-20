#!/usr/bin/env python3
"""Eval config — per-task API mapping and output paths (no verify bots)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

EVAL_SCRIPTS = Path(__file__).resolve().parent
if str(EVAL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EVAL_SCRIPTS))

import portfolio as p  # noqa: E402

ROOT = p.ROOT
ORCH_CONFIG_PATH = p.EVAL_DIR / "eval-config.json"
LEGACY_CONFIG_PATH = p.EVAL_DIR / "orchestrator-config.json"

TASK_ORDER = (
    [f"B{i}" for i in range(1, 7)]
    + [f"I{i}" for i in range(1, 7)]
    + [f"A{i}" for i in range(1, 7)]
    + [f"D{i}" for i in range(1, 7)]
)


def default_config() -> dict[str, Any]:
    return {
        "default_api_id": None,
        "task_api_map": {},
        "output_map": {},
    }


def load_config() -> dict[str, Any]:
    p.ensure_eval_dir()
    cfg = default_config()
    path = ORCH_CONFIG_PATH if ORCH_CONFIG_PATH.exists() else LEGACY_CONFIG_PATH
    if path.exists():
        cfg.update(json.loads(path.read_text(encoding="utf-8")))
    for legacy_key in ("agent_name", "run_tests", "use_api_for_all_tasks", "api_base_url", "project_name"):
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
    clean = {k: cfg[k] for k in default_config() if k in cfg}
    for k in ("task_api_map", "output_map", "default_api_id"):
        if k in cfg:
            clean[k] = cfg[k]
    ORCH_CONFIG_PATH.write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")
    return clean


def orchestrator_status() -> dict[str, Any]:
    """Dashboard config block (legacy name kept for API compat)."""
    return {
        "config": load_config(),
        "config_path": str(ORCH_CONFIG_PATH.relative_to(ROOT)),
        "external_apis": p.load_external_apis(),
        "task_order": list(TASK_ORDER),
    }
