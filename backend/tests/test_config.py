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


def test_frontend_origin_merged_into_cors() -> None:
    """Verify FRONTEND_ORIGIN is merged into BACKEND_CORS_ORIGINS."""
    s = Settings(
        FRONTEND_ORIGIN="https://iris-frontend.vercel.app, https://preview.vercel.app",
        BACKEND_CORS_ORIGINS="http://localhost:3000",
    )
    assert "https://iris-frontend.vercel.app" in s.BACKEND_CORS_ORIGINS
    assert "https://preview.vercel.app" in s.BACKEND_CORS_ORIGINS
    assert "http://localhost:3000" in s.BACKEND_CORS_ORIGINS


def test_database_url_normalization() -> None:
    """Verify postgres:// and postgresql:// are normalized to postgresql+psycopg2://."""
    s1 = Settings(DATABASE_URL="postgres://user:pass@host:5432/db?sslmode=require")
    assert s1.DATABASE_URL.startswith("postgresql+psycopg2://")

    s2 = Settings(DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require")
    assert s2.DATABASE_URL.startswith("postgresql+psycopg2://")

    s3 = Settings(DATABASE_URL="sqlite:///tmp/test.db")
    assert s3.DATABASE_URL == "sqlite:///tmp/test.db"
