"""Health check endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import check_database_connection, get_db
from backend.app.schemas.health import AppStatus, DatabaseStatus, HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System and Database Health Check",
    description="Check backend operational status and live database connectivity.",
    responses={
        status.HTTP_200_OK: {"description": "Backend and database are healthy"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database is unreachable or degraded"},
    },
)
def get_health(
    response: Response,
    db: Session = Depends(get_db),
) -> HealthResponse:
    """Evaluate application and database health."""
    db_connected, _ = check_database_connection(db)

    now = datetime.now(timezone.utc)
    if db_connected:
        return HealthResponse(
            status=AppStatus.HEALTHY,
            database=DatabaseStatus.CONNECTED,
            environment=settings.ENVIRONMENT,
            version=settings.VERSION,
            timestamp=now,
        )

    # If database is unreachable, flag response as 503 Service Unavailable
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status=AppStatus.UNHEALTHY,
        database=DatabaseStatus.DISCONNECTED,
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        timestamp=now,
    )
