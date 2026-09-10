"""Unified risk serving predictor for the IRIS repository (PR-10).

This module provides a unified, deterministic, auditable, and fail-closed serving
interface (UnifiedRiskPredictor) across all three IRIS risk domains:
1. Schedule Extension Risk (Locked production model via ScheduleExtensionPredictor)
2. Cost Overrun Risk (Research-only, governed as NOT_READY_FOR_PRODUCTION)
3. Implementation Risk (Decision support, governed as VIABLE_WITH_LIMITATIONS, fail-closed serving)

Key guarantees:
- Parity: Exact numerical parity (< 1e-12) with standalone ScheduleExtensionPredictor.
- Fail-closed validation: Prohibited leakage, NaN, infinity, unknown features,
  missing features, contradictory regimes, and structural gap months fail closed.
- Governance preservation: Cost overrun is NEVER exposed as an autonomous production gate.
  Implementation risk is clearly labeled for decision support with human review.
- Immutability: No state or model parameter mutation during inference.
- Determinism: Repeated calls and call ordering produce identical responses.
"""

from __future__ import annotations

import copy
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from src.ml.build_artifacts import DEFAULT_ARTIFACT_RELPATH, file_sha256
from src.ml.dataset_builder import (
    COMPLETED_SHA256,
    HORIZON,
    ONGOING_SHA256,
    segment_for_month,
)
from src.ml.predict_schedule import (
    ALLOWED_METADATA_KEYS as SCHEDULE_ALLOWED_METADATA_KEYS,
    PredictionResult,
    ScheduleExtensionPredictor,
)

SERVING_CONTRACT_VERSION = "1.0.0"

MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

# Prohibited leakage fields across all three ML risk domains
PROHIBITED_LEAKAGE_FIELDS: frozenset[str] = frozenset(
    {
        # Schedule target & future outcome leakage
        "target_effective_schedule_ext_3m",
        "target_extension_3m",
        "extension_type",
        "baseline_completion_date",
        "target_event_revised_completion_date",
        # Cost overrun target & future outcome leakage
        "target_effective_cost_esc_3m",
        "cost_revision_type",
        "cost_diff",
        "target_event_revised_cost",
        "baseline_cost",
        "baseline_cost_source",
        # Implementation risk target & future outcome leakage
        "target_progress_stagnation_3m",
        "progress_stagnation_subtype",
        "delta_physical_progress_3m",
        "baseline_progress",
        "future_progress_t3",
        # Shared future / event / completion leakage
        "target_event_month",
        "target_window_end_month",
        "eventually_completed",
        "completion_report_month",
        "actual_completion_date",
        "completed_revised_cost",
        "completed_cumulative_expenditure",
    }
)

ALLOWED_TOP_LEVEL_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "project_id",
        "project_code",
        "report_month",
        "regime",
        "identifier_regime",
        "continuous_segment",
        "features",
    }
)

SCHEDULE_DECISION_THRESHOLD = 0.50

# Governance constants
GOVERNANCE_STATUS_SCHEDULE = "LOCKED_PRODUCTION"
GOVERNANCE_STATUS_COST = "NOT_READY_FOR_PRODUCTION"
GOVERNANCE_STATUS_IMPLEMENTATION = "VIABLE_WITH_LIMITATIONS"


@dataclass(frozen=True)
class DomainRiskResult:
    """Result for an individual risk domain."""

    status: str
    regime: str | None
    risk_score: float | None
    prediction: int | None
    threshold: float | None
    model_version: str | None
    operational_status: str
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "regime": self.regime,
            "risk_score": self.risk_score,
            "prediction": self.prediction,
            "threshold": self.threshold,
            "model_version": self.model_version,
            "operational_status": self.operational_status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class UnifiedRiskPredictionResult:
    """Deterministic unified risk serving output for a single project observation."""

    project_id: str | None
    report_month: str
    schedule_extension: DomainRiskResult
    cost_overrun: DomainRiskResult
    implementation_risk: DomainRiskResult
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "report_month": self.report_month,
            "schedule_extension": self.schedule_extension.to_dict(),
            "cost_overrun": self.cost_overrun.to_dict(),
            "implementation_risk": self.implementation_risk.to_dict(),
            "metadata": dict(self.metadata),
        }


class UnifiedRiskPredictor:
    """Stateless, deterministic unified risk predictor across all IRIS ML domains."""

    def __init__(
        self,
        schedule_predictor: ScheduleExtensionPredictor,
        artifacts_dir: Path,
        serving_contract_version: str = SERVING_CONTRACT_VERSION,
    ) -> None:
        self.schedule_predictor = schedule_predictor
        self.artifacts_dir = artifacts_dir.resolve()
        self.serving_contract_version = serving_contract_version

    @classmethod
    def load(
        cls,
        artifacts_dir: Path | str | None = None,
        verify_hashes: bool = True,
    ) -> "UnifiedRiskPredictor":
        """Load underlying production artifacts and initialize the unified predictor."""
        target_dir = Path(artifacts_dir) if artifacts_dir else DEFAULT_ARTIFACT_RELPATH
        target_dir = target_dir.resolve()

        schedule_predictor = ScheduleExtensionPredictor.load(
            artifacts_dir=target_dir,
            verify_hashes=verify_hashes,
        )

        return cls(
            schedule_predictor=schedule_predictor,
            artifacts_dir=target_dir,
        )

    def validate_request_structure(
        self, request: dict[str, Any]
    ) -> tuple[str | None, str, str | None, dict[str, Any]]:
        """Validate top-level request structure, leakage, numerics, and extract (project_id, report_month, regime, features)."""
        if not isinstance(request, dict):
            raise ValueError(f"Request must be a dictionary, got {type(request)}")

        # 1. Check prohibited leakage fields across the entire request
        all_keys = set(request.keys())
        if "features" in request and isinstance(request["features"], dict):
            all_keys.update(request["features"].keys())

        leakage_found = all_keys & PROHIBITED_LEAKAGE_FIELDS
        if leakage_found:
            raise ValueError(
                f"Prohibited leakage field(s) detected in request: {sorted(leakage_found)}"
            )

        # 2. Extract and validate report_month
        report_month = request.get("report_month")
        if not report_month or not isinstance(report_month, str):
            raise ValueError("Required field 'report_month' is missing or not a string.")
        report_month = report_month.strip()
        if not MONTH_PATTERN.fullmatch(report_month):
            raise ValueError(
                f"Invalid 'report_month' '{report_month}'. Must match YYYY-MM format."
            )

        # 3. Extract and validate project_id
        raw_project_id = request.get("project_id") or request.get("project_code")
        project_id: str | None = None
        if raw_project_id is not None:
            if not isinstance(raw_project_id, (str, int)):
                raise ValueError(
                    f"Invalid project_id type: {type(raw_project_id)}. Must be string or integer."
                )
            project_id = str(raw_project_id).strip()
            if not project_id:
                raise ValueError("project_id cannot be an empty string.")

        # 4. Extract and validate regime
        raw_regime = request.get("regime") or request.get("identifier_regime")
        regime: str | None = None
        if raw_regime is not None:
            if not isinstance(raw_regime, str):
                raise ValueError(f"Invalid regime type: {type(raw_regime)}. Must be string.")
            regime = raw_regime.strip().upper()
            if regime not in ("LEGACY", "MODERN"):
                raise ValueError(
                    f"Unsupported regime '{raw_regime}'. Must be 'LEGACY' or 'MODERN'."
                )

        # 5. Extract features dictionary
        if request.get("features") is not None:
            if not isinstance(request["features"], dict):
                raise ValueError("Field 'features' must be a dictionary.")
            features_dict = dict(request["features"])
        else:
            # Flat payload: any key that is not an allowed top-level metadata key is treated as a feature
            features_dict = {
                k: v
                for k, v in request.items()
                if k not in ALLOWED_TOP_LEVEL_METADATA_KEYS
            }


        # 6. Check for NaN and Infinity values in features
        for feat_name, feat_val in features_dict.items():
            if isinstance(feat_val, float):
                if math.isnan(feat_val):
                    raise ValueError(f"NaN value rejected for numeric feature '{feat_name}'.")
                if math.isinf(feat_val):
                    raise ValueError(f"Infinite value rejected for numeric feature '{feat_name}'.")
            elif isinstance(feat_val, str):
                s_val = feat_val.strip().lower()
                if s_val in ("nan", "+nan", "-nan"):
                    raise ValueError(f"NaN value rejected for numeric feature '{feat_name}'.")
                if s_val in ("inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"):
                    raise ValueError(f"Infinite value rejected for numeric feature '{feat_name}'.")

        return project_id, report_month, regime, features_dict

    def resolve_regime_and_segment(
        self, report_month: str, declared_regime: str | None = None
    ) -> tuple[int, str]:
        """Resolve continuous segment and regime, failing closed on structural gaps and contradictions."""
        seg_info = segment_for_month(report_month)
        if seg_info is None:
            raise ValueError(
                f"Cannot assign report_month '{report_month}' to a continuous model segment. "
                "Month is unassigned, outside contract range, or falls in a structural gap month "
                "(e.g. 2023-12, 2024-04, 2024-05)."
            )
        segment_id, contract_regime = seg_info

        if declared_regime is not None:
            regime_upper = declared_regime.strip().upper()
            if regime_upper != contract_regime:
                raise ValueError(
                    f"Declared regime '{regime_upper}' contradicts contract segment regime "
                    f"'{contract_regime}' for month '{report_month}'."
                )

        return segment_id, contract_regime

    def evaluate_schedule_extension(
        self,
        features: dict[str, Any],
        report_month: str,
        regime: str,
        project_id: str | None,
    ) -> DomainRiskResult:
        """Run schedule extension prediction through ScheduleExtensionPredictor."""
        # Prepare row for schedule predictor
        row = dict(features)
        if project_id:
            row["project_code"] = project_id
        row["report_month"] = report_month
        row["identifier_regime"] = regime

        try:
            pred_result: PredictionResult = self.schedule_predictor.predict_one(
                features=row,
                regime=regime,
                report_month=report_month,
            )

            risk_score = float(pred_result.probability)
            prediction = 1 if risk_score >= SCHEDULE_DECISION_THRESHOLD else 0

            return DomainRiskResult(
                status="AVAILABLE",
                regime=pred_result.regime,
                risk_score=risk_score,
                prediction=prediction,
                threshold=SCHEDULE_DECISION_THRESHOLD,
                model_version=pred_result.model_identifier,
                operational_status=GOVERNANCE_STATUS_SCHEDULE,
                reason=None,
            )
        except Exception as exc:
            # If the schedule predictor fails validation, let it raise or report
            raise exc

    def evaluate_cost_overrun(
        self,
        segment_id: str | int,
        regime: str,
    ) -> DomainRiskResult:
        """Evaluate Cost Overrun domain under PR-07 NOT_READY_FOR_PRODUCTION governance."""
        return DomainRiskResult(
            status="NOT_AVAILABLE",
            regime=regime,
            risk_score=None,
            prediction=None,
            threshold=None,
            model_version=None,
            operational_status=GOVERNANCE_STATUS_COST,
            reason=(
                "Cost overrun modeling is research-only and classified as NOT_READY_FOR_PRODUCTION "
                "under PR-07. Due to severe class imbalance (~2.18%) and low precision lift, "
                "no autonomous production model artifact is deployed for live scoring."
            ),
        )

    def evaluate_implementation_risk(
        self,
        segment_id: str | int,
        regime: str,
    ) -> DomainRiskResult:
        """Evaluate Implementation Risk domain under PR-09 VIABLE_WITH_LIMITATIONS governance."""
        # Segments 1 and 2 structurally omit physical progress
        if str(segment_id).upper() in ("SEGMENT_1", "SEGMENT_2", "1", "2"):
            return DomainRiskResult(
                status="INELIGIBLE",
                regime=regime,
                risk_score=None,
                prediction=None,
                threshold=None,
                model_version=None,
                operational_status=GOVERNANCE_STATUS_IMPLEMENTATION,
                reason=(
                    f"Observation falls in continuous Segment '{segment_id}' where physical progress "
                    "was structurally unavailable. Historical implementation risk cannot be evaluated."
                ),
            )

        # Segments 3 and 4: PR-09 evaluated candidate models for decision support, but no
        # production serialized predictor artifact exists in artifacts/ml/implementation_risk_model_v1/.
        # Per PR-10 requirements: fail closed and expose domain as unavailable without retraining.
        return DomainRiskResult(
            status="NOT_AVAILABLE",
            regime=regime,
            risk_score=None,
            prediction=None,
            threshold=None,
            model_version=None,
            operational_status=GOVERNANCE_STATUS_IMPLEMENTATION,
            reason=(
                "Implementation risk is classified as VIABLE_WITH_LIMITATIONS for decision support "
                "with human review under PR-09. However, no serialized production model artifact exists "
                "in artifacts/ml/implementation_risk_model_v1/ (evaluation artifacts only). "
                "Inference-time retraining is prohibited; serving fails closed until model serialization."
            ),
        )

    def predict_one(self, request: dict[str, Any]) -> dict[str, Any]:
        """Perform deterministic unified risk prediction on a single project observation."""
        project_id, report_month, declared_regime, features = (
            self.validate_request_structure(request)
        )

        # Resolve continuous segment and contract regime
        segment_id, resolved_regime = self.resolve_regime_and_segment(
            report_month=report_month,
            declared_regime=declared_regime,
        )

        # Evaluate Domain 1: Schedule Extension Risk
        schedule_res = self.evaluate_schedule_extension(
            features=features,
            report_month=report_month,
            regime=resolved_regime,
            project_id=project_id,
        )

        # Evaluate Domain 2: Cost Overrun Risk
        cost_res = self.evaluate_cost_overrun(
            segment_id=segment_id,
            regime=resolved_regime,
        )

        # Evaluate Domain 3: Implementation Risk
        impl_res = self.evaluate_implementation_risk(
            segment_id=segment_id,
            regime=resolved_regime,
        )

        metadata = {
            "serving_contract_version": self.serving_contract_version,
            "deterministic": True,
            "continuous_segment": segment_id,
            "governance": {
                "schedule_extension": GOVERNANCE_STATUS_SCHEDULE,
                "cost_overrun": GOVERNANCE_STATUS_COST,
                "implementation_risk": GOVERNANCE_STATUS_IMPLEMENTATION,
            },
        }

        unified_result = UnifiedRiskPredictionResult(
            project_id=project_id,
            report_month=report_month,
            schedule_extension=schedule_res,
            cost_overrun=cost_res,
            implementation_risk=impl_res,
            metadata=metadata,
        )

        return unified_result.to_dict()

    def predict_batch(
        self, requests: Sequence[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Perform deterministic unified risk prediction on a batch of project observations."""
        if not requests:
            return []

        # Process each request deterministically
        results = [self.predict_one(req) for req in requests]
        return results
