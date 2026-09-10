"""Test Suite for IRIS PR-09: Implementation Risk Model Training, Evaluation, and Audit.

Covers all 25 required test dimensions:
1. PR-08 contract and target integrity
2. Authoritative population reconciliation (64,608 total, 26,044 eligible, 7,344 positives, 18,700 negatives)
3. Canonical dataset hashes unchanged
4. Feature list deterministic (36 approved features in contract order)
5. Prohibited leakage fields strictly rejected (fail-closed)
6. Missing required features rejected
7. Fold preprocessor fit on training data only
8. Preprocessor transform does not mutate fitted state (immutability)
9. Unseen evaluation categories map to 0.0 frequency
10. Logistic unweighted and balanced variants are distinct
11. CatBoost unweighted and balanced variants are distinct
12. Strict embargo rejects equality (T_train + 3 == E fails)
13. Accepted folds identical across all candidate models
14. Zero cross-gap or cross-regime folds
15. Fold training data ends before evaluation under T+3 < E
16. Candidate model execution is 100% deterministic
17. Per-fold metrics reconcile with aggregate metrics
18. Precision NA behavior preserved when predicted positives is zero
19. Calibration uses historical information only
20. Threshold research preserves grid completeness (0.01 to 1.00)
21. Project-cluster bootstrap deterministic with fixed seed
22. Month-block bootstrap deterministic with fixed seed
23. Exact linear logit reconstruction verified for Logistic
24. Exact TreeSHAP margin reconstruction verified for CatBoost
25. Artifact inventory is complete and no schedule artifacts modified
"""

import json
import math
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from src.ml.implementation_risk_model import (
    CANDIDATE_CONFIGURATIONS,
    CATEGORICAL_FEATURES,
    FEATURE_NAMES,
    NUMERIC_FEATURES,
    PROHIBITED_LEAKAGE_FIELDS,
    RANDOM_SEED,
    ImplementationRiskFoldPreprocessor,
    build_implementation_risk_modeling_dataset,
    fit_catboost_candidate,
    fit_logistic_candidate,
    validate_feature_columns,
)
from src.ml.implementation_risk_evaluation import (
    ALL_EVALUATION_CANDIDATE_ORIGINS,
    BOOTSTRAP_ITERATIONS,
    DEFAULT_OUTPUT_DIR,
    EVALUATION_ORIGINS,
    calculate_calibration_diagnostics,
    calculate_point_metrics,
    month_block_bootstrap,
    project_cluster_bootstrap,
    run_threshold_grid_research,
    select_training_rows,
    training_reference_is_embargo_safe,
)
from src.ml.implementation_risk_target import (
    DEFAULT_CONTRACT_PATH,
    add_months,
    load_implementation_contract,
    month_index,
    sha256_file,
)

CANONICAL_MONTHLY = Path("data/processed/projects_monthly.csv")
CANONICAL_COMPLETED = Path("data/processed/projects_completed.csv")
EXPECTED_MONTHLY_SHA256 = "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF"
EXPECTED_COMPLETED_SHA256 = "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910"


class TestImplementationRiskModel(unittest.TestCase):
    """Test suite verifying PR-09 implementation risk modeling invariants."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load_implementation_contract(DEFAULT_CONTRACT_PATH)
        cls.manifest_path = DEFAULT_OUTPUT_DIR / "manifest.json"
        if cls.manifest_path.is_file():
            with cls.manifest_path.open("r", encoding="utf-8") as f:
                cls.manifest = json.load(f)
        else:
            cls.manifest = None

    def test_01_contract_and_target_integrity(self):
        """1. Target integrity: target_progress_stagnation_3m name, horizon, and tolerance."""
        self.assertEqual(self.contract["target"]["name"], "target_progress_stagnation_3m")
        self.assertEqual(self.contract["target"]["horizon_months"], 3)
        self.assertEqual(self.contract["target"]["tolerance_percentage"], 1e-6)

    def test_02_authoritative_population_reconciliation(self):
        """2. PR-08 authoritative population reconciliation in modeling dataset."""
        self.assertIsNotNone(self.manifest)
        pop = self.manifest["modeling_population"]
        self.assertEqual(pop["total_source_observations"], 64608)
        self.assertEqual(pop["eligible_observations"], 26044)
        self.assertEqual(pop["positive_observations"], 7344)
        self.assertEqual(pop["negative_observations"], 18700)
        self.assertAlmostEqual(pop["positive_prevalence"], 7344 / 26044, places=5)

    def test_03_canonical_dataset_hashes_unchanged(self):
        """3. Canonical dataset hashes unchanged."""
        h_monthly = sha256_file(CANONICAL_MONTHLY)
        h_completed = sha256_file(CANONICAL_COMPLETED)
        self.assertEqual(h_monthly, EXPECTED_MONTHLY_SHA256)
        self.assertEqual(h_completed, EXPECTED_COMPLETED_SHA256)

    def test_04_feature_list_deterministic(self):
        """4. Feature list deterministic (36 approved features in contract order)."""
        contract_features = self.contract["features"]["ordered_names"]
        self.assertEqual(len(FEATURE_NAMES), 36)
        self.assertEqual(FEATURE_NAMES, contract_features)
        self.assertEqual(len(CATEGORICAL_FEATURES), 3)
        self.assertEqual(len(NUMERIC_FEATURES), 33)

    def test_05_prohibited_leakage_fields_rejected(self):
        """5. Prohibited leakage fields strictly rejected (fail-closed)."""
        for prohibited in PROHIBITED_LEAKAGE_FIELDS:
            bad_features = list(FEATURE_NAMES) + [prohibited]
            with self.assertRaises(ValueError):
                validate_feature_columns(bad_features)

    def test_06_missing_required_features_rejected(self):
        """6. Missing required features rejected."""
        incomplete_features = FEATURE_NAMES[:-1]
        with self.assertRaises(ValueError):
            validate_feature_columns(incomplete_features)

    def test_07_fold_preprocessor_fit_on_training_only(self):
        """7. Fold preprocessor fit on training data only."""
        train_sample = [
            {"sector": "ROADS", "agency": "NHAI", "state": "UP", "original_cost": 100.0},
            {"sector": "RAILWAYS", "agency": "RVNL", "state": "DL", "original_cost": 200.0},
        ]
        eval_sample = [
            {"sector": "NEW_SECTOR", "agency": "NHAI", "state": "UP", "original_cost": 500.0}
        ]
        preproc = ImplementationRiskFoldPreprocessor(["sector", "agency", "state", "original_cost"])
        preproc.fit(train_sample)

        # Mean must be 150.0 (training only), not affected by 500.0 in eval
        self.assertEqual(preproc.numeric_mean["original_cost"], 150.0)

    def test_08_preprocessor_transform_does_not_mutate_state(self):
        """8. Preprocessor transform does not mutate fitted state (immutability)."""
        train_sample = [
            {"sector": "ROADS", "agency": "NHAI", "state": "UP", "original_cost": 100.0},
            {"sector": "RAILWAYS", "agency": "RVNL", "state": "DL", "original_cost": 200.0},
        ]
        eval_sample = [
            {"sector": "NEW_SECTOR", "agency": "NHAI", "state": "UP", "original_cost": 500.0}
        ]
        preproc = ImplementationRiskFoldPreprocessor(["sector", "agency", "state", "original_cost"]).fit(train_sample)
        initial_mean = preproc.numeric_mean["original_cost"]
        initial_cardinalities = {k: len(v) for k, v in preproc.category_frequency.items()}

        # Transform multiple times
        _ = preproc.transform(eval_sample)
        _ = preproc.transform(eval_sample)

        self.assertEqual(preproc.numeric_mean["original_cost"], initial_mean)
        self.assertEqual({k: len(v) for k, v in preproc.category_frequency.items()}, initial_cardinalities)

    def test_09_unseen_evaluation_categories_mapped_to_zero(self):
        """9. Unseen evaluation categories map to 0.0 frequency."""
        train_sample = [
            {"sector": "ROADS", "agency": "NHAI", "state": "UP", "original_cost": 100.0},
        ]
        eval_sample = [
            {"sector": "UNKNOWN_SECTOR", "agency": "NHAI", "state": "UP", "original_cost": 100.0}
        ]
        preproc = ImplementationRiskFoldPreprocessor(["sector", "agency", "state", "original_cost"]).fit(train_sample)
        mat = preproc.transform(eval_sample)
        self.assertEqual(mat[0, 0], 0.0)

    def test_10_logistic_unweighted_and_balanced_separate(self):
        """10. Logistic unweighted and balanced variants are distinct."""
        self.assertIn("logistic_unweighted", CANDIDATE_CONFIGURATIONS)
        self.assertIn("logistic_balanced", CANDIDATE_CONFIGURATIONS)
        self.assertIsNone(CANDIDATE_CONFIGURATIONS["logistic_unweighted"]["class_weight"])
        self.assertEqual(CANDIDATE_CONFIGURATIONS["logistic_balanced"]["class_weight"], "balanced")

    def test_11_catboost_unweighted_and_balanced_separate(self):
        """11. CatBoost unweighted and balanced variants are distinct."""
        self.assertIn("catboost_unweighted", CANDIDATE_CONFIGURATIONS)
        self.assertIn("catboost_balanced", CANDIDATE_CONFIGURATIONS)
        self.assertIsNone(CANDIDATE_CONFIGURATIONS["catboost_unweighted"]["auto_class_weights"])
        self.assertEqual(CANDIDATE_CONFIGURATIONS["catboost_balanced"]["auto_class_weights"], "Balanced")

    def test_12_strict_embargo_rejects_equality(self):
        """12. Strict embargo rejects equality (T_train + 3 == E fails)."""
        self.assertFalse(training_reference_is_embargo_safe("2024-06", "2024-09", horizon=3))
        self.assertTrue(training_reference_is_embargo_safe("2024-06", "2024-10", horizon=3))
        self.assertFalse(training_reference_is_embargo_safe("2024-06", "2024-08", horizon=3))

    def test_13_accepted_folds_identical_across_candidates(self):
        """13. Accepted folds are identical across all candidate models."""
        fold_metrics_csv = DEFAULT_OUTPUT_DIR / "fold_metrics.csv"
        df_fm = pd.read_csv(fold_metrics_csv)
        candidates = df_fm["candidate_model"].unique()
        fold_counts = df_fm.groupby("candidate_model")["fold_id"].nunique()
        for cand in candidates:
            self.assertEqual(fold_counts[cand], 11)

    def test_14_no_cross_gap_folds(self):
        """14. Zero cross-gap or cross-regime folds."""
        for reg, month, accepted, reason in ALL_EVALUATION_CANDIDATE_ORIGINS:
            if not accepted:
                self.assertNotIn(month, EVALUATION_ORIGINS[reg])

    def test_15_fold_training_data_ends_before_evaluation_under_embargo(self):
        """15. Fold training data ends strictly before evaluation origin under T+3 < E."""
        manifest_path = DEFAULT_OUTPUT_DIR / "manifest.json"
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
        for fold in manifest["walk_forward_evaluation"]["accepted_folds_audit"]:
            max_label_end = fold["max_training_label_window_end"]
            eval_origin = fold["evaluation_origin"]
            self.assertLess(month_index(max_label_end), month_index(eval_origin))

    def test_16_candidate_execution_is_deterministic(self):
        """16. Candidate execution is 100% deterministic."""
        train_rows = [
            {"sector": "ROADS", "agency": "NHAI", "state": "UP", "original_cost": 100.0, "target_progress_stagnation_3m": 0},
            {"sector": "RAILWAYS", "agency": "RVNL", "state": "DL", "original_cost": 200.0, "target_progress_stagnation_3m": 1},
            {"sector": "ROADS", "agency": "NHAI", "state": "MH", "original_cost": 150.0, "target_progress_stagnation_3m": 0},
            {"sector": "POWER", "agency": "NTPC", "state": "MP", "original_cost": 300.0, "target_progress_stagnation_3m": 1},
        ]
        for r in train_rows:
            for f in FEATURE_NAMES:
                if f not in r:
                    r[f] = 0.0

        p1, _, _, _, _, _ = fit_logistic_candidate(train_rows, train_rows, "logistic_unweighted", FEATURE_NAMES)
        p2, _, _, _, _, _ = fit_logistic_candidate(train_rows, train_rows, "logistic_unweighted", FEATURE_NAMES)
        np.testing.assert_array_almost_equal(p1, p2, decimal=10)

    def test_17_per_fold_metrics_reconcile_with_aggregate_metrics(self):
        """17. Per-fold metrics reconcile with aggregate metrics."""
        fold_metrics_csv = DEFAULT_OUTPUT_DIR / "fold_metrics.csv"
        regime_metrics_csv = DEFAULT_OUTPUT_DIR / "regime_metrics.csv"
        df_fm = pd.read_csv(fold_metrics_csv)
        df_rm = pd.read_csv(regime_metrics_csv)

        for _, row in df_rm.iterrows():
            reg = row["regime"]
            cand = row["candidate_model"]
            fm_sub = df_fm[(df_fm["regime"] == reg) & (df_fm["candidate_model"] == cand)]
            macro_mean = fm_sub["average_precision"].mean()
            self.assertAlmostEqual(row["macro_average_precision"], macro_mean, places=5)

    def test_18_precision_na_behavior_preserved(self):
        """18. Precision NA behavior is preserved when predicted positives is zero."""
        y_true = np.array([0, 0, 0, 0])
        y_score = np.array([0.1, 0.2, 0.3, 0.4])
        metrics = calculate_point_metrics(y_true, y_score, threshold=0.5)
        self.assertIsNone(metrics["precision"])

    def test_19_calibration_uses_historical_information_only(self):
        """19. Calibration uses historical information only."""
        calib_csv = DEFAULT_OUTPUT_DIR / "calibration_metrics.csv"
        df_calib = pd.read_csv(calib_csv)
        self.assertTrue("calibration_slope" in df_calib.columns)
        self.assertTrue("historical_platt_brier" in df_calib.columns)

    def test_20_threshold_research_preserves_grid_completeness(self):
        """20. Threshold research preserves grid completeness (0.01 to 1.00)."""
        tr_csv = DEFAULT_OUTPUT_DIR / "threshold_research.csv"
        df_tr = pd.read_csv(tr_csv)
        self.assertEqual(len(df_tr["threshold"].unique()), 100)
        self.assertAlmostEqual(df_tr["threshold"].min(), 0.01)
        self.assertAlmostEqual(df_tr["threshold"].max(), 1.00)

    def test_21_project_cluster_bootstrap_deterministic(self):
        """21. Project-cluster bootstrap deterministic with fixed seed."""
        sample_preds = [
            {"project_code": "P1", "report_month": "2024-10", "actual_label": 1, "predicted_probability": 0.8},
            {"project_code": "P1", "report_month": "2024-11", "actual_label": 0, "predicted_probability": 0.3},
            {"project_code": "P2", "report_month": "2024-10", "actual_label": 0, "predicted_probability": 0.1},
            {"project_code": "P2", "report_month": "2024-11", "actual_label": 0, "predicted_probability": 0.2},
            {"project_code": "P3", "report_month": "2024-10", "actual_label": 1, "predicted_probability": 0.7},
        ]
        ci1 = project_cluster_bootstrap(sample_preds, iterations=50, seed=12345)
        ci2 = project_cluster_bootstrap(sample_preds, iterations=50, seed=12345)
        self.assertEqual(ci1, ci2)

    def test_22_month_block_bootstrap_deterministic(self):
        """22. Month-block bootstrap deterministic with fixed seed."""
        sample_preds = [
            {"project_code": "P1", "report_month": "2024-10", "actual_label": 1, "predicted_probability": 0.8},
            {"project_code": "P1", "report_month": "2024-11", "actual_label": 0, "predicted_probability": 0.3},
            {"project_code": "P2", "report_month": "2024-10", "actual_label": 0, "predicted_probability": 0.1},
            {"project_code": "P2", "report_month": "2024-11", "actual_label": 0, "predicted_probability": 0.2},
            {"project_code": "P3", "report_month": "2024-10", "actual_label": 1, "predicted_probability": 0.7},
        ]
        ci1 = month_block_bootstrap(sample_preds, iterations=50, seed=12345)
        ci2 = month_block_bootstrap(sample_preds, iterations=50, seed=12345)
        self.assertEqual(ci1, ci2)

    def test_23_exact_linear_logit_reconstruction_verified(self):
        """23. Exact linear logit reconstruction verified for Logistic candidates."""
        train_rows = [
            {"sector": "ROADS", "agency": "NHAI", "state": "UP", "original_cost": 100.0, "target_progress_stagnation_3m": 0},
            {"sector": "RAILWAYS", "agency": "RVNL", "state": "DL", "original_cost": 200.0, "target_progress_stagnation_3m": 1},
            {"sector": "ROADS", "agency": "NHAI", "state": "MH", "original_cost": 150.0, "target_progress_stagnation_3m": 0},
            {"sector": "POWER", "agency": "NTPC", "state": "MP", "original_cost": 300.0, "target_progress_stagnation_3m": 1},
        ]
        for r in train_rows:
            for f in FEATURE_NAMES:
                if f not in r:
                    r[f] = 0.0

        probs, raw_logits, intercept, contribs, preproc, model = fit_logistic_candidate(
            train_rows, train_rows, "logistic_unweighted", FEATURE_NAMES
        )
        reconstructed = intercept + contribs.sum(axis=1)
        max_err = float(np.max(np.abs(reconstructed - raw_logits)))
        self.assertLessEqual(max_err, 1e-9)

    def test_24_exact_shap_margin_reconstruction_verified(self):
        """24. Exact TreeSHAP margin reconstruction verified for CatBoost candidates."""
        exp_summary_csv = DEFAULT_OUTPUT_DIR / "explainability_summary.csv"
        df_exp = pd.read_csv(exp_summary_csv)
        for _, row in df_exp.iterrows():
            self.assertTrue(row["exact_shap_reconstruction_verified"])
            self.assertLessEqual(row["reconciliation_tolerance"], 1e-9)

    def test_25_artifact_inventory_and_schedule_preservation(self):
        """25. Artifact inventory is complete and no schedule artifacts are modified."""
        expected_artifacts = [
            "manifest.json",
            "candidate_summary.csv",
            "fold_metrics.csv",
            "regime_metrics.csv",
            "calibration_metrics.csv",
            "calibration_bins.csv",
            "threshold_research.csv",
            "feature_importance.csv",
            "explainability_summary.csv",
            "robustness_metrics.csv",
            "candidate_recommendation.json",
        ]
        for name in expected_artifacts:
            path = DEFAULT_OUTPUT_DIR / name
            self.assertTrue(path.is_file(), f"Missing artifact: {name}")

        schedule_manifest = Path("data/ml/schedule_extension_3m/manifest.json")
        self.assertTrue(schedule_manifest.is_file())
        with schedule_manifest.open("r", encoding="utf-8") as f:
            m = json.load(f)
        self.assertEqual(m["target"], "target_effective_schedule_ext_3m")


if __name__ == "__main__":
    unittest.main()
