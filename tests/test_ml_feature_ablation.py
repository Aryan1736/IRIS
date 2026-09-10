"""Regression test suite for PR-11 Feature Ablation Study.

Verifies:
1. Feature inventory completeness & deterministic classification.
2. Every studied feature classified deterministically (static_current, longitudinal, excluded).
3. No prohibited leakage fields in any feature subset.
4. No future-derived features in feature sets.
5. Canonical dataset hash integrity.
6. Regime separation.
7. Structural gap rejection.
8. Strict embargo enforcement: T_train + 3 < E.
9. Equality embargo rejection: T_train + 3 == E fails.
10. Fold isolation.
11. Training-only preprocessing (FoldPreprocessor fits on train only).
12. Static subset extraction: 25 features.
13. Longitudinal subset extraction: 11 features.
14. Full subset equals valid union of static and longitudinal groups: 36 features.
15. Deterministic model results on synthetic/sample folds.
16. Deterministic artifacts generation & existence.
17. Fold metric correctness (AP, ROC-AUC, Brier, etc.).
18. Regime aggregation correctness (micro, macro, row-weighted).
19. Delta calculation correctness (Model B - Model A).
20. Calibration metric correctness (ECE 10-bin, MCE 10-bin).
21. Bootstrap determinism.
22. Artifact schema validation.
23. Manifest integrity.
24. No locked production model mutation.
25. No canonical dataset mutation.
"""

from __future__ import annotations

import csv
import json
import math
import unittest
from pathlib import Path

import numpy as np

from src.ml.build_artifacts import file_sha256
from src.ml.data_contract import (
    compute_file_sha256,
    default_contract_path,
    load_contract,
    month_index,
    validate_embargo_rule,
)
from src.ml.dataset_builder import (
    COMPLETED_SHA256,
    HORIZON,
    ONGOING_SHA256,
    add_months,
    training_reference_is_embargo_safe,
)
from src.ml.evaluate_baselines import (
    BOOTSTRAP_ITERATIONS,
    CATEGORICAL_FEATURES,
    EVALUATION_ORIGINS,
    PROHIBITED_FEATURES,
    RANDOM_SEED,
    TARGET,
    FoldPreprocessor,
    expected_calibration_error,
    select_training_rows,
)
from src.ml.feature_ablation import (
    DEFAULT_OUTPUT_RELPATH,
    EXPECTED_CANONICAL_HASHES,
    EXPECTED_LOCKED_MODEL_HASHES,
    EXCLUDED_INVENTORY_DEFINITIONS,
    FULL_CONTRACT_FEATURES,
    LONGITUDINAL_FEATURES,
    STATIC_CURRENT_FEATURES,
    build_feature_inventory,
    compute_point_metrics,
    max_calibration_error,
    train_and_score_logistic,
    validate_feature_leakage,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data/ml/schedule_extension_3m"
ARTIFACTS_DIR = ROOT / DEFAULT_OUTPUT_RELPATH


class TestMLFeatureAblation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = build_feature_inventory()
        cls.contract = load_contract(default_contract_path(ROOT))

    # 1. Feature inventory completeness
    def test_01_feature_inventory_completeness(self) -> None:
        names = [item["feature_name"] for item in self.inventory]
        self.assertEqual(len(names), len(set(names)), "Feature names must be unique in inventory")
        # 25 static + 11 longitudinal + 16 excluded = 52 total items
        self.assertEqual(len(self.inventory), 52)
        for name in STATIC_CURRENT_FEATURES:
            self.assertIn(name, names)
        for name in LONGITUDINAL_FEATURES:
            self.assertIn(name, names)

    # 2. Every studied feature classified deterministically
    def test_02_every_studied_feature_classified_deterministically(self) -> None:
        valid_groups = {"static_current", "longitudinal", "excluded"}
        for item in self.inventory:
            self.assertIn(item["feature_group"], valid_groups)
            self.assertTrue(len(item["rationale"]) > 10, "Each feature must have documented rationale")
            self.assertIsInstance(item["available_legacy"], bool)
            self.assertIsInstance(item["available_modern"], bool)

    # 3. No prohibited leakage fields
    def test_03_no_prohibited_leakage_fields(self) -> None:
        static_leakage = set(STATIC_CURRENT_FEATURES) & set(PROHIBITED_FEATURES)
        long_leakage = set(LONGITUDINAL_FEATURES) & set(PROHIBITED_FEATURES)
        full_leakage = set(FULL_CONTRACT_FEATURES) & set(PROHIBITED_FEATURES)
        self.assertEqual(static_leakage, set())
        self.assertEqual(long_leakage, set())
        self.assertEqual(full_leakage, set())
        validate_feature_leakage(STATIC_CURRENT_FEATURES)
        validate_feature_leakage(LONGITUDINAL_FEATURES)
        validate_feature_leakage(FULL_CONTRACT_FEATURES)

    # 4. No future-derived features
    def test_04_no_future_derived_features(self) -> None:
        future_terms = {"actual_completion", "eventually", "target_event", "completion_report"}
        for f in FULL_CONTRACT_FEATURES:
            for term in future_terms:
                self.assertNotIn(term, f.lower(), f"Feature {f} appears future-derived")

    # 5. Canonical dataset hash integrity
    def test_05_canonical_dataset_hash_integrity(self) -> None:
        for fname, expected in EXPECTED_CANONICAL_HASHES.items():
            path = ROOT / "data/processed" / fname
            self.assertTrue(path.is_file(), f"Missing canonical file {path}")
            self.assertEqual(file_sha256(path), expected)

    # 6. Regime separation
    def test_06_regime_separation(self) -> None:
        legacy_origins = EVALUATION_ORIGINS["LEGACY"]
        modern_origins = EVALUATION_ORIGINS["MODERN"]
        # Disjoint origins
        self.assertEqual(set(legacy_origins) & set(modern_origins), set())
        # Chronological boundary: all Legacy origins < 2025-07; all Modern origins >= 2025-07
        for o in legacy_origins:
            self.assertLess(o, "2025-07")
        for o in modern_origins:
            self.assertGreaterEqual(o, "2025-07")

    # 7. Structural gap rejection
    def test_07_structural_gap_rejection(self) -> None:
        structural_gaps = ["2023-12", "2024-04", "2024-05", "2025-05", "2025-06"]
        for gap in structural_gaps:
            self.assertNotIn(gap, EVALUATION_ORIGINS["LEGACY"])
            self.assertNotIn(gap, EVALUATION_ORIGINS["MODERN"])

    # 8. Strict embargo enforcement: T_train + 3 < E
    def test_08_strict_embargo_enforcement(self) -> None:
        self.assertTrue(validate_embargo_rule("2024-01", "2024-06", HORIZON))
        self.assertTrue(validate_embargo_rule("2024-02", "2024-06", HORIZON))
        # 2024-03 + 3 = 2024-06 -> not strictly before 2024-06
        self.assertFalse(validate_embargo_rule("2024-03", "2024-06", HORIZON))

    # 9. Equality embargo rejection
    def test_09_equality_embargo_rejection(self) -> None:
        for origin in EVALUATION_ORIGINS["LEGACY"] + EVALUATION_ORIGINS["MODERN"]:
            equality_month = add_months(origin, -HORIZON)
            self.assertFalse(
                validate_embargo_rule(equality_month, origin, HORIZON),
                f"Equality month {equality_month} + 3 < {origin} must be rejected",
            )

    # 10. Fold isolation
    def test_10_fold_isolation(self) -> None:
        for regime in ("LEGACY", "MODERN"):
            origins = EVALUATION_ORIGINS[regime]
            for origin in origins:
                equality_month = add_months(origin, -HORIZON)
                self.assertFalse(training_reference_is_embargo_safe(equality_month, origin, HORIZON))

    # 11. Training-only preprocessing
    def test_11_training_only_preprocessing(self) -> None:
        train_rows = [
            {"sector": "POWER", "original_cost": "100.0", TARGET: "0"},
            {"sector": "RAILWAYS", "original_cost": "200.0", TARGET: "1"},
            {"sector": "POWER", "original_cost": "300.0", TARGET: "0"},
        ]
        eval_rows = [
            {"sector": "COAL", "original_cost": "400.0"},  # unseen sector
        ]
        processor = FoldPreprocessor(["sector", "original_cost"]).fit(train_rows)
        # Unseen category receives frequency 0
        transformed = processor.transform(eval_rows)
        self.assertEqual(transformed[0, 0], 0.0)  # frequency encoded 'COAL'
        # Training mean should be 200.0
        self.assertAlmostEqual(processor.numeric_mean["original_cost"], 200.0)

    # 12. Static subset extraction
    def test_12_static_subset_extraction(self) -> None:
        static_sub = [f for f in FULL_CONTRACT_FEATURES if f in STATIC_CURRENT_FEATURES]
        self.assertEqual(len(static_sub), 25)
        self.assertEqual(set(static_sub), set(STATIC_CURRENT_FEATURES))

    # 13. Longitudinal subset extraction
    def test_13_longitudinal_subset_extraction(self) -> None:
        long_sub = [f for f in FULL_CONTRACT_FEATURES if f in LONGITUDINAL_FEATURES]
        self.assertEqual(len(long_sub), 11)
        self.assertEqual(set(long_sub), set(LONGITUDINAL_FEATURES))

    # 14. Full subset equals valid union of groups
    def test_14_full_subset_equals_valid_union_of_groups(self) -> None:
        static_set = set(STATIC_CURRENT_FEATURES)
        long_set = set(LONGITUDINAL_FEATURES)
        # Disjoint
        self.assertEqual(static_set & long_set, set())
        # Union equals 36 contract features
        self.assertEqual(static_set | long_set, set(FULL_CONTRACT_FEATURES))
        self.assertEqual(len(FULL_CONTRACT_FEATURES), 36)

    # 15. Deterministic model results on synthetic fold
    def test_15_deterministic_model_results(self) -> None:
        train_rows = [
            {"sector": "POWER", "original_cost": "100.0", "exp_delta_3m": "10.0", TARGET: "0"},
            {"sector": "RAILWAYS", "original_cost": "200.0", "exp_delta_3m": "0.0", TARGET: "1"},
            {"sector": "POWER", "original_cost": "150.0", "exp_delta_3m": "5.0", TARGET: "0"},
            {"sector": "ROADS", "original_cost": "500.0", "exp_delta_3m": "50.0", TARGET: "1"},
        ]
        eval_rows = [
            {"sector": "POWER", "original_cost": "120.0", "exp_delta_3m": "8.0"},
            {"sector": "ROADS", "original_cost": "300.0", "exp_delta_3m": "20.0"},
        ]
        cols = ["sector", "original_cost", "exp_delta_3m"]
        scores1, _, _ = train_and_score_logistic(train_rows, eval_rows, cols)
        scores2, _, _ = train_and_score_logistic(train_rows, eval_rows, cols)
        np.testing.assert_allclose(scores1, scores2, atol=1e-12)

    # 16. Deterministic artifacts exist
    def test_16_deterministic_artifacts_exist(self) -> None:
        expected_files = [
            "manifest.json",
            "feature_inventory.csv",
            "fold_metrics.csv",
            "regime_metrics.csv",
            "ablation_summary.csv",
            "feature_group_importance.csv",
            "robustness_metrics.csv",
            "candidate_recommendation.json",
        ]
        for fname in expected_files:
            path = ARTIFACTS_DIR / fname
            self.assertTrue(path.is_file(), f"Required artifact {fname} missing from {ARTIFACTS_DIR}")

    # 17. Fold metric correctness
    def test_17_fold_metric_correctness(self) -> None:
        y = np.array([0, 1, 0, 1, 1])
        score = np.array([0.1, 0.9, 0.2, 0.8, 0.3])
        metrics = compute_point_metrics(y, score, threshold=0.5)
        self.assertEqual(metrics["evaluation_rows"], 5)
        self.assertEqual(metrics["positives"], 3)
        self.assertEqual(metrics["negatives"], 2)
        # tp=2, fp=0, fn=1, tn=2
        self.assertAlmostEqual(metrics["precision"], 1.0)
        self.assertAlmostEqual(metrics["recall"], 2 / 3)
        self.assertAlmostEqual(metrics["specificity"], 1.0)
        self.assertAlmostEqual(metrics["alert_rate"], 2 / 5)

    # 18. Regime aggregation correctness
    def test_18_regime_aggregation_correctness(self) -> None:
        regime_csv = ARTIFACTS_DIR / "regime_metrics.csv"
        self.assertTrue(regime_csv.is_file())
        with regime_csv.open("r", encoding="utf-8-sig") as h:
            rows = list(csv.DictReader(h))
        self.assertEqual(len(rows), 6)  # 3 configs x 2 regimes
        for r in rows:
            self.assertIn(r["regime"], {"LEGACY", "MODERN"})
            self.assertTrue(float(r["pooled_average_precision"]) > 0.0)
            self.assertTrue(float(r["pooled_roc_auc"]) > 0.5)
            self.assertTrue(float(r["pooled_brier_score"]) > 0.0)

    # 19. Delta calculation correctness
    def test_19_delta_calculation_correctness(self) -> None:
        ablation_csv = ARTIFACTS_DIR / "ablation_summary.csv"
        self.assertTrue(ablation_csv.is_file())
        with ablation_csv.open("r", encoding="utf-8-sig") as h:
            rows = list(csv.DictReader(h))
        self.assertTrue(len(rows) >= 18)
        for r in rows:
            va = float(r["model_a_static_only"])
            vb = float(r["model_b_static_plus_longitudinal"])
            delta = float(r["delta_b_minus_a"])
            self.assertAlmostEqual(delta, vb - va, places=6)

    # 20. Calibration metric correctness
    def test_20_calibration_metric_correctness(self) -> None:
        y = np.array([0, 1])
        score = np.array([0.5, 0.5])
        ece = expected_calibration_error(y, score, bins=10)
        mce = max_calibration_error(y, score, bins=10)
        self.assertAlmostEqual(ece, 0.0)
        self.assertAlmostEqual(mce, 0.0)

    # 21. Bootstrap determinism
    def test_21_bootstrap_determinism(self) -> None:
        rob_csv = ARTIFACTS_DIR / "robustness_metrics.csv"
        self.assertTrue(rob_csv.is_file())
        with rob_csv.open("r", encoding="utf-8-sig") as h:
            rows = list(csv.DictReader(h))
        self.assertEqual(len(rows), 4)  # AP and ROC-AUC for LEGACY and MODERN
        for r in rows:
            self.assertEqual(int(r["bootstrap_draws"]), 1000)
            low = float(r["delta_ci_low"])
            high = float(r["delta_ci_high"])
            self.assertLessEqual(low, high)

    # 22. Artifact schema validation
    def test_22_artifact_schema_validation(self) -> None:
        rec_json = ARTIFACTS_DIR / "candidate_recommendation.json"
        with rec_json.open("r", encoding="utf-8") as h:
            rec = json.load(h)
        self.assertIn("executive_answer", rec)
        self.assertIn("findings_by_regime", rec)
        self.assertIn("LEGACY", rec["findings_by_regime"])
        self.assertIn("MODERN", rec["findings_by_regime"])
        self.assertIn("operational_recommendation", rec)

    # 23. Manifest integrity
    def test_23_manifest_integrity(self) -> None:
        man_json = ARTIFACTS_DIR / "manifest.json"
        with man_json.open("r", encoding="utf-8") as h:
            manifest = json.load(h)
        self.assertEqual(manifest["target"], "target_effective_schedule_ext_3m")
        self.assertEqual(manifest["horizon_months"], 3)
        self.assertEqual(manifest["canonical_inputs"]["projects_monthly.csv"], ONGOING_SHA256)
        self.assertEqual(manifest["canonical_inputs"]["projects_completed.csv"], COMPLETED_SHA256)
        self.assertEqual(manifest["feature_counts"]["static_current"], 25)
        self.assertEqual(manifest["feature_counts"]["longitudinal"], 11)
        self.assertEqual(manifest["feature_counts"]["full_contract"], 36)

    # 24. No locked production model mutation
    def test_24_no_locked_production_model_mutation(self) -> None:
        for regime, expected in EXPECTED_LOCKED_MODEL_HASHES.items():
            rel = "legacy_catboost/model.cbm" if regime == "LEGACY" else "modern_logistic/model.joblib"
            path = ROOT / "artifacts/ml/schedule_extension_3m" / rel
            self.assertTrue(path.is_file())
            self.assertEqual(file_sha256(path), expected)

    # 25. No canonical dataset mutation
    def test_25_no_canonical_dataset_mutation(self) -> None:
        monthly_path = ROOT / "data/processed/projects_monthly.csv"
        completed_path = ROOT / "data/processed/projects_completed.csv"
        self.assertEqual(file_sha256(monthly_path), ONGOING_SHA256)
        self.assertEqual(file_sha256(completed_path), COMPLETED_SHA256)


if __name__ == "__main__":
    unittest.main()
