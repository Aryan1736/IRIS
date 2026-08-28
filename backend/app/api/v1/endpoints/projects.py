"""Project REST endpoints for listings, filters, trajectories, and history."""

from __future__ import annotations

from typing import Literal
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.project_month import ProjectMonthObservationRead
from backend.app.schemas.projects import (
    FilterOptionsResponse,
    PaginatedProjectsResponse,
    ProjectCostRevisionsResponse,
    ProjectDetailResponse,
    ProjectScheduleExtensionsResponse,
    ProjectTrajectoryResponse,
    QuickSearchResult,
)
from backend.app.services.project_service import ProjectService

router = APIRouter()

SortByFields = Literal[
    "report_month",
    "project_name",
    "project_code",
    "original_cost",
    "revised_cost",
    "cumulative_expenditure",
    "physical_progress",
    "approval_date",
    "original_completion_date",
    "revised_completion_date",
]
SortOrder = Literal["asc", "desc"]


@router.get(
    "/projects",
    response_model=PaginatedProjectsResponse,
    summary="List Projects with Filtering and Pagination",
    description="Retrieve paginated list of project observations supporting sector, state, agency, report_month, and search filters.",
)
def list_projects(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    project_code: str | None = Query(default=None, description="Filter by project code (prefix or substring)"),
    report_month: str | None = Query(default=None, description="Exact report month, e.g. 2026-07"),
    sector: str | None = Query(default=None, description="Filter by sector"),
    state: str | None = Query(default=None, description="Filter by state"),
    agency: str | None = Query(default=None, description="Filter by implementing agency"),
    ministry: str | None = Query(default=None, description="Filter by ministry"),
    search: str | None = Query(default=None, description="Search by project name, project code, or agency"),
    sort_by: SortByFields = Query(default="report_month", description="Field to sort by"),
    sort_order: SortOrder = Query(default="desc", description="Sort direction (asc or desc)"),
    db: Session = Depends(get_db),
) -> PaginatedProjectsResponse:
    """Return paginated project observations."""
    service = ProjectService(db)
    return service.list_projects(
        page=page,
        page_size=page_size,
        project_code=project_code,
        report_month=report_month,
        sector=sector,
        state=state,
        agency=agency,
        ministry=ministry,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/projects/filters/options",
    response_model=FilterOptionsResponse,
    summary="Get Dynamic Filter Options",
    description="Retrieve distinct non-null values for sectors, states, agencies, ministries, and report months currently available in the database.",
)
def get_filter_options(
    db: Session = Depends(get_db),
) -> FilterOptionsResponse:
    """Return distinct filter options."""
    service = ProjectService(db)
    return service.get_filter_options()


@router.get(
    "/projects/search/quick",
    response_model=list[QuickSearchResult],
    summary="Quick Search for Projects",
    description="Lightweight endpoint matching project name or project code for discovery and autocomplete UI components.",
)
def quick_search(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results to return (max 50)"),
    db: Session = Depends(get_db),
) -> list[QuickSearchResult]:
    """Return quick search results."""
    service = ProjectService(db)
    return service.quick_search(query=q, limit=limit)


@router.get(
    "/projects/{project_code}",
    response_model=ProjectDetailResponse,
    summary="Get Project Detail by Project Code",
    description="Retrieve project-level summary metrics, observation span, and latest observation record.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Project code was not found in the database"},
    },
)
def get_project_detail(
    project_code: str = Path(..., description="Canonical source project identifier"),
    db: Session = Depends(get_db),
) -> ProjectDetailResponse:
    """Return project detail and latest observation."""
    service = ProjectService(db)
    return service.get_project_detail(project_code=project_code)


@router.get(
    "/projects/{project_code}/latest-snapshot",
    response_model=ProjectMonthObservationRead,
    summary="Get Latest Project Observation Snapshot",
    description="Retrieve the complete 31-field observation record from the latest available report month.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Project code was not found in the database"},
    },
)
def get_latest_snapshot(
    project_code: str = Path(..., description="Canonical source project identifier"),
    db: Session = Depends(get_db),
) -> ProjectMonthObservationRead:
    """Return complete latest observation record."""
    service = ProjectService(db)
    return service.get_latest_snapshot(project_code=project_code)


@router.get(
    "/projects/{project_code}/trajectory",
    response_model=ProjectTrajectoryResponse,
    summary="Get Chronological Project Trajectory",
    description="Retrieve full chronological timeline of monthly observations ordered by report_month ASC without artificial imputation.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Project code was not found in the database"},
    },
)
def get_trajectory(
    project_code: str = Path(..., description="Canonical source project identifier"),
    db: Session = Depends(get_db),
) -> ProjectTrajectoryResponse:
    """Return chronological project timeline."""
    service = ProjectService(db)
    return service.get_trajectory(project_code=project_code)


@router.get(
    "/projects/{project_code}/cost-revisions",
    response_model=ProjectCostRevisionsResponse,
    summary="Get Historical Cost Revisions",
    description="Retrieve chronological original, revised, and cumulative expenditure observations without subjective classification.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Project code was not found in the database"},
    },
)
def get_cost_revisions(
    project_code: str = Path(..., description="Canonical source project identifier"),
    db: Session = Depends(get_db),
) -> ProjectCostRevisionsResponse:
    """Return cost revision history."""
    service = ProjectService(db)
    return service.get_cost_revisions(project_code=project_code)


@router.get(
    "/projects/{project_code}/schedule-extensions",
    response_model=ProjectScheduleExtensionsResponse,
    summary="Get Historical Schedule & Milestone History",
    description="Retrieve chronological original and revised completion dates and start dates without manufactured delay classifications.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Project code was not found in the database"},
    },
)
def get_schedule_extensions(
    project_code: str = Path(..., description="Canonical source project identifier"),
    db: Session = Depends(get_db),
) -> ProjectScheduleExtensionsResponse:
    """Return schedule milestone history."""
    service = ProjectService(db)
    return service.get_schedule_extensions(project_code=project_code)
