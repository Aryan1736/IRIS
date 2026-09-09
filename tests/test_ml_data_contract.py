"""Tests for IRIS ML data contract and validation pipeline.

Verifies strict enforcement of canonical input integrity, feature set and ordering,
leakage prohibitions, target semantics, continuous segment definitions, and embargo rules.
"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ml.data_contract import (
    CanonicalHashMismatchError,
    CanonicalRowCountMismatchError,
    ContractValidationError,
    EmbargoViolationError,
    FeatureContractError,
    LeakageViolationError,
    SegmentViolationError,
    TargetContractError,
    check_embargo,
    default_contract_path,
    load_contract,
    validate_built_dataset,
    validate_canonical_inputs,
    validate_continuous_segments,
    validate_contract_structure,
    validate_embargo_rule,
    validate_features,
    validate_leakage_exclusion,
    validate_target_spec,
)
from src.ml.dataset_builder import FEATURE_COLUMNS, METADATA_COLUMNS, SEGMENTS


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "schemas" / "schedule_extension_3m_v1.contract.json"
DATASET_DIR = ROOT / "data" / "ml" / "schedule_extension_3m"


class MLDataContractValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_contract(CONTRACT_PATH)

    def test_01_contract_version_and_metadata_readable(self) -> None:
        """Requirement: Contract version is readable and valid."""
        self.assertEqual(self.contract["contract_version"], "1.0.0")
        self.assertEqual(self.contract["dataset_name"], "schedule_extension_3m_v1")
        self.assertIn("target", self.contract)
        self.assertIn("features", self.contract)
        self.assertIn("embargo", self.contract)

    def test_02_valid_canonical_dataset_passes_contract_validation(self) -> None:
        """Requirement: Valid canonical dataset passes contract validation."""
        results = validate_canonical_inputs(ROOT, self.contract)
        self.assertEqual(len(results), 2)
        self.assertEqual(results["projects_monthly.csv"]["rows"], 64608)
        self.assertEqual(
            results["projects_monthly.csv"]["sha256"],
            "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF",
        )
        self.assertEqual(results["projects_completed.csv"]["rows"], 876)
        self.assertEqual(
            results["projects_completed.csv"]["sha256"],
            "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910",
        )

    def test_03_wrong_hash_fails(self) -> None:
        """Requirement: Wrong canonical hash fails loudly."""
        corrupted_contract = copy.deepcopy(self.contract)
        corrupted_contract["canonical_inputs"]["projects_monthly.csv"]["sha256"] = (
            "0000000000000000000000000000000000000000000000000000000000000000"
        )
        with self.assertRaises(CanonicalHashMismatchError) as ctx:
            validate_canonical_inputs(ROOT, corrupted_contract)
        self.assertIn("Canonical hash mismatch", str(ctx.exception))

    def test_04_wrong_row_count_fails(self) -> None:
        """Requirement: Wrong canonical row count fails loudly."""
        corrupted_contract = copy.deepcopy(self.contract)
        corrupted_contract["canonical_inputs"]["projects_monthly.csv"]["rows"] = 99999
        with self.assertRaises(CanonicalRowCountMismatchError) as ctx:
            validate_canonical_inputs(ROOT, corrupted_contract)
        self.assertIn("Canonical row count mismatch", str(ctx.exception))

    def test_05_missing_required_feature_fails(self) -> None:
        """Requirement: Missing required feature fails."""
        features_with_omission = [f for f in FEATURE_COLUMNS if f != "physical_progress_t"]
        with self.assertRaises(FeatureContractError) as ctx:
            validate_features(features_with_omission, self.contract)
        self.assertIn("Missing required feature", str(ctx.exception))
        self.assertIn("physical_progress_t", str(ctx.exception))

    def test_06_extra_feature_not_in_contract_fails(self) -> None:
        """Requirement: Extra feature not in contract fails where strictness is required."""
        # Test candidate drift features that are explicitly excluded
        drift_features = ["month_of_fiscal_year", "is_fiscal_yearend", "report_month_index"]
        for drift_feat in drift_features:
            features_with_extra = list(FEATURE_COLUMNS) + [drift_feat]
            with self.assertRaises(FeatureContractError) as ctx:
                validate_features(features_with_extra, self.contract)
            self.assertIn("Unexpected extra feature", str(ctx.exception))
            self.assertIn(drift_feat, str(ctx.exception))

    def test_07_wrong_feature_ordering_fails(self) -> None:
        """Requirement: Wrong feature ordering fails."""
        reordered_features = list(FEATURE_COLUMNS)
        # Swap first two features
        reordered_features[0], reordered_features[1] = reordered_features[1], reordered_features[0]
        with self.assertRaises(FeatureContractError) as ctx:
            validate_features(reordered_features, self.contract, strict_order=True)
        self.assertIn("Feature ordering mismatch", str(ctx.exception))

    def test_08_leakage_field_inside_feature_list_fails(self) -> None:
        """Requirement: Leakage field inside feature list fails."""
        prohibited_samples = [
            "eventually_completed",
            "completion_report_month",
            "target_event_month",
            "target_event_revised_completion_date",
            "project_code",
            "project_name",
            "target_effective_schedule_ext_3m",
            "actual_completion_date",
        ]
        for prohibited in prohibited_samples:
            features_with_leakage = list(FEATURE_COLUMNS) + [prohibited]
            with self.assertRaises(LeakageViolationError) as ctx:
                validate_leakage_exclusion(features_with_leakage, self.contract)
            self.assertIn("Prohibited leakage columns detected", str(ctx.exception))
            self.assertIn(prohibited, str(ctx.exception))

    def test_09_wrong_target_name_fails(self) -> None:
        """Requirement: Wrong target name fails."""
        with self.assertRaises(TargetContractError) as ctx:
            validate_target_spec("target_cost_overrun_3m", 3, self.contract)
        self.assertIn("Target name mismatch", str(ctx.exception))

    def test_10_wrong_horizon_fails(self) -> None:
        """Requirement: Wrong horizon fails."""
        with self.assertRaises(TargetContractError) as ctx:
            validate_target_spec("target_effective_schedule_ext_3m", 6, self.contract)
        self.assertIn("Target horizon mismatch", str(ctx.exception))

    def test_11_wrong_embargo_configuration_fails(self) -> None:
        """Requirement: Wrong embargo configuration fails (strict T + 3 < E)."""
        # T="2025-01", horizon=3 -> window ends at 2025-04
        # If E="2025-04", T + 3 == E (NOT strictly < E) -> must fail embargo
        self.assertFalse(validate_embargo_rule("2025-01", "2025-04", horizon=3))
        with self.assertRaises(EmbargoViolationError):
            check_embargo("2025-01", "2025-04", horizon=3)

        # If E="2025-03", T + 3 > E -> must fail embargo
        self.assertFalse(validate_embargo_rule("2025-01", "2025-03", horizon=3))
        with self.assertRaises(EmbargoViolationError):
            check_embargo("2025-01", "2025-03", horizon=3)

        # If E="2025-05", T + 3 < E -> strictly safe
        self.assertTrue(validate_embargo_rule("2025-01", "2025-05", horizon=3))
        check_embargo("2025-01", "2025-05", horizon=3)  # Does not raise

    def test_12_segment_mutation_fails(self) -> None:
        """Requirement: Segment mutation fails."""
        # Bridge 2023-12 gap by modifying segment 1 end
        mutated_segments = list(SEGMENTS)
        mutated_segments[0] = ("SEGMENT_1", "LEGACY", "2023-01", "2023-12")
        with self.assertRaises(SegmentViolationError) as ctx:
            validate_continuous_segments(mutated_segments, self.contract)
        self.assertIn("Segment mismatch", str(ctx.exception))

        # Bridge June-July 2025 redesign boundary by merging segments 3 and 4
        fewer_segments = mutated_segments[:3]
        with self.assertRaises(SegmentViolationError) as ctx:
            validate_continuous_segments(fewer_segments, self.contract)
        self.assertIn("Segment count mismatch", str(ctx.exception))

    def test_13_feature_families_cover_all_36_features(self) -> None:
        """Verify that 9 feature families in the contract partition the exact 36 features."""
        families = self.contract["features"]["families"]
        self.assertEqual(len(families), 9)

        all_family_features: list[str] = []
        for family_name, feat_list in families.items():
            all_family_features.extend(feat_list)

        self.assertEqual(len(all_family_features), 36)
        self.assertEqual(set(all_family_features), set(FEATURE_COLUMNS))
        self.assertEqual(len(set(all_family_features)), 36)

    def test_14_existing_schedule_target_builder_compatible_with_contract(self) -> None:
        """Requirement: Existing schedule target builder constants match contract."""
        validate_features(FEATURE_COLUMNS, self.contract, strict_order=True)
        validate_continuous_segments(SEGMENTS, self.contract)
        validate_target_spec("target_effective_schedule_ext_3m", 3, self.contract)
        validate_leakage_exclusion(FEATURE_COLUMNS, self.contract)

    def test_15_built_dataset_conforms_to_contract(self) -> None:
        """Verify that existing generated dataset on disk conforms to the contract."""
        if DATASET_DIR.is_dir():
            audit_result = validate_built_dataset(DATASET_DIR, self.contract)
            self.assertEqual(audit_result["status"], "PASS")
            self.assertEqual(audit_result["legacy"]["rows"], 25406)
            self.assertEqual(audit_result["legacy"]["positive_rows"], 2634)
            self.assertEqual(audit_result["modern"]["rows"], 11899)
            self.assertEqual(audit_result["modern"]["positive_rows"], 4327)


if __name__ == "__main__":
    unittest.main()
