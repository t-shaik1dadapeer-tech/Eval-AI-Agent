from fastapi.testclient import TestClient


def test_create_transaction(client: TestClient) -> None:
    response = client.post(
        "/transactions",
        json={"type": "credit", "amount": 100.0, "description": "Salary"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "credit"
    assert body["amount"] == 100.0
    assert body["description"] == "Salary"
    assert "id" in body
    assert "created_at" in body


def test_get_transactions(client: TestClient) -> None:
    client.post("/transactions", json={"type": "credit", "amount": 50.0})
    client.post("/transactions", json={"type": "debit", "amount": 20.0})

    response = client.get("/transactions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["amount"] == 50.0
    assert body[1]["type"] == "debit"


def test_get_balance(client: TestClient) -> None:
    client.post("/transactions", json={"type": "credit", "amount": 100.0})
    client.post("/transactions", json={"type": "debit", "amount": 30.0})

    response = client.get("/balance")

    assert response.status_code == 200
    body = response.json()
    assert body["balance"] == 70.0
    assert body["transaction_count"] == 2


def test_invalid_transaction_validation(client: TestClient) -> None:
    response = client.post(
        "/transactions",
        json={"type": "credit", "amount": -10.0},
    )
    assert response.status_code == 422

    response = client.post(
        "/transactions",
        json={"type": "invalid", "amount": 10.0},
    )
    assert response.status_code == 422

    response = client.post(
        "/transactions",
        json={"type": "credit", "amount": 0},
    )
    assert response.status_code == 422


def test_debit_balance_calculation(client: TestClient) -> None:
    client.post("/transactions", json={"type": "credit", "amount": 200.0})
    client.post("/transactions", json={"type": "debit", "amount": 75.5})
    client.post("/transactions", json={"type": "debit", "amount": 24.5})

    response = client.get("/balance")

    assert response.status_code == 200
    assert response.json()["balance"] == 100.0
