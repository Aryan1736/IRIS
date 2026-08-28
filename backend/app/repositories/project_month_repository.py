"""Repository for canonical project-month observations."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.project_month import ProjectMonthObservation


class ProjectMonthRepository:
    """Encapsulates database operations for ProjectMonthObservation."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_project_code_and_month(
        self,
        project_code: str,
        report_month: str,
    ) -> ProjectMonthObservation | None:
        """Fetch an observation by exact project_code and report_month."""
        stmt = select(ProjectMonthObservation).where(
            ProjectMonthObservation.project_code == project_code,
            ProjectMonthObservation.report_month == report_month,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def count(self) -> int:
        """Count total project-month observation rows in serving layer."""
        stmt = select(func.count(ProjectMonthObservation.id))
        return self.db.execute(stmt).scalar_one() or 0

    def count_distinct_projects(self) -> int:
        """Count distinct project codes across all observations."""
        stmt = select(func.count(func.distinct(ProjectMonthObservation.project_code)))
        return self.db.execute(stmt).scalar_one() or 0
