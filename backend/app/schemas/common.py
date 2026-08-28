"""Common API schemas, response envelopes, and error contracts."""

from __future__ import annotations

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Standardized error detail representation."""
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    """Consistent API error envelope."""
    error: ErrorDetail
    request_id: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    """Standard API success response envelope."""
    data: T
    request_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
