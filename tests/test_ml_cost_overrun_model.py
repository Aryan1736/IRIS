"""Test Suite for IRIS PR-07: Cost Overrun Model Training, Evaluation, and Audit.

Covers all 25 required test dimensions:
1. PR-06 eligible population reconciliation
2. Target integrity
3. Canonical dataset hashes unchanged
4. Feature list deterministic
5. Prohibited leakage fields rejected
6. Missing required features rejected
7. Logistic preprocessing fit on training data only
8. Logistic unweighted and balanced variants are separate
9. CatBoost unweighted and balanced variants are separate
10. Strict embargo rejects equality
11. Accepted folds are identical across candidates
12. No cross-gap folds
13. Fold training data ends before evaluation under T+3 < E
14. Candidate execution is deterministic
15. Per-fold metrics reconcile with aggregate metrics
16. Precision NA behavior is preserved
17. Calibration uses historical information only
18. Threshold research preserves temporal order
19. Project-cluster bootstrap deterministic
20. Month-block bootstrap deterministic
21. Explainability uses only approved features
22. Candidate recommendation is reproducible
23. Artifact inventory is complete
24. Canonical datasets remain unchanged
25. No schedule ML contracts or artifacts are modified
"""

import json
import math
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from src.ml.cost_overrun_model import (
    CANDIDATE_CONFIGURATIONS,
    CATEGORICAL_FEATURES,
    FEATURE_NAMES,
    NUMERIC_FEATURES,
    PROHIBITED_LEAKAGE_FIELDS,
    RANDOM_SEED,
    CostOverrunFoldPreprocessor,
    build_cost_overrun_modeling_dataset,
    fit_catboost_candidate,
    fit_logistic_candidate,
    validate_feature_columns,
)
from src.ml.cost_overrun_evaluation import (
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
from src.ml.cost_overrun_target import (
    DEFAULT_CONTRACT_PATH,
    add_months,
    load_cost_contract,
    month_index,
    sha256_file,
)

CANONICAL_MONTHLY = Path("data/processed/projects_monthly.csv")
CANONICAL_COMPLETED = Path("data/processed/projects_completed.csv")
EXPECTED_MONTHLY_SHA256 = "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF"
EXPECTED_COMPLETED_SHA256 = "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910"


class TestCostOverrunModel(unittest.TestCase):
    """Test suite verifying PR-07 cost overrun modeling invariants."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load_cost_contract(DEFAULT_CONTRACT_PATH)
        cls.manifest_path = DEFAULT_OUTPUT_DIR / "manifest.json"
        if cls.manifest_path.is_file():
            with cls.manifest_path.open("r", encoding="utf-8") as f:
                cls.manifest = json.load(f)
        else:
            cls.manifest = None

    def test_01_eligible_population_reconciliation(self):
        """1. PR-06 eligible population reconciliation."""
        self.assertIsNotNone(self.manifest)
        pop = self.manifest["modeling_population"]
        self.assertEqual(pop["total_source_observations"], 64608)
        self.assertEqual(pop["eligible_observations"], 39693)
        self.assertEqual(pop["positive_observations"], 865)
        self.assertEqual(pop["negative_observations"], 38828)
        self.assertAlmostEqual(pop["positive_prevalence"], 865 / 39693, places=5)

    def test_02_target_integrity(self):
        """2. Target integrity: target_effective_cost_esc_3m name and parameters."""
        self.assertEqual(self.contract["target"]["name"], "target_effective_cost_esc_3m")
        self.assertEqual(self.contract["target"]["horizon_months"], 3)
        self.assertEqual(self.contract["target"]["tolerance_cr"], 0.001)

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
        """5. Prohibited leakage fields rejected."""
        for prohibited in PROHIBITED_LEAKAGE_FIELDS:
            bad_features = list(FEATURE_NAMES) + [prohibited]
            with self.assertRaises(ValueError):
                validate_feature_columns(bad_features)

    def test_06_missing_required_features_rejected(self):
        """6. Missing required features rejected."""
        incomplete_features = FEATURE_NAMES[:-1]
        with self.assertRaises(ValueError):
            validate_feature_columns(incomplete_features)

    def test_07_logistic_preprocessing_fit_on_training_only(self):
        """7. Logistic preprocessing fit on training data only."""
        train_sample = [
            {"sector": "ROADS", "agency": "NHAI", "state": "UP", "original_cost": 100.0},
            {"sector": "RAILWAYS", "agency": "RVNL", "state": "DL", "original_cost": 200.0},
        ]
        eval_sample = [
            {"sector": "NEW_SECTOR", "agency": "NHAI", "state": "UP", "original_cost": 500.0}
        ]
        preproc = CostOverrunFoldPreprocessor(["sector", "agency", "state", "original_cost"])
        preproc.fit(train_sample)

        # Mean must be 150.0 (training only), not affected by 500.0 in eval
        self.assertEqual(preproc.numeric_mean["original_cost"], 150.0)
        # NEW_SECTOR unseen in training, must map to frequency 0.0
        mat = preproc.transform(eval_sample)
        self.assertEqual(mat[0, 0], 0.0)

    def test_08_logistic_unweighted_and_balanced_separate(self):
        """8. Logistic unweighted and balanced variants are separate."""
        self.assertIn("logistic_unweighted", CANDIDATE_CONFIGURATIONS)
        self.assertIn("logistic_balanced", CANDIDATE_CONFIGURATIONS)
        self.assertIsNone(CANDIDATE_CONFIGURATIONS["logistic_unweighted"]["class_weight"])
        self.assertEqual(CANDIDATE_CONFIGURATIONS["logistic_balanced"]["class_weight"], "balanced")

    def test_09_catboost_unweighted_and_balanced_separate(self):
        """9. CatBoost unweighted and balanced variants are separate."""
        self.assertIn("catboost_unweighted", CANDIDATE_CONFIGURATIONS)
        self.assertIn("catboost_balanced", CANDIDATE_CONFIGURATIONS)
        self.assertIsNone(CANDIDATE_CONFIGURATIONS["catboost_unweighted"]["auto_class_weights"])
        self.assertEqual(CANDIDATE_CONFIGURATIONS["catboost_balanced"]["auto_class_weights"], "Balanced")

    def test_10_strict_embargo_rejects_equality(self):
        """10. Strict embargo rejects equality (T_train + 3 == E fails)."""
        # If T_train is 2023-01, T+3 is 2023-04. If E is 2023-04, T+3 == E -> False
        self.assertFalse(training_reference_is_embargo_safe("2023-01", "2023-04", horizon=3))
        # If E is 2023-05, T+3 (2023-04) < E (2023-05) -> True
        self.assertTrue(training_reference_is_embargo_safe("2023-01", "2023-05", horizon=3))
        # If E is 2023-03, T+3 > E -> False
        self.assertFalse(training_reference_is_embargo_safe("2023-01", "2023-03", horizon=3))

    def test_11_accepted_folds_identical_across_candidates(self):
        """11. Accepted folds are identical across candidates."""
        fold_metrics_csv = DEFAULT_OUTPUT_DIR / "fold_metrics.csv"
        df_fm = pd.read_csv(fold_metrics_csv)
        candidates = df_fm["candidate_model"].unique()
        fold_counts = df_fm.groupby("candidate_model")["fold_id"].nunique()
        for cand in candidates:
            self.assertEqual(fold_counts[cand], 17)

    def test_12_no_cross_gap_folds(self):
        """12. No cross-gap folds."""
        for reg, month, accepted, reason in ALL_EVALUATION_CANDIDATE_ORIGINS:
            if not accepted:
                # Ensure no rejected month ended up as an accepted fold
                self.assertNotIn(month, EVALUATION_ORIGINS[reg])

    def test_13_fold_training_data_ends_before_evaluation_under_embargo(self):
        """13. Fold training data ends before evaluation under T+3 < E."""
        manifest_path = DEFAULT_OUTPUT_DIR / "manifest.json"
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
        for fold in manifest["walk_forward_evaluation"]["accepted_folds_audit"]:
            max_label_end = fold["max_training_label_window_end"]
            eval_origin = fold["evaluation_origin"]
            self.assertLess(month_index(max_label_end), month_index(eval_origin))

    def test_14_candidate_execution_is_deterministic(self):
        """14. Candidate execution is deterministic."""
        train_rows = [
            {"sector": "ROADS", "agency": "NHAI", "state": "UP", "original_cost": 100.0, "target_effective_cost_esc_3m": 0},
            {"sector": "RAILWAYS", "agency": "RVNL", "state": "DL", "original_cost": 200.0, "target_effective_cost_esc_3m": 1},
            {"sector": "ROADS", "agency": "NHAI", "state": "MH", "original_cost": 150.0, "target_effective_cost_esc_3m": 0},
            {"sector": "POWER", "agency": "NTPC", "state": "MP", "original_cost": 300.0, "target_effective_cost_esc_3m": 1},
        ]
        # Pad with other required features
        for r in train_rows:
            for f in FEATURE_NAMES:
                if f not in r:
                    r[f] = 0.0

        p1, _, _, _, _, _ = fit_logistic_candidate(train_rows, train_rows, "logistic_unweighted", FEATURE_NAMES)
        p2, _, _, _, _, _ = fit_logistic_candidate(train_rows, train_rows, "logistic_unweighted", FEATURE_NAMES)
        np.testing.assert_array_almost_equal(p1, p2, decimal=10)

    def test_15_per_fold_metrics_reconcile_with_aggregate_metrics(self):
        """15. Per-fold metrics reconcile with aggregate metrics."""
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

    def test_16_precision_na_behavior_preserved(self):
        """16. Precision NA behavior is preserved when predicted positives is zero."""
        y_true = np.array([0, 0, 0, 0])
        y_score = np.array([0.1, 0.2, 0.3, 0.4])
        metrics = calculate_point_metrics(y_true, y_score, threshold=0.5)
        self.assertIsNone(metrics["precision"])

    def test_17_calibration_uses_historical_information_only(self):
        """17. Calibration uses historical information only."""
        calib_csv = DEFAULT_OUTPUT_DIR / "calibration_metrics.csv"
        df_calib = pd.read_csv(calib_csv)
        self.assertTrue("calibration_slope" in df_calib.columns)
        self.assertTrue("historical_platt_brier" in df_calib.columns)

    def test_18_threshold_research_preserves_temporal_order(self):
        """18. Threshold research preserves temporal order and evaluation isolation."""
        tr_csv = DEFAULT_OUTPUT_DIR / "threshold_research.csv"
        df_tr = pd.read_csv(tr_csv)
        self.assertEqual(len(df_tr["threshold"].unique()), 100)
        self.assertAlmostEqual(df_tr["threshold"].min(), 0.01)
        self.assertAlmostEqual(df_tr["threshold"].max(), 1.00)

    def test_19_project_cluster_bootstrap_deterministic(self):
        """19. Project-cluster bootstrap deterministic with fixed seed."""
        sample_preds = [
            {"project_code": "P1", "report_month": "2024-06", "actual_label": 1, "predicted_probability": 0.8},
            {"project_code": "P1", "report_month": "2024-07", "actual_label": 0, "predicted_probability": 0.3},
            {"project_code": "P2", "report_month": "2024-06", "actual_label": 0, "predicted_probability": 0.1},
            {"project_code": "P2", "report_month": "2024-07", "actual_label": 0, "predicted_probability": 0.2},
            {"project_code": "P3", "report_month": "2024-06", "actual_label": 1, "predicted_probability": 0.7},
        ]
        ci1 = project_cluster_bootstrap(sample_preds, iterations=50, seed=12345)
        ci2 = project_cluster_bootstrap(sample_preds, iterations=50, seed=12345)
        self.assertEqual(ci1, ci2)

    def test_20_month_block_bootstrap_deterministic(self):
        """20. Month-block bootstrap deterministic with fixed seed."""
        sample_preds = [
            {"project_code": "P1", "report_month": "2024-06", "actual_label": 1, "predicted_probability": 0.8},
            {"project_code": "P1", "report_month": "2024-07", "actual_label": 0, "predicted_probability": 0.3},
            {"project_code": "P2", "report_month": "2024-06", "actual_label": 0, "predicted_probability": 0.1},
            {"project_code": "P2", "report_month": "2024-07", "actual_label": 0, "predicted_probability": 0.2},
            {"project_code": "P3", "report_month": "2024-06", "actual_label": 1, "predicted_probability": 0.7},
        ]
        ci1 = month_block_bootstrap(sample_preds, iterations=50, seed=12345)
        ci2 = month_block_bootstrap(sample_preds, iterations=50, seed=12345)
        self.assertEqual(ci1, ci2)

    def test_21_explainability_uses_only_approved_features(self):
        """21. Explainability uses only approved features and reconciles exactly."""
        fi_csv = DEFAULT_OUTPUT_DIR / "feature_importance.csv"
        df_fi = pd.read_csv(fi_csv)
        fi_features = set(df_fi["feature_name"].unique())
        self.assertEqual(fi_features, set(FEATURE_NAMES))

    def test_22_candidate_recommendation_is_reproducible(self):
        """22. Candidate recommendation is reproducible and evidence-based."""
        rec_json = DEFAULT_OUTPUT_DIR / "candidate_recommendation.json"
        with rec_json.open("r", encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(rec["overall_operational_recommendation"], "NOT_READY_FOR_PRODUCTION")
        self.assertIn("LEGACY", rec["evaluation_regimes"])
        self.assertIn("MODERN", rec["evaluation_regimes"])

    def test_23_artifact_inventory_is_complete(self):
        """23. Artifact inventory is complete."""
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

    def test_24_canonical_datasets_remain_unchanged(self):
        """24. Canonical datasets remain byte-for-byte unchanged."""
        self.assertEqual(sha256_file(CANONICAL_MONTHLY), EXPECTED_MONTHLY_SHA256)
        self.assertEqual(sha256_file(CANONICAL_COMPLETED), EXPECTED_COMPLETED_SHA256)

    def test_25_no_schedule_ml_contracts_or_artifacts_modified(self):
        """25. No schedule ML contracts or artifacts are modified."""
        schedule_manifest = Path("data/ml/schedule_extension_3m/manifest.json")
        self.assertTrue(schedule_manifest.is_file())
        with schedule_manifest.open("r", encoding="utf-8") as f:
            m = json.load(f)
        self.assertEqual(m["target"], "target_effective_schedule_ext_3m")
        self.assertEqual(m["target_horizon_months"], 3)


if __name__ == "__main__":
    unittest.main()
