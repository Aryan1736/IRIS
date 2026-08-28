"""Service implementing domain logic for project observations and history."""

from __future__ import annotations

import math
from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError
from backend.app.repositories.project_repository import ProjectRepository
from backend.app.schemas.project_month import ProjectMonthObservationRead
from backend.app.schemas.projects import (
    CostRevisionPoint,
    FilterOptionsResponse,
    PaginatedProjectsResponse,
    ProjectCostRevisionsResponse,
    ProjectDetailResponse,
    ProjectScheduleExtensionsResponse,
    ProjectSummaryItem,
    ProjectTrajectoryPoint,
    ProjectTrajectoryResponse,
    QuickSearchResult,
    ScheduleExtensionPoint,
)


class ProjectService:
    """Business logic and aggregation for Project endpoints."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProjectRepository(db)

    def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        project_code: str | None = None,
        report_month: str | None = None,
        sector: str | None = None,
        state: str | None = None,
        agency: str | None = None,
        ministry: str | None = None,
        search: str | None = None,
        sort_by: str = "report_month",
        sort_order: str = "desc",
    ) -> PaginatedProjectsResponse:
        """Return paginated project observations with filters."""
        items, total = self.repo.list_projects(
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
        total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 1
        summary_items = [ProjectSummaryItem.model_validate(item) for item in items]

        return PaginatedProjectsResponse(
            items=summary_items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_filter_options(self) -> FilterOptionsResponse:
        """Return available dynamic filter options."""
        options = self.repo.get_filter_options()
        return FilterOptionsResponse(**options)

    def quick_search(self, query: str, limit: int = 10) -> list[QuickSearchResult]:
        """Perform lightweight autocomplete/discovery search."""
        if not query or not query.strip():
            return []
        results = self.repo.quick_search(query=query, limit=limit)
        return [QuickSearchResult(**r) for r in results]

    def get_project_detail(self, project_code: str) -> ProjectDetailResponse:
        """Return aggregated summary and latest snapshot for a specific project."""
        stats = self.repo.get_project_stats(project_code)
        if not stats:
            raise NotFoundError(f"Project with code '{project_code}' was not found in the serving layer.")

        latest_obs = self.repo.get_latest_observation(project_code)
        if latest_obs is None:
            raise NotFoundError(f"Observation for project '{project_code}' could not be loaded.")

        return ProjectDetailResponse(
            project_code=latest_obs.project_code,
            project_name=latest_obs.project_name,
            agency=latest_obs.agency,
            ministry=latest_obs.ministry,
            sector=latest_obs.sector,
            state=latest_obs.state,
            first_reported_month=stats["first_month"],
            latest_report_month=stats["latest_month"],
            total_observations_count=stats["total_count"],
            latest_observation=ProjectMonthObservationRead.model_validate(latest_obs),
        )

    def get_latest_snapshot(self, project_code: str) -> ProjectMonthObservationRead:
        """Return the exact latest observation record for a project."""
        obs = self.repo.get_latest_observation(project_code)
        if obs is None:
            raise NotFoundError(f"Project with code '{project_code}' was not found in the serving layer.")
        return ProjectMonthObservationRead.model_validate(obs)

    def get_trajectory(self, project_code: str) -> ProjectTrajectoryResponse:
        """Return full chronological trajectory of observations for a project."""
        observations = self.repo.get_trajectory(project_code)
        if not observations:
            raise NotFoundError(f"Project with code '{project_code}' was not found in the serving layer.")

        trajectory_points = [
            ProjectTrajectoryPoint(
                report_month=obs.report_month,
                original_cost=float(obs.original_cost) if obs.original_cost is not None else None,
                revised_cost=float(obs.revised_cost) if obs.revised_cost is not None else None,
                cumulative_expenditure=float(obs.cumulative_expenditure) if obs.cumulative_expenditure is not None else None,
                physical_progress=float(obs.physical_progress) if obs.physical_progress is not None else None,
                approval_date=obs.approval_date,
                start_date=obs.start_date,
                original_completion_date=obs.original_completion_date,
                revised_completion_date=obs.revised_completion_date,
                agency=obs.agency,
                ministry=obs.ministry,
                sector=obs.sector,
                state=obs.state,
            )
            for obs in observations
        ]

        latest = observations[-1]
        return ProjectTrajectoryResponse(
            project_code=project_code,
            project_name=latest.project_name,
            observations_count=len(observations),
            trajectory=trajectory_points,
        )

    def get_cost_revisions(self, project_code: str) -> ProjectCostRevisionsResponse:
        """Return historical cost revisions and latest cost ratio without subjective classification."""
        observations = self.repo.get_trajectory(project_code)
        if not observations:
            raise NotFoundError(f"Project with code '{project_code}' was not found in the serving layer.")

        revisions = [
            CostRevisionPoint(
                report_month=obs.report_month,
                original_cost=float(obs.original_cost) if obs.original_cost is not None else None,
                revised_cost=float(obs.revised_cost) if obs.revised_cost is not None else None,
                cumulative_expenditure=float(obs.cumulative_expenditure) if obs.cumulative_expenditure is not None else None,
                original_cost_raw=obs.original_cost_raw,
                revised_cost_raw=obs.revised_cost_raw,
                cumulative_expenditure_raw=obs.cumulative_expenditure_raw,
            )
            for obs in observations
        ]

        latest = observations[-1]
        latest_orig = float(latest.original_cost) if latest.original_cost is not None else None
        latest_rev = float(latest.revised_cost) if latest.revised_cost is not None else None

        cost_revision_ratio = None
        if latest_orig is not None and latest_rev is not None and latest_orig > 0:
            cost_revision_ratio = round(latest_rev / latest_orig, 4)

        return ProjectCostRevisionsResponse(
            project_code=project_code,
            project_name=latest.project_name,
            revisions=revisions,
            latest_original_cost=latest_orig,
            latest_revised_cost=latest_rev,
            cost_revision_ratio=cost_revision_ratio,
        )

    def get_schedule_extensions(self, project_code: str) -> ProjectScheduleExtensionsResponse:
        """Return historical milestone and completion date timeline without manufactured delay flags."""
        observations = self.repo.get_trajectory(project_code)
        if not observations:
            raise NotFoundError(f"Project with code '{project_code}' was not found in the serving layer.")

        timeline = [
            ScheduleExtensionPoint(
                report_month=obs.report_month,
                approval_date=obs.approval_date,
                start_date=obs.start_date,
                original_completion_date=obs.original_completion_date,
                revised_completion_date=obs.revised_completion_date,
                approval_date_raw=obs.approval_date_raw,
                original_completion_date_raw=obs.original_completion_date_raw,
                revised_completion_date_raw=obs.revised_completion_date_raw,
            )
            for obs in observations
        ]

        latest = observations[-1]
        return ProjectScheduleExtensionsResponse(
            project_code=project_code,
            project_name=latest.project_name,
            timeline=timeline,
            latest_original_completion_date=latest.original_completion_date,
            latest_revised_completion_date=latest.revised_completion_date,
        )
