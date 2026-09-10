"""Regression tests for IRIS PR-06 Cost Overrun Target Definition.

Covers:
1. Contract version is readable.
2. Contract structure validates.
3. Target name is correct.
4. Positive condition behaves correctly.
5. Negative condition behaves correctly.
6. Missing outcome does not become negative.
7. Ongoing/right-censored observations are excluded from supervised labels.
8. Zero baseline handling is explicit.
9. Missing baseline handling is explicit.
10. Invalid numeric values fail or are excluded deterministically.
11. Positive/negative counts reconcile.
12. All source observations receive a deterministic disposition.
13. Temporal feasibility logic rejects future-known outcomes at prediction time.
14. Target source fields are identified as prohibited future model inputs.
15. Leakage fields cannot enter the allowed feature population.
16. Completed-project logic behaves deterministically.
17. Repeated target generation produces identical outputs.
18. Generated artifacts reconcile with source counts.
19. Canonical datasets remain byte-for-byte unchanged.
20. Target recommendation is supported by generated audit evidence.
"""

import json
from pathlib import Path
import unittest

import pandas as pd

from src.ml.cost_overrun_target import (
    DEFAULT_CONTRACT_PATH,
    DEFAULT_OUTPUT_DIR,
    TOLERANCE_CR,
    audit_completed_cost_overrun,
    audit_leakage,
    audit_temporal_feasibility,
    build_cost_overrun_population,
    classify_cost_target,
    load_cost_contract,
    reconcile_population,
    sha256_file,
)

CANONICAL_MONTHLY = Path("data/processed/projects_monthly.csv")
CANONICAL_COMPLETED = Path("data/processed/projects_completed.csv")

EXPECTED_MONTHLY_SHA256 = "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF"
EXPECTED_COMPLETED_SHA256 = "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910"


class TestCostOverrunTargetContract(unittest.TestCase):
    """Contract schema and metadata verification tests."""

    def setUp(self):
        self.contract = load_cost_contract(DEFAULT_CONTRACT_PATH)

    def test_01_contract_version_is_readable(self):
        """1. Contract version is readable and semver-compliant."""
        self.assertIn("contract_version", self.contract)
        self.assertEqual(self.contract["contract_version"], "1.0.0")

    def test_02_contract_structure_validates(self):
        """2. Contract structure validates with all required sections."""
        required_keys = [
            "dataset_name",
            "contract_version",
            "dataset_type",
            "target",
            "audited_candidates",
            "features",
            "columns",
            "embargo",
            "continuous_segments",
            "canonical_inputs",
            "expected_dataset_metrics",
            "policies",
            "viability_recommendation",
        ]
        for key in required_keys:
            self.assertIn(key, self.contract)
        self.assertEqual(len(self.contract["continuous_segments"]), 4)

    def test_03_target_name_is_correct(self):
        """3. Target name is strictly target_effective_cost_esc_3m."""
        self.assertEqual(self.contract["target"]["name"], "target_effective_cost_esc_3m")
        self.assertEqual(self.contract["target"]["horizon_months"], 3)
        self.assertEqual(self.contract["target"]["tolerance_cr"], 0.001)


class TestTargetClassificationLogic(unittest.TestCase):
    """Synthetic unit tests for classification rules, edge cases, and censoring."""

    def test_04_positive_condition_behaves_correctly(self):
        """4. Positive condition triggers when future revised_cost exceeds baseline."""
        # Unrevised at T, first revision at T+2 exceeding original cost
        current = {"project_code": "P1", "report_month": "2023-01", "original_cost": 100.0}
        by_month = {
            "2023-01": current,
            "2023-02": {"project_code": "P1", "report_month": "2023-02", "original_cost": 100.0},
            "2023-03": {"project_code": "P1", "report_month": "2023-03", "original_cost": 100.0, "revised_cost": 120.0},
            "2023-04": {"project_code": "P1", "report_month": "2023-04", "original_cost": 100.0, "revised_cost": 120.0},
        }
        dec = classify_cost_target(current, by_month, [])
        self.assertTrue(dec.eligible)
        self.assertEqual(dec.reason, "ELIGIBLE_POSITIVE")
        self.assertEqual(dec.label, 1)
        self.assertEqual(dec.cost_revision_type, "FIRST_COST_REVISION")
        self.assertEqual(dec.event_month, "2023-03")
        self.assertAlmostEqual(dec.cost_diff, 20.0)

        # Already revised at T, subsequent upward revision at T+1
        current_rev = {"project_code": "P1", "report_month": "2023-01", "original_cost": 100.0, "revised_cost": 120.0}
        by_month_rev = {
            "2023-01": current_rev,
            "2023-02": {"project_code": "P1", "report_month": "2023-02", "original_cost": 100.0, "revised_cost": 150.0},
            "2023-03": {"project_code": "P1", "report_month": "2023-03", "original_cost": 100.0, "revised_cost": 150.0},
            "2023-04": {"project_code": "P1", "report_month": "2023-04", "original_cost": 100.0, "revised_cost": 150.0},
        }
        dec2 = classify_cost_target(current_rev, by_month_rev, [])
        self.assertTrue(dec2.eligible)
        self.assertEqual(dec2.label, 1)
        self.assertEqual(dec2.cost_revision_type, "SUBSEQUENT_COST_REVISION")
        self.assertEqual(dec2.event_month, "2023-02")
        self.assertAlmostEqual(dec2.cost_diff, 30.0)

    def test_05_negative_condition_behaves_correctly(self):
        """5. Negative condition triggers when window is fully observed with no escalation."""
        current = {"project_code": "P2", "report_month": "2023-01", "original_cost": 100.0}
        by_month = {
            "2023-01": current,
            "2023-02": {"project_code": "P2", "report_month": "2023-02", "original_cost": 100.0},
            "2023-03": {"project_code": "P2", "report_month": "2023-03", "original_cost": 100.0},
            "2023-04": {"project_code": "P2", "report_month": "2023-04", "original_cost": 100.0},
        }
        dec = classify_cost_target(current, by_month, [])
        self.assertTrue(dec.eligible)
        self.assertEqual(dec.reason, "ELIGIBLE_NEGATIVE")
        self.assertEqual(dec.label, 0)
        self.assertEqual(dec.cost_revision_type, "NONE")
        self.assertEqual(dec.cost_diff, 0.0)

    def test_06_missing_outcome_does_not_become_negative(self):
        """6. Missing future outcome (null reset after revision) is ambiguous, not negative."""
        current = {"project_code": "P3", "report_month": "2023-01", "original_cost": 100.0, "revised_cost": 120.0}
        # Month T+2 has a null reset, not reporting revised_cost
        by_month = {
            "2023-01": current,
            "2023-02": {"project_code": "P3", "report_month": "2023-02", "original_cost": 100.0, "revised_cost": 120.0},
            "2023-03": {"project_code": "P3", "report_month": "2023-03", "original_cost": 100.0},  # null reset!
            "2023-04": {"project_code": "P3", "report_month": "2023-04", "original_cost": 100.0, "revised_cost": 120.0},
        }
        dec = classify_cost_target(current, by_month, [])
        self.assertFalse(dec.eligible)
        self.assertEqual(dec.reason, "FUTURE_REVISION_PERSISTENCE_AMBIGUOUS")
        self.assertIsNone(dec.label)

    def test_07_ongoing_right_censored_excluded_from_supervised_labels(self):
        """7. Ongoing/right-censored observations (boundary crossing or panel exit) are excluded."""
        # Case A: Boundary crossing (2023-09 to 2023-12 crosses into gap month)
        current_bnd = {"project_code": "P4", "report_month": "2023-09", "original_cost": 100.0}
        dec_bnd = classify_cost_target(current_bnd, {"2023-09": current_bnd}, [])
        self.assertFalse(dec_bnd.eligible)
        self.assertEqual(dec_bnd.reason, "STRUCTURAL_GAP_OR_REGIME_BOUNDARY")
        self.assertIsNone(dec_bnd.label)

        # Case B: Disappeared from panel before T+3
        current_exit = {"project_code": "P5", "report_month": "2023-01", "original_cost": 100.0}
        by_month_exit = {
            "2023-01": current_exit,
            "2023-02": {"project_code": "P5", "report_month": "2023-02", "original_cost": 100.0},
            # Missing 2023-03 and 2023-04
        }
        dec_exit = classify_cost_target(current_exit, by_month_exit, [])
        self.assertFalse(dec_exit.eligible)
        self.assertEqual(dec_exit.reason, "PROJECT_DISAPPEARED_OR_PANEL_EXIT")
        self.assertIsNone(dec_exit.label)

    def test_08_zero_baseline_handling_is_explicit(self):
        """8. Zero baseline original_cost is explicitly rejected as ineligible."""
        current = {"project_code": "P6", "report_month": "2023-01", "original_cost": 0.0}
        by_month = {"2023-01": current, "2023-02": current, "2023-03": current, "2023-04": current}
        dec = classify_cost_target(current, by_month, [])
        self.assertFalse(dec.eligible)
        self.assertEqual(dec.reason, "MISSING_OR_NONPOSITIVE_BASELINE_COST")

    def test_09_missing_baseline_handling_is_explicit(self):
        """9. Missing/null original_cost is explicitly rejected as ineligible."""
        current = {"project_code": "P7", "report_month": "2023-01", "original_cost": None}
        by_month = {"2023-01": current, "2023-02": current, "2023-03": current, "2023-04": current}
        dec = classify_cost_target(current, by_month, [])
        self.assertFalse(dec.eligible)
        self.assertEqual(dec.reason, "MISSING_OR_NONPOSITIVE_BASELINE_COST")

    def test_10_invalid_numeric_values_handled_deterministically(self):
        """10. Negative or non-numeric cost values fail closed deterministically."""
        current_neg = {"project_code": "P8", "report_month": "2023-01", "original_cost": -50.0}
        by_month = {"2023-01": current_neg, "2023-02": current_neg, "2023-03": current_neg, "2023-04": current_neg}
        dec_neg = classify_cost_target(current_neg, by_month, [])
        self.assertFalse(dec_neg.eligible)
        self.assertEqual(dec_neg.reason, "MISSING_OR_NONPOSITIVE_BASELINE_COST")

        current_str = {"project_code": "P9", "report_month": "2023-01", "original_cost": "INVALID"}
        by_month_str = {"2023-01": current_str, "2023-02": current_str, "2023-03": current_str, "2023-04": current_str}
        dec_str = classify_cost_target(current_str, by_month_str, [])
        self.assertFalse(dec_str.eligible)
        self.assertEqual(dec_str.reason, "MISSING_OR_NONPOSITIVE_BASELINE_COST")


class TestCanonicalDatasetReconciliation(unittest.TestCase):
    """Tests evaluating target population against actual canonical datasets."""

    @classmethod
    def setUpClass(cls):
        cls.contract = load_cost_contract(DEFAULT_CONTRACT_PATH)
        cls.df_monthly = pd.read_csv(CANONICAL_MONTHLY, low_memory=False)
        cls.df_completed = pd.read_csv(CANONICAL_COMPLETED, low_memory=False)
        cls.classified_df = build_cost_overrun_population(
            cls.df_monthly,
            horizon=cls.contract["target"]["horizon_months"],
            tolerance=cls.contract["target"]["tolerance_cr"],
        )
        cls.reconciliation = reconcile_population(cls.classified_df)

    def test_11_positive_negative_counts_reconcile(self):
        """11. Positive and negative counts match exact contract metrics."""
        expected = self.contract["expected_dataset_metrics"]
        self.assertEqual(self.reconciliation.eligible_positives, expected["positive_rows"]["TOTAL"])
        self.assertEqual(self.reconciliation.eligible_negatives, expected["negative_rows"]["TOTAL"])
        self.assertEqual(
            self.reconciliation.eligible_positives + self.reconciliation.eligible_negatives,
            expected["eligible_rows"]["TOTAL"],
        )

    def test_12_all_source_observations_receive_deterministic_disposition(self):
        """12. All 64,608 source observations receive a deterministic disposition."""
        self.assertTrue(self.reconciliation.reconciled)
        self.assertEqual(self.reconciliation.total_observations, 64608)
        self.assertEqual(
            self.reconciliation.total_observations,
            (
                self.reconciliation.eligible_positives
                + self.reconciliation.eligible_negatives
                + self.reconciliation.censored_segment_boundary
                + self.reconciliation.censored_panel_exit
                + self.reconciliation.ineligible_baseline_ambiguous
                + self.reconciliation.ineligible_future_ambiguous
            ),
        )

    def test_13_temporal_feasibility_walk_forward_rejection(self):
        """13. Temporal feasibility rejects future-known outcomes at prediction time."""
        # Windows at segment tails must be censored
        censored_tails = self.classified_df[
            self.classified_df["report_month"].isin(["2023-09", "2023-10", "2023-11", "2024-01", "2025-04", "2026-05"])
        ]
        self.assertTrue((~censored_tails["eligible"]).all())

        # Forward embargo rule verification
        embargo = self.contract["embargo"]
        self.assertEqual(embargo["horizon_months"], 3)
        self.assertIn("T + 3 < E", embargo["formula"])

    def test_14_target_source_fields_identified_as_prohibited(self):
        """14. Target-defining fields and event attributes are strictly prohibited."""
        prohibited = set(self.contract["columns"]["leakage_strictly_prohibited"])
        critical_targets = [
            "target_effective_cost_esc_3m",
            "cost_revision_type",
            "cost_diff",
            "target_event_month",
            "target_event_revised_cost",
            "baseline_cost",
            "baseline_cost_source",
            "eventually_completed",
            "completion_report_month",
        ]
        for field in critical_targets:
            self.assertIn(field, prohibited)

    def test_15_leakage_fields_cannot_enter_feature_population(self):
        """15. Leakage audit confirms zero prohibited fields in feature set."""
        features = self.contract["features"]["ordered_names"]
        audit = audit_leakage(self.contract, features)
        self.assertTrue(audit["is_leak_free"])
        self.assertEqual(len(audit["direct_leakage_fields"]), 0)

    def test_16_completed_project_logic_behaves_deterministically(self):
        """16. Completed-project audit runs deterministically and documents unviability."""
        audit = audit_completed_cost_overrun(self.df_completed, self.df_monthly)
        self.assertEqual(audit.total_completed, 876)
        self.assertEqual(audit.valid_baseline_cost, 851)
        self.assertEqual(audit.missing_baseline_cost, 25)
        self.assertEqual(audit.revised_cost_reported_completed, 170)
        self.assertEqual(audit.revised_cost_missing_completed, 706)
        self.assertEqual(audit.ongoing_projects_never_completed, 3862)
        self.assertEqual(audit.viability_status, "NOT_YET_VIABLE")

    def test_17_repeated_target_generation_produces_identical_outputs(self):
        """17. Repeated execution against canonical data produces identical outputs."""
        sample_subset = self.df_monthly.iloc[:500]
        run1 = build_cost_overrun_population(sample_subset)
        run2 = build_cost_overrun_population(sample_subset)
        pd.testing.assert_frame_equal(run1, run2)

    def test_18_generated_artifacts_reconcile_with_source_counts(self):
        """18. Generated audit artifacts exist and reconcile with source counts."""
        manifest_path = DEFAULT_OUTPUT_DIR / "manifest.json"
        self.assertTrue(manifest_path.is_file(), "manifest.json must exist")
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["reconciliation"]["total_observations"], 64608)
        self.assertEqual(manifest["reconciliation"]["eligible_positives"], 865)
        self.assertEqual(manifest["reconciliation"]["eligible_negatives"], 38828)

    def test_19_canonical_datasets_remain_byte_for_byte_unchanged(self):
        """19. Canonical datasets retain exact authoritative SHA-256 digests."""
        monthly_hash = sha256_file(CANONICAL_MONTHLY)
        completed_hash = sha256_file(CANONICAL_COMPLETED)
        self.assertEqual(monthly_hash, EXPECTED_MONTHLY_SHA256)
        self.assertEqual(completed_hash, EXPECTED_COMPLETED_SHA256)

    def test_20_target_recommendation_is_supported_by_evidence(self):
        """20. Viability recommendation is VIABLE_WITH_LIMITATIONS based on audit evidence."""
        rec = self.contract["viability_recommendation"]
        self.assertEqual(rec["status"], "VIABLE_WITH_LIMITATIONS")
        self.assertEqual(rec["primary_target"], "target_effective_cost_esc_3m")
        self.assertAlmostEqual(self.reconciliation.positive_prevalence, 0.0218, places=3)
        self.assertGreater(self.reconciliation.class_imbalance_ratio, 40.0)


if __name__ == "__main__":
    unittest.main()
