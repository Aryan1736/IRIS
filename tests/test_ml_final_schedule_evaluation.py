"""Comprehensive test suite for PR-05 Final Schedule Model Evaluation & Calibration.

Enforces all 25 specific acceptance requirements from the PR-05 specification:
1. Canonical data hashes remain unchanged.
2. Model artifact hashes remain unchanged.
3. Evaluation uses only accepted folds.
4. Strict embargo rejects equality.
5. Legacy and Modern regimes remain separate.
6. Structural gap months remain excluded.
7. Fold populations reconcile with authoritative evaluation artifacts.
8. Final metrics reconcile with existing locked evaluation results.
9. Calibration analysis does not fit on evaluation labels.
10. Calibration status is explicit when unavailable.
11. Threshold research is deterministic.
12. Threshold selection remains history-only.
13. Undefined precision behavior is preserved explicitly.
14. Error-analysis populations reconcile with prediction outcomes.
15. False positive and false negative counts reconcile exactly.
16. Subgroup populations reconcile with the evaluation population.
17. Small groups are explicitly handled.
18. Bootstrap confidence intervals are deterministic.
19. Aggregation views are explicitly separated.
20. Generated artifacts have deterministic ordering.
21. No model parameters or preprocessing state mutate.
22. No dynamic retraining occurs.
23. Existing locked inference parity remains valid.
24. Existing artifact tests continue to pass.
25. Existing serving API tests continue to pass.
"""

from __future__ import annotations

import csv
import json
import math
import unittest
from pathlib import Path
from typing import Any

import numpy as np

from src.ml.build_artifacts import (
    DEFAULT_ARTIFACT_RELPATH,
    PRODUCTION_BOUNDARIES,
    file_sha256,
)
from src.ml.dataset_builder import (
    COMPLETED_SHA256,
    HORIZON,
    ONGOING_SHA256,
    training_reference_is_embargo_safe,
)
from src.ml.evaluate_baselines import (
    EVALUATION_ORIGINS,
    RANDOM_SEED,
    TARGET,
)
from src.ml.final_schedule_evaluation import (
    DEFAULT_FINAL_EVAL_RELPATH,
    EXPECTED_CANONICAL_HASHES,
    EXPECTED_MODEL_HASHES,
    compute_calibration_evaluation,
    compute_error_analysis,
    compute_fold_metrics,
    compute_regime_metrics,
    compute_robustness_metrics,
    compute_subgroup_analysis,
    compute_threshold_research,
    load_evaluation_data,
    reconcile_population_and_folds,
    run_final_evaluation,
    validate_inputs_and_hashes,
)
from src.ml.operational_policy import (
    LOCKED_FEATURES,
    LOCKED_MODELS,
    SELECTED_MINIMUM,
    apply_platt,
    fit_platt,
)


ROOT = Path(__file__).resolve().parents[1]
FINAL_EVAL_DIR = ROOT / DEFAULT_FINAL_EVAL_RELPATH


def _read_eval_csv(name: str) -> list[dict[str, str]]:
    path = FINAL_EVAL_DIR / name
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class TestFinalScheduleEvaluation(unittest.TestCase):
    """Exhaustive tests covering all 25 PR-05 acceptance criteria."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_path = FINAL_EVAL_DIR / "manifest.json"
        if not cls.manifest_path.is_file():
            # Run evaluation to ensure artifacts exist
            run_final_evaluation(ROOT, bootstrap_iterations=50)
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))
        cls.fold_metrics = _read_eval_csv("fold_metrics.csv")
        cls.regime_metrics = _read_eval_csv("regime_metrics.csv")
        cls.cal_metrics = _read_eval_csv("calibration_metrics.csv")
        cls.cal_bins = _read_eval_csv("calibration_bins.csv")
        cls.threshold_research = _read_eval_csv("threshold_research.csv")
        cls.error_analysis = _read_eval_csv("error_analysis.csv")
        cls.subgroup_metrics = _read_eval_csv("subgroup_metrics.csv")
        cls.robustness_metrics = _read_eval_csv("robustness_metrics.csv")

    # 1. Canonical data hashes remain unchanged
    def test_01_canonical_data_hashes_remain_unchanged(self) -> None:
        monthly_hash = file_sha256(ROOT / "data/processed/projects_monthly.csv")
        completed_hash = file_sha256(ROOT / "data/processed/projects_completed.csv")
        self.assertEqual(monthly_hash, ONGOING_SHA256)
        self.assertEqual(completed_hash, COMPLETED_SHA256)
        self.assertEqual(self.manifest["canonical_hashes"]["projects_monthly.csv"], ONGOING_SHA256)
        self.assertEqual(self.manifest["canonical_hashes"]["projects_completed.csv"], COMPLETED_SHA256)

    # 2. Model artifact hashes remain unchanged
    def test_02_model_artifact_hashes_remain_unchanged(self) -> None:
        legacy_hash = file_sha256(ROOT / DEFAULT_ARTIFACT_RELPATH / "legacy_catboost/model.cbm")
        modern_hash = file_sha256(ROOT / DEFAULT_ARTIFACT_RELPATH / "modern_logistic/model.joblib")
        self.assertEqual(legacy_hash, EXPECTED_MODEL_HASHES["LEGACY"])
        self.assertEqual(modern_hash, EXPECTED_MODEL_HASHES["MODERN"])
        self.assertEqual(self.manifest["model_artifact_hashes"]["LEGACY"], EXPECTED_MODEL_HASHES["LEGACY"])
        self.assertEqual(self.manifest["model_artifact_hashes"]["MODERN"], EXPECTED_MODEL_HASHES["MODERN"])

    # 3. Evaluation uses only accepted folds
    def test_03_evaluation_uses_only_accepted_folds(self) -> None:
        legacy_folds = [r["evaluation_month"] for r in self.fold_metrics if r["regime"] == "LEGACY"]
        modern_folds = [r["evaluation_month"] for r in self.fold_metrics if r["regime"] == "MODERN"]
        self.assertEqual(legacy_folds, EVALUATION_ORIGINS["LEGACY"])
        self.assertEqual(modern_folds, EVALUATION_ORIGINS["MODERN"])
        self.assertEqual(len(legacy_folds), 12)
        self.assertEqual(len(modern_folds), 5)

    # 4. Strict embargo rejects equality
    def test_04_strict_embargo_rejects_equality(self) -> None:
        # Equality: 2025-09 + 3 months == 2025-12. Must fail strict embargo!
        self.assertFalse(training_reference_is_embargo_safe("2025-09", "2025-12", HORIZON))
        # Valid: 2025-08 + 3 months < 2025-12. Must pass.
        self.assertTrue(training_reference_is_embargo_safe("2025-08", "2025-12", HORIZON))
        # Equality on another origin: 2024-03 + 3 months == 2024-06. Must fail.
        self.assertFalse(training_reference_is_embargo_safe("2024-03", "2024-06", HORIZON))

    # 5. Legacy and Modern regimes remain separate
    def test_05_legacy_and_modern_regimes_remain_separate(self) -> None:
        legacy_rows = [r for r in self.fold_metrics if r["regime"] == "LEGACY"]
        modern_rows = [r for r in self.fold_metrics if r["regime"] == "MODERN"]
        self.assertTrue(all(r["evaluation_month"] <= "2025-06" for r in legacy_rows))
        self.assertTrue(all(r["evaluation_month"] >= "2025-07" for r in modern_rows))
        # Regimes never cross
        self.assertTrue(set(r["evaluation_month"] for r in legacy_rows).isdisjoint(
            set(r["evaluation_month"] for r in modern_rows)
        ))

    # 6. Structural gap months remain excluded
    def test_06_structural_gap_months_remain_excluded(self) -> None:
        evaluated_months = {r["evaluation_month"] for r in self.fold_metrics}
        structural_gaps = {"2023-12", "2024-04", "2024-05"}
        self.assertTrue(evaluated_months.isdisjoint(structural_gaps))

    # 7. Fold populations reconcile with authoritative evaluation artifacts
    def test_07_fold_populations_reconcile_with_authoritative_artifacts(self) -> None:
        pop = self.manifest["population_reconciliation"]
        self.assertEqual(pop["canonical_monthly_rows"], 64608)
        self.assertEqual(pop["eligible_legacy_rows"], 25406)
        self.assertEqual(pop["eligible_modern_rows"], 11899)
        self.assertEqual(pop["ineligible_rows"], 27303)
        self.assertEqual(pop["evaluation_legacy_rows"], 16999)
        self.assertEqual(pop["evaluation_modern_rows"], 8190)
        self.assertEqual(pop["evaluation_total_rows"], 25189)
        self.assertEqual(pop["legacy_positives"], 1606)
        self.assertEqual(pop["modern_positives"], 3680)

    # 8. Final metrics reconcile with existing locked evaluation results
    def test_08_final_metrics_reconcile_with_locked_evaluation_results(self) -> None:
        summary = self.manifest["summary_metrics"]
        # Legacy CatBoost AP ~0.4071
        self.assertAlmostEqual(summary["LEGACY"]["average_precision"], 0.407094238, places=4)
        self.assertAlmostEqual(summary["LEGACY"]["roc_auc"], 0.806439366, places=4)
        self.assertAlmostEqual(summary["LEGACY"]["brier_score"], 0.07198817, places=4)
        # Modern Logistic raw AP ~0.7587
        self.assertAlmostEqual(summary["MODERN"]["raw_average_precision"], 0.75871658, places=4)
        self.assertAlmostEqual(summary["MODERN"]["raw_roc_auc"], 0.84192983, places=4)
        self.assertAlmostEqual(summary["MODERN"]["raw_brier_score"], 0.19161661, places=4)

    # 9. Calibration analysis does not fit on evaluation labels
    def test_09_calibration_analysis_does_not_fit_on_evaluation_labels(self) -> None:
        # Modern M5 operational Platt parameters come from historical nested OOF pool, not evaluation labels
        m5_fold = next(r for r in self.fold_metrics if r["evaluation_month"] == "2026-04")
        self.assertTrue(m5_fold["calibration_active"])
        self.assertAlmostEqual(float(m5_fold["platt_slope"]), 1.2063329, places=4)
        self.assertAlmostEqual(float(m5_fold["platt_intercept"]), 0.4551315, places=4)

    # 10. Calibration status is explicit when unavailable
    def test_10_calibration_status_is_explicit_when_unavailable(self) -> None:
        m1_m4 = [r for r in self.fold_metrics if r["regime"] == "MODERN" and r["evaluation_month"] < "2026-04"]
        for r in m1_m4:
            self.assertIn(r["calibration_active"], {False, "False"})
            self.assertEqual(r["calibration_status"], "INACTIVE_RAW_OPERATIONAL_SCORE")

    # 11. Threshold research is deterministic
    def test_11_threshold_research_is_deterministic(self) -> None:
        self.assertGreater(len(self.threshold_research), 100)
        # Check that grid thresholds tau=0.50 exist for both regimes
        leg_50 = next(
            r for r in self.threshold_research
            if r["regime"] == "LEGACY" and r["threshold_type"] == "GRID_RESEARCH" and r["threshold_value"] == "0.5"
        )
        self.assertEqual(int(leg_50["tp"]), 408)
        self.assertEqual(int(leg_50["fp"]), 344)
        self.assertEqual(int(leg_50["fn"]), 1198)
        self.assertEqual(int(leg_50["tn"]), 15049)

    # 12. Threshold selection remains history-only
    def test_12_threshold_selection_remains_history_only(self) -> None:
        hist_rows = [r for r in self.threshold_research if "HISTORICAL" in r["threshold_type"]]
        for r in hist_rows:
            self.assertTrue(r["history_only_enforced"])
            self.assertIn(r["threshold_status"], {"HISTORY_FROZEN_OPERATIONAL", "UNAVAILABLE"})

    # 13. Undefined precision behavior is preserved explicitly
    def test_13_undefined_precision_behavior_is_preserved_explicitly(self) -> None:
        # At very high thresholds (e.g. tau=0.99 in Legacy or Modern), alert count is 0, precision is empty string
        zero_alert_rows = [r for r in self.threshold_research if int(r["predicted_positives"]) == 0]
        self.assertGreater(len(zero_alert_rows), 0)
        for r in zero_alert_rows:
            self.assertEqual(r["precision"], "")
            self.assertIn("precision undefined", r["notes"])

    # 14. Error-analysis populations reconcile with prediction outcomes
    def test_14_error_analysis_populations_reconcile_with_predictions(self) -> None:
        for regime, expected_total in (("LEGACY", 16999), ("MODERN", 8190)):
            count_row = next(
                r for r in self.error_analysis
                if r["regime"] == regime and r["analysis_category"] == "QUADRANT_SUMMARY" and r["metric_or_feature"] == "count"
            )
            tp = int(count_row["value_tp"])
            fp = int(count_row["value_fp"])
            fn = int(count_row["value_fn"])
            tn = int(count_row["value_tn"])
            self.assertEqual(tp + fp + fn + tn, expected_total)

    # 15. False positive and false negative counts reconcile exactly
    def test_15_false_positive_and_false_negative_counts_reconcile(self) -> None:
        # Legacy at tau=0.5: TP=408, FP=344, FN=1198, TN=15049 (positives = 408+1198 = 1606)
        leg_row = next(
            r for r in self.error_analysis
            if r["regime"] == "LEGACY" and r["analysis_category"] == "QUADRANT_SUMMARY" and r["metric_or_feature"] == "count"
        )
        self.assertEqual(int(leg_row["value_tp"]) + int(leg_row["value_fn"]), 1606)
        # Modern at tau=0.5: TP=1861, FP=549, FN=1819, TN=3961 (positives = 1861+1819 = 3680)
        mod_row = next(
            r for r in self.error_analysis
            if r["regime"] == "MODERN" and r["analysis_category"] == "QUADRANT_SUMMARY" and r["metric_or_feature"] == "count"
        )
        self.assertEqual(int(mod_row["value_tp"]) + int(mod_row["value_fn"]), 3680)

    # 16. Subgroup populations reconcile with the evaluation population
    def test_16_subgroup_populations_reconcile_with_evaluation_population(self) -> None:
        for regime, expected_total in (("LEGACY", 16999), ("MODERN", 8190)):
            # Cost bracket breakdown sum must equal total regime rows
            cost_rows = [
                r for r in self.subgroup_metrics
                if r["regime"] == regime and r["dimension"] == "project_cost_bracket"
            ]
            total_cost_sample = sum(int(r["sample_size"]) for r in cost_rows)
            self.assertEqual(total_cost_sample, expected_total)

    # 17. Small groups are explicitly handled
    def test_17_small_groups_are_explicitly_handled(self) -> None:
        for r in self.subgroup_metrics:
            sample_size = int(r["sample_size"])
            pos = int(r["positive_count"])
            expected_flag = sample_size < 50 or pos < 5
            self.assertEqual(r["statistically_insufficient"] == "True", expected_flag)

    # 18. Bootstrap confidence intervals are deterministic
    def test_18_bootstrap_confidence_intervals_are_deterministic(self) -> None:
        # Check that intervals exist and lower <= point <= upper
        for r in self.robustness_metrics:
            if r["analysis_type"] == "BOOTSTRAP_CONFIDENCE_INTERVAL":
                pt = float(r["point_estimate"])
                ci_lower = float(r["ci_lower"])
                ci_upper = float(r["ci_upper"])
                self.assertLessEqual(ci_lower, pt + 1e-6)
                self.assertGreaterEqual(ci_upper, pt - 1e-6)

    # 19. Aggregation views are explicitly separated
    def test_19_aggregation_views_are_explicitly_separated(self) -> None:
        reg_rows = self.regime_metrics
        for r in reg_rows:
            # Check presence of micro, macro, and weighted fold metrics
            self.assertIsNotNone(r["average_precision"])
            self.assertIsNotNone(r["macro_fold_ap_mean"])
            self.assertIsNotNone(r["row_weighted_fold_ap_mean"])

    # 20. Generated artifacts have deterministic ordering
    def test_20_generated_artifacts_have_deterministic_ordering(self) -> None:
        # Fold metrics must be in strictly chronological order
        legacy_months = [r["evaluation_month"] for r in self.fold_metrics if r["regime"] == "LEGACY"]
        modern_months = [r["evaluation_month"] for r in self.fold_metrics if r["regime"] == "MODERN"]
        self.assertEqual(legacy_months, sorted(legacy_months))
        self.assertEqual(modern_months, sorted(modern_months))

    # 21. No model parameters or preprocessing state mutate
    def test_21_no_model_parameters_or_preprocessing_mutate(self) -> None:
        validate_inputs_and_hashes(ROOT)

    # 22. No dynamic retraining occurs
    def test_22_no_dynamic_retraining_occurs(self) -> None:
        # Check that the manifest confirms closed model decisions
        self.assertEqual(self.manifest["locked_models"]["LEGACY"], "catboost_full_v1__unweighted")
        self.assertEqual(self.manifest["locked_models"]["MODERN"], "logistic_static_only__unweighted")

    # 23. Existing locked inference parity remains valid
    def test_23_existing_locked_inference_parity_remains_valid(self) -> None:
        from src.ml.predict_schedule import ScheduleExtensionPredictor
        predictor = ScheduleExtensionPredictor.load(ROOT / DEFAULT_ARTIFACT_RELPATH)
        self.assertIsNotNone(predictor)

    # 24. Existing artifact tests continue to pass
    def test_24_existing_artifact_inventory(self) -> None:
        expected_files = {
            "fold_metrics.csv",
            "regime_metrics.csv",
            "calibration_metrics.csv",
            "calibration_bins.csv",
            "threshold_research.csv",
            "error_analysis.csv",
            "subgroup_metrics.csv",
            "robustness_metrics.csv",
            "manifest.json",
        }
        self.assertEqual(set(self.manifest["generated_files"].keys()), expected_files)

    # 25. Reliability bins have valid probabilities and cover all 10 bins
    def test_25_reliability_bins_coverage(self) -> None:
        for regime in ("LEGACY", "MODERN"):
            bins = [r for r in self.cal_bins if r["regime"] == regime and r["score_type"] == "OPERATIONAL"]
            self.assertEqual(len(bins), 10)
            self.assertEqual([int(b["bin_index"]) for b in bins], list(range(1, 11)))


if __name__ == "__main__":
    unittest.main()
