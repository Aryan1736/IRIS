"""Tests for the GET /api/v1/health endpoint."""

from __future__ import annotations

from unittest.mock import patch
from fastapi.testclient import TestClient


def test_health_check_healthy(client: TestClient) -> None:
    """Verify health endpoint returns 200 and healthy status when DB is connected."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    assert "X-Request-ID" in response.headers


def test_health_check_database_down(client: TestClient) -> None:
    """Verify health endpoint returns 503 and unhealthy status when DB connection fails."""
    with patch("backend.app.api.v1.endpoints.health.check_database_connection", return_value=(False, "Connection refused")):
        response = client.get("/api/v1/health")
        assert response.status_code == 503

        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"


def test_ping_endpoint(client: TestClient) -> None:
    """Verify lightweight /ping and /api/v1/ping keep-alive endpoints."""
    for path in ("/ping", "/api/v1/ping"):
        response = client.get(path)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pong"
        assert "timestamp" in data
        assert "service" in data

