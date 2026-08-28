"""Tests for error handling, exception handlers, and request correlation IDs."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_404_structured_error(client: TestClient) -> None:
    """Verify structured response on 404 endpoints."""
    response = client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]
    assert "request_id" in data
    assert "X-Request-ID" in response.headers


def test_custom_request_id_propagation(client: TestClient) -> None:
    """Verify incoming X-Request-ID header is preserved in response."""
    custom_id = "custom-req-id-12345"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id
