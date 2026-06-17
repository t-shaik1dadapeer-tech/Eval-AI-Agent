from fastapi.testclient import TestClient


def test_valid_conversion(client: TestClient) -> None:
    response = client.post(
        "/convert",
        json={"amount": 100, "from_currency": "USD", "to_currency": "INR"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == 100
    assert body["from_currency"] == "USD"
    assert body["to_currency"] == "INR"
    assert body["converted_amount"] == 8300.0


def test_invalid_currency(client: TestClient) -> None:
    response = client.post(
        "/convert",
        json={"amount": 100, "from_currency": "USD", "to_currency": "GBP"},
    )
    assert response.status_code == 422


def test_invalid_amount(client: TestClient) -> None:
    response = client.post(
        "/convert",
        json={"amount": -10, "from_currency": "USD", "to_currency": "INR"},
    )
    assert response.status_code == 422


def test_unsupported_currency_pair(client: TestClient) -> None:
    response = client.post(
        "/convert",
        json={"amount": 100, "from_currency": "INR", "to_currency": "EUR"},
    )
    assert response.status_code == 400
    assert "No conversion rate" in response.json()["detail"]
