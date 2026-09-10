"""IRIS PR-09 Implementation Risk Model Definitions, Feature Policy, Preprocessing, and Estimators.

This module implements the model training, feature extraction, fold preprocessing,
candidate model definitions (Logistic Regression baseline and CatBoost challenger),
and model explainability for the 3-month physical-progress stagnation target
(target_progress_stagnation_3m).

Strict leakage controls, fail-closed feature validation, and deterministic execution
are enforced throughout.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence

import catboost as cb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.ml.implementation_risk_target import (
    DEFAULT_CONTRACT_PATH,
    HORIZON,
    TOLERANCE_PROGRESS,
    add_months,
    classify_implementation_target,
    load_implementation_contract,
    month_index,
    months_between,
    regime_for_month,
    segment_for_month,
    sha256_file,
)

RANDOM_SEED = 20260910

FEATURE_NAMES = [
    "sector",
    "agency",
    "state",
    "original_cost",
    "cumulative_expenditure_t",
    "revised_cost_t",
    "physical_progress_t",
    "project_age_months",
    "months_to_original_schedule",
    "months_to_effective_schedule",
    "schedule_revision_lag_months",
    "schedule_has_been_revised",
    "months_since_start",
    "expenditure_to_original_cost_ratio",
    "revised_to_original_cost_ratio",
    "cost_has_been_revised",
    "exp_delta_1m",
    "exp_delta_3m",
    "past_exp_stagnant_3m",
    "past_progress_delta_3m",
    "past_progress_stagnant_3m",
    "n_prior_schedule_extensions",
    "n_prior_cost_revisions",
    "observed_tenure_months",
    "state_is_missing",
    "approval_date_is_missing",
    "original_completion_date_is_missing",
    "revised_cost_is_present",
    "revised_date_is_present",
    "physical_progress_is_present",
    "physical_progress_supported",
    "start_date_is_present",
    "start_date_supported",
    "exp_delta_1m_is_supported",
    "exp_delta_3m_is_supported",
    "progress_delta_3m_is_supported",
]

CATEGORICAL_FEATURES = ["sector", "agency", "state"]
NUMERIC_FEATURES = [name for name in FEATURE_NAMES if name not in CATEGORICAL_FEATURES]

PROHIBITED_LEAKAGE_FIELDS = {
    "target_progress_stagnation_3m",
    "progress_stagnation_subtype",
    "delta_physical_progress_3m",
    "baseline_progress",
    "future_progress_t3",
    "target_window_end_month",
    "target_extension_3m",
    "target_effective_cost_esc_3m",
    "cost_revision_type",
    "cost_diff",
    "target_event_month",
    "target_event_revised_cost",
    "eventually_completed",
    "completion_report_month",
    "actual_completion_date",
    "completed_revised_cost",
    "completed_cumulative_expenditure",
    "project_code",
    "project_name",
    "legacy_ocms_code",
    "pmgid",
    "source_file",
    "source_page",
    "source_pages",
    "source_row_number",
    "source_serial_number",
    "extraction_method",
}

CATBOOST_PARAMS = {
    "iterations": 300,
    "learning_rate": 0.05,
    "depth": 5,
    "l2_leaf_reg": 3.0,
    "random_seed": RANDOM_SEED,
    "verbose": False,
    "thread_count": 4,
    "allow_writing_files": False,
}

LOGISTIC_PARAMS = {
    "l1_ratio": 0.0,
    "C": 1.0,
    "solver": "lbfgs",
    "max_iter": 2000,
    "random_state": RANDOM_SEED,
}

CANDIDATE_CONFIGURATIONS = {
    "prevalence": {
        "family": "BaselinePrevalence",
        "variant": "empirical_rate",
        "class_weight": None,
        "hyperparameters": {},
    },
    "logistic_unweighted": {
        "family": "LogisticRegression",
        "variant": "unweighted",
        "class_weight": None,
        "hyperparameters": LOGISTIC_PARAMS,
    },
    "logistic_balanced": {
        "family": "LogisticRegression",
        "variant": "balanced",
        "class_weight": "balanced",
        "hyperparameters": LOGISTIC_PARAMS,
    },
    "catboost_unweighted": {
        "family": "CatBoost",
        "variant": "unweighted",
        "auto_class_weights": None,
        "hyperparameters": CATBOOST_PARAMS,
    },
    "catboost_balanced": {
        "family": "CatBoost",
        "variant": "balanced",
        "auto_class_weights": "Balanced",
        "hyperparameters": CATBOOST_PARAMS,
    },
}

CATEGORICAL_MISSING_SENTINEL = "__MISSING__"


def validate_feature_columns(features: Sequence[str]) -> list[str]:
    """Validate that features contain all approved contract features and zero prohibited fields."""
    features_set = set(features)
    prohibited_found = features_set.intersection(PROHIBITED_LEAKAGE_FIELDS)
    if prohibited_found:
        raise ValueError(
            f"Prohibited leakage fields detected in feature matrix: {sorted(prohibited_found)}"
        )
    missing = set(FEATURE_NAMES) - features_set
    if missing:
        raise ValueError(f"Missing required contract features: {sorted(missing)}")
    return list(FEATURE_NAMES)


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return None if (math.isnan(value) or np.isnan(value)) else float(value)
    s = str(value).strip()
    if s == "" or s.lower() in ("nan", "none", "null"):
        return None
    try:
        val = float(s)
        return None if math.isnan(val) else val
    except (ValueError, TypeError):
        return None


def _to_str(value: Any) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    return "" if s.lower() in ("nan", "none", "null") else s


def _ratio(num: float | None, den: float | None) -> float | None:
    if num is None or den in (None, 0.0):
        return None
    return num / den


def _effective_schedule_baseline(row: dict[str, Any]) -> str:
    rev = _to_str(row.get("revised_completion_date"))
    if rev:
        return rev
    orig = _to_str(row.get("original_completion_date"))
    if orig:
        return orig
    return ""


def _prior_historical_counts(
    history: list[dict[str, Any]], report_month: str
) -> tuple[int, int, int]:
    """Count prior schedule extensions and cost revisions observed prior to or at report_month."""
    rows = [r for r in history if r["report_month"] <= report_month]
    schedule_count = 0
    cost_count = 0
    last_schedule = ""
    last_cost: float | None = None
    for r in rows:
        orig_date = _to_str(r.get("original_completion_date"))
        rev_date = _to_str(r.get("revised_completion_date"))
        if not last_schedule and orig_date:
            last_schedule = orig_date
        if rev_date:
            if last_schedule and month_index(rev_date) > month_index(last_schedule):
                schedule_count += 1
            last_schedule = rev_date

        orig_c = _to_float(r.get("original_cost"))
        rev_c = _to_float(r.get("revised_cost"))
        if last_cost is None and orig_c is not None:
            last_cost = orig_c
        if rev_c is not None:
            if last_cost is not None and rev_c > last_cost:
                cost_count += 1
            last_cost = rev_c
    return schedule_count, cost_count, len(rows)


def extract_features_at_t(
    current: dict[str, Any],
    by_month: dict[str, dict[str, Any]],
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Extract approved 36 contract features strictly at prediction time T."""
    month = current["report_month"]
    orig_cost = _to_float(current.get("original_cost"))
    rev_cost = _to_float(current.get("revised_cost"))
    exp = _to_float(current.get("cumulative_expenditure"))
    prog = _to_float(current.get("physical_progress"))
    baseline_schedule = _effective_schedule_baseline(current)

    prior_1 = by_month.get(add_months(month, -1))
    prior_3 = by_month.get(add_months(month, -3))
    curr_seg_info = segment_for_month(month)
    same_segment = curr_seg_info["name"] if curr_seg_info else "NONE"

    def usable_prior(row: dict[str, Any] | None) -> bool:
        if row is None:
            return False
        r_seg = segment_for_month(row["report_month"])
        return r_seg is not None and r_seg["name"] == same_segment

    exp_1 = _to_float(prior_1.get("cumulative_expenditure")) if usable_prior(prior_1) else None
    exp_3 = _to_float(prior_3.get("cumulative_expenditure")) if usable_prior(prior_3) else None
    prog_3 = _to_float(prior_3.get("physical_progress")) if usable_prior(prior_3) else None

    exp_delta_1 = exp - exp_1 if (exp is not None and exp_1 is not None) else None
    exp_delta_3 = exp - exp_3 if (exp is not None and exp_3 is not None) else None
    prog_delta_3 = prog - prog_3 if (prog is not None and prog_3 is not None) else None

    sched_count, cost_count, depth = _prior_historical_counts(history, month)
    phys_supported = month >= "2024-06"
    start_supported = month >= "2025-08"

    appr_date = _to_str(current.get("approval_date"))
    orig_comp = _to_str(current.get("original_completion_date"))
    rev_comp = _to_str(current.get("revised_completion_date"))
    start_date = _to_str(current.get("start_date"))
    state = _to_str(current.get("state"))
    sector = _to_str(current.get("sector"))
    agency = _to_str(current.get("agency"))

    return {
        "sector": sector,
        "agency": agency,
        "state": state,
        "original_cost": orig_cost,
        "cumulative_expenditure_t": exp,
        "revised_cost_t": rev_cost,
        "physical_progress_t": prog,
        "project_age_months": months_between(appr_date, month) if appr_date else None,
        "months_to_original_schedule": months_between(month, orig_comp) if orig_comp else None,
        "months_to_effective_schedule": months_between(month, baseline_schedule) if baseline_schedule else None,
        "schedule_revision_lag_months": months_between(orig_comp, rev_comp) if (orig_comp and rev_comp) else None,
        "schedule_has_been_revised": int(bool(rev_comp)),
        "months_since_start": months_between(start_date, month) if start_date else None,
        "expenditure_to_original_cost_ratio": _ratio(exp, orig_cost),
        "revised_to_original_cost_ratio": _ratio(rev_cost, orig_cost),
        "cost_has_been_revised": int(rev_cost is not None),
        "exp_delta_1m": exp_delta_1,
        "exp_delta_3m": exp_delta_3,
        "past_exp_stagnant_3m": int(exp_delta_3 == 0.0) if exp_delta_3 is not None else None,
        "past_progress_delta_3m": prog_delta_3,
        "past_progress_stagnant_3m": int(prog_delta_3 <= 1e-6) if prog_delta_3 is not None else None,
        "n_prior_schedule_extensions": sched_count,
        "n_prior_cost_revisions": cost_count,
        "observed_tenure_months": depth,
        "state_is_missing": int(not bool(state)),
        "approval_date_is_missing": int(not bool(appr_date)),
        "original_completion_date_is_missing": int(not bool(orig_comp)),
        "revised_cost_is_present": int(rev_cost is not None),
        "revised_date_is_present": int(bool(rev_comp)),
        "physical_progress_is_present": int(prog is not None),
        "physical_progress_supported": int(phys_supported),
        "start_date_is_present": int(bool(start_date)),
        "start_date_supported": int(start_supported),
        "exp_delta_1m_is_supported": int(exp_delta_1 is not None),
        "exp_delta_3m_is_supported": int(exp_delta_3 is not None),
        "progress_delta_3m_is_supported": int(prog_delta_3 is not None),
    }


def build_implementation_risk_modeling_dataset(
    df_monthly: pd.DataFrame,
    contract_path: Path | str = DEFAULT_CONTRACT_PATH,
) -> pd.DataFrame:
    """Construct the reconciled eligible modeling population and 36 prediction-time features.

    Excludes right-censored, structurally ineligible, and ambiguous observations.
    Fails closed if the resulting population drifts from PR-08 authoritative counts.
    """
    contract = load_implementation_contract(contract_path)
    validate_feature_columns(contract["features"]["ordered_names"])

    df_sorted = df_monthly.sort_values(["project_code", "report_month"]).copy()
    projects = df_sorted.groupby("project_code")

    records = []
    for p_code, group in projects:
        rows = group.to_dict("records")
        by_month = {r["report_month"]: r for r in rows}

        for i, current in enumerate(rows):
            history = rows[:i]
            decision = classify_implementation_target(
                current,
                by_month,
                horizon=contract["target"]["horizon_months"],
                tolerance=contract["target"]["tolerance_percentage"],
            )
            if decision.eligible:
                features = extract_features_at_t(current, by_month, history)
                features["project_code"] = p_code
                features["report_month"] = current["report_month"]
                features["identifier_regime"] = regime_for_month(current["report_month"])
                seg_info = segment_for_month(current["report_month"])
                features["continuous_segment"] = seg_info["name"] if seg_info else "NONE"
                features["target_progress_stagnation_3m"] = decision.label
                features["progress_stagnation_subtype"] = decision.progress_subtype
                features["target_window_end_month"] = decision.window_end
                records.append(features)

    df_modeling = pd.DataFrame(records)

    # Validate against authoritative population invariants
    expected_eligible = contract["expected_dataset_metrics"]["eligible_rows"]["TOTAL"]
    expected_pos = contract["expected_dataset_metrics"]["eligible_positives"]["TOTAL"]
    expected_neg = contract["expected_dataset_metrics"]["eligible_negatives"]["TOTAL"]

    actual_eligible = len(df_modeling)
    actual_pos = int((df_modeling["target_progress_stagnation_3m"] == 1).sum())
    actual_neg = int((df_modeling["target_progress_stagnation_3m"] == 0).sum())

    if (
        actual_eligible != expected_eligible
        or actual_pos != expected_pos
        or actual_neg != expected_neg
    ):
        raise ValueError(
            f"Authoritative population drift detected: "
            f"eligible={actual_eligible} (expected {expected_eligible}), "
            f"positives={actual_pos} (expected {expected_pos}), "
            f"negatives={actual_neg} (expected {expected_neg})"
        )

    return df_modeling


class ImplementationRiskFoldPreprocessor:
    """Training-fold-only frequency encoding for categoricals and numeric standardization.

    Numeric missingness is represented explicitly as 0 in standardized matrix space
    plus an accompanying binary missingness indicator (__missing=1).
    Categorical unseen values receive frequency 0.0.
    Preprocessor is immutable after fitting: transform() never mutates state.
    """

    def __init__(self, feature_columns: Sequence[str] = FEATURE_NAMES) -> None:
        self.feature_columns = list(feature_columns)
        self.categorical = [f for f in self.feature_columns if f in CATEGORICAL_FEATURES]
        self.numeric = [f for f in self.feature_columns if f not in CATEGORICAL_FEATURES]
        self.category_frequency: dict[str, dict[str, float]] = {}
        self.numeric_mean: dict[str, float] = {}
        self.numeric_scale: dict[str, float] = {}
        self.numeric_missing_count: dict[str, int] = {}
        self.fit_row_count = 0
        self.fitted = False

    @property
    def output_columns(self) -> list[str]:
        fields = [f"{name}__train_frequency" for name in self.categorical]
        for name in self.numeric:
            fields.extend((f"{name}__standardized", f"{name}__missing"))
        return fields

    def fit(self, rows: Sequence[dict[str, Any]]) -> "ImplementationRiskFoldPreprocessor":
        if not rows:
            raise ValueError("Cannot fit preprocessing on empty training fold")
        self.fit_row_count = len(rows)

        # Categorical frequency encoding
        for name in self.categorical:
            counts = Counter((_to_str(row.get(name)) or CATEGORICAL_MISSING_SENTINEL) for row in rows)
            self.category_frequency[name] = {
                cat: count / len(rows) for cat, count in sorted(counts.items())
            }

        # Numeric standardization
        for name in self.numeric:
            raw_vals = np.asarray([_to_float(row.get(name)) for row in rows], dtype=float)
            valid = raw_vals[np.isfinite(raw_vals)]
            self.numeric_missing_count[name] = int(len(raw_vals) - len(valid))
            if len(valid) > 0:
                mean = float(valid.mean())
                scale = float(valid.std())
                self.numeric_mean[name] = mean
                self.numeric_scale[name] = scale if scale > 0.0 else 1.0
            else:
                self.numeric_mean[name] = 0.0
                self.numeric_scale[name] = 1.0

        self.fitted = True
        return self

    def transform(self, rows: Sequence[dict[str, Any]]) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("Preprocessor must be fit on training rows before transform")
        matrix = np.zeros((len(rows), len(self.output_columns)), dtype=float)
        for row_index, row in enumerate(rows):
            col_index = 0
            for name in self.categorical:
                cat = _to_str(row.get(name)) or CATEGORICAL_MISSING_SENTINEL
                matrix[row_index, col_index] = self.category_frequency[name].get(cat, 0.0)
                col_index += 1
            for name in self.numeric:
                val = _to_float(row.get(name))
                if val is None or math.isnan(val):
                    matrix[row_index, col_index] = 0.0
                    matrix[row_index, col_index + 1] = 1.0
                else:
                    matrix[row_index, col_index] = (val - self.numeric_mean[name]) / self.numeric_scale[name]
                    matrix[row_index, col_index + 1] = 0.0
                col_index += 2
        return matrix

    def audit(self, evaluation_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
        unseen = {}
        for name in self.categorical:
            known = self.category_frequency[name]
            unseen[name] = sum(
                1 for r in evaluation_rows if (_to_str(r.get(name)) or CATEGORICAL_MISSING_SENTINEL) not in known
            )
        return {
            "fit_row_count": self.fit_row_count,
            "input_feature_count": len(self.feature_columns),
            "output_matrix_column_count": len(self.output_columns),
            "categorical_cardinalities": {k: len(v) for k, v in self.category_frequency.items()},
            "unseen_evaluation_categories": unseen,
            "numeric_training_missing_counts": self.numeric_missing_count,
        }


def prepare_catboost_df(
    rows: Sequence[dict[str, Any]],
    feature_columns: Sequence[str] = FEATURE_NAMES,
) -> tuple[pd.DataFrame, list[str]]:
    """Prepare a pandas DataFrame for CatBoost with string sentinels for missing categoricals."""
    df = pd.DataFrame([{col: row.get(col) for col in feature_columns} for row in rows])
    cat_cols = [c for c in feature_columns if c in CATEGORICAL_FEATURES]
    for c in cat_cols:
        df[c] = df[c].fillna("").astype(str).replace("", CATEGORICAL_MISSING_SENTINEL)
    num_cols = [c for c in feature_columns if c not in CATEGORICAL_FEATURES]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, cat_cols


def fit_logistic_candidate(
    training_rows: Sequence[dict[str, Any]],
    scoring_rows: Sequence[dict[str, Any]],
    candidate_name: str,
    feature_columns: Sequence[str] = FEATURE_NAMES,
) -> tuple[np.ndarray, np.ndarray, float, np.ndarray, ImplementationRiskFoldPreprocessor, LogisticRegression]:
    """Fit a Logistic candidate on training rows and score evaluation rows.

    Returns:
        probabilities, raw_logits, intercept, contributions_matrix, preprocessor, model
    """
    config = CANDIDATE_CONFIGURATIONS[candidate_name]
    preprocessor = ImplementationRiskFoldPreprocessor(feature_columns).fit(training_rows)
    x_train = preprocessor.transform(training_rows)
    x_score = preprocessor.transform(scoring_rows)
    y_train = np.asarray([int(r["target_progress_stagnation_3m"]) for r in training_rows], dtype=int)

    model = LogisticRegression(
        l1_ratio=config["hyperparameters"]["l1_ratio"],
        C=config["hyperparameters"]["C"],
        solver=config["hyperparameters"]["solver"],
        max_iter=config["hyperparameters"]["max_iter"],
        class_weight=config["class_weight"],
        random_state=config["hyperparameters"]["random_state"],
    )
    model.fit(x_train, y_train)

    probs = np.asarray(model.predict_proba(x_score)[:, 1], dtype=float)
    raw_logits = np.asarray(model.decision_function(x_score), dtype=float)
    intercept = float(model.intercept_[0])
    coefs = np.asarray(model.coef_[0], dtype=float)
    contributions = x_score * coefs

    return probs, raw_logits, intercept, contributions, preprocessor, model


def fit_catboost_candidate(
    training_rows: Sequence[dict[str, Any]],
    scoring_rows: Sequence[dict[str, Any]],
    candidate_name: str,
    feature_columns: Sequence[str] = FEATURE_NAMES,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, np.ndarray, cb.CatBoostClassifier]:
    """Fit a CatBoost candidate on training rows and score evaluation rows.

    Returns:
        probabilities, raw_scores, feature_importances, expected_base_value, shap_contributions, model
    """
    config = CANDIDATE_CONFIGURATIONS[candidate_name]
    x_train, cat_cols = prepare_catboost_df(training_rows, feature_columns)
    x_score, _ = prepare_catboost_df(scoring_rows, feature_columns)
    y_train = np.asarray([int(r["target_progress_stagnation_3m"]) for r in training_rows], dtype=int)

    model = cb.CatBoostClassifier(
        iterations=config["hyperparameters"]["iterations"],
        learning_rate=config["hyperparameters"]["learning_rate"],
        depth=config["hyperparameters"]["depth"],
        l2_leaf_reg=config["hyperparameters"]["l2_leaf_reg"],
        random_seed=config["hyperparameters"]["random_seed"],
        auto_class_weights=config["auto_class_weights"],
        thread_count=config["hyperparameters"]["thread_count"],
        verbose=config["hyperparameters"]["verbose"],
        allow_writing_files=config["hyperparameters"]["allow_writing_files"],
        cat_features=cat_cols if cat_cols else None,
    )
    model.fit(x_train, y_train)

    pool_score = cb.Pool(x_score, cat_features=cat_cols if cat_cols else None, feature_names=list(feature_columns))
    probs = np.asarray(model.predict_proba(pool_score)[:, 1], dtype=float)
    raw_scores = np.asarray(model.predict(pool_score, prediction_type="RawFormulaVal"), dtype=float).reshape(-1)

    importances = np.asarray(model.get_feature_importance(type="PredictionValuesChange"), dtype=float)
    shap_vals = np.asarray(model.get_feature_importance(pool_score, type="ShapValues"), dtype=float)
    shap_contributions = shap_vals[:, :-1]
    expected_base_val = float(shap_vals[0, -1]) if len(shap_vals) > 0 else 0.0

    return probs, raw_scores, importances, expected_base_val, shap_contributions, model
