import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.transaction_service import transaction_service


@pytest.fixture(autouse=True)
def clear_transactions() -> None:
    transaction_service.clear()
    yield
    transaction_service.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
