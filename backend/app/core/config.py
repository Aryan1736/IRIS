"""Application configuration loaded from environment variables."""

from __future__ import annotations

import json
import re
from typing import Annotated, Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def sanitize_database_url(url: str) -> str:
    """Sanitize database URL to strip passwords and credentials for safe logging and error reporting."""
    if not url or not isinstance(url, str):
        return "<empty>"
    try:
        prefix = "jdbc:" if url.startswith("jdbc:") else ""
        raw = url[len(prefix):]
        parts = urlsplit(raw)

        # Sanitize authority credentials (user:password@host:port)
        netloc = parts.netloc
        if "@" in netloc:
            auth, host_port = netloc.split("@", 1)
            if ":" in auth:
                user, _ = auth.split(":", 1)
                auth = f"{user}:***"
            else:
                auth = "***"
            netloc = f"{auth}@{host_port}"

        # Sanitize query parameters containing sensitive keys
        if parts.query:
            query_pairs = parse_qsl(parts.query, keep_blank_values=True)
            sanitized_pairs = []
            for k, v in query_pairs:
                if k.lower() in ("password", "pwd", "secret", "token", "key"):
                    sanitized_pairs.append((k, "***"))
                else:
                    sanitized_pairs.append((k, v))
            query = urlencode(sanitized_pairs, safe="*")
        else:
            query = parts.query

        sanitized = urlunsplit((parts.scheme, netloc, parts.path, query, parts.fragment))
        return f"{prefix}{sanitized}"
    except Exception:
        clean = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)
        clean = re.sub(r"(password|pwd|token|secret)=([^&]+)", r"\1=***", clean, flags=re.IGNORECASE)
        return clean


def normalize_database_url(url: str) -> str:
    """Validate and normalize a database URL for SQLAlchemy engine creation.

    Supported schemes:
    - postgresql://...
    - postgresql+<driver>://... (e.g. postgresql+psycopg://, postgresql+psycopg2://)
    - jdbc:postgresql://... (normalized to postgresql://...)
    - jdbc:postgresql+<driver>://... (normalized to postgresql+<driver>://...)
    - postgres://... (normalized to postgresql://...)
    - sqlite://...
    """
    if not url or not isinstance(url, str) or not url.strip():
        raise ValueError("DATABASE_URL must be a non-empty string.")

    clean = url.strip()

    # Strip jdbc: prefix if present
    if clean.startswith("jdbc:"):
        clean = clean[5:]

    # Normalize legacy postgres:// to standard postgresql://
    if clean.startswith("postgres://"):
        clean = "postgresql://" + clean[11:]

    # Validate scheme
    if "://" not in clean:
        sanitized = sanitize_database_url(url)
        raise ValueError(f"Invalid database URL '{sanitized}': missing scheme separator '://'.")

    scheme = clean.split("://", 1)[0].lower()
    allowed_bases = ("postgresql", "sqlite")
    base_scheme = scheme.split("+", 1)[0]
    if base_scheme not in allowed_bases:
        sanitized = sanitize_database_url(url)
        raise ValueError(
            f"Unsupported database URL scheme '{scheme}' in '{sanitized}'. "
            f"Expected postgresql, postgresql+<driver>, or sqlite."
        )

    return clean


class Settings(BaseSettings):
    """Application settings using Pydantic v2 BaseSettings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "PAIMANA / IRIS API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    # Database Configuration
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/paimana_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Serving Artifact Configuration
    SERVING_DIR: str = "data/serving"

    # CORS Configuration
    FRONTEND_ORIGIN: str | None = None
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: Any) -> str:
        return normalize_database_url(v)

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass
        elif isinstance(v, (list, tuple)):
            return [str(item).strip() for item in v if str(item).strip()]
        return []

    def model_post_init(self, __context: Any) -> None:
        if self.FRONTEND_ORIGIN:
            origins = [o.strip() for o in self.FRONTEND_ORIGIN.split(",") if o.strip()]
            for origin in origins:
                if origin not in self.BACKEND_CORS_ORIGINS:
                    self.BACKEND_CORS_ORIGINS.append(origin)


settings = Settings()
