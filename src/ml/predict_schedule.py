"""Reusable, deterministic inference engine for IRIS schedule-extension prediction.

This module provides a framework-independent, stateless inference interface
(ScheduleExtensionPredictor) for scoring project-month observations using the
serialized production model artifacts.

Key guarantees:
1. Strict contract & input validation: unknown or missing features fail closed.
2. Safe regime selection: explicit or segment-derived based on frozen contract.
3. Deterministic scoring: identical probabilities and raw margin/logit scores.
4. Explainability compatibility: native inputs preserved for TreeSHAP (Legacy)
   and exact linear logit contribution reconciliation (Modern).
5. Zero dynamic retraining: no model fitting, threshold tuning, or request-time imputation.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import catboost as cb
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.ml.build_artifacts import DEFAULT_ARTIFACT_RELPATH, file_sha256
from src.ml.challenger_catboost import (
    CATEGORICAL_MISSING_SENTINEL,
    prepare_catboost_df,
)
from src.ml.dataset_builder import HORIZON, segment_for_month
from src.ml.evaluate_baselines import (
    CATEGORICAL_FEATURES,
    TARGET,
    FoldPreprocessor,
    _as_float,
)
from src.ml.operational_policy import LOCKED_FEATURES, LOCKED_MODELS
from src.ml.robustness_audit import FULL_V1_FEATURES, STATIC_AT_T_FEATURES


ALLOWED_METADATA_KEYS = {
    "project_code",
    "report_month",
    "identifier_regime",
    "continuous_segment",
}


@dataclass(frozen=True)
class PredictionResult:
    """Deterministic prediction result for a single project-month observation."""

    raw_score: float
    probability: float
    regime: str
    model_identifier: str
    target: str
    horizon_months: int
    contract_version: str
    features_used: list[str]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_score": self.raw_score,
            "probability": self.probability,
            "regime": self.regime,
            "model_identifier": self.model_identifier,
            "target": self.target,
            "horizon_months": self.horizon_months,
            "contract_version": self.contract_version,
            "features_used": list(self.features_used),
            "metadata": dict(self.metadata),
        }


class ScheduleExtensionPredictor:
    """Stateless forward-pass inference interface for locked schedule-extension models."""

    def __init__(
        self,
        artifacts_dir: Path,
        manifest: dict[str, Any],
        legacy_model: cb.CatBoostClassifier,
        modern_model: LogisticRegression,
        modern_preprocessor: FoldPreprocessor,
    ) -> None:
        self.artifacts_dir = artifacts_dir.resolve()
        self.manifest = manifest
        self.legacy_model = legacy_model
        self.modern_model = modern_model
        self.modern_preprocessor = modern_preprocessor

        self.contract_version = manifest.get("contract_version", "1.0.0")
        self.target = manifest.get("target", TARGET)
        self.horizon_months = manifest.get("horizon_months", HORIZON)

        self._legacy_features = list(manifest["models"]["LEGACY"]["feature_ordering"])
        self._modern_features = list(manifest["models"]["MODERN"]["feature_ordering"])

    @classmethod
    def load(
        cls,
        artifacts_dir: Path | str | None = None,
        verify_hashes: bool = True,
    ) -> "ScheduleExtensionPredictor":
        """Load serialized model artifacts and manifest from disk."""
        target_dir = Path(artifacts_dir) if artifacts_dir else DEFAULT_ARTIFACT_RELPATH
        target_dir = target_dir.resolve()

        manifest_path = target_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"Schedule model artifact manifest not found at {manifest_path}. "
                "Build artifacts first using src.ml.build_artifacts."
            )

        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        legacy_relpath = manifest["models"]["LEGACY"]["artifact_relpath"]
        modern_relpath = manifest["models"]["MODERN"]["artifact_relpath"]
        legacy_path = target_dir / legacy_relpath
        modern_path = target_dir / modern_relpath

        if not legacy_path.exists():
            raise FileNotFoundError(f"Legacy CatBoost artifact not found at {legacy_path}")
        if not modern_path.exists():
            raise FileNotFoundError(f"Modern Logistic artifact not found at {modern_path}")

        if verify_hashes:
            actual_legacy_sha = file_sha256(legacy_path)
            expected_legacy_sha = manifest["models"]["LEGACY"]["artifact_sha256"]
            if actual_legacy_sha != expected_legacy_sha:
                raise ValueError(
                    f"Legacy CatBoost SHA-256 mismatch: expected {expected_legacy_sha}, got {actual_legacy_sha}"
                )

            actual_modern_sha = file_sha256(modern_path)
            expected_modern_sha = manifest["models"]["MODERN"]["artifact_sha256"]
            if actual_modern_sha != expected_modern_sha:
                raise ValueError(
                    f"Modern Logistic SHA-256 mismatch: expected {expected_modern_sha}, got {actual_modern_sha}"
                )

        legacy_model = cb.CatBoostClassifier()
        legacy_model.load_model(str(legacy_path), format="cbm")

        modern_bundle = joblib.load(modern_path)
        modern_model = modern_bundle["model"]
        modern_preprocessor = modern_bundle["preprocessor"]

        return cls(
            artifacts_dir=target_dir,
            manifest=manifest,
            legacy_model=legacy_model,
            modern_model=modern_model,
            modern_preprocessor=modern_preprocessor,
        )

    def resolve_regime(
        self,
        regime: str | None = None,
        report_month: str | None = None,
    ) -> str:
        """Resolve and validate the appropriate model regime without silent boundary crossing."""
        if regime is not None:
            regime_upper = regime.strip().upper()
            if regime_upper not in ("LEGACY", "MODERN"):
                raise ValueError(f"Unsupported regime '{regime}'. Must be 'LEGACY' or 'MODERN'.")
            if report_month is not None:
                seg_info = segment_for_month(report_month)
                if seg_info is None:
                    raise ValueError(
                        f"Cannot assign report_month '{report_month}' to a continuous model segment. "
                        "Month is unassigned, outside contract range, or falls in a structural gap month "
                        "(e.g. 2023-12, 2024-04, 2024-05)."
                    )
                _, expected_regime = seg_info
                if regime_upper != expected_regime:
                    raise ValueError(
                        f"Declared regime '{regime_upper}' contradicts contract segment regime "
                        f"'{expected_regime}' for month '{report_month}'."
                    )
            return regime_upper

        if report_month is not None:
            seg_info = segment_for_month(report_month)
            if seg_info is None:
                raise ValueError(
                    f"Cannot assign report_month '{report_month}' to a continuous model segment. "
                    "Month is unassigned, outside contract range, or falls in a structural gap month "
                    "(e.g. 2023-12, 2024-04, 2024-05)."
                )
            _, seg_regime = seg_info
            return seg_regime

        raise ValueError(
            "Regime could not be determined. Explicit 'regime' or valid 'report_month' must be provided."
        )

    def get_features_for_regime(self, regime: str) -> list[str]:
        """Return the exact ordered list of features required for the regime."""
        if regime == "LEGACY":
            return list(self._legacy_features)
        if regime == "MODERN":
            return list(self._modern_features)
        raise ValueError(f"Unknown regime '{regime}'")

    def validate_row(
        self,
        row: dict[str, Any],
        regime: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Validate input row against contract and return (features_dict, metadata_dict)."""
        required_features = self.get_features_for_regime(regime)
        required_set = set(required_features)
        provided_keys = set(row.keys())

        missing = required_set - provided_keys
        if missing:
            raise ValueError(
                f"Missing {len(missing)} required features for {regime} model: {sorted(missing)}"
            )

        unknown = provided_keys - required_set - ALLOWED_METADATA_KEYS
        if unknown:
            raise ValueError(
                f"Unknown / prohibited feature inputs not accepted in contract: {sorted(unknown)}"
            )

        validated_features: dict[str, Any] = {}
        for feature in required_features:
            raw_val = row[feature]
            if feature in CATEGORICAL_FEATURES:
                validated_features[feature] = (
                    raw_val.strip() if isinstance(raw_val, str) else str(raw_val or "")
                )
            else:
                if raw_val is None or raw_val == "":
                    validated_features[feature] = ""
                elif isinstance(raw_val, (int, float, np.integer, np.floating)):
                    if math.isnan(float(raw_val)):
                        validated_features[feature] = ""
                    else:
                        validated_features[feature] = str(float(raw_val))
                elif isinstance(raw_val, str):
                    val_str = raw_val.strip()
                    if val_str == "":
                        validated_features[feature] = ""
                    else:
                        try:
                            f_val = float(val_str)
                            validated_features[feature] = (
                                "" if math.isnan(f_val) else str(f_val)
                            )
                        except ValueError as exc:
                            raise ValueError(
                                f"Invalid numeric value '{raw_val}' for feature '{feature}': {exc}"
                            ) from exc
                else:
                    raise ValueError(
                        f"Unsupported type {type(raw_val)} for numeric feature '{feature}': {raw_val}"
                    )

        metadata: dict[str, Any] = {
            k: row[k] for k in ALLOWED_METADATA_KEYS if k in row and row[k] is not None
        }
        return validated_features, metadata

    def predict_one(
        self,
        features: dict[str, Any],
        regime: str | None = None,
        report_month: str | None = None,
    ) -> PredictionResult:
        """Run deterministic forward-pass inference on a single observation."""
        return self.predict_batch([features], regime=regime, report_month=report_month)[0]

    def predict_batch(
        self,
        rows: Sequence[dict[str, Any]],
        regime: str | None = None,
        report_month: str | None = None,
    ) -> list[PredictionResult]:
        """Run deterministic forward-pass inference on a sequence of observations."""
        if not rows:
            return []

        resolved_regime = self.resolve_regime(
            regime=regime,
            report_month=report_month or rows[0].get("report_month"),
        )
        required_features = self.get_features_for_regime(resolved_regime)

        validated_rows: list[dict[str, Any]] = []
        metadata_list: list[dict[str, Any]] = []
        for index, row in enumerate(rows):
            row_month = row.get("report_month")
            if row_month and row_month != report_month:
                row_regime = self.resolve_regime(report_month=row_month)
                if row_regime != resolved_regime:
                    raise ValueError(
                        f"Batch contains mixed regimes at index {index}: "
                        f"row month '{row_month}' requires '{row_regime}', but batch is '{resolved_regime}'."
                    )
            v_feat, v_meta = self.validate_row(row, resolved_regime)
            validated_rows.append(v_feat)
            metadata_list.append(v_meta)

        if resolved_regime == "LEGACY":
            x_df, cat_cols = prepare_catboost_df(validated_rows, required_features)
            pool = cb.Pool(
                x_df,
                cat_features=cat_cols if cat_cols else None,
                feature_names=required_features,
            )
            raw_scores = np.asarray(
                self.legacy_model.predict(pool, prediction_type="RawFormulaVal"), dtype=float
            ).reshape(-1)
            probabilities = np.asarray(
                self.legacy_model.predict_proba(pool)[:, 1], dtype=float
            ).reshape(-1)
            model_id = LOCKED_MODELS["LEGACY"]

        else:
            x_matrix = self.modern_preprocessor.transform(validated_rows)
            raw_scores = np.asarray(
                self.modern_model.decision_function(x_matrix), dtype=float
            ).reshape(-1)
            probabilities = np.asarray(
                self.modern_model.predict_proba(x_matrix)[:, 1], dtype=float
            ).reshape(-1)
            model_id = LOCKED_MODELS["MODERN"]

        results: list[PredictionResult] = []
        for i in range(len(rows)):
            results.append(
                PredictionResult(
                    raw_score=float(raw_scores[i]),
                    probability=float(probabilities[i]),
                    regime=resolved_regime,
                    model_identifier=model_id,
                    target=self.target,
                    horizon_months=self.horizon_months,
                    contract_version=self.contract_version,
                    features_used=required_features,
                    metadata=metadata_list[i],
                )
            )
        return results

    def get_model(self, regime: str) -> Any:
        """Return raw model object for explainability or inspection."""
        r = regime.strip().upper()
        if r == "LEGACY":
            return self.legacy_model
        if r == "MODERN":
            return self.modern_model
        raise ValueError(f"Unknown regime '{regime}'")

    def get_preprocessor(self, regime: str) -> FoldPreprocessor | None:
        """Return fitted preprocessor for Modern regime."""
        r = regime.strip().upper()
        if r == "MODERN":
            return self.modern_preprocessor
        if r == "LEGACY":
            return None
        raise ValueError(f"Unknown regime '{regime}'")
