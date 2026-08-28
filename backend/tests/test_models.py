"""Tests for SQLAlchemy models, constraints, and repositories."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.project_month import ProjectMonthObservation
from backend.app.repositories.project_month_repository import ProjectMonthRepository


def test_create_project_month_observation_full(db_session: Session) -> None:
    """Verify persisting a project observation with all 31 canonical fields."""
    obs = ProjectMonthObservation(
        project_code="108480",
        legacy_ocms_code=None,
        pmgid=None,
        project_name="NEW BROAD GAUGE LINE BETWEEN JIND-SONIPAT",
        agency="NORTHERN RAILWAY",
        ministry="MINISTRY OF RAILWAYS",
        sector="RAILWAYS",
        state="HARYANA",
        approval_date="2003-12",
        start_date="2004-01",
        original_completion_date="2010-03",
        revised_completion_date="2026-03",
        original_cost=425.00,
        revised_cost=1184.27,
        cumulative_expenditure=1024.50,
        physical_progress=95.0,
        report_month="2026-07",
        approval_date_raw="12/2003",
        start_date_raw="01/2004",
        original_completion_date_raw="03/2010",
        revised_completion_date_raw="03/2026",
        original_cost_raw="425.00",
        revised_cost_raw="1184.27",
        cumulative_expenditure_raw="1024.50",
        physical_progress_raw="95.0",
        source_file="FlashReport_July_2026.pdf",
        source_page=55,
        source_pages="55",
        source_row_number=12,
        source_serial_number=1,
        extraction_method="pdfplumber-lines-v1",
    )
    db_session.add(obs)
    db_session.commit()

    repo = ProjectMonthRepository(db_session)
    fetched = repo.get_by_project_code_and_month("108480", "2026-07")
    assert fetched is not None
    assert fetched.project_name == "NEW BROAD GAUGE LINE BETWEEN JIND-SONIPAT"
    assert fetched.original_cost == 425.00
    assert fetched.physical_progress == 95.0
    assert repo.count() == 1
    assert repo.count_distinct_projects() == 1


def test_unique_constraint_project_code_and_report_month(db_session: Session) -> None:
    """Verify unique constraint on (project_code, report_month)."""
    obs1 = ProjectMonthObservation(
        project_code="108480",
        project_name="Project 1",
        report_month="2026-07",
        source_file="file1.pdf",
        source_page=1,
        extraction_method="pdfplumber-lines-v1",
    )
    obs2 = ProjectMonthObservation(
        project_code="108480",
        project_name="Project 1 Duplicate",
        report_month="2026-07",
        source_file="file2.pdf",
        source_page=2,
        extraction_method="pdfplumber-lines-v1",
    )

    db_session.add(obs1)
    db_session.commit()

    db_session.add(obs2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_nullable_fields_preservation(db_session: Session) -> None:
    """Verify legacy or approval-only layout records with structurally absent fields persist cleanly."""
    obs = ProjectMonthObservation(
        project_code="N12345678",  # Legacy 9-char code
        project_name="LEGACY PROJECT WITHOUT MINISTRY OR START DATE",
        report_month="2024-06",
        agency="NHAI",
        ministry=None,  # Structurally absent in legacy layout
        start_date=None,  # Structurally absent in legacy layout
        original_cost=500.0,
        revised_cost=None,
        cumulative_expenditure=None,
        physical_progress=None,
        source_file="FR_JUNE_2024.pdf",
        source_page=42,
        extraction_method="pdfplumber-lines-v1",
    )
    db_session.add(obs)
    db_session.commit()

    repo = ProjectMonthRepository(db_session)
    fetched = repo.get_by_project_code_and_month("N12345678", "2024-06")
    assert fetched is not None
    assert fetched.ministry is None
    assert fetched.start_date is None
    assert fetched.revised_cost is None
