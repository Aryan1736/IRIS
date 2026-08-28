"""Tests for Core Project APIs (Pass 2)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.project_month import ProjectMonthObservation


@pytest.fixture
def sample_projects_data(db_session: Session) -> list[ProjectMonthObservation]:
    """Seed test database with multi-month project observations."""
    obs = [
        # Project 1 (Legacy era: N10000001) - 3 months
        ProjectMonthObservation(
            project_code="N10000001",
            project_name="Dedicated Freight Corridor Western",
            agency="DFCCIL",
            ministry="RAILWAYS",
            sector="RAILWAYS",
            state="MAHARASHTRA",
            report_month="2024-06",
            approval_date="2008-02",
            original_completion_date="2018-03",
            revised_completion_date="2024-12",
            original_cost=28181.0,
            revised_cost=51101.0,
            cumulative_expenditure=45000.0,
            physical_progress=85.0,
            source_file="FlashReport_June_2024.pdf",
            source_page=10,
            source_row_number=1,
            source_serial_number=1,
            extraction_method="legacy-nine-column-v1",
        ),
        ProjectMonthObservation(
            project_code="N10000001",
            project_name="Dedicated Freight Corridor Western",
            agency="DFCCIL",
            ministry="RAILWAYS",
            sector="RAILWAYS",
            state="MAHARASHTRA",
            report_month="2024-07",
            approval_date="2008-02",
            original_completion_date="2018-03",
            revised_completion_date="2025-03",
            original_cost=28181.0,
            revised_cost=51101.0,
            cumulative_expenditure=46000.0,
            physical_progress=88.0,
            source_file="FlashReport_July_2024.pdf",
            source_page=10,
            source_row_number=1,
            source_serial_number=1,
            extraction_method="legacy-nine-column-v1",
        ),
        ProjectMonthObservation(
            project_code="N10000001",
            project_name="Dedicated Freight Corridor Western",
            agency="DFCCIL",
            ministry="RAILWAYS",
            sector="RAILWAYS",
            state="MAHARASHTRA",
            report_month="2024-08",
            approval_date="2008-02",
            original_completion_date="2018-03",
            revised_completion_date="2025-06",
            original_cost=28181.0,
            revised_cost=52000.0,
            cumulative_expenditure=47500.0,
            physical_progress=90.0,
            source_file="FlashReport_August_2024.pdf",
            source_page=10,
            source_row_number=1,
            source_serial_number=1,
            extraction_method="legacy-nine-column-v1",
        ),
        # Project 2 (Modern era: 201234) - 2 months
        ProjectMonthObservation(
            project_code="201234",
            project_name="Mumbai Metro Line 4",
            agency="MMRDA",
            ministry="HOUSING AND URBAN AFFAIRS",
            sector="URBAN DEVELOPMENT",
            state="MAHARASHTRA",
            report_month="2025-08",
            approval_date="2016-10",
            start_date="2018-06",
            original_completion_date="2022-12",
            revised_completion_date="2026-12",
            original_cost=14549.0,
            revised_cost=18500.0,
            cumulative_expenditure=9200.0,
            physical_progress=55.0,
            source_file="FlashReport_August_2025.pdf",
            source_page=15,
            source_row_number=5,
            source_serial_number=5,
            extraction_method="table6-eight-column-v1",
        ),
        ProjectMonthObservation(
            project_code="201234",
            project_name="Mumbai Metro Line 4",
            agency="MMRDA",
            ministry="HOUSING AND URBAN AFFAIRS",
            sector="URBAN DEVELOPMENT",
            state="MAHARASHTRA",
            report_month="2025-09",
            approval_date="2016-10",
            start_date="2018-06",
            original_completion_date="2022-12",
            revised_completion_date="2026-12",
            original_cost=14549.0,
            revised_cost=18500.0,
            cumulative_expenditure=9400.0,
            physical_progress=57.0,
            source_file="FlashReport_September_2025.pdf",
            source_page=15,
            source_row_number=5,
            source_serial_number=5,
            extraction_method="table6-eight-column-v1",
        ),
        # Project 3 (Highway project with null revised cost) - 1 month
        ProjectMonthObservation(
            project_code="309999",
            project_name="NH-44 Widening Section B",
            agency="NHAI",
            ministry="ROAD TRANSPORT AND HIGHWAYS",
            sector="ROAD TRANSPORT AND HIGHWAYS",
            state="TELANGANA",
            report_month="2026-07",
            approval_date="2020-01",
            start_date="2020-06",
            original_completion_date="2024-06",
            revised_completion_date=None,
            original_cost=1200.0,
            revised_cost=None,
            cumulative_expenditure=1150.0,
            physical_progress=95.0,
            source_file="FlashReport_July_2026.pdf",
            source_page=42,
            source_row_number=20,
            source_serial_number=20,
            extraction_method="table6-eight-column-v1",
        ),
    ]
    for o in obs:
        db_session.add(o)
    db_session.commit()
    return obs


def test_list_projects_default_pagination(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects with default pagination."""
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] == 6
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total_pages"] == 1
    assert len(data["items"]) == 6


def test_list_projects_filtering(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects with various filter parameters."""
    # Filter by sector
    res_sector = client.get("/api/v1/projects?sector=URBAN")
    assert res_sector.status_code == 200
    assert res_sector.json()["total"] == 2

    # Filter by state
    res_state = client.get("/api/v1/projects?state=TELANGANA")
    assert res_state.status_code == 200
    assert res_state.json()["total"] == 1
    assert res_state.json()["items"][0]["project_code"] == "309999"

    # Filter by report_month
    res_month = client.get("/api/v1/projects?report_month=2024-06")
    assert res_month.status_code == 200
    assert res_month.json()["total"] == 1

    # Filter by search
    res_search = client.get("/api/v1/projects?search=Freight")
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 3


def test_list_projects_sorting(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects sorting options."""
    response = client.get("/api/v1/projects?sort_by=original_cost&sort_order=desc")
    assert response.status_code == 200
    items = response.json()["items"]
    # DFCCIL has 28181.0, NHAI has 1200.0
    assert items[0]["original_cost"] == 28181.0
    assert items[-1]["original_cost"] == 1200.0


def test_get_filter_options(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/filters/options."""
    response = client.get("/api/v1/projects/filters/options")
    assert response.status_code == 200
    data = response.json()
    assert "RAILWAYS" in data["sectors"]
    assert "URBAN DEVELOPMENT" in data["sectors"]
    assert "MAHARASHTRA" in data["states"]
    assert "TELANGANA" in data["states"]
    assert "DFCCIL" in data["agencies"]
    assert "2026-07" in data["report_months"]
    assert "2024-06" in data["report_months"]


def test_quick_search(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/search/quick."""
    # Search by code
    res_code = client.get("/api/v1/projects/search/quick?q=201234")
    assert res_code.status_code == 200
    data = res_code.json()
    assert len(data) >= 1
    assert data[0]["project_code"] == "201234"
    assert "Mumbai Metro" in data[0]["project_name"]

    # Search by name
    res_name = client.get("/api/v1/projects/search/quick?q=Metro")
    assert res_name.status_code == 200
    assert len(res_name.json()) >= 1


def test_get_project_detail_success(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/{project_code} for existing project."""
    response = client.get("/api/v1/projects/N10000001")
    assert response.status_code == 200
    data = response.json()
    assert data["project_code"] == "N10000001"
    assert data["project_name"] == "Dedicated Freight Corridor Western"
    assert data["first_reported_month"] == "2024-06"
    assert data["latest_report_month"] == "2024-08"
    assert data["total_observations_count"] == 3
    assert data["latest_observation"]["report_month"] == "2024-08"
    assert data["latest_observation"]["revised_cost"] == 52000.0


def test_get_project_detail_not_found(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/{project_code} with non-existent code."""
    response = client.get("/api/v1/projects/NON_EXISTENT_CODE")
    assert response.status_code == 404
    err = response.json()
    assert err["error"]["code"] == "NOT_FOUND"


def test_get_latest_snapshot(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/{project_code}/latest-snapshot."""
    response = client.get("/api/v1/projects/201234/latest-snapshot")
    assert response.status_code == 200
    data = response.json()
    assert data["project_code"] == "201234"
    assert data["report_month"] == "2025-09"
    assert data["physical_progress"] == 57.0


def test_get_trajectory_chronological(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/{project_code}/trajectory."""
    response = client.get("/api/v1/projects/N10000001/trajectory")
    assert response.status_code == 200
    data = response.json()
    assert data["project_code"] == "N10000001"
    assert data["observations_count"] == 3
    # Check chronological ordering
    months = [p["report_month"] for p in data["trajectory"]]
    assert months == ["2024-06", "2024-07", "2024-08"]


def test_get_cost_revisions(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/{project_code}/cost-revisions."""
    response = client.get("/api/v1/projects/N10000001/cost-revisions")
    assert response.status_code == 200
    data = response.json()
    assert data["project_code"] == "N10000001"
    assert len(data["revisions"]) == 3
    assert data["latest_original_cost"] == 28181.0
    assert data["latest_revised_cost"] == 52000.0
    assert data["cost_revision_ratio"] == round(52000.0 / 28181.0, 4)


def test_get_schedule_extensions(client: TestClient, sample_projects_data: list[ProjectMonthObservation]) -> None:
    """Test GET /api/v1/projects/{project_code}/schedule-extensions."""
    response = client.get("/api/v1/projects/201234/schedule-extensions")
    assert response.status_code == 200
    data = response.json()
    assert data["project_code"] == "201234"
    assert len(data["timeline"]) == 2
    assert data["latest_original_completion_date"] == "2022-12"
    assert data["latest_revised_completion_date"] == "2026-12"


def test_empty_database_responses(client: TestClient) -> None:
    """Verify honest responses when database is completely empty."""
    # List endpoint returns empty items
    res_list = client.get("/api/v1/projects")
    assert res_list.status_code == 200
    assert res_list.json()["items"] == []
    assert res_list.json()["total"] == 0

    # Filter options returns empty lists
    res_opt = client.get("/api/v1/projects/filters/options")
    assert res_opt.status_code == 200
    assert res_opt.json()["sectors"] == []
    assert res_opt.json()["report_months"] == []

    # Quick search returns empty
    res_search = client.get("/api/v1/projects/search/quick?q=rail")
    assert res_search.status_code == 200
    assert res_search.json() == []

    # Project detail returns 404
    res_detail = client.get("/api/v1/projects/N10000001")
    assert res_detail.status_code == 404
