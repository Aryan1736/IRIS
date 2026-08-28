"""Repository for project listing, search, filtering, and trajectory operations."""

from __future__ import annotations

from typing import Any
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.models.project_month import ProjectMonthObservation


class ProjectRepository:
    """Encapsulates database operations for Project entities and observations."""

    def __init__(self, db: Session) -> None:
        self.db = db

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
    ) -> tuple[list[ProjectMonthObservation], int]:
        """Query paginated project observations with dynamic filtering and sorting."""
        stmt = select(ProjectMonthObservation)
        count_stmt = select(func.count(ProjectMonthObservation.id))

        filters = []
        if project_code:
            filters.append(ProjectMonthObservation.project_code.ilike(f"%{project_code.strip()}%"))
        if report_month:
            filters.append(ProjectMonthObservation.report_month == report_month.strip())
        if sector:
            filters.append(ProjectMonthObservation.sector.ilike(f"%{sector.strip()}%"))
        if state:
            filters.append(ProjectMonthObservation.state.ilike(f"%{state.strip()}%"))
        if agency:
            filters.append(ProjectMonthObservation.agency.ilike(f"%{agency.strip()}%"))
        if ministry:
            filters.append(ProjectMonthObservation.ministry.ilike(f"%{ministry.strip()}%"))
        if search:
            search_clean = f"%{search.strip()}%"
            filters.append(
                or_(
                    ProjectMonthObservation.project_name.ilike(search_clean),
                    ProjectMonthObservation.project_code.ilike(search_clean),
                    ProjectMonthObservation.agency.ilike(search_clean),
                )
            )

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        # Determine sort column
        sort_column_map = {
            "report_month": ProjectMonthObservation.report_month,
            "project_name": ProjectMonthObservation.project_name,
            "project_code": ProjectMonthObservation.project_code,
            "original_cost": ProjectMonthObservation.original_cost,
            "revised_cost": ProjectMonthObservation.revised_cost,
            "cumulative_expenditure": ProjectMonthObservation.cumulative_expenditure,
            "physical_progress": ProjectMonthObservation.physical_progress,
            "approval_date": ProjectMonthObservation.approval_date,
            "original_completion_date": ProjectMonthObservation.original_completion_date,
            "revised_completion_date": ProjectMonthObservation.revised_completion_date,
        }
        col = sort_column_map.get(sort_by, ProjectMonthObservation.report_month)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(col.asc(), ProjectMonthObservation.id.asc())
        else:
            stmt = stmt.order_by(col.desc(), ProjectMonthObservation.id.desc())

        # Total count
        total = self.db.execute(count_stmt).scalar_one() or 0

        # Pagination
        offset_val = max(0, (page - 1) * page_size)
        stmt = stmt.offset(offset_val).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())

        return items, total

    def get_filter_options(self) -> dict[str, list[str]]:
        """Retrieve distinct non-null options for UI filters."""
        def _get_distinct(column: Any) -> list[str]:
            stmt = (
                select(column)
                .where(column.is_not(None), column != "")
                .distinct()
                .order_by(column.asc())
            )
            return [str(val) for val in self.db.execute(stmt).scalars().all() if val]

        sectors = _get_distinct(ProjectMonthObservation.sector)
        states = _get_distinct(ProjectMonthObservation.state)
        agencies = _get_distinct(ProjectMonthObservation.agency)
        ministries = _get_distinct(ProjectMonthObservation.ministry)

        # Report months sorted descending
        months_stmt = (
            select(ProjectMonthObservation.report_month)
            .where(ProjectMonthObservation.report_month.is_not(None))
            .distinct()
            .order_by(ProjectMonthObservation.report_month.desc())
        )
        report_months = [str(val) for val in self.db.execute(months_stmt).scalars().all() if val]

        return {
            "sectors": sectors,
            "states": states,
            "agencies": agencies,
            "ministries": ministries,
            "report_months": report_months,
        }

    def quick_search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Lightweight discovery search by project code or project name."""
        query_pattern = f"%{query.strip()}%"
        # Find distinct project codes matching query, with their latest record
        stmt = (
            select(
                ProjectMonthObservation.project_code,
                ProjectMonthObservation.project_name,
                ProjectMonthObservation.agency,
                func.max(ProjectMonthObservation.report_month).label("latest_month"),
            )
            .where(
                or_(
                    ProjectMonthObservation.project_code.ilike(query_pattern),
                    ProjectMonthObservation.project_name.ilike(query_pattern),
                    ProjectMonthObservation.agency.ilike(query_pattern),
                )
            )
            .group_by(
                ProjectMonthObservation.project_code,
                ProjectMonthObservation.project_name,
                ProjectMonthObservation.agency,
            )
            .order_by(func.max(ProjectMonthObservation.report_month).desc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "project_code": r.project_code,
                "project_name": r.project_name,
                "agency": r.agency,
                "latest_report_month": r.latest_month,
            }
            for r in rows
        ]

    def get_latest_observation(self, project_code: str) -> ProjectMonthObservation | None:
        """Fetch the single latest observation for a project_code."""
        stmt = (
            select(ProjectMonthObservation)
            .where(ProjectMonthObservation.project_code == project_code)
            .order_by(ProjectMonthObservation.report_month.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_trajectory(self, project_code: str) -> list[ProjectMonthObservation]:
        """Fetch all chronological observations for a project_code ordered by report_month ASC."""
        stmt = (
            select(ProjectMonthObservation)
            .where(ProjectMonthObservation.project_code == project_code)
            .order_by(ProjectMonthObservation.report_month.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_project_stats(self, project_code: str) -> dict[str, Any] | None:
        """Fetch summary statistics and observation span for a project_code."""
        stmt = (
            select(
                func.count(ProjectMonthObservation.id).label("total_count"),
                func.min(ProjectMonthObservation.report_month).label("first_month"),
                func.max(ProjectMonthObservation.report_month).label("latest_month"),
            )
            .where(ProjectMonthObservation.project_code == project_code)
        )
        row = self.db.execute(stmt).one()
        if not row or row.total_count == 0:
            return None
        return {
            "total_count": row.total_count,
            "first_month": row.first_month,
            "latest_month": row.latest_month,
        }
