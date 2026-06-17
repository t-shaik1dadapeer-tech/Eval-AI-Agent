from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extras import RealDictCursor


def get_database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://d2user:d2pass@localhost:5432/transactions",
    )


@contextmanager
def get_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    conn = psycopg2.connect(get_database_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def wait_for_database(max_attempts: int = 30, delay_seconds: float = 1.0) -> None:
    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return
        except Exception as exc:  # noqa: BLE001 - retry until DB ready
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError(f"database not ready after {max_attempts} attempts: {last_error}")


def insert_transaction(transaction_id: str, amount: float) -> dict:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO transactions (transaction_id, amount, status)
                VALUES (%s, %s, 'PENDING')
                RETURNING id, transaction_id, amount, status, created_at
                """,
                (transaction_id, amount),
            )
            row = cur.fetchone()
            return dict(row)


def list_transactions() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, transaction_id, amount, status, created_at
                FROM transactions
                ORDER BY id ASC
                """
            )
            return [dict(row) for row in cur.fetchall()]


def get_transaction_by_id(transaction_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, transaction_id, amount, status, created_at
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
