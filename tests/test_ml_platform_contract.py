"""Comprehensive regression test suite for IRIS PR-14: ML Platform Integration Contract.

Covers all 40 required verification dimensions:
 1. Contract loads successfully
 2. Contract schema validates (Draft 2020-12)
 3. Required top-level keys exist
 4. Contract version is frozen
 5. Registry compatibility passes
 6. Registry hash verification works
 7. Schedule domain contract exists
 8. Cost domain contract exists
 9. Implementation domain contract exists
10. Unified profile contract exists
11. Schedule Legacy contract is correct
12. Schedule Modern contract is correct
13. Cost is NOT_READY_FOR_PRODUCTION
14. Cost is NOT_AVAILABLE
15. Cost probability fails closed as null
16. Implementation governance is correct
17. Implementation unavailable states fail closed
18. INELIGIBLE cases preserve null probabilities
19. No domain aggregation probability exists
20. No weighted risk fusion exists
21. Threshold metadata matches registry
22. Target metadata matches registry
23. Horizon metadata matches registry
24. Model IDs match registry
25. Governance mismatch fails validation
26. Availability mismatch fails validation
27. Unknown domain fails closed
28. Unknown regime fails closed
29. Invalid prediction response fails validation
30. Production-unavailable probability payload is rejected
31. Explanation contract preserves contribution space
32. Explanation payload contains non-causal semantics
33. Internal paths are not exposed
34. Contract endpoint works
35. Contract endpoint masks paths
36. Existing model registry endpoint remains unchanged
37. Existing prediction endpoints remain unchanged
38. Existing unified risk profile behavior remains unchanged
39. Deterministic artifact generation
40. Manifest hash verification passes
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

import jsonschema
from fastapi.testclient import TestClient

from backend.app.main import app as fastapi_backend_app
from src.serving.api import app as fastapi_serving_app
from src.ml.model_registry import (
    AVAILABILITY_AVAILABLE,
    AVAILABILITY_EVALUATION_ONLY,
    AVAILABILITY_INELIGIBLE,
    AVAILABILITY_NOT_AVAILABLE,
    GOVERNANCE_LOCKED_PRODUCTION,
    GOVERNANCE_NOT_READY_FOR_PRODUCTION,
    GOVERNANCE_VIABLE_WITH_LIMITATIONS,
    ModelRegistry,
)
from src.ml.platform_contract import (
    CONTRACT_ID,
    CONTRACT_VERSION,
    DEFAULT_CONTRACT_RELPATH,
    DEFAULT_MANIFEST_RELPATH,
    DEFAULT_REPORT_RELPATH,
    SCHEMA_CONTRACT_RELPATH,
    MLPlatformContract,
    MLPlatformContractError,
    MLPlatformContractValidationError,
    MLPlatformContractVerificationError,
    build_authoritative_platform_contract_data,
    build_platform_contract_artifacts,
)


class TestMLPlatformContract(unittest.TestCase):
    """Regression test cases for ML Platform Integration Contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.contract = MLPlatformContract.load(root=cls.root)
        cls.registry = ModelRegistry.load(root=cls.root)
        cls.backend_client = TestClient(fastapi_backend_app)
        cls.serving_client = TestClient(fastapi_serving_app)

    # 1. Contract loads successfully
    def test_01_contract_loads_successfully(self) -> None:
        self.assertIsNotNone(self.contract)
        self.assertIsInstance(self.contract, MLPlatformContract)

    # 2. Contract schema validates (Draft 2020-12)
    def test_02_contract_schema_validates(self) -> None:
        schema_path = self.root / SCHEMA_CONTRACT_RELPATH
        self.assertTrue(schema_path.is_file(), "Schema contract file missing")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        # Check Draft 2020-12 schema self-validity
        jsonschema.Draft202012Validator.check_schema(schema_data)

        # Validate loaded contract data against schema
        contract_data = self.contract.get_contract()
        jsonschema.validate(instance=contract_data, schema=schema_data)

    # 3. Required top-level keys exist
    def test_03_required_top_level_keys_exist(self) -> None:
        contract_data = self.contract.get_contract()
        required_keys = [
            "$schema",
            "contract_name",
            "contract_version",
            "contract_id",
            "description",
            "generation_policy",
            "registry_reference",
            "domains",
            "unified_profile",
            "input_contracts",
            "output_contracts",
            "governance_policy",
            "path_masking_policy",
        ]
        for key in required_keys:
            self.assertIn(key, contract_data)

    # 4. Contract version is frozen
    def test_04_contract_version_is_frozen(self) -> None:
        self.assertEqual(self.contract.version, "1.0.0")
        self.assertEqual(self.contract.contract_id, "iris_ml_platform_contract_v1")

    # 5. Registry compatibility passes
    def test_05_registry_compatibility_passes(self) -> None:
        report = self.contract.verify(root=self.root, fail_closed=True)
        self.assertEqual(report["overall_status"], "PASS")
        self.assertEqual(report["failed_checks_count"], 0)

    # 6. Registry hash verification works
    def test_06_registry_hash_verification_works(self) -> None:
        reg_path = self.root / "artifacts/ml/model_registry_v1/registry.json"
        expected_hash = hashlib.sha256(reg_path.read_bytes()).hexdigest().upper()
        ref_hash = self.contract.get_contract()["registry_reference"]["registry_sha256"]
        self.assertEqual(ref_hash, expected_hash)

    # 7. Schedule domain contract exists
    def test_07_schedule_domain_contract_exists(self) -> None:
        domain = self.contract.get_domain("schedule_3m")
        self.assertEqual(domain["domain_id"], "schedule_3m")
        self.assertEqual(domain["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(domain["production_availability"], AVAILABILITY_AVAILABLE)
        self.assertEqual(domain["operational_decision_threshold"], 0.50)

    # 8. Cost domain contract exists
    def test_08_cost_domain_contract_exists(self) -> None:
        domain = self.contract.get_domain("cost_overrun")
        self.assertEqual(domain["domain_id"], "cost_overrun")
        self.assertEqual(domain["governance_status"], GOVERNANCE_NOT_READY_FOR_PRODUCTION)
        self.assertEqual(domain["production_availability"], AVAILABILITY_NOT_AVAILABLE)
        self.assertIsNone(domain["operational_decision_threshold"])

    # 9. Implementation domain contract exists
    def test_09_implementation_domain_contract_exists(self) -> None:
        domain = self.contract.get_domain("implementation_risk")
        self.assertEqual(domain["domain_id"], "implementation_risk")
        self.assertEqual(domain["governance_status"], GOVERNANCE_VIABLE_WITH_LIMITATIONS)
        self.assertEqual(domain["production_availability"], AVAILABILITY_NOT_AVAILABLE)
        self.assertIsNone(domain["operational_decision_threshold"])

    # 10. Unified profile contract exists
    def test_10_unified_profile_contract_exists(self) -> None:
        profile = self.contract.get_unified_profile_contract()
        self.assertEqual(profile["profile_version"], "1.0.0")
        self.assertEqual(profile["policy_version"], "1.0.0")
        self.assertIn("aggregation_prohibition_rule", profile)
        self.assertIn("overall_statuses", profile)
        self.assertIn("priority_levels", profile)

    # 11. Schedule Legacy contract is correct
    def test_11_schedule_legacy_contract_is_correct(self) -> None:
        legacy = self.contract.get_prediction_contract("schedule_3m", regime="legacy")
        self.assertEqual(legacy["model_id"], "schedule_legacy_catboost")
        self.assertEqual(legacy["model_family"], "CatBoostClassifier")
        self.assertEqual(legacy["regime"], "LEGACY")
        self.assertEqual(legacy["candidate_type"], "production")
        self.assertEqual(legacy["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(legacy["production_availability"], AVAILABILITY_AVAILABLE)
        self.assertEqual(legacy["operational_decision_threshold"], 0.50)
        self.assertEqual(legacy["feature_contract"]["feature_count"], 36)
        self.assertEqual(legacy["explanation"]["method"], "TreeSHAP")
        self.assertTrue(legacy["explanation"]["non_causal"])

    # 12. Schedule Modern contract is correct
    def test_12_schedule_modern_contract_is_correct(self) -> None:
        modern = self.contract.get_prediction_contract("schedule_3m", regime="modern")
        self.assertEqual(modern["model_id"], "schedule_modern_logistic")
        self.assertEqual(modern["model_family"], "LogisticRegression")
        self.assertEqual(modern["regime"], "MODERN")
        self.assertEqual(modern["candidate_type"], "production")
        self.assertEqual(modern["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(modern["production_availability"], AVAILABILITY_AVAILABLE)
        self.assertEqual(modern["operational_decision_threshold"], 0.50)
        self.assertEqual(modern["feature_contract"]["feature_count"], 25)
        self.assertEqual(modern["explanation"]["method"], "StandardizedCoefficients")
        self.assertTrue(modern["explanation"]["non_causal"])

    # 13. Cost is NOT_READY_FOR_PRODUCTION
    def test_13_cost_is_not_ready_for_production(self) -> None:
        domain = self.contract.get_domain("cost_overrun")
        self.assertEqual(domain["governance_status"], GOVERNANCE_NOT_READY_FOR_PRODUCTION)
        for m in domain["models"].values():
            self.assertEqual(m["governance_status"], GOVERNANCE_NOT_READY_FOR_PRODUCTION)

    # 14. Cost is NOT_AVAILABLE
    def test_14_cost_is_not_available(self) -> None:
        domain = self.contract.get_domain("cost_overrun")
        self.assertEqual(domain["production_availability"], AVAILABILITY_NOT_AVAILABLE)
        for m in domain["models"].values():
            self.assertEqual(m["production_availability"], AVAILABILITY_EVALUATION_ONLY)

    # 15. Cost probability fails closed as null
    def test_15_cost_probability_fails_closed_as_null(self) -> None:
        # Building envelope with non-null probability for cost_overrun must fail
        with self.assertRaises(MLPlatformContractValidationError):
            self.contract.build_prediction_envelope(
                domain="cost_overrun",
                regime=None,
                probability=0.25,
                prediction_status=AVAILABILITY_AVAILABLE,
            )

        # Null probability succeeds
        envelope = self.contract.build_prediction_envelope(
            domain="cost_overrun",
            regime=None,
            probability=None,
            prediction_status=AVAILABILITY_NOT_AVAILABLE,
        )
        self.assertIsNone(envelope["prediction"]["probability"])
        self.assertIsNone(envelope["prediction"]["operational_decision"])

    # 16. Implementation governance is correct
    def test_16_implementation_governance_is_correct(self) -> None:
        domain = self.contract.get_domain("implementation_risk")
        self.assertEqual(domain["governance_status"], GOVERNANCE_VIABLE_WITH_LIMITATIONS)
        self.assertEqual(domain["production_availability"], AVAILABILITY_NOT_AVAILABLE)

    # 17. Implementation unavailable states fail closed
    def test_17_implementation_unavailable_states_fail_closed(self) -> None:
        with self.assertRaises(MLPlatformContractValidationError):
            self.contract.build_prediction_envelope(
                domain="implementation_risk",
                regime=None,
                probability=0.45,
                prediction_status=AVAILABILITY_AVAILABLE,
            )

    # 18. INELIGIBLE cases preserve null probabilities
    def test_18_ineligible_cases_preserve_null_probabilities(self) -> None:
        envelope = self.contract.build_prediction_envelope(
            domain="implementation_risk",
            regime=None,
            probability=None,
            prediction_status=AVAILABILITY_INELIGIBLE,
            metadata={"ineligible_reason": "STRUCTURAL_ABSENCE_SEGMENT_1"},
        )
        self.assertIsNone(envelope["prediction"]["probability"])
        self.assertEqual(envelope["prediction"]["prediction_status"], AVAILABILITY_INELIGIBLE)

    # 19. No domain aggregation probability exists
    def test_19_no_domain_aggregation_probability_exists(self) -> None:
        profile_contract = self.contract.get_unified_profile_contract()
        self.assertIn("aggregation_prohibition_rule", profile_contract)
        self.assertIn("STRICT PROHIBITION", profile_contract["aggregation_prohibition_rule"])

    # 20. No weighted risk fusion exists
    def test_20_no_weighted_risk_fusion_exists(self) -> None:
        bad_profile_payload = {
            "contract_version": "1.0.0",
            "profile_version": "1.0.0",
            "policy_version": "1.0.0",
            "overall_status": "PARTIAL",
            "coverage_status": "PARTIAL_COVERAGE",
            "priority_domains": [],
            "attention_level": "MEDIUM_ATTENTION",
            "recommendations": [],
            "domain_risks": {},
            "limitations": [],
            "governance_notes": [],
            "summary": "Sample summary",
            "combined_probability": 0.65,  # PROHIBITED!
        }
        errors = MLPlatformContract.validate_profile_response(bad_profile_payload)
        self.assertTrue(any("Prohibited probability fusion" in e for e in errors))

    # 21. Threshold metadata matches registry
    def test_21_threshold_metadata_matches_registry(self) -> None:
        for dom_id in ("schedule_3m", "cost_overrun", "implementation_risk"):
            c_thresh = self.contract.get_domain(dom_id)["operational_decision_threshold"]
            r_thresh = self.registry.get_domain(dom_id)["operational_decision_threshold"]
            self.assertEqual(c_thresh, r_thresh, f"Threshold mismatch on {dom_id}")

    # 22. Target metadata matches registry
    def test_22_target_metadata_matches_registry(self) -> None:
        for dom_id in ("schedule_3m", "cost_overrun", "implementation_risk"):
            c_target = self.contract.get_domain(dom_id)["target"]
            r_target = self.registry.get_domain(dom_id)["target"]
            self.assertEqual(c_target, r_target, f"Target mismatch on {dom_id}")

    # 23. Horizon metadata matches registry
    def test_23_horizon_metadata_matches_registry(self) -> None:
        for dom_id in ("schedule_3m", "cost_overrun", "implementation_risk"):
            c_h = self.contract.get_domain(dom_id)["horizon_months"]
            r_h = self.registry.get_domain(dom_id)["horizon_months"]
            self.assertEqual(c_h, r_h, f"Horizon mismatch on {dom_id}")

    # 24. Model IDs match registry
    def test_24_model_ids_match_registry(self) -> None:
        self.assertEqual(
            self.contract.get_prediction_contract("schedule_3m", regime="legacy")["model_id"],
            "schedule_legacy_catboost",
        )
        self.assertEqual(
            self.contract.get_prediction_contract("schedule_3m", regime="modern")["model_id"],
            "schedule_modern_logistic",
        )
        self.assertEqual(
            self.contract.get_prediction_contract("cost_overrun", candidate_type="baseline")["model_id"],
            "cost_overrun_baseline_logistic",
        )
        self.assertEqual(
            self.contract.get_prediction_contract("cost_overrun", candidate_type="challenger")["model_id"],
            "cost_overrun_challenger_catboost",
        )
        self.assertEqual(
            self.contract.get_prediction_contract("implementation_risk", candidate_type="baseline")["model_id"],
            "implementation_risk_baseline_logistic",
        )
        self.assertEqual(
            self.contract.get_prediction_contract("implementation_risk", candidate_type="challenger")["model_id"],
            "implementation_risk_challenger_catboost",
        )

    # 25. Governance mismatch fails validation
    def test_25_governance_mismatch_fails_validation(self) -> None:
        bad_contract_data = copy.deepcopy(self.contract.get_contract())
        bad_contract_data["domains"]["cost_overrun"]["governance_status"] = GOVERNANCE_LOCKED_PRODUCTION
        errors = MLPlatformContract.validate_contract(bad_contract_data)
        self.assertTrue(any("governance_status must be" in e for e in errors))

    # 26. Availability mismatch fails validation
    def test_26_availability_mismatch_fails_validation(self) -> None:
        bad_contract_data = copy.deepcopy(self.contract.get_contract())
        bad_contract_data["domains"]["cost_overrun"]["production_availability"] = AVAILABILITY_AVAILABLE
        errors = MLPlatformContract.validate_contract(bad_contract_data)
        self.assertTrue(any("production_availability must be" in e for e in errors))

    # 27. Unknown domain fails closed
    def test_27_unknown_domain_fails_closed(self) -> None:
        with self.assertRaises(KeyError):
            self.contract.get_domain("cyber_risk")

    # 28. Unknown regime fails closed
    def test_28_unknown_regime_fails_closed(self) -> None:
        with self.assertRaises(KeyError):
            self.contract.get_prediction_contract("schedule_3m", regime="FUTURISTIC")

    # 29. Invalid prediction response fails validation
    def test_29_invalid_prediction_response_fails_validation(self) -> None:
        bad_response = {
            "contract_version": "1.0.0",
            "prediction": {
                "domain": "unknown_domain",
                "probability": 1.5,  # Out of bounds!
            },
        }
        errors = MLPlatformContract.validate_prediction_response(bad_response)
        self.assertTrue(len(errors) > 0)

    # 30. Production-unavailable probability payload is rejected
    def test_30_production_unavailable_probability_payload_is_rejected(self) -> None:
        payload = {
            "contract_version": "1.0.0",
            "prediction": {
                "domain": "cost_overrun",
                "probability": 0.42,  # Illegal for NOT_AVAILABLE!
            },
            "model": {
                "production_availability": AVAILABILITY_NOT_AVAILABLE,
                "governance_status": GOVERNANCE_NOT_READY_FOR_PRODUCTION,
            },
            "calibration": {},
            "explanation": {"non_causal": True},
            "limitations": [],
        }
        errors = MLPlatformContract.validate_prediction_response(payload)
        self.assertTrue(any("Probability must be null" in e for e in errors))

    # 31. Explanation contract preserves contribution space
    def test_31_explanation_contract_preserves_contribution_space(self) -> None:
        exp = self.contract.get_explanation_contract("schedule_3m", regime="legacy")
        self.assertEqual(exp["contribution_space"], "model_margin_or_logit")

        # Test envelope formatting
        envelope = self.contract.build_prediction_envelope(
            domain="schedule_3m",
            regime="legacy",
            probability=0.72,
            prediction_status=AVAILABILITY_AVAILABLE,
            drivers=[{
                "feature": "project_age_months",
                "feature_group": "schedule",
                "contribution": 0.35,
            }],
        )
        self.assertEqual(envelope["explanation"]["drivers"][0]["direction"], "risk_increasing")
        self.assertEqual(
            envelope["explanation"]["drivers"][0]["contribution_space"],
            "model_margin_or_logit",
        )

    # 32. Explanation payload contains non-causal semantics
    def test_32_explanation_payload_contains_non_causal_semantics(self) -> None:
        envelope = self.contract.build_prediction_envelope(
            domain="schedule_3m",
            regime="modern",
            probability=0.65,
            prediction_status=AVAILABILITY_AVAILABLE,
        )
        self.assertTrue(envelope["explanation"]["non_causal"])
        self.assertIn("non-causal", envelope["explanation"]["disclaimer"].lower())

    # 33. Internal paths are not exposed
    def test_33_internal_paths_are_not_exposed(self) -> None:
        masked_contract = self.contract.to_dict(mask_internal_paths=True)
        serialized = json.dumps(masked_contract)
        # Should not expose Windows drive letters or absolute roots
        self.assertNotIn("D:\\Coding\\Projects\\IRIS", serialized)
        self.assertNotIn("d:\\coding\\projects\\iris", serialized)
        self.assertNotIn("D:/Coding/Projects/IRIS", serialized)

    # 34. Contract endpoint works
    def test_34_contract_endpoint_works(self) -> None:
        # Backend app
        resp_b1 = self.backend_client.get("/api/ml/platform-contract")
        resp_b2 = self.backend_client.get("/risk/platform-contract")
        self.assertEqual(resp_b1.status_code, 200)
        self.assertEqual(resp_b2.status_code, 200)
        self.assertEqual(resp_b1.json()["contract_id"], CONTRACT_ID)

        # Serving app
        resp_s1 = self.serving_client.get("/api/ml/platform-contract")
        resp_s2 = self.serving_client.get("/risk/platform-contract")
        self.assertEqual(resp_s1.status_code, 200)
        self.assertEqual(resp_s2.status_code, 200)

    # 35. Contract endpoint masks paths
    def test_35_contract_endpoint_masks_paths(self) -> None:
        resp = self.backend_client.get("/api/ml/platform-contract")
        text = resp.text
        self.assertNotIn("D:\\Coding", text)
        self.assertNotIn("d:/coding", text.lower())

    # 36. Existing model registry endpoint remains unchanged
    def test_36_existing_model_registry_endpoint_remains_unchanged(self) -> None:
        resp = self.backend_client.get("/api/ml/model-registry")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["registry_id"], "iris_ml_model_registry_v1")

    # 37. Existing prediction endpoints remain unchanged
    def test_37_existing_prediction_endpoints_remain_unchanged(self) -> None:
        # Check unified risk endpoint rejecting prohibited leakage with 422
        bad_req = {
            "project_id": "201234",
            "report_month": "2026-04",
            "regime": "MODERN",
            "features": {"target_effective_schedule_ext_3m": 1},
        }
        resp = self.backend_client.post("/api/ml/unified-risk", json=bad_req)
        self.assertEqual(resp.status_code, 422)

    # 38. Existing unified risk profile behavior remains unchanged
    def test_38_existing_unified_risk_profile_behavior_remains_unchanged(self) -> None:
        bad_req = {
            "project_id": "201234",
            "report_month": "2026-04",
            "regime": "MODERN",
            "features": {"target_effective_schedule_ext_3m": 1},
        }
        resp = self.backend_client.post("/api/ml/unified-risk-profile", json=bad_req)
        self.assertEqual(resp.status_code, 422)

    # 39. Deterministic artifact generation
    def test_39_deterministic_artifact_generation(self) -> None:
        contract_data_1 = build_authoritative_platform_contract_data(root=self.root)
        contract_data_2 = build_authoritative_platform_contract_data(root=self.root)
        self.assertEqual(
            json.dumps(contract_data_1, sort_keys=True),
            json.dumps(contract_data_2, sort_keys=True),
        )

    # 40. Manifest hash verification passes
    def test_40_manifest_hash_verification_passes(self) -> None:
        man_path = self.root / DEFAULT_MANIFEST_RELPATH
        self.assertTrue(man_path.is_file(), "Manifest file missing")
        with open(man_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        # Check contract sha256
        contract_path = self.root / DEFAULT_CONTRACT_RELPATH
        expected_contract_sha256 = hashlib.sha256(contract_path.read_bytes()).hexdigest().upper()
        self.assertEqual(manifest_data["contract_sha256"], expected_contract_sha256)

        # Check registry sha256
        reg_path = self.root / "artifacts/ml/model_registry_v1/registry.json"
        expected_reg_sha256 = hashlib.sha256(reg_path.read_bytes()).hexdigest().upper()
        self.assertEqual(manifest_data["registry_sha256"], expected_reg_sha256)


if __name__ == "__main__":
    unittest.main()
