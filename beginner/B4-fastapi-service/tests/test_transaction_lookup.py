from uuid import uuid4

from fastapi.testclient import TestClient


def test_get_transaction_by_id(client: TestClient) -> None:
    create_response = client.post(
        "/transactions",
        json={"type": "credit", "amount": 42.0, "description": "Lookup test"},
    )
    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]

    response = client.get(f"/transactions/{transaction_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == transaction_id
    assert body["type"] == "credit"
    assert body["amount"] == 42.0
    assert body["description"] == "Lookup test"


def test_get_transaction_not_found(client: TestClient) -> None:
    response = client.get(f"/transactions/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Transaction not found"}


def test_get_transaction_invalid_uuid(client: TestClient) -> None:
    response = client.get("/transactions/not-a-uuid")

    assert response.status_code == 422
