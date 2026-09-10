"""Risk intelligence and model-serving endpoints."""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.services.risk_service import (
    get_serving_repository,
    get_unified_risk_intelligence,
    get_unified_risk_predictor,
)
from src.serving.repository import ServingRepository, score_distribution
from src.serving.schemas import (
    DashboardOptionsResponse,
    HistoryResponse,
    ModelInfoResponse,
    ProjectListResponse,
    RiskRecord,
    SummaryResponse,
    UnifiedRiskProfileRequest,
    UnifiedRiskProfileResponse,
    UnifiedRiskRequest,
    UnifiedRiskResponse,
)

router = APIRouter()

MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
Regime = Literal["LEGACY", "MODERN"]


def _validate_month(value: str) -> str:
    if not MONTH_PATTERN.fullmatch(value):
        raise HTTPException(
            status_code=422, detail="report_month must use a valid YYYY-MM value"
        )
    return value


@router.get(
    "/options",
    response_model=DashboardOptionsResponse,
    summary="Get Risk Dashboard Options",
    description="Retrieve available evaluation report months, default active month, available regimes, and distinct non-null metadata filter values.",
)
def get_risk_options(
    report_month: Annotated[
        str | None, Query(description="Optional evaluation month as YYYY-MM")
    ] = None,
    repo: ServingRepository = Depends(get_serving_repository),
) -> dict[str, Any]:
    month = _validate_month(report_month) if report_month is not None else None
    try:
        return repo.dashboard_options(month)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="Get Portfolio Risk Summary",
    description="Retrieve portfolio-level score distributions, quantiles, regime metadata, sector risk summaries, and top-N ranked projects.",
)
def get_risk_summary(
    report_month: Annotated[str, Query(description="Evaluation month as YYYY-MM")],
    regime: Regime | None = None,
    top_n: Annotated[int, Query(ge=1, le=50, description="Number of top risk projects to include")] = 10,
    sector: str | None = None,
    agency: str | None = None,
    ministry: str | None = None,
    state: str | None = None,
    search: Annotated[str | None, Query(max_length=200)] = None,
    repo: ServingRepository = Depends(get_serving_repository),
) -> dict[str, Any]:
    month = _validate_month(report_month)
    normalized_search = search.strip() if search and search.strip() else None
    rows = repo.month_scores(
        month,
        regime,
        sector=sector,
        agency=agency,
        ministry=ministry,
        state=state,
        search=normalized_search,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Risk summary population not found")

    regimes: dict[str, dict[str, Any]] = {}
    for row in rows:
        item = regimes.setdefault(
            row["regime"],
            {
                "regime": row["regime"],
                "model_id": row["model_id"],
                "project_count": 0,
                "calibration_active": False,
            },
        )
        item["project_count"] += 1
        item["calibration_active"] = item["calibration_active"] or bool(
            row["calibration_active"]
        )

    top = [
        {
            "project_code": row["project_code"],
            "project_name": row["project_name"],
            "agency": row["agency"],
            "ministry": row["ministry"],
            "sector": row["sector"],
            "state": row["state"],
            "regime": row["regime"],
            "model_id": row["model_id"],
            "raw_probability": float(row["raw_probability"]),
            "risk_probability": float(row["risk_probability"]),
            "calibration_active": bool(row["calibration_active"]),
            "risk_rank": int(row["risk_rank"]),
            "risk_percentile": float(row["risk_percentile"]),
            "population_size": int(row["population_size"]),
        }
        for row in rows[:top_n]
    ]

    return {
        "report_month": month,
        "regime_filter": regime,
        "filters": {
            "regime": regime,
            "min_risk_probability": None,
            "max_risk_probability": None,
            "sector": sector,
            "agency": agency,
            "ministry": ministry,
            "state": state,
            "search": normalized_search,
        },
        "project_count": len(rows),
        "score_distribution": score_distribution(
            [float(row["risk_probability"]) for row in rows]
        ),
        "top_risk_projects": top,
        "regimes": [regimes[key] for key in sorted(regimes)],
        "sector_summary": repo.sector_summary(rows),
    }


@router.get(
    "/projects",
    response_model=ProjectListResponse,
    summary="List Ranked Risk Projects",
    description="Retrieve paginated list of evaluated projects strictly ordered by risk rank, including calibrated probabilities and signed feature contributors.",
)
def list_risk_projects(
    report_month: Annotated[str, Query(description="Evaluation month as YYYY-MM")],
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page (max 100)")] = 25,
    regime: Regime | None = None,
    min_risk_probability: Annotated[float | None, Query(ge=0.0, le=1.0, description="Minimum risk probability")] = None,
    max_risk_probability: Annotated[float | None, Query(ge=0.0, le=1.0, description="Maximum risk probability")] = None,
    sector: str | None = None,
    agency: str | None = None,
    ministry: str | None = None,
    state: str | None = None,
    search: Annotated[str | None, Query(max_length=200, description="Substring search on project code or name")] = None,
    repo: ServingRepository = Depends(get_serving_repository),
) -> dict[str, Any]:
    month = _validate_month(report_month)
    if (
        min_risk_probability is not None
        and max_risk_probability is not None
        and min_risk_probability > max_risk_probability
    ):
        raise HTTPException(
            status_code=422,
            detail="min_risk_probability cannot exceed max_risk_probability",
        )

    normalized_search = search.strip() if search and search.strip() else None
    total, items = repo.list_records(
        report_month=month,
        regime=regime,
        min_probability=min_risk_probability,
        max_probability=max_risk_probability,
        sector=sector,
        agency=agency,
        ministry=ministry,
        state=state,
        search=normalized_search,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No risk records match the query")

    return {
        "report_month": month,
        "filters": {
            "regime": regime,
            "min_risk_probability": min_risk_probability,
            "max_risk_probability": max_risk_probability,
            "sector": sector,
            "agency": agency,
            "ministry": ministry,
            "state": state,
            "search": normalized_search,
        },
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": items,
    }


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Get Model Governance and Architecture Info",
    description="Retrieve model families, features, explainability methods, calibration policies, and target specifications.",
)
def get_model_info(
    repo: ServingRepository = Depends(get_serving_repository),
) -> dict[str, Any]:
    return repo.model_info()


@router.get(
    "/project/{project_code}",
    response_model=RiskRecord,
    summary="Get Exact Project Risk Record",
    description="Retrieve the complete RiskRecord for a single project code in a specific report month, including signed TreeSHAP/logistic contributors.",
)
def get_project_risk_record(
    project_code: str,
    report_month: Annotated[str, Query(description="Evaluation month as YYYY-MM")],
    repo: ServingRepository = Depends(get_serving_repository),
) -> dict[str, Any]:
    record = repo.get_record(project_code, _validate_month(report_month))
    if record is None:
        raise HTTPException(status_code=404, detail="Project-month risk record not found")
    return record


@router.get(
    "/project/{project_code}/history",
    response_model=HistoryResponse,
    summary="Get Exact Project Risk History",
    description="Retrieve chronological risk history for an exact project code across all evaluated months. No crosswalk lookups or completion inferences.",
)
def get_project_risk_history(
    project_code: str,
    regime: Regime | None = None,
    repo: ServingRepository = Depends(get_serving_repository),
) -> dict[str, Any]:
    records = repo.history(project_code, regime)
    if not records:
        raise HTTPException(status_code=404, detail="Project risk history not found")
    return {
        "project_code": project_code,
        "regime_filter": regime,
        "count": len(records),
        "items": records,
    }


@router.post(
    "/unified",
    response_model=UnifiedRiskResponse,
    summary="Unified Multi-Domain Risk Prediction",
    description=(
        "Run deterministic, fail-closed multi-domain risk evaluation across Schedule Extension, "
        "Cost Overrun (research-only / NOT_READY_FOR_PRODUCTION), and Implementation Risk "
        "(decision support / VIABLE_WITH_LIMITATIONS). Requires valid contract features and report month."
    ),
)
@router.post(
    "/unified-risk",
    response_model=UnifiedRiskResponse,
    include_in_schema=False,
)
def predict_unified_risk(
    request: UnifiedRiskRequest,
    predictor: Any = Depends(get_unified_risk_predictor),
) -> dict[str, Any]:
    payload = request.model_dump()
    try:
        return predictor.predict_one(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}") from exc


@router.post(
    "/profile",
    response_model=UnifiedRiskProfileResponse,
    summary="Unified Multi-Domain Project Risk Profile",
    description=(
        "Generate a deterministic, governance-aware Project Risk Profile synthesizing "
        "Schedule Extension, Cost Overrun, and Implementation Risk. Enforces strict prohibitions "
        "on arbitrary probability aggregation while providing priority ordering, attention level, "
        "human-review recommendations, and explicit limitations."
    ),
)
@router.post(
    "/unified-profile",
    response_model=UnifiedRiskProfileResponse,
    include_in_schema=False,
)
def predict_unified_risk_profile(
    request: UnifiedRiskProfileRequest,
    intelligence: Any = Depends(get_unified_risk_intelligence),
) -> dict[str, Any]:
    payload = request.model_dump()
    try:
        return intelligence.predict_one(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}") from exc


@router.get(
    "/model-registry",
    summary="Get Authoritative ML Model Registry",
    description="Retrieve authoritative ML Model Registry and Governance metadata covering all risk domains.",
)
def get_model_registry() -> dict[str, Any]:
    from src.ml.model_registry import ModelRegistry
    return ModelRegistry.load().to_dict(mask_internal_paths=True)


@router.get(
    "/platform-contract",
    summary="Get Authoritative ML Platform Integration Contract",
    description="Retrieve authoritative ML Platform Integration Contract metadata, schemas, domain definitions, and governance boundaries.",
)
def get_platform_contract() -> dict[str, Any]:
    from src.ml.platform_contract import MLPlatformContract
    return MLPlatformContract.load().to_dict(mask_internal_paths=True)


