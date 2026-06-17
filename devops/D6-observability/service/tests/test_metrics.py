"""Tests for metrics endpoint."""

from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_exposes_prometheus_format() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "request_count_by_endpoint" in body
    assert "error_count" in body
