"""Pydantic schemas for ProjectMonthObservation records."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProjectMonthObservationRead(BaseModel):
    """Schema representing an ongoing project-month observation as served by the API."""

    id: int
    project_code: str
    legacy_ocms_code: str | None = None
    pmgid: str | None = None
    project_name: str
    agency: str | None = None
    ministry: str | None = None
    sector: str | None = None
    state: str | None = None

    approval_date: str | None = None
    start_date: str | None = None
    original_completion_date: str | None = None
    revised_completion_date: str | None = None

    original_cost: float | None = None
    revised_cost: float | None = None
    cumulative_expenditure: float | None = None
    physical_progress: float | None = None

    report_month: str

    approval_date_raw: str | None = None
    start_date_raw: str | None = None
    original_completion_date_raw: str | None = None
    revised_completion_date_raw: str | None = None
    original_cost_raw: str | None = None
    revised_cost_raw: str | None = None
    cumulative_expenditure_raw: str | None = None
    physical_progress_raw: str | None = None

    source_file: str
    source_page: int
    source_pages: str | None = None
    source_row_number: int | None = None
    source_serial_number: int | None = None
    extraction_method: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
