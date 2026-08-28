"""Structured error responses and custom exception handlers."""

from __future__ import annotations

import logging
from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

LOGGER = logging.getLogger("paimana.api.errors")


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found", details: Any | None = None) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class DatabaseConnectionError(AppException):
    """Database connectivity failure."""

    def __init__(self, message: str = "Database connection failed", details: Any | None = None) -> None:
        super().__init__(
            code="DATABASE_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class DatasetNotIngestedError(AppException):
    """Dataset has not yet been ingested into the serving layer."""

    def __init__(self, message: str = "Canonical dataset has not been ingested yet", details: Any | None = None) -> None:
        super().__init__(
            code="DATASET_NOT_INGESTED",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


def make_error_response(
    code: str,
    message: str,
    status_code: int,
    request: Request,
    details: Any | None = None,
) -> JSONResponse:
    """Build a structured JSON error response conforming to API error contract."""
    request_id = getattr(request.state, "request_id", None)
    payload = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "request_id": request_id,
    }
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        LOGGER.warning("Application exception: code=%s message=%s", exc.code, exc.message)
        return make_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            request=request,
            details=exc.details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            code = "NOT_FOUND"
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = "FORBIDDEN"
        elif exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            code = "SERVICE_UNAVAILABLE"

        message = exc.detail if exc.detail else "An HTTP error occurred"
        return make_error_response(
            code=code,
            message=message,
            status_code=exc.status_code,
            request=request,
            details=None,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        LOGGER.info("Validation error on %s: %s", request.url.path, exc.errors())
        return make_error_response(
            code="VALIDATION_ERROR",
            message="Invalid request parameters or payload",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            request=request,
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        LOGGER.exception("Unhandled internal exception on %s: %s", request.url.path, str(exc))
        return make_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request=request,
            details=None,
        )
