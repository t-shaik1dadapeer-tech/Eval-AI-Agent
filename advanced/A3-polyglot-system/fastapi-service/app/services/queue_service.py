from __future__ import annotations

import json
import os
from pathlib import Path

from app.schemas.transaction import TransactionCreate

SYSTEM_ROOT = Path(
    os.environ.get(
        "FRAUD_SYSTEM_ROOT",
        Path(__file__).resolve().parents[3],
    )
)


def get_queue_file() -> Path:
    return Path(
        os.environ.get(
            "TRANSACTIONS_QUEUE_FILE",
            SYSTEM_ROOT / "shared" / "data" / "transactions.json",
        )
    )


def _ensure_queue_file() -> None:
    queue_file = get_queue_file()
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    if not queue_file.exists():
        queue_file.write_text("[]\n", encoding="utf-8")


def _read_queue() -> list[dict]:
    _ensure_queue_file()
    queue_file = get_queue_file()
    raw = queue_file.read_text(encoding="utf-8").strip() or "[]"
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("queue file must contain a JSON array")
    return data


def _write_queue(transactions: list[dict]) -> None:
    _ensure_queue_file()
    get_queue_file().write_text(json.dumps(transactions, indent=2) + "\n", encoding="utf-8")


def enqueue_transaction(payload: TransactionCreate) -> None:
    queue = _read_queue()
    entry = payload.model_dump()
    entry["status"] = "pending"
    queue.append(entry)
    _write_queue(queue)


def clear_queue() -> None:
    _write_queue([])
