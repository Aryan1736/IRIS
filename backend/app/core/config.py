"""Application configuration loaded from environment variables."""

from __future__ import annotations

import json
from typing import Annotated, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("postgres://"):
                return v_clean.replace("postgres://", "postgresql+psycopg2://", 1)
            if v_clean.startswith("postgresql://") and not v_clean.startswith("postgresql+"):
                return v_clean.replace("postgresql://", "postgresql+psycopg2://", 1)
            return v_clean
        return str(v)

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
