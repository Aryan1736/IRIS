"""Build reproducible, versioned schedule-extension model artifacts for IRIS.

This module fits the locked production schedule-extension models for both
supported regimes (Legacy CatBoost full_v1 and Modern Logistic static_only)
using strictly matured historical observations under the frozen contract (H=3).
It serializes the native model artifacts (.cbm and .joblib with FoldPreprocessor)
and generates a machine-readable artifact manifest with SHA-256 integrity digests.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any, Sequence

import catboost as cb
import joblib
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression

from src.ml.challenger_catboost import (
    CATBOOST_PARAMS,
    CATEGORICAL_MISSING_SENTINEL,
    prepare_catboost_df,
)
from src.ml.data_contract import (
    default_contract_path,
    load_contract,
    validate_canonical_inputs,
)
from src.ml.dataset_builder import (
    COMPLETED_SHA256,
    HORIZON,
    ONGOING_SHA256,
    SEGMENTS,
    add_months,
    month_index,
    segment_for_month,
    sha256,
    training_reference_is_embargo_safe,
)
from src.ml.evaluate_baselines import (
    CATEGORICAL_FEATURES,
    RANDOM_SEED,
    TARGET,
    FoldPreprocessor,
    _as_float,
)
from src.ml.operational_policy import LOCKED_FEATURES, LOCKED_MODELS
from src.ml.robustness_audit import FULL_V1_FEATURES, STATIC_AT_T_FEATURES


ARTIFACT_SCHEMA_VERSION = "1.0.0"
DEFAULT_ARTIFACT_RELPATH = Path("artifacts/ml/schedule_extension_3m")

PRODUCTION_BOUNDARIES = {
    "LEGACY": {
        "start_month": "2023-01",
        "cutoff_month": "2025-03",
        "target_matures_by": "2025-06",
        "rationale": (
            "Latest fully matured observation month in Segment 3 under H=3 horizon before "
            "the 2025-06 to 2025-07 identifier redesign regime boundary."
        ),
    },
    "MODERN": {
        "start_month": "2025-07",
        "cutoff_month": "2026-04",
        "target_matures_by": "2026-07",
        "rationale": (
            "Latest fully matured observation month in Segment 4 under H=3 horizon before "
            "the end of available canonical ongoing project data (2026-07)."
        ),
    },
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def select_production_training_rows(
    eligible_rows: Sequence[dict[str, str]], regime: str
) -> list[dict[str, str]]:
    """Select observations with fully matured target windows for production fitting."""
    boundary = PRODUCTION_BOUNDARIES[regime]
    cutoff_month = boundary["cutoff_month"]
    start_month = boundary["start_month"]
    rows = [
        row
        for row in eligible_rows
        if row["identifier_regime"] == regime
        and start_month <= row["report_month"] <= cutoff_month
    ]
    for row in rows:
        end_month = row["target_window_end_month"]
        if end_month > boundary["target_matures_by"]:
            raise RuntimeError(
                f"Production row label window {end_month} exceeds regime boundary "
                f"{boundary['target_matures_by']}"
            )
    return sorted(rows, key=lambda r: (r["report_month"], r["project_code"]))


def fit_and_serialize_legacy_catboost(
    training_rows: Sequence[dict[str, str]],
    output_path: Path,
) -> dict[str, Any]:
    """Train locked CatBoost model and save to native .cbm binary."""
    features = list(LOCKED_FEATURES["LEGACY"])
    x_train, cat_cols = prepare_catboost_df(training_rows, features)
    y_train = np.asarray([int(row[TARGET]) for row in training_rows], dtype=int)

    model = cb.CatBoostClassifier(
        **CATBOOST_PARAMS,
        auto_class_weights=None,
    )
    model.fit(
        x_train,
        y_train,
        cat_features=cat_cols if cat_cols else None,
        verbose=False,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(output_path), format="cbm")

    feature_importances = dict(zip(features, (float(v) for v in model.get_feature_importance())))
    return {
        "output_path": output_path,
        "sha256": file_sha256(output_path),
        "row_count": len(training_rows),
        "positive_count": int(y_train.sum()),
        "negative_count": int(len(y_train) - y_train.sum()),
        "feature_importances": feature_importances,
    }


def fit_and_serialize_modern_logistic(
    training_rows: Sequence[dict[str, str]],
    output_path: Path,
) -> dict[str, Any]:
    """Train locked FoldPreprocessor + LogisticRegression and save via joblib."""
    features = list(LOCKED_FEATURES["MODERN"])
    preprocessor = FoldPreprocessor(features).fit(training_rows)
    x_train = preprocessor.transform(training_rows)
    y_train = np.asarray([int(row[TARGET]) for row in training_rows], dtype=int)

    model = LogisticRegression(
        l1_ratio=0.0,
        C=1.0,
        solver="lbfgs",
        max_iter=2000,
        class_weight=None,
        random_state=RANDOM_SEED,
    )
    model.fit(x_train, y_train)

    bundle = {
        "model": model,
        "preprocessor": preprocessor,
        "model_identifier": LOCKED_MODELS["MODERN"],
        "regime": "MODERN",
        "features": features,
        "target": TARGET,
        "horizon_months": HORIZON,
        "random_seed": RANDOM_SEED,
        "training_metadata": {
            "row_count": len(training_rows),
            "positive_count": int(y_train.sum()),
            "negative_count": int(len(y_train) - y_train.sum()),
            "cutoff_month": PRODUCTION_BOUNDARIES["MODERN"]["cutoff_month"],
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, output_path, compress=3)

    return {
        "output_path": output_path,
        "sha256": file_sha256(output_path),
        "row_count": len(training_rows),
        "positive_count": int(y_train.sum()),
        "negative_count": int(len(y_train) - y_train.sum()),
        "intercept": float(model.intercept_[0]),
        "coefficient_count": len(model.coef_[0]),
        "transformed_columns": preprocessor.output_columns,
    }


def build_all_artifacts(
    root: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Build and serialize both schedule-extension model artifacts and manifest."""
    root = root.resolve()
    target_output_dir = (output_dir or (root / DEFAULT_ARTIFACT_RELPATH)).resolve()
    target_output_dir.mkdir(parents=True, exist_ok=True)

    contract = load_contract(default_contract_path(root))
    validate_canonical_inputs(root, contract)

    canonical_hashes = {
        "projects_monthly.csv": sha256(root / "data/processed/projects_monthly.csv"),
        "projects_completed.csv": sha256(root / "data/processed/projects_completed.csv"),
    }
    if canonical_hashes != {
        "projects_monthly.csv": ONGOING_SHA256,
        "projects_completed.csv": COMPLETED_SHA256,
    }:
        raise RuntimeError(f"Canonical inputs hash verification failed: {canonical_hashes}")

    dataset_dir = root / "data/ml/schedule_extension_3m"
    legacy_eligible_path = dataset_dir / "eligible_legacy.csv"
    modern_eligible_path = dataset_dir / "eligible_modern.csv"
    if not legacy_eligible_path.exists() or not modern_eligible_path.exists():
        raise FileNotFoundError(
            f"Approved eligible datasets missing in {dataset_dir}. Run src.ml.dataset_builder first."
        )

    legacy_rows = _read_csv(legacy_eligible_path)
    modern_rows = _read_csv(modern_eligible_path)

    legacy_train_rows = select_production_training_rows(legacy_rows, "LEGACY")
    modern_train_rows = select_production_training_rows(modern_rows, "MODERN")

    legacy_artifact_path = target_output_dir / "legacy_catboost/model.cbm"
    modern_artifact_path = target_output_dir / "modern_logistic/model.joblib"
    manifest_path = target_output_dir / "manifest.json"

    legacy_result = fit_and_serialize_legacy_catboost(legacy_train_rows, legacy_artifact_path)
    modern_result = fit_and_serialize_modern_logistic(modern_train_rows, modern_artifact_path)

    manifest: dict[str, Any] = {
        "manifest_version": ARTIFACT_SCHEMA_VERSION,
        "contract_version": contract.get("contract_version", "1.0.0"),
        "dataset_name": contract.get("dataset_name", "schedule_extension_3m_v1"),
        "target": TARGET,
        "horizon_months": HORIZON,
        "embargo_rule": "strict_walk_forward (T + 3 < E)",
        "canonical_inputs": {
            "projects_monthly.csv": ONGOING_SHA256,
            "projects_completed.csv": COMPLETED_SHA256,
        },
        "environment": {
            "python_version": platform.python_version(),
            "catboost_version": cb.__version__,
            "scikit_learn_version": sklearn.__version__,
            "numpy_version": np.__version__,
            "joblib_version": joblib.__version__,
        },
        "models": {
            "LEGACY": {
                "model_identifier": LOCKED_MODELS["LEGACY"],
                "model_family": "CatBoostClassifier",
                "regime": "LEGACY",
                "artifact_relpath": "legacy_catboost/model.cbm",
                "artifact_format": "cbm",
                "artifact_sha256": legacy_result["sha256"],
                "feature_count": len(LOCKED_FEATURES["LEGACY"]),
                "feature_ordering": list(LOCKED_FEATURES["LEGACY"]),
                "categorical_features": list(CATEGORICAL_FEATURES),
                "hyperparameters": {
                    "iterations": CATBOOST_PARAMS["iterations"],
                    "learning_rate": CATBOOST_PARAMS["learning_rate"],
                    "depth": CATBOOST_PARAMS["depth"],
                    "l2_leaf_reg": CATBOOST_PARAMS["l2_leaf_reg"],
                    "random_seed": CATBOOST_PARAMS["random_seed"],
                    "auto_class_weights": None,
                },
                "production_training_boundary": {
                    "start_month": PRODUCTION_BOUNDARIES["LEGACY"]["start_month"],
                    "cutoff_month": PRODUCTION_BOUNDARIES["LEGACY"]["cutoff_month"],
                    "target_matures_by": PRODUCTION_BOUNDARIES["LEGACY"]["target_matures_by"],
                    "training_row_count": legacy_result["row_count"],
                    "positive_row_count": legacy_result["positive_count"],
                    "negative_row_count": legacy_result["negative_count"],
                    "rationale": PRODUCTION_BOUNDARIES["LEGACY"]["rationale"],
                },
                "operational_calibration": "uncalibrated_raw_probabilities",
            },
            "MODERN": {
                "model_identifier": LOCKED_MODELS["MODERN"],
                "model_family": "LogisticRegression",
                "regime": "MODERN",
                "artifact_relpath": "modern_logistic/model.joblib",
                "artifact_format": "joblib",
                "artifact_sha256": modern_result["sha256"],
                "feature_count": len(LOCKED_FEATURES["MODERN"]),
                "feature_ordering": list(LOCKED_FEATURES["MODERN"]),
                "categorical_features": list(CATEGORICAL_FEATURES),
                "preprocessor": {
                    "type": "FoldPreprocessor",
                    "output_feature_count": len(modern_result["transformed_columns"]),
                    "categorical_encoding": "TRAIN_FREQUENCY",
                    "numeric_encoding": "TRAIN_STANDARDIZED + MISSING_INDICATOR",
                },
                "hyperparameters": {
                    "penalty": "l2",
                    "C": 1.0,
                    "solver": "lbfgs",
                    "max_iter": 2000,
                    "class_weight": None,
                    "random_state": RANDOM_SEED,
                },
                "production_training_boundary": {
                    "start_month": PRODUCTION_BOUNDARIES["MODERN"]["start_month"],
                    "cutoff_month": PRODUCTION_BOUNDARIES["MODERN"]["cutoff_month"],
                    "target_matures_by": PRODUCTION_BOUNDARIES["MODERN"]["target_matures_by"],
                    "training_row_count": modern_result["row_count"],
                    "positive_row_count": modern_result["positive_count"],
                    "negative_row_count": modern_result["negative_count"],
                    "rationale": PRODUCTION_BOUNDARIES["MODERN"]["rationale"],
                },
                "operational_calibration": (
                    "uncalibrated_raw_probabilities (platt scaling evaluated conditionally)"
                ),
            },
        },
    }

    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    return {
        "manifest_path": manifest_path,
        "legacy_artifact_path": legacy_artifact_path,
        "legacy_sha256": legacy_result["sha256"],
        "modern_artifact_path": modern_artifact_path,
        "modern_sha256": modern_result["sha256"],
        "manifest": manifest,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build reproducible schedule-extension model artifacts."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current working dir)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory for model artifacts (default: artifacts/ml/schedule_extension_3m)",
    )
    args = parser.parse_args()
    result = build_all_artifacts(args.root, args.output)
    print(f"Artifact manifest written to {result['manifest_path']}")
    print(f"Legacy CatBoost SHA-256: {result['legacy_sha256']}")
    print(f"Modern Logistic SHA-256: {result['modern_sha256']}")


if __name__ == "__main__":
    main()
