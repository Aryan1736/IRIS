"""Deployment smoke tests verifying the real runtime serving artifact and endpoints."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.risk_service import get_serving_repository, reset_cached_repository, resolve_serving_dir
from src.serving.repository import ServingRepository

EXPECTED_SERVING_SQLITE_SHA256 = (
    "5D4574319F258328FF106C9B51AC4963D8CD6A3464DCE4A5AF4AD6210DEADC42"
)


def _compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def test_serving_artifacts_exist_and_hashes_match() -> None:
    """Verify that runtime serving files exist and match the locked SHA-256 hash."""
    serving_dir = resolve_serving_dir("data/serving")
    db_path = serving_dir / "iris_risk_serving_v1.sqlite3"
    manifest_path = serving_dir / "serving_manifest.json"

    assert db_path.is_file(), f"Missing serving database at {db_path}"
    assert manifest_path.is_file(), f"Missing serving manifest at {manifest_path}"

    actual_db_hash = _compute_sha256(db_path)
    assert actual_db_hash == EXPECTED_SERVING_SQLITE_SHA256, (
        f"Serving database hash mismatch: expected {EXPECTED_SERVING_SQLITE_SHA256}, got {actual_db_hash}"
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["database"]["sha256"] == EXPECTED_SERVING_SQLITE_SHA256
    assert manifest["serving_artifact_version"] == "iris_serving_v1_1"
    assert manifest["serving_contract_version"] == "1.1"
    assert manifest["target"] == "target_effective_schedule_ext_3m"
    assert manifest["record_counts"]["project_months"] == 25_189


def test_real_serving_repository_loads_without_mocking() -> None:
    """Verify that ServingRepository instantiates directly against the real on-disk artifact."""
    reset_cached_repository()
    serving_dir = resolve_serving_dir("data/serving")
    repo = ServingRepository(serving_dir)
    health = repo.health()
    assert health["status"] == "ok"
    assert health["project_month_records"] == 25_189
    assert health["target"] == "target_effective_schedule_ext_3m"


def test_real_risk_endpoints_return_actual_data(client: TestClient) -> None:
    """Smoke test real FastAPI endpoints serving the live SQLite artifact."""
    reset_cached_repository()
    # 1. Options endpoint
    options_res = client.get("/api/v1/risk/options")
    assert options_res.status_code == 200
    options = options_res.json()
    assert len(options["report_months"]) == 17
    assert options["default_report_month"] == "2026-04"
    assert options["selected_report_month"] == "2026-04"
    assert options["regimes"] == ["MODERN"]

    assert len(options["sectors"]) > 0
    assert len(options["agencies"]) > 0

    # 2. Summary endpoint
    summary_res = client.get("/api/v1/risk/summary", params={"report_month": "2026-04"})
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["project_count"] == 1625
    assert "score_distribution" in summary
    assert summary["score_distribution"]["minimum"] >= 0.0
    assert summary["score_distribution"]["maximum"] <= 1.0
    assert len(summary["top_risk_projects"]) == 10
    assert len(summary["sector_summary"]) > 0

    # 3. Projects ranked list
    projects_res = client.get(
        "/api/v1/risk/projects",
        params={"report_month": "2026-04", "page": 1, "page_size": 5},
    )
    assert projects_res.status_code == 200
    projects = projects_res.json()
    assert projects["total"] == 1625
    assert len(projects["items"]) == 5
    assert projects["items"][0]["risk_rank"] == 1
    assert projects["items"][0]["risk_percentile"] == 1.0
    assert len(projects["items"][0]["top_positive_contributors"]) > 0

    top_project_code = projects["items"][0]["project_code"]

    # 4. Project detail
    detail_res = client.get(
        f"/api/v1/risk/project/{top_project_code}",
        params={"report_month": "2026-04"},
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["project_code"] == top_project_code
    assert detail["report_month"] == "2026-04"
    assert detail["risk_rank"] == 1
    assert detail["target"] == "target_effective_schedule_ext_3m"

    # 5. Project history
    history_res = client.get(f"/api/v1/risk/project/{top_project_code}/history")
    assert history_res.status_code == 200
    history = history_res.json()
    assert history["project_code"] == top_project_code
    assert history["count"] >= 1

    # 6. Model info
    model_info_res = client.get("/api/v1/risk/model-info")
    assert model_info_res.status_code == 200
    model_info = model_info_res.json()
    assert model_info["status"] == "READY"
    assert model_info["target"] == "target_effective_schedule_ext_3m"
    assert len(model_info["models"]) == 2

    # 7. Direct proxy mount
    direct_res = client.get("/risk/options")
    assert direct_res.status_code == 200
    assert direct_res.json() == options
