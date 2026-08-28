"""Tests for dataset ingestion CLI and activation safety guards."""

from __future__ import annotations

import csv
from pathlib import Path
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.dataset_metadata import DatasetMetadata
from backend.app.models.project_month import ProjectMonthObservation
from backend.cli.ingest import compute_sha256, ingest_canonical_csv


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    """Create a temporary valid canonical CSV for testing ingestion."""
    csv_file = tmp_path / "test_projects_monthly.csv"
    fields = [
        "project_code", "legacy_ocms_code", "pmgid", "project_name",
        "agency", "ministry", "sector", "state",
        "approval_date", "start_date", "original_completion_date", "revised_completion_date",
        "original_cost", "revised_cost", "cumulative_expenditure", "physical_progress",
        "report_month",
        "approval_date_raw", "start_date_raw", "original_completion_date_raw", "revised_completion_date_raw",
        "original_cost_raw", "revised_cost_raw", "cumulative_expenditure_raw", "physical_progress_raw",
        "source_file", "source_page", "source_pages", "source_row_number", "source_serial_number",
        "extraction_method",
    ]
    rows = [
        {
            "project_code": "100100",
            "legacy_ocms_code": "",
            "pmgid": "",
            "project_name": "Test Highway Expansion",
            "agency": "NHAI",
            "ministry": "ROAD TRANSPORT",
            "sector": "ROADS",
            "state": "KARNATAKA",
            "approval_date": "2021-04",
            "start_date": "2021-09",
            "original_completion_date": "2024-03",
            "revised_completion_date": "",
            "original_cost": "500.5",
            "revised_cost": "",
            "cumulative_expenditure": "320.0",
            "physical_progress": "65.0",
            "report_month": "2026-01",
            "approval_date_raw": "04/2021",
            "start_date_raw": "09/2021",
            "original_completion_date_raw": "03/2024",
            "revised_completion_date_raw": "",
            "original_cost_raw": "500.50",
            "revised_cost_raw": "",
            "cumulative_expenditure_raw": "320.00",
            "physical_progress_raw": "65.0%",
            "source_file": "FlashReport_January_2026.pdf",
            "source_page": "12",
            "source_pages": "",
            "source_row_number": "1",
            "source_serial_number": "1",
            "extraction_method": "table6-eight-column-v1",
        },
        {
            "project_code": "100100",
            "legacy_ocms_code": "",
            "pmgid": "",
            "project_name": "Test Highway Expansion",
            "agency": "NHAI",
            "ministry": "ROAD TRANSPORT",
            "sector": "ROADS",
            "state": "KARNATAKA",
            "approval_date": "2021-04",
            "start_date": "2021-09",
            "original_completion_date": "2024-03",
            "revised_completion_date": "2024-12",
            "original_cost": "500.5",
            "revised_cost": "550.0",
            "cumulative_expenditure": "380.0",
            "physical_progress": "75.0",
            "report_month": "2026-02",
            "approval_date_raw": "04/2021",
            "start_date_raw": "09/2021",
            "original_completion_date_raw": "03/2024",
            "revised_completion_date_raw": "12/2024",
            "original_cost_raw": "500.50",
            "revised_cost_raw": "550.00",
            "cumulative_expenditure_raw": "380.00",
            "physical_progress_raw": "75.0%",
            "source_file": "FlashReport_February_2026.pdf",
            "source_page": "12",
            "source_pages": "",
            "source_row_number": "1",
            "source_serial_number": "1",
            "extraction_method": "table6-eight-column-v1",
        },
    ]

    with csv_file.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    return csv_file


def test_ingest_activation_safety_unverified(db_session: Session, sample_csv_path: Path) -> None:
    """Ingestion without --dev or verified sha256 must default to INGESTED_UNVERIFIED."""
    meta = ingest_canonical_csv(
        csv_path=sample_csv_path,
        session=db_session,
        is_dev=False,
    )
    assert meta.status == "INGESTED_UNVERIFIED"
    assert meta.row_count == 2
    assert meta.unique_projects_count == 1
    assert meta.covered_months == ["2026-01", "2026-02"]


def test_ingest_activation_safety_dev_flag(db_session: Session, sample_csv_path: Path) -> None:
    """Ingestion with is_dev=True must mark dataset as ACTIVE."""
    meta = ingest_canonical_csv(
        csv_path=sample_csv_path,
        session=db_session,
        is_dev=True,
    )
    assert meta.status == "ACTIVE"


def test_ingest_activation_safety_matching_sha256(db_session: Session, sample_csv_path: Path) -> None:
    """Ingestion with verified expected sha256 must mark dataset as ACTIVE."""
    sha = compute_sha256(sample_csv_path)
    meta = ingest_canonical_csv(
        csv_path=sample_csv_path,
        session=db_session,
        expected_sha256=sha,
        is_dev=False,
    )
    assert meta.status == "ACTIVE"


def test_ingest_supersedes_previous_active(db_session: Session, sample_csv_path: Path) -> None:
    """A new ACTIVE dataset must transition previous ACTIVE dataset to SUPERSEDED."""
    # First active dataset
    meta1 = ingest_canonical_csv(
        csv_path=sample_csv_path,
        session=db_session,
        dataset_version="v1.0",
        is_dev=True,
    )
    assert meta1.status == "ACTIVE"

    # Second active dataset with clear_existing=True
    meta2 = ingest_canonical_csv(
        csv_path=sample_csv_path,
        session=db_session,
        dataset_version="v2.0",
        is_dev=True,
        clear_existing=True,
    )
    assert meta2.status == "ACTIVE"

    # Check that meta1 is now SUPERSEDED
    db_session.refresh(meta1)
    assert meta1.status == "SUPERSEDED"


def test_ingest_preserves_nulls_and_raw_fields(db_session: Session, sample_csv_path: Path) -> None:
    """Verify that empty canonical fields stay None without synthetic fallback."""
    ingest_canonical_csv(csv_path=sample_csv_path, session=db_session, is_dev=True)

    stmt = (
        select(ProjectMonthObservation)
        .where(
            ProjectMonthObservation.project_code == "100100",
            ProjectMonthObservation.report_month == "2026-01",
        )
    )
    obs = db_session.execute(stmt).scalar_one()
    assert obs.revised_cost is None
    assert obs.revised_completion_date is None
    assert obs.original_cost == 500.5
    assert obs.physical_progress == 65.0
    assert obs.original_cost_raw == "500.50"


def test_ingest_empty_csv_not_marked_active(db_session: Session, tmp_path: Path) -> None:
    """An empty CSV file (header only) must not be marked ACTIVE even if is_dev=True."""
    empty_csv = tmp_path / "empty_projects.csv"
    with empty_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["project_code", "report_month", "project_name"])

    meta = ingest_canonical_csv(csv_path=empty_csv, session=db_session, is_dev=True)
    assert meta.status == "EMPTY"
    assert meta.row_count == 0

