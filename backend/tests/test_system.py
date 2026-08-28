"""Tests for the GET /api/v1/system/dataset-info endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.dataset_metadata import DatasetMetadata


def test_dataset_info_empty_state(client: TestClient) -> None:
    """Verify endpoint honestly reports NOT_INGESTED when no metadata exists."""
    response = client.get("/api/v1/system/dataset-info")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "NOT_INGESTED"
    assert data["dataset_version"] is None
    assert data["canonical_sha256"] is None
    assert data["row_count"] == 0
    assert data["unique_projects_count"] == 0
    assert data["covered_months"] == []
    assert data["ingested_at"] is None


def test_dataset_info_metadata_with_zero_rows_returns_not_ingested(
    client: TestClient,
    db_session: Session,
) -> None:
    """Verify that an ACTIVE metadata record with row_count=0 reports NOT_INGESTED."""
    empty_meta = DatasetMetadata(
        dataset_version="empty_v1",
        canonical_sha256="0000000000000000000000000000000000000000000000000000000000000000",
        covered_months=[],
        row_count=0,
        unique_projects_count=0,
        source_version_identifier="paimana-empty",
        status="ACTIVE",
        ingested_at=datetime.now(timezone.utc),
    )
    db_session.add(empty_meta)
    db_session.commit()

    response = client.get("/api/v1/system/dataset-info")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "NOT_INGESTED"
    assert data["dataset_version"] is None
    assert data["canonical_sha256"] is None
    assert data["row_count"] == 0
    assert data["covered_months"] == []


def test_dataset_info_unverified_metadata_reports_not_ingested(
    client: TestClient,
    db_session: Session,
) -> None:
    """Verify that an unverified dataset record does not report ACTIVE."""
    unverified_meta = DatasetMetadata(
        dataset_version="unverified_v1",
        canonical_sha256="ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890",
        covered_months=["2026-01"],
        row_count=100,
        unique_projects_count=50,
        source_version_identifier="paimana-unverified",
        status="INGESTED_UNVERIFIED",
        ingested_at=datetime.now(timezone.utc),
    )
    db_session.add(unverified_meta)
    db_session.commit()

    response = client.get("/api/v1/system/dataset-info")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "NOT_INGESTED"
    assert data["row_count"] == 0


def test_dataset_info_populated_state(client: TestClient, db_session: Session) -> None:
    """Verify endpoint returns active dataset metadata when present with valid row_count."""
    meta = DatasetMetadata(
        dataset_version="2024-01_to_2026-07_v1",
        canonical_sha256="FE115E5FE71CC70552669FC4E0ACC2699B14CFE7545A319EEAEAF577E4DB95C3",
        covered_months=["2024-01", "2024-02", "2024-03", "2024-06", "2026-07"],
        row_count=46568,
        unique_projects_count=4412,
        source_version_identifier="paimana-export-v1",
        status="ACTIVE",
        ingested_at=datetime.now(timezone.utc),
    )
    db_session.add(meta)
    db_session.commit()

    response = client.get("/api/v1/system/dataset-info")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ACTIVE"
    assert data["dataset_version"] == "2024-01_to_2026-07_v1"
    assert data["canonical_sha256"] == "FE115E5FE71CC70552669FC4E0ACC2699B14CFE7545A319EEAEAF577E4DB95C3"
    assert data["row_count"] == 46568
    assert data["unique_projects_count"] == 4412
    assert len(data["covered_months"]) == 5
