"""Tests for environment configuration and settings."""

from __future__ import annotations

import json
from backend.app.core.config import Settings


def test_default_settings() -> None:
    """Verify default configuration attributes."""
    s = Settings()
    assert s.PROJECT_NAME == "PAIMANA / IRIS API"
    assert s.API_V1_PREFIX == "/api/v1"
    assert s.ENVIRONMENT in ["development", "testing", "staging", "production"]
    assert len(s.BACKEND_CORS_ORIGINS) >= 1


def test_cors_origins_parsing_comma_separated() -> None:
    """Verify CORS origins parsing from comma-separated string."""
    s = Settings(BACKEND_CORS_ORIGINS="http://localhost:3000, https://myapp.com")
    assert s.BACKEND_CORS_ORIGINS == ["http://localhost:3000", "https://myapp.com"]


def test_cors_origins_parsing_json_array() -> None:
    """Verify CORS origins parsing from JSON array string."""
    json_origins = json.dumps(["http://localhost:8080", "https://dashboard.org"])
    s = Settings(BACKEND_CORS_ORIGINS=json_origins)
    assert s.BACKEND_CORS_ORIGINS == ["http://localhost:8080", "https://dashboard.org"]
