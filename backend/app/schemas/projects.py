"""Pydantic schemas for project endpoints, listings, filters, trajectories, and history."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.project_month import ProjectMonthObservationRead


class ProjectSummaryItem(BaseModel):
    """Lightweight project summary for list and search results."""

    id: int
    project_code: str
    project_name: str
    agency: str | None = None
    ministry: str | None = None
    sector: str | None = None
    state: str | None = None
    report_month: str

    approval_date: str | None = None
    original_completion_date: str | None = None
    revised_completion_date: str | None = None

    original_cost: float | None = None
    revised_cost: float | None = None
    cumulative_expenditure: float | None = None
    physical_progress: float | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedProjectsResponse(BaseModel):
    """Paginated response envelope for project listings."""

    items: list[ProjectSummaryItem]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class FilterOptionsResponse(BaseModel):
    """Available dynamic filter options derived from current database observations."""

    sectors: list[str] = Field(default_factory=list)
    states: list[str] = Field(default_factory=list)
    agencies: list[str] = Field(default_factory=list)
    ministries: list[str] = Field(default_factory=list)
    report_months: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class QuickSearchResult(BaseModel):
    """Lightweight search result for autocomplete and quick discovery."""

    project_code: str
    project_name: str
    agency: str | None = None
    latest_report_month: str

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(BaseModel):
    """High-level summary and latest observation for a specific project_code."""

    project_code: str
    project_name: str
    agency: str | None = None
    ministry: str | None = None
    sector: str | None = None
    state: str | None = None
    first_reported_month: str
    latest_report_month: str
    total_observations_count: int
    latest_observation: ProjectMonthObservationRead

    model_config = ConfigDict(from_attributes=True)


class ProjectTrajectoryPoint(BaseModel):
    """Chronological observation point in a project's timeline."""

    report_month: str
    original_cost: float | None = None
    revised_cost: float | None = None
    cumulative_expenditure: float | None = None
    physical_progress: float | None = None

    approval_date: str | None = None
    start_date: str | None = None
    original_completion_date: str | None = None
    revised_completion_date: str | None = None

    agency: str | None = None
    ministry: str | None = None
    sector: str | None = None
    state: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectTrajectoryResponse(BaseModel):
    """Chronological historical trajectory of a project."""

    project_code: str
    project_name: str
    observations_count: int
    trajectory: list[ProjectTrajectoryPoint]

    model_config = ConfigDict(from_attributes=True)


class CostRevisionPoint(BaseModel):
    """Cost observation record for cost revision tracking."""

    report_month: str
    original_cost: float | None = None
    revised_cost: float | None = None
    cumulative_expenditure: float | None = None
    original_cost_raw: str | None = None
    revised_cost_raw: str | None = None
    cumulative_expenditure_raw: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectCostRevisionsResponse(BaseModel):
    """Historical cost revision data for a project."""

    project_code: str
    project_name: str
    revisions: list[CostRevisionPoint]
    latest_original_cost: float | None = None
    latest_revised_cost: float | None = None
    cost_revision_ratio: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ScheduleExtensionPoint(BaseModel):
    """Schedule milestone observation record."""

    report_month: str
    approval_date: str | None = None
    start_date: str | None = None
    original_completion_date: str | None = None
    revised_completion_date: str | None = None
    approval_date_raw: str | None = None
    original_completion_date_raw: str | None = None
    revised_completion_date_raw: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectScheduleExtensionsResponse(BaseModel):
    """Historical schedule timeline and completion date evolution."""

    project_code: str
    project_name: str
    timeline: list[ScheduleExtensionPoint]
    latest_original_completion_date: str | None = None
    latest_revised_completion_date: str | None = None

    model_config = ConfigDict(from_attributes=True)
