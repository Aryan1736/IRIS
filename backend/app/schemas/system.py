"""System metadata schema definitions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class DatasetServingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NOT_INGESTED = "NOT_INGESTED"
    INGESTED_UNVERIFIED = "INGESTED_UNVERIFIED"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class DatasetInfoResponse(BaseModel):
    """Payload returned by GET /api/v1/system/dataset-info."""
    status: DatasetServingStatus
    dataset_version: str | None = None
    canonical_sha256: str | None = None
    covered_months: list[str] = []
    row_count: int = 0
    unique_projects_count: int | None = None
    source_version_identifier: str | None = None
    ingested_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
