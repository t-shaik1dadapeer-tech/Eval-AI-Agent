import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.queue_service import clear_queue

SYSTEM_ROOT = Path(__file__).resolve().parents[2]
TEST_QUEUE = SYSTEM_ROOT / "shared" / "data" / "test_transactions.json"


@pytest.fixture(autouse=True)
def isolated_queue(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    queue_file = tmp_path / "transactions.json"
    queue_file.write_text("[]\n", encoding="utf-8")
    monkeypatch.setenv("TRANSACTIONS_QUEUE_FILE", str(queue_file))
    monkeypatch.setenv("FRAUD_SYSTEM_ROOT", str(SYSTEM_ROOT))
    yield
    if queue_file.exists():
        queue_file.unlink()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_valid_transaction(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    response = client.post(
        "/transactions",
        json={
            "transaction_id": "txn-001",
            "user_id": "user-123",
            "amount": 15000,
            "merchant": "electronics",
            "country": "IN",
        },
    )

    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "transaction_id": "txn-001"}

    queue_path = Path(os.environ["TRANSACTIONS_QUEUE_FILE"])
    queue = queue_path.read_text(encoding="utf-8")
    assert "txn-001" in queue
    assert "pending" in queue


def test_invalid_amount(client: TestClient) -> None:
    response = client.post(
        "/transactions",
        json={
            "transaction_id": "txn-002",
            "user_id": "user-123",
            "amount": -5,
            "merchant": "electronics",
            "country": "IN",
        },
    )

    assert response.status_code == 422


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}
