"""Comprehensive regression test suite for IRIS PR-12: Unified Risk Intelligence.

Covers all 30 required test dimensions:
1. Successful profile generation (Legacy and Modern)
2. Deterministic repeated output
3. Schedule AVAILABLE propagation
4. Cost NOT_AVAILABLE propagation
5. Implementation INELIGIBLE propagation (Segments 1 & 2)
6. Implementation NOT_AVAILABLE propagation (Segments 3 & 4)
7. FULL profile status (mocked 3-available scenario)
8. PARTIAL profile status (Segment 3/4 baseline)
9. LIMITED profile status (Segment 1/2 baseline)
10. UNAVAILABLE profile status (0 available)
11. INELIGIBLE profile status (all ineligible)
12. Coverage classification (COMPLETE, PARTIAL, LIMITED, NO_PREDICTIVE)
13. Priority ordering without probability aggregation
14. Unavailable domain is not treated as low risk
15. Attention classification (HIGH, MEDIUM, LIMITED_ASSESSMENT, ROUTINE, NO_ASSESSMENT)
16. Human-review recommendations deterministic trigger
17. Structural gap rejection (e.g. 2024-05)
18. Regime contradiction rejection
19. Prohibited leakage rejection
20. NaN rejection
21. Infinity rejection
22. Unknown feature rejection
23. Batch ordering preservation
24. Batch determinism
25. Predictor state immutability
26. Schedule inference parity preservation (< 1e-12)
27. Cost governance preservation
28. Implementation governance preservation
29. API validation (422 for malformed requests)
30. API response schema conformance
"""

from __future__ import annotations

import copy
import csv
import json
import math
import unittest
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from backend.app.main import app as fastapi_backend_app
from src.ml.build_artifacts import DEFAULT_ARTIFACT_RELPATH
from src.ml.predict_schedule import ALLOWED_METADATA_KEYS
from src.ml.unified_risk_intelligence import (
    ATTENTION_HIGH,
    ATTENTION_LIMITED,
    ATTENTION_MEDIUM,
    ATTENTION_NONE,
    ATTENTION_ROUTINE,
    COST_DOMAIN,
    COVERAGE_COMPLETE,
    COVERAGE_LIMITED,
    COVERAGE_NONE,
    COVERAGE_PARTIAL,
    HIGH_PRIORITY_THRESHOLD,
    IMPLEMENTATION_DOMAIN,
    MEDIUM_PRIORITY_THRESHOLD,
    POLICY_VERSION,
    PRIORITY_HIGH,
    PRIORITY_INELIGIBLE,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_UNAVAILABLE,
    PROFILE_VERSION,
    REC_COST_NOT_READY,
    REC_IMPLEMENTATION_LIMITATIONS,
    REC_INSUFFICIENT_COVERAGE,
    REC_REVIEW_SCHEDULE,
    REC_STRUCTURAL_LIMITATION,
    SCHEDULE_DOMAIN,
    STATUS_FULL,
    STATUS_INELIGIBLE,
    STATUS_LIMITED,
    STATUS_PARTIAL,
    STATUS_UNAVAILABLE,
    UnifiedRiskIntelligence,
)
from src.ml.unified_risk_predictor import (
    GOVERNANCE_STATUS_COST,
    GOVERNANCE_STATUS_IMPLEMENTATION,
    GOVERNANCE_STATUS_SCHEDULE,
    SCHEDULE_DECISION_THRESHOLD,
    UnifiedRiskPredictor,
)
from src.serving.api import create_app as create_standalone_serving_app

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data/ml/schedule_extension_3m"
ARTIFACT_DIR = ROOT / DEFAULT_ARTIFACT_RELPATH
TOLERANCE = 1e-12


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _extract_contract_features(
    row: dict[str, Any], features: list[str]
) -> dict[str, Any]:
    extracted = {k: row[k] for k in features if k in row}
    for meta_key in ALLOWED_METADATA_KEYS:
        if meta_key in row and row[meta_key] is not None:
            extracted[meta_key] = row[meta_key]
    return extracted


class TestUnifiedRiskIntelligence(unittest.TestCase):
    """Comprehensive test suite for UnifiedRiskIntelligence and Project Risk Profile."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.intelligence = UnifiedRiskIntelligence.load(
            artifacts_dir=ARTIFACT_DIR,
            verify_hashes=True,
        )
        cls.predictor = cls.intelligence.predictor
        cls.schedule_predictor = cls.predictor.schedule_predictor

        # Load reference rows
        cls.legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        cls.modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")

        cls.legacy_features = cls.schedule_predictor.get_features_for_regime("LEGACY")
        cls.modern_features = cls.schedule_predictor.get_features_for_regime("MODERN")

        # Representative valid modern row (Segment 4, 2026-04)
        cls.sample_modern_raw = next(
            r for r in cls.modern_rows if r["report_month"] == "2026-04"
        )
        cls.sample_modern_dict = _extract_contract_features(
            cls.sample_modern_raw, cls.modern_features
        )

        # Representative valid legacy row (Segment 3, 2024-10)
        cls.sample_legacy_raw = next(
            r for r in cls.legacy_rows if r["report_month"] == "2024-10"
        )
        cls.sample_legacy_dict = _extract_contract_features(
            cls.sample_legacy_raw, cls.legacy_features
        )

        # Segment 1 row (2023-07: physical progress structurally omitted)
        cls.sample_segment1_raw = next(
            r for r in cls.legacy_rows if r["report_month"] == "2023-07"
        )
        cls.sample_segment1_dict = _extract_contract_features(
            cls.sample_segment1_raw, cls.legacy_features
        )

        cls.backend_client = TestClient(fastapi_backend_app)
        cls.standalone_client = TestClient(create_standalone_serving_app())

    # 1. Successful profile generation (Legacy and Modern)
    def test_01_successful_profile_generation(self) -> None:
        # Modern profile
        modern_profile = self.intelligence.predict_one(self.sample_modern_dict)
        self.assertIn("project", modern_profile)
        self.assertIn("domains", modern_profile)
        self.assertIn("profile", modern_profile)
        self.assertIn("metadata", modern_profile)
        self.assertEqual(modern_profile["project"]["report_month"], "2026-04")
        self.assertEqual(modern_profile["metadata"]["profile_version"], PROFILE_VERSION)
        self.assertEqual(modern_profile["metadata"]["policy_version"], POLICY_VERSION)
        self.assertTrue(modern_profile["metadata"]["generated_deterministically"])

        # Legacy profile
        legacy_profile = self.intelligence.predict_one(self.sample_legacy_dict)
        self.assertEqual(legacy_profile["project"]["report_month"], "2024-10")
        self.assertIn(SCHEDULE_DOMAIN, legacy_profile["domains"])
        self.assertIn(COST_DOMAIN, legacy_profile["domains"])
        self.assertIn(IMPLEMENTATION_DOMAIN, legacy_profile["domains"])

    # 2. Deterministic repeated output
    def test_02_deterministic_repeated_output(self) -> None:
        p1 = self.intelligence.predict_one(self.sample_modern_dict)
        p2 = self.intelligence.predict_one(self.sample_modern_dict)
        self.assertEqual(p1, p2)
        self.assertEqual(json.dumps(p1, sort_keys=True), json.dumps(p2, sort_keys=True))

    # 3. Schedule AVAILABLE propagation
    def test_03_schedule_available_propagation(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        sched = res["domains"][SCHEDULE_DOMAIN]
        self.assertEqual(sched["status"], "AVAILABLE")
        self.assertEqual(sched["operational_status"], GOVERNANCE_STATUS_SCHEDULE)
        self.assertIsInstance(sched["risk_score"], float)
        self.assertIn(sched["prediction"], (0, 1))
        self.assertEqual(sched["threshold"], SCHEDULE_DECISION_THRESHOLD)

    # 4. Cost NOT_AVAILABLE propagation
    def test_04_cost_not_available_propagation(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        cost = res["domains"][COST_DOMAIN]
        self.assertEqual(cost["status"], "NOT_AVAILABLE")
        self.assertEqual(cost["operational_status"], GOVERNANCE_STATUS_COST)
        self.assertIsNone(cost["risk_score"])
        self.assertIsNone(cost["prediction"])
        self.assertIsNone(cost["threshold"])

    # 5. Implementation INELIGIBLE propagation (Segments 1 & 2)
    def test_05_implementation_ineligible_propagation(self) -> None:
        res = self.intelligence.predict_one(self.sample_segment1_dict)
        impl = res["domains"][IMPLEMENTATION_DOMAIN]
        self.assertEqual(impl["status"], "INELIGIBLE")
        self.assertEqual(impl["operational_status"], GOVERNANCE_STATUS_IMPLEMENTATION)
        self.assertIsNone(impl["risk_score"])

    # 6. Implementation NOT_AVAILABLE propagation (Segments 3 & 4)
    def test_06_implementation_not_available_propagation(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        impl = res["domains"][IMPLEMENTATION_DOMAIN]
        self.assertEqual(impl["status"], "NOT_AVAILABLE")
        self.assertEqual(impl["operational_status"], GOVERNANCE_STATUS_IMPLEMENTATION)
        self.assertIsNone(impl["risk_score"])

    # 7. FULL profile status (mocked 3-available scenario)
    def test_07_full_profile_status(self) -> None:
        mock_serving = {
            "project_id": "test-123",
            "report_month": "2026-04",
            SCHEDULE_DOMAIN: {
                "status": "AVAILABLE",
                "risk_score": 0.45,
                "operational_status": GOVERNANCE_STATUS_SCHEDULE,
            },
            COST_DOMAIN: {
                "status": "AVAILABLE",
                "risk_score": 0.25,
                "operational_status": "LOCKED_PRODUCTION",
            },
            IMPLEMENTATION_DOMAIN: {
                "status": "AVAILABLE",
                "risk_score": 0.35,
                "operational_status": "LOCKED_PRODUCTION",
            },
            "metadata": {"continuous_segment": 4},
        }
        res = self.intelligence.evaluate_profile_from_serving(mock_serving)
        self.assertEqual(res["profile"]["overall_status"], STATUS_FULL)
        self.assertEqual(res["profile"]["coverage_status"], COVERAGE_COMPLETE)
        self.assertEqual(res["profile"]["available_domain_count"], 3)
        self.assertEqual(res["profile"]["unavailable_domain_count"], 0)
        self.assertEqual(res["profile"]["ineligible_domain_count"], 0)

    # 8. PARTIAL profile status (Segment 3/4 baseline)
    def test_08_partial_profile_status(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        self.assertEqual(res["profile"]["overall_status"], STATUS_PARTIAL)
        self.assertEqual(res["profile"]["coverage_status"], COVERAGE_PARTIAL)
        self.assertEqual(res["profile"]["available_domain_count"], 1)
        self.assertEqual(res["profile"]["unavailable_domain_count"], 2)
        self.assertEqual(res["profile"]["ineligible_domain_count"], 0)

    # 9. LIMITED profile status (Segment 1/2 baseline)
    def test_09_limited_profile_status(self) -> None:
        res = self.intelligence.predict_one(self.sample_segment1_dict)
        self.assertEqual(res["profile"]["overall_status"], STATUS_LIMITED)
        self.assertEqual(res["profile"]["coverage_status"], COVERAGE_LIMITED)
        self.assertEqual(res["profile"]["available_domain_count"], 1)
        self.assertEqual(res["profile"]["unavailable_domain_count"], 1)
        self.assertEqual(res["profile"]["ineligible_domain_count"], 1)

    # 10. UNAVAILABLE profile status (0 available)
    def test_10_unavailable_profile_status(self) -> None:
        mock_serving = {
            "project_id": "test-none",
            "report_month": "2026-04",
            SCHEDULE_DOMAIN: {
                "status": "NOT_AVAILABLE",
                "risk_score": None,
                "operational_status": "UNAVAILABLE",
            },
            COST_DOMAIN: {
                "status": "NOT_AVAILABLE",
                "risk_score": None,
                "operational_status": GOVERNANCE_STATUS_COST,
            },
            IMPLEMENTATION_DOMAIN: {
                "status": "NOT_AVAILABLE",
                "risk_score": None,
                "operational_status": GOVERNANCE_STATUS_IMPLEMENTATION,
            },
            "metadata": {"continuous_segment": 4},
        }
        res = self.intelligence.evaluate_profile_from_serving(mock_serving)
        self.assertEqual(res["profile"]["overall_status"], STATUS_UNAVAILABLE)
        self.assertEqual(res["profile"]["coverage_status"], COVERAGE_NONE)
        self.assertEqual(res["profile"]["attention_level"], ATTENTION_NONE)

    # 11. INELIGIBLE profile status (all ineligible)
    def test_11_ineligible_profile_status(self) -> None:
        mock_serving = {
            "project_id": "test-all-ineligible",
            "report_month": "2026-04",
            SCHEDULE_DOMAIN: {
                "status": "INELIGIBLE",
                "risk_score": None,
                "operational_status": "INELIGIBLE",
            },
            COST_DOMAIN: {
                "status": "INELIGIBLE",
                "risk_score": None,
                "operational_status": "INELIGIBLE",
            },
            IMPLEMENTATION_DOMAIN: {
                "status": "INELIGIBLE",
                "risk_score": None,
                "operational_status": "INELIGIBLE",
            },
            "metadata": {"continuous_segment": 1},
        }
        res = self.intelligence.evaluate_profile_from_serving(mock_serving)
        self.assertEqual(res["profile"]["overall_status"], STATUS_INELIGIBLE)
        self.assertEqual(res["profile"]["coverage_status"], COVERAGE_NONE)
        self.assertEqual(res["profile"]["ineligible_domain_count"], 3)

    # 12. Coverage classification
    def test_12_coverage_classification(self) -> None:
        # COMPLETE
        c1 = self.intelligence._classify_coverage(3, 0, 0, 3)
        self.assertEqual(c1, COVERAGE_COMPLETE)
        # PARTIAL
        c2 = self.intelligence._classify_coverage(1, 2, 0, 3)
        self.assertEqual(c2, COVERAGE_PARTIAL)
        # LIMITED
        c3 = self.intelligence._classify_coverage(1, 1, 1, 3)
        self.assertEqual(c3, COVERAGE_LIMITED)
        # NONE
        c4 = self.intelligence._classify_coverage(0, 3, 0, 3)
        self.assertEqual(c4, COVERAGE_NONE)

    # 13. Priority ordering without probability aggregation
    def test_13_priority_ordering_without_probability_aggregation(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        priorities = res["profile"]["priority_domains"]
        self.assertEqual(len(priorities), 3)

        # Check that domains have rank 1, 2, 3
        ranks = [p["rank"] for p in priorities]
        self.assertEqual(ranks, [1, 2, 3])

        # Verify no combined or average score field exists in profile
        self.assertNotIn("overall_risk", res["profile"])
        self.assertNotIn("average_risk", res["profile"])
        self.assertNotIn("combined_risk", res["profile"])
        self.assertNotIn("max_risk", res["profile"])

    # 14. Unavailable domain is not treated as low risk
    def test_14_unavailable_domain_is_not_treated_as_low_risk(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        priorities = {p["domain"]: p for p in res["profile"]["priority_domains"]}

        cost_p = priorities[COST_DOMAIN]
        self.assertEqual(cost_p["priority_level"], PRIORITY_UNAVAILABLE)
        self.assertNotEqual(cost_p["priority_level"], PRIORITY_LOW)
        self.assertIn("not be interpreted as low risk", cost_p["rationale"])

    # 15. Attention classification
    def test_15_attention_classification(self) -> None:
        # High attention when schedule >= 0.50
        mock_high = {
            "project_id": "test",
            "report_month": "2026-04",
            SCHEDULE_DOMAIN: {
                "status": "AVAILABLE",
                "risk_score": 0.85,
                "operational_status": GOVERNANCE_STATUS_SCHEDULE,
            },
            COST_DOMAIN: {
                "status": "NOT_AVAILABLE",
                "risk_score": None,
                "operational_status": GOVERNANCE_STATUS_COST,
            },
            IMPLEMENTATION_DOMAIN: {
                "status": "NOT_AVAILABLE",
                "risk_score": None,
                "operational_status": GOVERNANCE_STATUS_IMPLEMENTATION,
            },
            "metadata": {"continuous_segment": 4},
        }
        r_high = self.intelligence.evaluate_profile_from_serving(mock_high)
        self.assertEqual(r_high["profile"]["attention_level"], ATTENTION_HIGH)

        # Medium attention when schedule in [0.30, 0.50)
        mock_med = copy.deepcopy(mock_high)
        mock_med[SCHEDULE_DOMAIN]["risk_score"] = 0.40
        r_med = self.intelligence.evaluate_profile_from_serving(mock_med)
        self.assertEqual(r_med["profile"]["attention_level"], ATTENTION_MEDIUM)

        # Limited assessment when schedule < 0.30 but coverage is partial
        mock_low = copy.deepcopy(mock_high)
        mock_low[SCHEDULE_DOMAIN]["risk_score"] = 0.15
        r_low = self.intelligence.evaluate_profile_from_serving(mock_low)
        self.assertEqual(r_low["profile"]["attention_level"], ATTENTION_LIMITED)

        # Routine when schedule < 0.30 and coverage is complete
        mock_routine = {
            "project_id": "test",
            "report_month": "2026-04",
            SCHEDULE_DOMAIN: {
                "status": "AVAILABLE",
                "risk_score": 0.15,
                "operational_status": GOVERNANCE_STATUS_SCHEDULE,
            },
            COST_DOMAIN: {
                "status": "AVAILABLE",
                "risk_score": 0.10,
                "operational_status": "LOCKED_PRODUCTION",
            },
            IMPLEMENTATION_DOMAIN: {
                "status": "AVAILABLE",
                "risk_score": 0.20,
                "operational_status": "LOCKED_PRODUCTION",
            },
            "metadata": {"continuous_segment": 4},
        }
        r_routine = self.intelligence.evaluate_profile_from_serving(mock_routine)
        self.assertEqual(r_routine["profile"]["attention_level"], ATTENTION_ROUTINE)

    # 16. Human-review recommendations
    def test_16_human_review_recommendations(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        recs = res["profile"]["recommendations"]
        rec_codes = {r["code"] for r in recs}

        # In modern sample: cost is not ready, coverage is partial, impl is limited
        self.assertIn(REC_COST_NOT_READY, rec_codes)
        self.assertIn(REC_INSUFFICIENT_COVERAGE, rec_codes)
        self.assertIn(REC_IMPLEMENTATION_LIMITATIONS, rec_codes)

        # In segment 1: structural limitation
        res_seg1 = self.intelligence.predict_one(self.sample_segment1_dict)
        seg1_codes = {r["code"] for r in res_seg1["profile"]["recommendations"]}
        self.assertIn(REC_STRUCTURAL_LIMITATION, seg1_codes)

    # 17. Structural gap rejection
    def test_17_structural_gap_rejection(self) -> None:
        bad = dict(self.sample_modern_dict)
        bad["report_month"] = "2024-05"  # Unassigned gap month
        with self.assertRaises(ValueError) as ctx:
            self.intelligence.predict_one(bad)
        self.assertIn("continuous model segment", str(ctx.exception))

    # 18. Regime contradiction rejection
    def test_18_regime_contradiction_rejection(self) -> None:
        bad = dict(self.sample_modern_dict)
        bad["regime"] = "LEGACY"  # Contradicts Modern segment
        with self.assertRaises(ValueError) as ctx:
            self.intelligence.predict_one(bad)
        self.assertIn("contradicts contract segment regime", str(ctx.exception))

    # 19. Prohibited leakage rejection
    def test_19_leakage_rejection(self) -> None:
        bad = dict(self.sample_modern_dict)
        bad["target_effective_schedule_ext_3m"] = 1.0
        with self.assertRaises(ValueError) as ctx:
            self.intelligence.predict_one(bad)
        self.assertIn("Prohibited leakage field", str(ctx.exception))

    # 20. NaN rejection
    def test_20_nan_rejection(self) -> None:
        bad = dict(self.sample_modern_dict)
        feat_name = list(self.modern_features)[0]
        bad[feat_name] = float("nan")
        with self.assertRaises(ValueError) as ctx:
            self.intelligence.predict_one(bad)
        self.assertIn("NaN value rejected", str(ctx.exception))

    # 21. Infinity rejection
    def test_21_infinity_rejection(self) -> None:
        bad = dict(self.sample_modern_dict)
        feat_name = list(self.modern_features)[0]
        bad[feat_name] = float("inf")
        with self.assertRaises(ValueError) as ctx:
            self.intelligence.predict_one(bad)
        self.assertIn("Infinite value rejected", str(ctx.exception))

    # 22. Unknown feature rejection
    def test_22_unknown_feature_rejection(self) -> None:
        bad = dict(self.sample_modern_dict)
        bad["unauthorized_experimental_feature"] = 42.0
        with self.assertRaises(ValueError) as ctx:
            self.intelligence.predict_one(bad)
        self.assertIn("Unknown / prohibited feature inputs", str(ctx.exception))


    # 23. Batch ordering preservation
    def test_23_batch_ordering_preservation(self) -> None:
        row1 = dict(self.sample_modern_dict)
        row1["project_id"] = "PROJ-AAA"

        row2 = dict(self.sample_modern_dict)
        row2["project_id"] = "PROJ-BBB"

        batch_res = self.intelligence.predict_batch([row1, row2])
        self.assertEqual(len(batch_res), 2)
        self.assertEqual(batch_res[0]["project"]["project_identifier"], "PROJ-AAA")
        self.assertEqual(batch_res[1]["project"]["project_identifier"], "PROJ-BBB")

    # 24. Batch determinism
    def test_24_batch_determinism(self) -> None:
        row1 = dict(self.sample_modern_dict)
        row2 = dict(self.sample_legacy_dict)

        batch_res = self.intelligence.predict_batch([row1, row2])
        single_1 = self.intelligence.predict_one(row1)
        single_2 = self.intelligence.predict_one(row2)

        self.assertEqual(batch_res[0], single_1)
        self.assertEqual(batch_res[1], single_2)

    # 25. Predictor state immutability
    def test_25_predictor_state_immutability(self) -> None:
        pre_state = copy.deepcopy(self.sample_modern_dict)
        _ = self.intelligence.predict_one(self.sample_modern_dict)
        self.assertEqual(self.sample_modern_dict, pre_state)

    # 26. Schedule inference parity preservation (< 1e-12)
    def test_26_schedule_inference_parity_preservation(self) -> None:
        intel_res = self.intelligence.predict_one(self.sample_modern_dict)
        serving_res = self.predictor.predict_one(self.sample_modern_dict)

        score_intel = intel_res["domains"][SCHEDULE_DOMAIN]["risk_score"]
        score_serving = serving_res[SCHEDULE_DOMAIN]["risk_score"]

        self.assertIsNotNone(score_intel)
        self.assertIsNotNone(score_serving)
        self.assertAlmostEqual(score_intel, score_serving, delta=TOLERANCE)

    # 27. Cost governance preservation
    def test_27_cost_governance_preservation(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        cost = res["domains"][COST_DOMAIN]
        self.assertEqual(cost["operational_status"], GOVERNANCE_STATUS_COST)
        self.assertEqual(cost["status"], "NOT_AVAILABLE")
        self.assertIsNone(cost["risk_score"])
        self.assertIn("NOT_READY_FOR_PRODUCTION", cost["reason"])

    # 28. Implementation governance preservation
    def test_28_implementation_governance_preservation(self) -> None:
        res = self.intelligence.predict_one(self.sample_modern_dict)
        impl = res["domains"][IMPLEMENTATION_DOMAIN]
        self.assertEqual(impl["operational_status"], GOVERNANCE_STATUS_IMPLEMENTATION)
        self.assertIn("VIABLE_WITH_LIMITATIONS", impl["reason"])

    # 29. API validation (422 for malformed requests)
    def test_29_api_validation_rejection(self) -> None:
        # Leakage rejection
        bad_leakage = dict(self.sample_modern_dict)
        bad_leakage["target_effective_schedule_ext_3m"] = 1.0
        resp = self.backend_client.post("/api/ml/unified-risk-profile", json=bad_leakage)
        self.assertEqual(resp.status_code, 422)

        # Gap month rejection
        bad_gap = dict(self.sample_modern_dict)
        bad_gap["report_month"] = "2024-05"
        resp_gap = self.backend_client.post("/api/ml/unified-risk-profile", json=bad_gap)
        self.assertEqual(resp_gap.status_code, 422)

    # 30. API response schema conformance
    def test_30_api_response_schema_conformance(self) -> None:
        # Test across /api/ml/unified-risk-profile and /api/v1/risk/profile
        resp1 = self.backend_client.post(
            "/api/ml/unified-risk-profile", json=self.sample_modern_dict
        )
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()

        resp2 = self.backend_client.post(
            "/api/v1/risk/profile", json=self.sample_modern_dict
        )
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()

        self.assertEqual(data1, data2)
        self.assertIn("project", data1)
        self.assertIn("domains", data1)
        self.assertIn("profile", data1)
        self.assertIn("metadata", data1)
        self.assertIn("priority_domains", data1["profile"])
        self.assertIn("recommendations", data1["profile"])
        self.assertIn("limitations", data1["profile"])
        self.assertIn("governance_notes", data1["profile"])
        self.assertIn("summary", data1["profile"])

        # Also test standalone serving app /risk/profile
        resp_standalone = self.standalone_client.post(
            "/risk/profile", json=self.sample_modern_dict
        )
        self.assertEqual(resp_standalone.status_code, 200)
        self.assertEqual(resp_standalone.json(), data1)


if __name__ == "__main__":
    unittest.main()
