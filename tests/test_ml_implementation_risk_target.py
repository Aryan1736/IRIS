"""Comprehensive regression tests for IRIS PR-08 Implementation Risk Target Definition.

Covers:
1. Contract exists and parses.
2. Contract version is valid.
3. Target definition is explicit.
4. Dataset hashes validate.
5. Deterministic target classification.
6. Positive classification (progress stalled, zero advance, deterioration).
7. Negative classification (progress advance).
8. Right-censoring detection.
9. Panel-exit censoring.
10. Dataset-end censoring.
11. Structural-gap censoring.
12. Segment-boundary censoring.
13. Ambiguous observation handling (missing baseline, missing future, completed baseline).
14. Population reconciliation determinism.
15. Exact positive and negative counts reconciliation.
16. Temporal feasibility table structure and monthly coverage.
17. Strict embargo enforcement (T + 3 < E).
18. Equality T + H == E is strictly rejected.
19. Leakage fields are rejected.
20. Allowed feature families remain accepted.
21. Completed-project outcome fields are prohibited.
22. Artifacts are generated and exist on disk.
23. Artifact schemas are internally consistent.
24. Recommendation status is valid (VIABLE_WITH_LIMITATIONS).
25. Canonical datasets remain byte-for-byte unchanged.
"""

import json
from pathlib import Path
import unittest

import pandas as pd

from src.ml.implementation_risk_target import (
    DEFAULT_CONTRACT_PATH,
    DEFAULT_OUTPUT_DIR,
    HORIZON,
    TOLERANCE_PROGRESS,
    audit_completed_implementation_risk,
    audit_leakage,
    audit_temporal_feasibility,
    build_implementation_risk_population,
    classify_implementation_target,
    evaluate_embargo,
    load_implementation_contract,
    reconcile_population,
    sha256_file,
    validate_canonical_hashes,
)

CANONICAL_MONTHLY = Path("data/processed/projects_monthly.csv")
CANONICAL_COMPLETED = Path("data/processed/projects_completed.csv")

EXPECTED_MONTHLY_SHA256 = "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF"
EXPECTED_COMPLETED_SHA256 = "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910"


class TestImplementationRiskContract(unittest.TestCase):
    """Contract schema and metadata verification tests."""

    def setUp(self):
        self.contract = load_implementation_contract(DEFAULT_CONTRACT_PATH)

    def test_01_contract_exists_and_parses(self):
        """1. Contract exists and parses without errors."""
        self.assertTrue(DEFAULT_CONTRACT_PATH.is_file())
        self.assertIsInstance(self.contract, dict)

    def test_02_contract_version_is_valid(self):
        """2. Contract version is valid semver string."""
        self.assertIn("contract_version", self.contract)
        self.assertEqual(self.contract["contract_version"], "1.0.0")

    def test_03_target_definition_is_explicit(self):
        """3. Target definition is explicit with correct name, horizon, and tolerance."""
        target = self.contract["target"]
        self.assertEqual(target["name"], "target_progress_stagnation_3m")
        self.assertEqual(target["horizon_months"], 3)
        self.assertAlmostEqual(target["tolerance_percentage"], 1e-6)
        self.assertIn("description", target)
        self.assertIn("positive_rule", target)
        self.assertIn("negative_rule", target)
        self.assertIn("ambiguity_rules", target)
        self.assertIn("progress_subtypes", target)


class TestTargetClassificationLogic(unittest.TestCase):
    """Synthetic unit tests for classification rules, edge cases, and censoring."""

    def test_05_deterministic_target_classification(self):
        """5. Target classification is 100% deterministic on identical input."""
        current = {"project_code": "P1", "report_month": "2024-06", "physical_progress": 50.0}
        by_month = {
            "2024-06": current,
            "2024-07": {"project_code": "P1", "report_month": "2024-07", "physical_progress": 50.0},
            "2024-08": {"project_code": "P1", "report_month": "2024-08", "physical_progress": 50.0},
            "2024-09": {"project_code": "P1", "report_month": "2024-09", "physical_progress": 50.0},
        }
        dec1 = classify_implementation_target(current, by_month)
        dec2 = classify_implementation_target(current, by_month)
        self.assertEqual(dec1, dec2)

    def test_06_positive_classification(self):
        """6. Positive classification for stalled progress and downward revision."""
        # Flat progress (ZERO_ADVANCE)
        current_flat = {"project_code": "P1", "report_month": "2024-06", "physical_progress": 45.0}
        by_month_flat = {
            "2024-06": current_flat,
            "2024-07": {"project_code": "P1", "report_month": "2024-07", "physical_progress": 45.0},
            "2024-08": {"project_code": "P1", "report_month": "2024-08", "physical_progress": 45.0},
            "2024-09": {"project_code": "P1", "report_month": "2024-09", "physical_progress": 45.0},
        }
        dec_flat = classify_implementation_target(current_flat, by_month_flat)
        self.assertTrue(dec_flat.eligible)
        self.assertEqual(dec_flat.label, 1)
        self.assertEqual(dec_flat.reason, "ELIGIBLE_POSITIVE")
        self.assertEqual(dec_flat.progress_subtype, "ZERO_ADVANCE")

        # Downward revision (DETERIORATION)
        current_det = {"project_code": "P2", "report_month": "2024-06", "physical_progress": 50.0}
        by_month_det = {
            "2024-06": current_det,
            "2024-07": {"project_code": "P2", "report_month": "2024-07", "physical_progress": 50.0},
            "2024-08": {"project_code": "P2", "report_month": "2024-08", "physical_progress": 48.0},
            "2024-09": {"project_code": "P2", "report_month": "2024-09", "physical_progress": 45.0},
        }
        dec_det = classify_implementation_target(current_det, by_month_det)
        self.assertTrue(dec_det.eligible)
        self.assertEqual(dec_det.label, 1)
        self.assertEqual(dec_det.reason, "ELIGIBLE_POSITIVE")
        self.assertEqual(dec_det.progress_subtype, "DETERIORATION")

    def test_07_negative_classification(self):
        """7. Negative classification when physical progress advances."""
        current = {"project_code": "P1", "report_month": "2024-06", "physical_progress": 45.0}
        by_month = {
            "2024-06": current,
            "2024-07": {"project_code": "P1", "report_month": "2024-07", "physical_progress": 47.0},
            "2024-08": {"project_code": "P1", "report_month": "2024-08", "physical_progress": 50.0},
            "2024-09": {"project_code": "P1", "report_month": "2024-09", "physical_progress": 52.5},
        }
        dec = classify_implementation_target(current, by_month)
        self.assertTrue(dec.eligible)
        self.assertEqual(dec.label, 0)
        self.assertEqual(dec.reason, "ELIGIBLE_NEGATIVE")
        self.assertEqual(dec.progress_subtype, "ADVANCE")
        self.assertAlmostEqual(dec.delta_progress, 7.5)

    def test_08_right_censoring_detection(self):
        """8. Right-censored observation is marked ineligible with exact reason."""
        # Panel exit at T+2
        current = {"project_code": "P1", "report_month": "2024-06", "physical_progress": 45.0}
        by_month = {
            "2024-06": current,
            "2024-07": {"project_code": "P1", "report_month": "2024-07", "physical_progress": 46.0},
            # 2024-08 and 2024-09 missing
        }
        dec = classify_implementation_target(current, by_month)
        self.assertFalse(dec.eligible)
        self.assertIsNone(dec.label)
        self.assertEqual(dec.reason, "PROJECT_DISAPPEARED_OR_PANEL_EXIT")

    def test_09_panel_exit_censoring(self):
        """9. Panel exit censoring detects disappearance in forward window."""
        current = {"project_code": "P1", "report_month": "2025-08", "physical_progress": 20.0}
        by_month = {
            "2025-08": current,
            "2025-09": {"project_code": "P1", "report_month": "2025-09", "physical_progress": 22.0},
            "2025-10": {"project_code": "P1", "report_month": "2025-10", "physical_progress": 24.0},
            # 2025-11 missing
        }
        dec = classify_implementation_target(current, by_month)
        self.assertFalse(dec.eligible)
        self.assertEqual(dec.reason, "PROJECT_DISAPPEARED_OR_PANEL_EXIT")

    def test_10_dataset_end_censoring(self):
        """10. Observations near dataset end (e.g. 2026-06) are boundary-censored."""
        current = {"project_code": "P1", "report_month": "2026-06", "physical_progress": 80.0}
        by_month = {"2026-06": current}
        dec = classify_implementation_target(current, by_month)
        self.assertFalse(dec.eligible)
        self.assertEqual(dec.reason, "STRUCTURAL_GAP_OR_REGIME_BOUNDARY")
        self.assertEqual(dec.window_end, "2026-09")

    def test_11_structural_gap_censoring(self):
        """11. Structural gap between 2024-03 and 2024-06 censors window."""
        current = {"project_code": "P1", "report_month": "2024-02", "physical_progress": 10.0}
        by_month = {"2024-02": current}
        dec = classify_implementation_target(current, by_month)
        self.assertFalse(dec.eligible)
        self.assertEqual(dec.reason, "STRUCTURAL_GAP_OR_REGIME_BOUNDARY")

    def test_12_segment_boundary_censoring(self):
        """12. Regime redesign boundary between 2025-06 and 2025-07 censors window."""
        current = {"project_code": "P1", "report_month": "2025-05", "physical_progress": 30.0}
        by_month = {"2025-05": current}
        dec = classify_implementation_target(current, by_month)
        self.assertFalse(dec.eligible)
        self.assertEqual(dec.reason, "STRUCTURAL_GAP_OR_REGIME_BOUNDARY")
        self.assertEqual(dec.window_end, "2025-08")

    def test_13_ambiguous_observation_handling(self):
        """13. Ambiguous observations (missing baseline, missing future, completed) handled cleanly."""
        # Missing baseline progress
        c_miss = {"project_code": "P1", "report_month": "2024-06", "physical_progress": None}
        bm_miss = {
            "2024-06": c_miss,
            "2024-07": {"project_code": "P1", "report_month": "2024-07", "physical_progress": 10.0},
            "2024-08": {"project_code": "P1", "report_month": "2024-08", "physical_progress": 10.0},
            "2024-09": {"project_code": "P1", "report_month": "2024-09", "physical_progress": 10.0},
        }
        dec_miss = classify_implementation_target(c_miss, bm_miss)
        self.assertFalse(dec_miss.eligible)
        self.assertEqual(dec_miss.reason, "MISSING_BASELINE_PROGRESS")

        # Baseline already completed (>= 100%)
        c_comp = {"project_code": "P1", "report_month": "2024-06", "physical_progress": 100.0}
        bm_comp = {
            "2024-06": c_comp,
            "2024-07": {"project_code": "P1", "report_month": "2024-07", "physical_progress": 100.0},
            "2024-08": {"project_code": "P1", "report_month": "2024-08", "physical_progress": 100.0},
            "2024-09": {"project_code": "P1", "report_month": "2024-09", "physical_progress": 100.0},
        }
        dec_comp = classify_implementation_target(c_comp, bm_comp)
        self.assertFalse(dec_comp.eligible)
        self.assertEqual(dec_comp.reason, "BASELINE_ALREADY_COMPLETED")

        # Future progress missing
        c_fut_miss = {"project_code": "P1", "report_month": "2024-06", "physical_progress": 50.0}
        bm_fut_miss = {
            "2024-06": c_fut_miss,
            "2024-07": {"project_code": "P1", "report_month": "2024-07", "physical_progress": 52.0},
            "2024-08": {"project_code": "P1", "report_month": "2024-08", "physical_progress": None},
            "2024-09": {"project_code": "P1", "report_month": "2024-09", "physical_progress": 55.0},
        }
        dec_fut_miss = classify_implementation_target(c_fut_miss, bm_fut_miss)
        self.assertFalse(dec_fut_miss.eligible)
        self.assertEqual(dec_fut_miss.reason, "FUTURE_PROGRESS_MISSING")

        # Unsupported layout (Segment 1)
        c_unsupp = {"project_code": "P1", "report_month": "2023-05", "physical_progress": None}
        bm_unsupp = {
            "2023-05": c_unsupp,
            "2023-06": {"project_code": "P1", "report_month": "2023-06", "physical_progress": None},
            "2023-07": {"project_code": "P1", "report_month": "2023-07", "physical_progress": None},
            "2023-08": {"project_code": "P1", "report_month": "2023-08", "physical_progress": None},
        }
        dec_unsupp = classify_implementation_target(c_unsupp, bm_unsupp)
        self.assertFalse(dec_unsupp.eligible)
        self.assertEqual(dec_unsupp.reason, "LAYOUT_PROGRESS_UNSUPPORTED")


class TestEmpiricalPopulationReconciliation(unittest.TestCase):
    """Full-dataset empirical population and reconciliation tests."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load_implementation_contract(DEFAULT_CONTRACT_PATH)
        cls.df_monthly = pd.read_csv(CANONICAL_MONTHLY, low_memory=False)
        cls.df_completed = pd.read_csv(CANONICAL_COMPLETED, low_memory=False)
        cls.classified_df = build_implementation_risk_population(cls.df_monthly)
        cls.reconciliation = reconcile_population(cls.classified_df)

    def test_04_dataset_hashes_validate(self):
        """4. Canonical dataset hashes validate against contract."""
        hashes = validate_canonical_hashes(Path("."), self.contract)
        self.assertTrue(all(hashes.values()))

    def test_14_population_reconciliation(self):
        """14. Population reconciliation is exact (sum of dispositions == total rows)."""
        self.assertTrue(self.reconciliation.reconciled)
        self.assertEqual(self.reconciliation.total_observations, 64608)

    def test_15_positive_negative_counts(self):
        """15. Exact positive, negative, and censoring counts match expected metrics."""
        self.assertEqual(self.reconciliation.eligible_positives, 7344)
        self.assertEqual(self.reconciliation.eligible_negatives, 18700)
        self.assertEqual(self.reconciliation.eligible_positives + self.reconciliation.eligible_negatives, 26044)
        self.assertEqual(self.reconciliation.censored_segment_boundary, 21489)
        self.assertEqual(self.reconciliation.censored_panel_exit, 2663)
        self.assertEqual(self.reconciliation.ineligible_layout_unsupported, 11993)
        self.assertEqual(self.reconciliation.ineligible_missing_baseline, 537)
        self.assertEqual(self.reconciliation.ineligible_baseline_completed, 1239)
        self.assertEqual(self.reconciliation.ineligible_future_missing, 643)

        # Prevalence ~ 28.20%
        self.assertAlmostEqual(self.reconciliation.positive_prevalence, 0.281984, places=4)
        # Class imbalance ~ 2.55 : 1
        self.assertAlmostEqual(self.reconciliation.class_imbalance_ratio, 2.5463, places=3)

    def test_16_temporal_feasibility(self):
        """16. Temporal feasibility audit table covers all 40 months and reflects positives."""
        temporal_df = audit_temporal_feasibility(self.classified_df)
        self.assertEqual(len(temporal_df), 40)
        self.assertEqual(temporal_df["total_observations"].sum(), 64608)
        self.assertEqual(temporal_df["positive_events"].sum(), 7344)
        self.assertEqual(temporal_df["negative_events"].sum(), 18700)

        # Segments 3 and 4 have robust positives in every eligible prediction month
        seg3_pos = temporal_df[temporal_df["continuous_segment"] == "SEGMENT_3"]["positive_events"].sum()
        seg4_pos = temporal_df[temporal_df["continuous_segment"] == "SEGMENT_4"]["positive_events"].sum()
        self.assertEqual(seg3_pos, 4335)
        self.assertEqual(seg4_pos, 3009)


class TestLeakageAndEmbargo(unittest.TestCase):
    """Verification of leakage prohibitions and strict embargo rules."""

    def setUp(self):
        self.contract = load_implementation_contract(DEFAULT_CONTRACT_PATH)

    def test_17_strict_embargo_enforcement(self):
        """17. Strict embargo logic T + H < E admits mature training observations."""
        # For evaluation origin E = 2026-01:
        # T = 2025-08 -> T+3 = 2025-11 < 2026-01 (True)
        self.assertTrue(evaluate_embargo("2025-08", "2026-01", horizon=3))
        # T = 2025-09 -> T+3 = 2025-12 < 2026-01 (True)
        self.assertTrue(evaluate_embargo("2025-09", "2026-01", horizon=3))

    def test_18_equality_t_plus_h_equals_e_rejected(self):
        """18. Equality T + H == E is strictly rejected by embargo rule."""
        # T = 2025-10 -> T+3 = 2026-01 == 2026-01 (False)
        self.assertFalse(evaluate_embargo("2025-10", "2026-01", horizon=3))
        # T = 2025-11 -> T+3 = 2026-02 > 2026-01 (False)
        self.assertFalse(evaluate_embargo("2025-11", "2026-01", horizon=3))

    def test_19_leakage_fields_are_rejected(self):
        """19. Prohibited leakage fields are caught by audit_leakage."""
        candidate_features_with_leakage = [
            "sector",
            "agency",
            "target_progress_stagnation_3m",  # direct target leakage!
            "future_progress_t3",              # future outcome leakage!
        ]
        audit = audit_leakage(self.contract, candidate_features_with_leakage)
        self.assertFalse(audit["is_leak_free"])
        self.assertIn("target_progress_stagnation_3m", audit["direct_leakage_fields"])
        self.assertIn("future_progress_t3", audit["direct_leakage_fields"])

    def test_20_allowed_feature_families_remain_accepted(self):
        """20. The 36 canonical features are completely leak-free."""
        audit = audit_leakage(self.contract, self.contract["features"]["ordered_names"])
        self.assertTrue(audit["is_leak_free"])
        self.assertEqual(len(audit["direct_leakage_fields"]), 0)
        self.assertEqual(audit["candidate_feature_count"], 36)

    def test_21_completed_project_outcome_fields_prohibited(self):
        """21. Completed project fields and outcomes are in prohibited list."""
        prohibited = set(self.contract["columns"]["leakage_strictly_prohibited"])
        completed_fields = [
            "actual_completion_date",
            "completed_revised_cost",
            "completed_cumulative_expenditure",
            "eventually_completed",
            "completion_report_month",
        ]
        for field in completed_fields:
            self.assertIn(field, prohibited)

        # Audit completed projects dataset shows unviability
        df_monthly = pd.read_csv(CANONICAL_MONTHLY, low_memory=False)
        df_completed = pd.read_csv(CANONICAL_COMPLETED, low_memory=False)
        completed_audit = audit_completed_implementation_risk(df_completed, df_monthly)
        self.assertEqual(completed_audit.viability_status, "NOT_YET_VIABLE")
        self.assertFalse(completed_audit.physical_progress_column_present)


class TestArtifactsAndViability(unittest.TestCase):
    """Verification of generated artifacts, schema consistency, and viability decision."""

    def setUp(self):
        self.output_dir = DEFAULT_OUTPUT_DIR

    def test_22_artifacts_are_generated(self):
        """22. All 6 required artifacts exist on disk."""
        expected_files = [
            "manifest.json",
            "target_population_summary.csv",
            "eligibility_summary.csv",
            "temporal_feasibility.csv",
            "leakage_audit.json",
            "candidate_recommendation.json",
        ]
        for fname in expected_files:
            fpath = self.output_dir / fname
            self.assertTrue(fpath.is_file(), f"Missing artifact: {fpath}")

    def test_23_artifact_schemas_are_internally_consistent(self):
        """23. Artifact schemas are internally consistent across JSON and CSV."""
        with (self.output_dir / "manifest.json").open("r", encoding="utf-8") as f:
            manifest = json.load(f)
        with (self.output_dir / "candidate_recommendation.json").open("r", encoding="utf-8") as f:
            rec = json.load(f)
        pop_summary = pd.read_csv(self.output_dir / "target_population_summary.csv")

        # Check total observations match
        self.assertEqual(manifest["population_reconciliation"]["total_observations"], 64608)
        self.assertEqual(rec["population_metrics"]["total_source_rows"], 64608)
        pop_dict = dict(zip(pop_summary["metric"], pop_summary["value"]))
        self.assertEqual(int(pop_dict["total_observations"]), 64608)
        self.assertEqual(int(pop_dict["eligible_positives"]), 7344)
        self.assertEqual(int(pop_dict["eligible_negatives"]), 18700)

    def test_24_recommendation_status_is_valid(self):
        """24. Recommendation status is VIABLE_WITH_LIMITATIONS with documented rationale."""
        with (self.output_dir / "candidate_recommendation.json").open("r", encoding="utf-8") as f:
            rec = json.load(f)
        self.assertEqual(rec["viability_status"], "VIABLE_WITH_LIMITATIONS")
        self.assertTrue(rec["recommended_for_pr09"])
        self.assertIn("primary_rationale", rec)
        self.assertIn("limitations", rec)
        self.assertTrue(len(rec["limitations"]) >= 3)

    def test_25_canonical_datasets_remain_unchanged(self):
        """25. Canonical processed datasets remain byte-for-byte unchanged."""
        monthly_hash = sha256_file(CANONICAL_MONTHLY)
        completed_hash = sha256_file(CANONICAL_COMPLETED)
        self.assertEqual(monthly_hash, EXPECTED_MONTHLY_SHA256)
        self.assertEqual(completed_hash, EXPECTED_COMPLETED_SHA256)


if __name__ == "__main__":
    unittest.main()
