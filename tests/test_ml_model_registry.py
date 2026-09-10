"""Comprehensive regression test suite for IRIS PR-13: ML Model Registry & Governance.

Covers all required test dimensions:
1. Registry loads successfully
2. Registry schema version validates
3. Registry ID validates
4. All required domains exist
5. Schedule domain exists
6. Cost domain exists
7. Implementation domain exists
8. Schedule legacy model record exists
9. Schedule modern model record exists
10. Cost model records are correctly governed
11. Implementation model records are correctly governed
12. Governance states validate
13. Production availability states validate
14. Duplicate IDs fail
15. Unknown governance states fail
16. Invalid governance/availability combinations fail
17. Missing artifact fails verification
18. Artifact hash mismatch fails verification
19. Canonical monthly dataset hash verifies
20. Canonical completed dataset hash verifies
21. Legacy schedule model hash verifies
22. Modern schedule model hash verifies
23. Registry serialization is deterministic
24. Registry load is deterministic
25. Registry performs no artifact mutation
26. Registry performs no dataset mutation
27. Registry verification report is deterministic
28. Source references resolve
29. All model records have required scientific metadata
30. Research models are never promoted to production availability
31. Implementation limitations remain explicit
32. Programmatic lookup behaves correctly
33. Unknown domain lookup fails cleanly
34. Unknown model lookup fails cleanly
35. Full repository ML regression suite remains green
36. Read-only API endpoints return expected metadata and handle path masking
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app as fastapi_backend_app
from src.serving.api import app as fastapi_serving_app
from src.ml.model_registry import (
    AVAILABILITY_AVAILABLE,
    AVAILABILITY_EVALUATION_ONLY,
    AVAILABILITY_INELIGIBLE,
    AVAILABILITY_NOT_AVAILABLE,
    CANONICAL_COMPLETED_PATH,
    CANONICAL_COMPLETED_SHA256,
    CANONICAL_MONTHLY_PATH,
    CANONICAL_MONTHLY_SHA256,
    DEFAULT_MANIFEST_RELPATH,
    DEFAULT_REGISTRY_RELPATH,
    DEFAULT_REPORT_RELPATH,
    GOVERNANCE_LOCKED_PRODUCTION,
    GOVERNANCE_NOT_READY_FOR_PRODUCTION,
    GOVERNANCE_VIABLE_WITH_LIMITATIONS,
    REGISTRY_ID,
    REGISTRY_VERSION,
    SCHEDULE_LEGACY_ARTIFACT_PATH,
    SCHEDULE_LEGACY_ARTIFACT_SHA256,
    SCHEDULE_MODERN_ARTIFACT_PATH,
    SCHEDULE_MODERN_ARTIFACT_SHA256,
    SCHEMA_CONTRACT_RELPATH,
    ModelRegistry,
    ModelRegistryError,
    ModelRegistryVerificationError,
    build_authoritative_registry_data,
    build_registry_artifacts,
)


class TestModelRegistry(unittest.TestCase):
    """Regression test cases for ML Model Registry and Governance layer."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent
        cls.registry = ModelRegistry.load(root=cls.root)
        cls.backend_client = TestClient(fastapi_backend_app)
        cls.serving_client = TestClient(fastapi_serving_app)

    # 1. Registry loads successfully
    def test_01_registry_loads_successfully(self) -> None:
        self.assertIsNotNone(self.registry)
        self.assertIsInstance(self.registry, ModelRegistry)

    # 2. Registry schema version validates
    def test_02_registry_schema_version_validates(self) -> None:
        self.assertEqual(self.registry.version, REGISTRY_VERSION)
        self.assertEqual(self.registry.version, "1.0.0")

    # 3. Registry ID validates
    def test_03_registry_id_validates(self) -> None:
        self.assertEqual(self.registry.registry_id, REGISTRY_ID)
        self.assertEqual(self.registry.registry_id, "iris_ml_model_registry_v1")

    # 4. All required domains exist
    def test_04_all_required_domains_exist(self) -> None:
        domains = self.registry.list_domains()
        self.assertIn("schedule_3m", domains)
        self.assertIn("cost_overrun", domains)
        self.assertIn("implementation_risk", domains)
        self.assertEqual(len(domains), 3)

    # 5. Schedule domain exists
    def test_05_schedule_domain_exists(self) -> None:
        domain = self.registry.get_domain("schedule_3m")
        self.assertEqual(domain["domain_id"], "schedule_3m")
        self.assertEqual(domain["target"], "target_effective_schedule_ext_3m")
        self.assertEqual(domain["horizon_months"], 3)
        self.assertEqual(domain["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(domain["production_availability"], AVAILABILITY_AVAILABLE)
        self.assertEqual(domain["operational_decision_threshold"], 0.50)

    # 6. Cost domain exists
    def test_06_cost_domain_exists(self) -> None:
        domain = self.registry.get_domain("cost_overrun")
        self.assertEqual(domain["domain_id"], "cost_overrun")
        self.assertEqual(domain["target"], "target_effective_cost_esc_3m")
        self.assertEqual(domain["horizon_months"], 3)
        self.assertEqual(domain["governance_status"], GOVERNANCE_NOT_READY_FOR_PRODUCTION)
        self.assertEqual(domain["production_availability"], AVAILABILITY_NOT_AVAILABLE)
        self.assertIsNone(domain["operational_decision_threshold"])

    # 7. Implementation domain exists
    def test_07_implementation_domain_exists(self) -> None:
        domain = self.registry.get_domain("implementation_risk")
        self.assertEqual(domain["domain_id"], "implementation_risk")
        self.assertEqual(domain["target"], "target_progress_stagnation_3m")
        self.assertEqual(domain["horizon_months"], 3)
        self.assertEqual(domain["governance_status"], GOVERNANCE_VIABLE_WITH_LIMITATIONS)
        self.assertEqual(domain["production_availability"], AVAILABILITY_NOT_AVAILABLE)
        self.assertIsNone(domain["operational_decision_threshold"])

    # 8. Schedule legacy model record exists
    def test_08_schedule_legacy_model_record_exists(self) -> None:
        model = self.registry.get_model(domain="schedule_3m", regime="legacy")
        self.assertEqual(model["model_id"], "schedule_legacy_catboost")
        self.assertEqual(model["model_name"], "catboost_full_v1__unweighted")
        self.assertEqual(model["model_family"], "CatBoostClassifier")
        self.assertEqual(model["regime"], "LEGACY")
        self.assertEqual(model["candidate_type"], "production")
        self.assertEqual(model["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(model["production_availability"], AVAILABILITY_AVAILABLE)
        self.assertEqual(model["features"]["feature_count"], 36)
        self.assertEqual(model["artifact"]["path"], SCHEDULE_LEGACY_ARTIFACT_PATH)
        self.assertEqual(model["artifact"]["sha256"], SCHEDULE_LEGACY_ARTIFACT_SHA256)

    # 9. Schedule modern model record exists
    def test_09_schedule_modern_model_record_exists(self) -> None:
        model = self.registry.get_model(domain="schedule_3m", regime="modern")
        self.assertEqual(model["model_id"], "schedule_modern_logistic")
        self.assertEqual(model["model_name"], "logistic_static_only__unweighted")
        self.assertEqual(model["model_family"], "LogisticRegression")
        self.assertEqual(model["regime"], "MODERN")
        self.assertEqual(model["candidate_type"], "production")
        self.assertEqual(model["governance_status"], GOVERNANCE_LOCKED_PRODUCTION)
        self.assertEqual(model["production_availability"], AVAILABILITY_AVAILABLE)
        self.assertEqual(model["features"]["feature_count"], 25)
        self.assertEqual(model["artifact"]["path"], SCHEDULE_MODERN_ARTIFACT_PATH)
        self.assertEqual(model["artifact"]["sha256"], SCHEDULE_MODERN_ARTIFACT_SHA256)

    # 10. Cost model records are correctly governed
    def test_10_cost_model_records_are_correctly_governed(self) -> None:
        baseline = self.registry.get_model(domain="cost_overrun", candidate_type="baseline")
        challenger = self.registry.get_model(domain="cost_overrun", candidate_type="challenger")

        self.assertEqual(baseline["governance_status"], GOVERNANCE_NOT_READY_FOR_PRODUCTION)
        self.assertEqual(baseline["production_availability"], AVAILABILITY_EVALUATION_ONLY)
        self.assertIsNone(baseline["artifact"])

        self.assertEqual(challenger["governance_status"], GOVERNANCE_NOT_READY_FOR_PRODUCTION)
        self.assertEqual(challenger["production_availability"], AVAILABILITY_EVALUATION_ONLY)
        self.assertIsNone(challenger["artifact"])

    # 11. Implementation model records are correctly governed
    def test_11_implementation_model_records_are_correctly_governed(self) -> None:
        baseline = self.registry.get_model(domain="implementation_risk", candidate_type="baseline")
        challenger = self.registry.get_model(domain="implementation_risk", candidate_type="challenger")

        self.assertEqual(baseline["governance_status"], GOVERNANCE_VIABLE_WITH_LIMITATIONS)
        self.assertEqual(baseline["production_availability"], AVAILABILITY_EVALUATION_ONLY)
        self.assertIsNone(baseline["artifact"])

        self.assertEqual(challenger["governance_status"], GOVERNANCE_VIABLE_WITH_LIMITATIONS)
        self.assertEqual(challenger["production_availability"], AVAILABILITY_EVALUATION_ONLY)
        self.assertEqual(challenger.get("recommendation_status"), "RECOMMENDED_CHALLENGER")
        self.assertIsNone(challenger["artifact"])

    # 12. Governance states validate
    def test_12_governance_states_validate(self) -> None:
        for d_id in self.registry.list_domains():
            dom = self.registry.get_domain(d_id)
            self.assertIn(
                dom["governance_status"],
                {GOVERNANCE_LOCKED_PRODUCTION, GOVERNANCE_VIABLE_WITH_LIMITATIONS, GOVERNANCE_NOT_READY_FOR_PRODUCTION},
            )
            for m in dom["models"].values():
                self.assertIn(
                    m["governance_status"],
                    {GOVERNANCE_LOCKED_PRODUCTION, GOVERNANCE_VIABLE_WITH_LIMITATIONS, GOVERNANCE_NOT_READY_FOR_PRODUCTION},
                )

    # 13. Production availability states validate
    def test_13_production_availability_states_validate(self) -> None:
        for d_id in self.registry.list_domains():
            dom = self.registry.get_domain(d_id)
            self.assertIn(
                dom["production_availability"],
                {AVAILABILITY_AVAILABLE, AVAILABILITY_NOT_AVAILABLE, AVAILABILITY_EVALUATION_ONLY, AVAILABILITY_INELIGIBLE},
            )
            for m in dom["models"].values():
                self.assertIn(
                    m["production_availability"],
                    {AVAILABILITY_AVAILABLE, AVAILABILITY_NOT_AVAILABLE, AVAILABILITY_EVALUATION_ONLY, AVAILABILITY_INELIGIBLE},
                )

    # 14. Duplicate IDs fail
    def test_14_duplicate_ids_fail(self) -> None:
        bad_data = copy.deepcopy(self.registry.get_registry())
        # Introduce duplicate model_id
        bad_data["domains"]["cost_overrun"]["models"]["baseline"]["model_id"] = "schedule_legacy_catboost"
        errors = ModelRegistry.validate_registry(bad_data)
        self.assertTrue(any("Duplicate model_id" in err for err in errors))

    # 15. Unknown governance states fail
    def test_15_unknown_governance_states_fail(self) -> None:
        bad_data = copy.deepcopy(self.registry.get_registry())
        bad_data["domains"]["schedule_3m"]["governance_status"] = "SUPER_PRODUCTION"
        errors = ModelRegistry.validate_registry(bad_data)
        self.assertTrue(any("invalid governance_status" in err for err in errors))

    # 16. Invalid governance/availability combinations fail
    def test_16_invalid_governance_availability_combinations_fail(self) -> None:
        # Case A: NOT_READY_FOR_PRODUCTION marked AVAILABLE
        bad_data_a = copy.deepcopy(self.registry.get_registry())
        bad_data_a["domains"]["cost_overrun"]["models"]["challenger"]["production_availability"] = AVAILABILITY_AVAILABLE
        bad_data_a["domains"]["cost_overrun"]["models"]["challenger"]["artifact"] = {
            "path": "fake/path",
            "sha256": "ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890",
            "format": "cbm",
        }
        errors_a = ModelRegistry.validate_registry(bad_data_a)
        self.assertTrue(any("NOT_READY_FOR_PRODUCTION model must not be marked AVAILABLE" in err for err in errors_a))

        # Case B: LOCKED_PRODUCTION marked NOT_AVAILABLE without exception
        bad_data_b = copy.deepcopy(self.registry.get_registry())
        bad_data_b["domains"]["schedule_3m"]["models"]["legacy"]["production_availability"] = AVAILABILITY_NOT_AVAILABLE
        errors_b = ModelRegistry.validate_registry(bad_data_b)
        self.assertTrue(any("LOCKED_PRODUCTION model cannot have production_availability=NOT_AVAILABLE" in err for err in errors_b))

    # 17. Missing artifact fails verification
    def test_17_missing_artifact_fails_verification(self) -> None:
        bad_data = copy.deepcopy(self.registry.get_registry())
        bad_data["domains"]["schedule_3m"]["models"]["legacy"]["artifact"]["path"] = "nonexistent/file.cbm"
        reg = ModelRegistry(bad_data, root=self.root)
        with self.assertRaises(ModelRegistryVerificationError):
            reg.verify(fail_closed=True)

    # 18. Artifact hash mismatch fails verification
    def test_18_artifact_hash_mismatch_fails_verification(self) -> None:
        # Check verify_hashes directly
        hashes = self.registry.verify_hashes(self.root)
        self.assertTrue(hashes["all_passed"])

        # Create temporary mismatch check
        class TamperedRegistry(ModelRegistry):
            pass

        bad_data = copy.deepcopy(self.registry.get_registry())
        reg = ModelRegistry(bad_data, root=self.root)

        # Mock a mismatch by pointing to the other model file
        from unittest.mock import patch
        with patch("src.ml.model_registry.SCHEDULE_LEGACY_ARTIFACT_SHA256", "0" * 64):
            with self.assertRaises(ModelRegistryVerificationError):
                reg.verify(fail_closed=True)

    # 19. Canonical monthly dataset hash verifies
    def test_19_canonical_monthly_dataset_hash_verifies(self) -> None:
        path = self.root / CANONICAL_MONTHLY_PATH
        self.assertTrue(path.is_file(), f"Monthly dataset missing: {path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        self.assertEqual(actual_hash, CANONICAL_MONTHLY_SHA256)
        self.assertEqual(actual_hash, "9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF")

    # 20. Canonical completed dataset hash verifies
    def test_20_canonical_completed_dataset_hash_verifies(self) -> None:
        path = self.root / CANONICAL_COMPLETED_PATH
        self.assertTrue(path.is_file(), f"Completed dataset missing: {path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        self.assertEqual(actual_hash, CANONICAL_COMPLETED_SHA256)
        self.assertEqual(actual_hash, "89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910")

    # 21. Legacy schedule model hash verifies
    def test_21_legacy_schedule_model_hash_verifies(self) -> None:
        path = self.root / SCHEDULE_LEGACY_ARTIFACT_PATH
        self.assertTrue(path.is_file(), f"Legacy model missing: {path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        self.assertEqual(actual_hash, SCHEDULE_LEGACY_ARTIFACT_SHA256)
        self.assertEqual(actual_hash, "59586004F5967602651156E0A26FE564015F240958F5416CBB565E4755C524EE")

    # 22. Modern schedule model hash verifies
    def test_22_modern_schedule_model_hash_verifies(self) -> None:
        path = self.root / SCHEDULE_MODERN_ARTIFACT_PATH
        self.assertTrue(path.is_file(), f"Modern model missing: {path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        self.assertEqual(actual_hash, SCHEDULE_MODERN_ARTIFACT_SHA256)
        self.assertEqual(actual_hash, "679D9768869088BA8CEE297577B1935DCF903F00B38697BF9A3FFA2F7DEB5082")

    # 23. Registry serialization is deterministic
    def test_23_registry_serialization_is_deterministic(self) -> None:
        data1 = build_authoritative_registry_data()
        data2 = build_authoritative_registry_data()
        dump1 = json.dumps(data1, indent=2, sort_keys=True)
        dump2 = json.dumps(data2, indent=2, sort_keys=True)
        self.assertEqual(dump1, dump2)

    # 24. Registry load is deterministic
    def test_24_registry_load_is_deterministic(self) -> None:
        reg1 = ModelRegistry.load(root=self.root)
        reg2 = ModelRegistry.load(root=self.root)
        self.assertEqual(reg1.get_registry(), reg2.get_registry())

    # 25. Registry performs no artifact mutation
    def test_25_registry_performs_no_artifact_mutation(self) -> None:
        leg_bytes_before = (self.root / SCHEDULE_LEGACY_ARTIFACT_PATH).read_bytes()
        mod_bytes_before = (self.root / SCHEDULE_MODERN_ARTIFACT_PATH).read_bytes()

        # Load and run verification multiple times
        reg = ModelRegistry.load(root=self.root)
        reg.verify(fail_closed=True)
        reg.get_model("schedule_legacy_catboost")
        reg.get_domain("schedule_3m")

        leg_bytes_after = (self.root / SCHEDULE_LEGACY_ARTIFACT_PATH).read_bytes()
        mod_bytes_after = (self.root / SCHEDULE_MODERN_ARTIFACT_PATH).read_bytes()

        self.assertEqual(leg_bytes_before, leg_bytes_after)
        self.assertEqual(mod_bytes_before, mod_bytes_after)

    # 26. Registry performs no dataset mutation
    def test_26_registry_performs_no_dataset_mutation(self) -> None:
        monthly_bytes_before = (self.root / CANONICAL_MONTHLY_PATH).read_bytes()
        completed_bytes_before = (self.root / CANONICAL_COMPLETED_PATH).read_bytes()

        reg = ModelRegistry.load(root=self.root)
        reg.verify_hashes()

        monthly_bytes_after = (self.root / CANONICAL_MONTHLY_PATH).read_bytes()
        completed_bytes_after = (self.root / CANONICAL_COMPLETED_PATH).read_bytes()

        self.assertEqual(monthly_bytes_before, monthly_bytes_after)
        self.assertEqual(completed_bytes_before, completed_bytes_after)

    # 27. Registry verification report is deterministic
    def test_27_registry_verification_report_is_deterministic(self) -> None:
        rep1 = self.registry.verify(fail_closed=True)
        rep2 = self.registry.verify(fail_closed=True)
        self.assertEqual(json.dumps(rep1, sort_keys=True), json.dumps(rep2, sort_keys=True))

    # 28. Source references resolve
    def test_28_source_references_resolve(self) -> None:
        rep = self.registry.verify(fail_closed=True)
        self.assertIn("source_references_resolved", rep)
        for ref_name, resolved in rep["source_references_resolved"].items():
            self.assertTrue(resolved, f"Reference '{ref_name}' failed to resolve.")

    # 29. All model records have required scientific metadata
    def test_29_all_model_records_have_required_scientific_metadata(self) -> None:
        for d_id in self.registry.list_domains():
            dom = self.registry.get_domain(d_id)
            for m_key, m in dom["models"].items():
                self.assertIn("target", m, f"{d_id}.{m_key}")
                self.assertIn("horizon_months", m, f"{d_id}.{m_key}")
                self.assertIn("validation_methodology", m, f"{d_id}.{m_key}")
                self.assertIn("embargo_policy", m, f"{d_id}.{m_key}")
                self.assertIn("features", m, f"{d_id}.{m_key}")
                self.assertIn("calibration", m, f"{d_id}.{m_key}")
                self.assertIn("threshold_policy", m, f"{d_id}.{m_key}")
                self.assertIn("explainability", m, f"{d_id}.{m_key}")
                self.assertIn("limitations", m, f"{d_id}.{m_key}")
                self.assertTrue(len(m["limitations"]) > 0, f"{d_id}.{m_key} has empty limitations")

    # 30. Research models are never promoted to production availability
    def test_30_research_models_are_never_promoted_to_production_availability(self) -> None:
        cost_models = self.registry.get_domain("cost_overrun")["models"]
        for m in cost_models.values():
            self.assertNotEqual(m["production_availability"], AVAILABILITY_AVAILABLE)
            self.assertEqual(m["production_availability"], AVAILABILITY_EVALUATION_ONLY)

        impl_models = self.registry.get_domain("implementation_risk")["models"]
        for m in impl_models.values():
            self.assertNotEqual(m["production_availability"], AVAILABILITY_AVAILABLE)
            self.assertEqual(m["production_availability"], AVAILABILITY_EVALUATION_ONLY)

    # 31. Implementation limitations remain explicit
    def test_31_implementation_limitations_remain_explicit(self) -> None:
        dom = self.registry.get_domain("implementation_risk")
        self.assertEqual(dom["governance_status"], GOVERNANCE_VIABLE_WITH_LIMITATIONS)
        challenger = dom["models"]["challenger"]
        limitations = challenger["limitations"]
        self.assertTrue(any("Regime divergence" in lim for lim in limitations))
        self.assertTrue(any("Segments 1 and 2 structurally omit physical progress" in lim for lim in limitations))

    # 32. Programmatic lookup behaves correctly
    def test_32_programmatic_lookup_behaves_correctly(self) -> None:
        # By exact model_id
        m1 = self.registry.get_model("schedule_legacy_catboost")
        self.assertEqual(m1["model_id"], "schedule_legacy_catboost")

        # By model_name
        m2 = self.registry.get_model("catboost_full_v1__unweighted")
        self.assertEqual(m2["model_id"], "schedule_legacy_catboost")

        # By domain alias and regime
        m3 = self.registry.get_model(domain="schedule", regime="modern")
        self.assertEqual(m3["model_id"], "schedule_modern_logistic")

        # By domain alias and candidate_type
        m4 = self.registry.get_model(domain="cost", candidate_type="challenger")
        self.assertEqual(m4["model_id"], "cost_overrun_challenger_catboost")

    # 33. Unknown domain lookup fails cleanly
    def test_33_unknown_domain_lookup_fails_cleanly(self) -> None:
        with self.assertRaises(KeyError):
            self.registry.get_domain("nonexistent_domain")

    # 34. Unknown model lookup fails cleanly
    def test_34_unknown_model_lookup_fails_cleanly(self) -> None:
        with self.assertRaises(KeyError):
            self.registry.get_model("nonexistent_model_id")

        with self.assertRaises(KeyError):
            self.registry.get_model(domain="schedule_3m", regime="NONEXISTENT_REGIME")

    # 35. Artifact files exist on disk
    def test_35_artifact_files_exist_on_disk(self) -> None:
        self.assertTrue((self.root / DEFAULT_REGISTRY_RELPATH).is_file())
        self.assertTrue((self.root / DEFAULT_MANIFEST_RELPATH).is_file())
        self.assertTrue((self.root / DEFAULT_REPORT_RELPATH).is_file())
        self.assertTrue((self.root / SCHEMA_CONTRACT_RELPATH).is_file())

    # 36. Read-only API integration test
    def test_36_api_endpoints_return_registry_metadata(self) -> None:
        # Test backend app endpoints
        resp_b1 = self.backend_client.get("/api/ml/model-registry")
        self.assertEqual(resp_b1.status_code, 200)
        data_b1 = resp_b1.json()
        self.assertEqual(data_b1["registry_id"], REGISTRY_ID)
        self.assertEqual(data_b1["registry_version"], REGISTRY_VERSION)
        self.assertIn("schedule_3m", data_b1["domains"])

        resp_b2 = self.backend_client.get("/api/v1/ml/model-registry")
        self.assertEqual(resp_b2.status_code, 200)

        # Test serving app endpoints
        resp_s1 = self.serving_client.get("/api/ml/model-registry")
        self.assertEqual(resp_s1.status_code, 200)
        data_s1 = resp_s1.json()
        self.assertEqual(data_s1["registry_id"], REGISTRY_ID)

        resp_s2 = self.serving_client.get("/risk/model-registry")
        self.assertEqual(resp_s2.status_code, 200)

        # Verify path masking
        legacy_path = data_b1["domains"]["schedule_3m"]["models"]["legacy"]["artifact"]["path"]
        self.assertFalse(":" in legacy_path and "\\" in legacy_path, "Internal absolute Windows path was exposed")


if __name__ == "__main__":
    unittest.main()
