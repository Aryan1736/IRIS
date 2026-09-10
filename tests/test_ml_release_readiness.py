"""Comprehensive regression test suite for IRIS PR-15: Final ML QA & Release Readiness.

Covers all 46 required verification dimensions:
 1. release module loads
 2. release manifest loads
 3. release report structure
 4. release ID/version
 5. canonical monthly dataset hash verification
 6. completed dataset hash verification
 7. artifact hash verification
 8. Legacy CatBoost artifact loading
 9. Modern Logistic artifact loading
10. feature contract availability
11. regime metadata consistency
12. target consistency
13. horizon consistency
14. inference parity for Legacy
15. inference parity for Modern
16. registry verification
17. registry fail-closed behavior
18. platform contract verification
19. registry/platform compatibility
20. unified intelligence verification
21. separate domain probability preservation
22. no probability aggregation
23. Cost unavailable behavior
24. Implementation unavailable behavior
25. Implementation ineligible behavior
26. unknown regime rejection
27. unknown domain rejection
28. structural gap rejection
29. invalid feature rejection
30. leakage rejection
31. NaN rejection
32. Infinity rejection
33. missing artifact failure simulation
34. hash mismatch failure simulation
35. explanation non-causal metadata
36. explanation contribution-space metadata
37. explanation consistency
38. API model registry compatibility
39. API platform contract compatibility
40. API profile compatibility
41. path masking
42. no absolute path exposure
43. no artifact binary exposure
44. deterministic repeated verification
45. overall release PASS derives from checks
46. release fails if required check fails
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app as fastapi_backend_app
from src.serving.api import app as fastapi_serving_app
from src.ml.model_registry import (
    AVAILABILITY_AVAILABLE,
    AVAILABILITY_INELIGIBLE,
    AVAILABILITY_NOT_AVAILABLE,
    CANONICAL_COMPLETED_PATH,
    CANONICAL_COMPLETED_SHA256,
    CANONICAL_MONTHLY_PATH,
    CANONICAL_MONTHLY_SHA256,
    GOVERNANCE_LOCKED_PRODUCTION,
    GOVERNANCE_NOT_READY_FOR_PRODUCTION,
    GOVERNANCE_VIABLE_WITH_LIMITATIONS,
    SCHEDULE_LEGACY_ARTIFACT_PATH,
    SCHEDULE_LEGACY_ARTIFACT_SHA256,
    SCHEDULE_MODERN_ARTIFACT_PATH,
    SCHEDULE_MODERN_ARTIFACT_SHA256,
    ModelRegistry,
    ModelRegistryVerificationError,
)
from src.ml.platform_contract import (
    CONTRACT_ID,
    CONTRACT_VERSION,
    NON_CAUSAL_DISCLAIMER,
    PROHIBITED_PROBABILITY_FUSION_KEYS,
    MLPlatformContract,
)
from src.ml.predict_schedule import ScheduleExtensionPredictor
from src.ml.release_readiness import (
    DEFAULT_COMPATIBILITY_REPORT_RELPATH,
    DEFAULT_MANIFEST_RELPATH,
    DEFAULT_RELEASE_REPORT_RELPATH,
    DEFAULT_VERIFICATION_REPORT_RELPATH,
    RELEASE_ID,
    RELEASE_VERSION,
    REQUIRED_RELEASE_GATES,
    ReleaseReadiness,
    ReleaseReadinessError,
    ReleaseReadinessVerificationError,
    mask_path,
    sanitize_payload,
)
from src.ml.unified_risk_intelligence import (
    COST_DOMAIN,
    IMPLEMENTATION_DOMAIN,
    SCHEDULE_DOMAIN,
    UnifiedRiskIntelligence,
)
from src.ml.unified_risk_predictor import (
    SCHEDULE_DECISION_THRESHOLD,
    UnifiedRiskPredictor,
)


class TestMLReleaseReadiness(unittest.TestCase):
    """Authoritative test suite for ML release readiness gate."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.readiness = ReleaseReadiness.load(root=cls.root)
        cls.backend_client = TestClient(fastapi_backend_app)
        cls.serving_client = TestClient(fastapi_serving_app)

    # 1. release module loads
    def test_01_release_module_loads(self) -> None:
        self.assertIsNotNone(self.readiness)
        self.assertIsInstance(self.readiness, ReleaseReadiness)
        self.assertEqual(self.readiness.root, self.root)

    # 2. release manifest loads
    def test_02_release_manifest_loads(self) -> None:
        man_path = self.root / DEFAULT_MANIFEST_RELPATH
        self.assertTrue(man_path.is_file(), f"Manifest missing at {man_path}")
        data = json.loads(man_path.read_text(encoding="utf-8"))
        self.assertEqual(data.get("manifest_version"), "1.0.0")
        self.assertEqual(data.get("release_id"), RELEASE_ID)
        self.assertEqual(data.get("release_version"), RELEASE_VERSION)

    # 3. release report structure
    def test_03_release_report_structure(self) -> None:
        rep_path = self.root / DEFAULT_RELEASE_REPORT_RELPATH
        self.assertTrue(rep_path.is_file(), f"Release report missing at {rep_path}")
        data = json.loads(rep_path.read_text(encoding="utf-8"))
        self.assertIn("release_id", data)
        self.assertIn("release_version", data)
        self.assertIn("overall_status", data)
        self.assertIn("release_ready", data)
        self.assertIn("summary", data)
        self.assertIn("checks", data)
        self.assertEqual(data["overall_status"], "PASS")
        self.assertTrue(data["release_ready"])
        for gate in REQUIRED_RELEASE_GATES:
            self.assertIn(gate, data["checks"])
            self.assertEqual(data["checks"][gate]["status"], "PASS")

    # 4. release ID/version
    def test_04_release_id_and_version(self) -> None:
        self.assertEqual(RELEASE_ID, "iris_ml_release_v1")
        self.assertEqual(RELEASE_VERSION, "1.0.0")

    # 5. canonical monthly dataset hash verification
    def test_05_canonical_monthly_dataset_hash_verification(self) -> None:
        path = self.root / CANONICAL_MONTHLY_PATH
        self.assertTrue(path.is_file())
        actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        self.assertEqual(actual, CANONICAL_MONTHLY_SHA256)
        self.assertEqual(actual, "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF")

    # 6. completed dataset hash verification
    def test_06_completed_dataset_hash_verification(self) -> None:
        path = self.root / CANONICAL_COMPLETED_PATH
        self.assertTrue(path.is_file())
        actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        self.assertEqual(actual, CANONICAL_COMPLETED_SHA256)
        self.assertEqual(actual, "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910")

    # 7. artifact hash verification
    def test_07_artifact_hash_verification(self) -> None:
        res = self.readiness.verify_locked_artifact_integrity()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(
            res["artifacts"]["legacy_catboost"]["actual_sha256"],
            SCHEDULE_LEGACY_ARTIFACT_SHA256,
        )
        self.assertEqual(
            res["artifacts"]["modern_logistic"]["actual_sha256"],
            SCHEDULE_MODERN_ARTIFACT_SHA256,
        )

    # 8. Legacy CatBoost artifact loading
    def test_08_legacy_catboost_artifact_loading(self) -> None:
        res = self.readiness.verify_artifact_loading()
        self.assertEqual(res["status"], "PASS")
        legacy = res["models_loaded"]["schedule_legacy"]
        self.assertEqual(legacy["model_family"], "CatBoostClassifier")
        self.assertEqual(legacy["regime"], "LEGACY")
        self.assertEqual(legacy["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(legacy["production_availability"], AVAILABILITY_AVAILABLE)

    # 9. Modern Logistic artifact loading
    def test_09_modern_logistic_artifact_loading(self) -> None:
        res = self.readiness.verify_artifact_loading()
        self.assertEqual(res["status"], "PASS")
        modern = res["models_loaded"]["schedule_modern"]
        self.assertEqual(modern["model_family"], "LogisticRegression")
        self.assertEqual(modern["regime"], "MODERN")
        self.assertEqual(modern["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(modern["production_availability"], AVAILABILITY_AVAILABLE)

    # 10. feature contract availability
    def test_10_feature_contract_availability(self) -> None:
        contract = self.readiness._platform_contract.get_feature_contract("schedule_3m", regime="LEGACY")
        self.assertEqual(contract["feature_count"], 36)
        self.assertEqual(len(contract["ordered_names"]), 36)

        contract_mod = self.readiness._platform_contract.get_feature_contract("schedule_3m", regime="MODERN")
        self.assertEqual(contract_mod["feature_count"], 25)
        self.assertEqual(len(contract_mod["ordered_names"]), 25)

    # 11. regime metadata consistency
    def test_11_regime_metadata_consistency(self) -> None:
        pred_legacy = self.readiness._predictor.get_model("LEGACY")
        self.assertIsNotNone(pred_legacy)
        pred_modern = self.readiness._predictor.get_model("MODERN")
        self.assertIsNotNone(pred_modern)

    # 12. target consistency
    def test_12_target_consistency(self) -> None:
        dom = self.readiness._platform_contract.get_domain("schedule_3m")
        self.assertEqual(dom["target"], "target_effective_schedule_ext_3m")

    # 13. horizon consistency
    def test_13_horizon_consistency(self) -> None:
        dom = self.readiness._platform_contract.get_domain("schedule_3m")
        self.assertEqual(dom["horizon_months"], 3)

    # 14. inference parity for Legacy
    def test_14_inference_parity_for_legacy(self) -> None:
        res = self.readiness.verify_live_inference_parity()
        self.assertEqual(res["status"], "PASS")
        summary = res["parity_summary"]
        self.assertTrue(summary["legacy_parity_passed"])
        self.assertLessEqual(summary["legacy_max_prob_diff"], 1e-9)
        self.assertLessEqual(summary["legacy_max_raw_diff"], 1e-9)

    # 15. inference parity for Modern
    def test_15_inference_parity_for_modern(self) -> None:
        res = self.readiness.verify_live_inference_parity()
        self.assertEqual(res["status"], "PASS")
        summary = res["parity_summary"]
        self.assertTrue(summary["modern_parity_passed"])
        self.assertLessEqual(summary["modern_max_prob_diff"], 1e-12)
        self.assertLessEqual(summary["modern_max_raw_diff"], 1e-12)

    # 16. registry verification
    def test_16_registry_verification(self) -> None:
        res = self.readiness.verify_model_registry()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(len(res["errors"]), 0)

    # 17. registry fail-closed behavior
    def test_17_registry_fail_closed_behavior(self) -> None:
        bad_data = copy.deepcopy(self.readiness._registry.get_registry())
        bad_data["domains"]["schedule_3m"]["models"]["legacy"]["artifact"]["path"] = "non_existent.cbm"
        tampered = ModelRegistry(bad_data, root=self.root)
        with self.assertRaises(ModelRegistryVerificationError):
            tampered.verify(fail_closed=True)

    # 18. platform contract verification
    def test_18_platform_contract_verification(self) -> None:
        res = self.readiness.verify_platform_contract()
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["failed_checks_count"], 0)

    # 19. registry/platform compatibility
    def test_19_registry_platform_compatibility(self) -> None:
        compat_path = self.root / DEFAULT_COMPATIBILITY_REPORT_RELPATH
        self.assertTrue(compat_path.is_file())
        data = json.loads(compat_path.read_text(encoding="utf-8"))
        for check_name, passed in data["cross_layer_checks"].items():
            self.assertTrue(passed, f"Compatibility check failed: {check_name}")

    # 20. unified intelligence verification
    def test_20_unified_intelligence_verification(self) -> None:
        res = self.readiness.verify_unified_risk_intelligence()
        self.assertEqual(res["status"], "PASS")

    # 21. separate domain probability preservation
    def test_21_separate_domain_probability_preservation(self) -> None:
        fixture = self.readiness._get_reference_fixture(regime="LEGACY")
        prof = self.readiness._intelligence.predict_one(fixture)
        domains = prof["domains"]
        self.assertIn(SCHEDULE_DOMAIN, domains)
        self.assertIn(COST_DOMAIN, domains)
        self.assertIn(IMPLEMENTATION_DOMAIN, domains)
        self.assertIsInstance(domains[SCHEDULE_DOMAIN]["risk_score"], float)
        self.assertIsNone(domains[COST_DOMAIN]["risk_score"])
        self.assertIsNone(domains[IMPLEMENTATION_DOMAIN]["risk_score"])

    # 22. no probability aggregation
    def test_22_no_probability_aggregation(self) -> None:
        fixture = self.readiness._get_reference_fixture(regime="MODERN")
        prof = self.readiness._intelligence.predict_one(fixture)
        for key in PROHIBITED_PROBABILITY_FUSION_KEYS:
            self.assertNotIn(key, prof)
            self.assertNotIn(key, prof.get("profile", {}))

    # 23. Cost unavailable behavior
    def test_23_cost_unavailable_behavior(self) -> None:
        fixture = self.readiness._get_reference_fixture(regime="MODERN")
        prof = self.readiness._intelligence.predict_one(fixture)
        cost = prof["domains"][COST_DOMAIN]
        self.assertEqual(cost["status"], AVAILABILITY_NOT_AVAILABLE)
        self.assertEqual(cost["operational_status"], GOVERNANCE_NOT_READY_FOR_PRODUCTION)
        self.assertIsNone(cost["risk_score"])

    # 24. Implementation unavailable behavior
    def test_24_implementation_unavailable_behavior(self) -> None:
        fixture = self.readiness._get_reference_fixture(regime="MODERN")
        prof = self.readiness._intelligence.predict_one(fixture)
        impl = prof["domains"][IMPLEMENTATION_DOMAIN]
        self.assertEqual(impl["operational_status"], GOVERNANCE_VIABLE_WITH_LIMITATIONS)
        self.assertEqual(impl["status"], AVAILABILITY_NOT_AVAILABLE)
        self.assertIsNone(impl["risk_score"])

    # 25. Implementation ineligible behavior
    def test_25_implementation_ineligible_behavior(self) -> None:
        fixture = self.readiness._get_reference_fixture(regime="LEGACY")
        prof = self.readiness._intelligence.predict_one(fixture)
        impl = prof["domains"][IMPLEMENTATION_DOMAIN]
        self.assertEqual(impl["status"], AVAILABILITY_INELIGIBLE)
        self.assertIsNone(impl["risk_score"])

    # 26. unknown regime rejection
    def test_26_unknown_regime_rejection(self) -> None:
        fixture = self.readiness._get_reference_fixture(regime="MODERN")
        with self.assertRaises((ValueError, KeyError)):
            self.readiness._predictor.predict_one(fixture, regime="UNKNOWN_ERA")

    # 27. unknown domain rejection
    def test_27_unknown_domain_rejection(self) -> None:
        with self.assertRaises((KeyError, ValueError)):
            self.readiness._platform_contract.get_domain("quality_risk")

    # 28. structural gap rejection
    def test_28_structural_gap_rejection(self) -> None:
        gap_fixture = {"project_code": "P001", "report_month": "2023-12", "original_cost": 100}
        with self.assertRaises(ValueError):
            self.readiness._predictor.validate_row(gap_fixture, regime="LEGACY")

    # 29. invalid feature rejection
    def test_29_invalid_feature_rejection(self) -> None:
        fixture = dict(self.readiness._get_reference_fixture(regime="MODERN"))
        fixture["arbitrary_new_feature"] = 123
        with self.assertRaises(ValueError):
            self.readiness._predictor.validate_row(fixture, regime="MODERN")

    # 30. leakage rejection
    def test_30_leakage_rejection(self) -> None:
        fixture = dict(self.readiness._get_reference_fixture(regime="MODERN"))
        fixture["actual_completion_date"] = "2026-10"
        with self.assertRaises(ValueError):
            self.readiness._predictor.validate_row(fixture, regime="MODERN")

    # 31. NaN rejection
    def test_31_nan_rejection(self) -> None:
        unified = UnifiedRiskPredictor.load(self.root / "artifacts/ml/schedule_extension_3m")
        fixture = dict(self.readiness._get_reference_fixture(regime="MODERN"))
        fixture["original_cost"] = float("nan")
        with self.assertRaises(ValueError):
            unified.validate_request_structure(fixture)

    # 32. Infinity rejection
    def test_32_infinity_rejection(self) -> None:
        unified = UnifiedRiskPredictor.load(self.root / "artifacts/ml/schedule_extension_3m")
        fixture = dict(self.readiness._get_reference_fixture(regime="MODERN"))
        fixture["original_cost"] = float("inf")
        with self.assertRaises(ValueError):
            unified.validate_request_structure(fixture)

    # 33. missing artifact failure simulation
    def test_33_missing_artifact_failure_simulation(self) -> None:
        bad_data = copy.deepcopy(self.readiness._registry.get_registry())
        bad_data["domains"]["schedule_3m"]["models"]["legacy"]["artifact"]["path"] = "missing_artifact.cbm"
        tampered = ModelRegistry(bad_data, root=self.root)
        with self.assertRaises(ModelRegistryVerificationError):
            tampered.verify(fail_closed=True)

    # 34. hash mismatch failure simulation
    def test_34_hash_mismatch_failure_simulation(self) -> None:
        bad_data = copy.deepcopy(self.readiness._registry.get_registry())
        bad_data["domains"]["schedule_3m"]["models"]["legacy"]["artifact"]["sha256"] = "F" * 64
        tampered = ModelRegistry(bad_data, root=self.root)
        with self.assertRaises(ModelRegistryVerificationError):
            tampered.verify(fail_closed=True)

    # 35. explanation non-causal metadata
    def test_35_explanation_non_causal_metadata(self) -> None:
        for regime in ("LEGACY", "MODERN"):
            exp = self.readiness._platform_contract.get_explanation_contract("schedule_3m", regime=regime)
            self.assertTrue(exp["non_causal"])
            self.assertIn("non-causal", exp["disclaimer"].lower())

    # 36. explanation contribution-space metadata
    def test_36_explanation_contribution_space_metadata(self) -> None:
        for regime in ("LEGACY", "MODERN"):
            exp = self.readiness._platform_contract.get_explanation_contract("schedule_3m", regime=regime)
            self.assertEqual(exp["contribution_space"], "model_margin_or_logit")

    # 37. explanation consistency
    def test_37_explanation_consistency(self) -> None:
        res = self.readiness.verify_explanation_consistency()
        self.assertEqual(res["status"], "PASS")

    # 38. API model registry compatibility
    def test_38_api_model_registry_compatibility(self) -> None:
        resp = self.backend_client.get("/api/ml/model-registry")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("domains", data)
        self.assertIn("schedule_3m", data["domains"])
        self.assertIn("cost_overrun", data["domains"])
        self.assertIn("implementation_risk", data["domains"])

    # 39. API platform contract compatibility
    def test_39_api_platform_contract_compatibility(self) -> None:
        resp = self.backend_client.get("/api/ml/platform-contract")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["contract_id"], CONTRACT_ID)
        self.assertEqual(data["contract_version"], CONTRACT_VERSION)

    # 40. API profile compatibility
    def test_40_api_profile_compatibility(self) -> None:
        fixture = self.readiness._get_reference_fixture(regime="MODERN")
        resp1 = self.backend_client.post("/risk/profile", json=fixture)
        self.assertEqual(resp1.status_code, 200)
        resp2 = self.backend_client.post("/api/ml/unified-risk-profile", json=fixture)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp1.json(), resp2.json())

    # 41. path masking
    def test_41_path_masking(self) -> None:
        masked = mask_path("C:\\Users\\DELL\\Projects\\IRIS\\data\\processed\\test.csv", self.root)
        self.assertFalse(masked.startswith("C:"))
        self.assertNotIn("\\", masked)

    # 42. no absolute path exposure
    def test_42_no_absolute_path_exposure(self) -> None:
        resp = self.backend_client.get("/api/ml/model-registry")
        text = resp.text
        self.assertFalse(bool(re.search(r'[A-Za-z]:[\\/]', text)))
        self.assertNotIn("users/dell", text.lower())

    # 43. no artifact binary exposure
    def test_43_no_artifact_binary_exposure(self) -> None:
        resp = self.backend_client.get("/api/ml/model-registry")
        text = resp.text
        self.assertEqual(resp.headers.get("content-type"), "application/json")
        # Ensure raw model binaries/pickles are not embedded in the JSON payload
        self.assertNotIn("base64", text.lower())
        self.assertNotIn("\x80\x03", text)
        self.assertNotIn("\x80\x04", text)

    # 44. deterministic repeated verification
    def test_44_deterministic_repeated_verification(self) -> None:
        res1 = self.readiness.verify(fail_closed=False)
        res2 = self.readiness.verify(fail_closed=False)
        self.assertEqual(res1["overall_status"], res2["overall_status"])
        self.assertEqual(res1["passed_gates"], res2["passed_gates"])
        self.assertEqual(res1["failed_gates"], res2["failed_gates"])

    # 45. overall release PASS derives from checks
    def test_45_overall_release_pass_derives_from_checks(self) -> None:
        res = self.readiness.verify(fail_closed=False)
        self.assertEqual(res["overall_status"], "PASS")
        self.assertTrue(res["release_ready"])
        self.assertEqual(res["passed_gates"], 11)
        self.assertEqual(res["failed_gates"], [])

    # 46. release fails if required check fails
    def test_46_release_fails_if_required_check_fails(self) -> None:
        # Construct mock readiness where dataset integrity fails
        tampered_rr = ReleaseReadiness.load(root=self.root)
        # Override a check to simulate failure
        tampered_rr.verify_dataset_integrity = lambda: {
            "status": "FAIL",
            "errors": ["Simulated canonical dataset corruption"],
        }
        res = tampered_rr.verify(fail_closed=False)
        self.assertEqual(res["overall_status"], "FAIL")
        self.assertFalse(res["release_ready"])
        self.assertIn("dataset_integrity", res["failed_gates"])

        with self.assertRaises(ReleaseReadinessVerificationError):
            tampered_rr.verify(fail_closed=True)


if __name__ == "__main__":
    unittest.main()
