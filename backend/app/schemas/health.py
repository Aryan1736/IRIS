"""Health check schema definitions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class AppStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DatabaseStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class HealthResponse(BaseModel):
    """Payload returned by GET /api/v1/health."""
    status: AppStatus
    database: DatabaseStatus
    environment: str
    version: str
    timestamp: datetime
