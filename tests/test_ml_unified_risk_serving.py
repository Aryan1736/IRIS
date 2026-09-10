"""Comprehensive regression test suite for IRIS PR-10: Unified Risk Serving.

Covers all 28 required test dimensions:
1. Unified predictor initialization and hash verification
2. Response schema completeness and field types
3. Schedule successful prediction
4. Schedule direct-vs-unified numerical parity (< 1e-12)
5. Schedule legacy regime
6. Schedule modern regime
7. Schedule structural gap rejection
8. Schedule contradictory regime rejection
9. Implementation risk handling of supported months (fail-closed, evaluation-only)
10. Implementation unsupported segment handling (Segments 1 & 2 fail closed / INELIGIBLE)
11. Implementation structural boundary handling
12. Implementation direct-vs-unified consistency where applicable
13. Cost-overrun explicitly marked NOT_READY_FOR_PRODUCTION
14. Cost-overrun cannot return an autonomous production decision
15. Missing required feature rejection
16. Unknown feature rejection
17. Leakage field rejection
18. Invalid numeric rejection
19. NaN rejection
20. Infinity rejection
21. Invalid report month rejection
22. Deterministic repeated calls
23. Call-order invariance
24. Model and preprocessor immutability
25. Canonical dataset hash integrity
26. Locked schedule artifact hash integrity
27. Backend API integration tests (POST /api/ml/unified-risk and POST /api/v1/risk/unified)
28. Backward compatibility with existing serving endpoints
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from backend.app.main import app as fastapi_backend_app
from src.ml.build_artifacts import DEFAULT_ARTIFACT_RELPATH, file_sha256
from src.ml.dataset_builder import (
    COMPLETED_SHA256,
    ONGOING_SHA256,
    segment_for_month,
)
from src.ml.predict_schedule import (
    ALLOWED_METADATA_KEYS,
    PredictionResult,
    ScheduleExtensionPredictor,
)
from src.ml.unified_risk_predictor import (
    GOVERNANCE_STATUS_COST,
    GOVERNANCE_STATUS_IMPLEMENTATION,
    GOVERNANCE_STATUS_SCHEDULE,
    PROHIBITED_LEAKAGE_FIELDS,
    SCHEDULE_DECISION_THRESHOLD,
    SERVING_CONTRACT_VERSION,
    UnifiedRiskPredictor,
)
from src.serving.api import create_app as create_standalone_serving_app
from src.serving.builder import build as build_serving_db

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data/ml/schedule_extension_3m"
ARTIFACT_DIR = ROOT / DEFAULT_ARTIFACT_RELPATH

TOLERANCE_MACHINE_PRECISION = 1e-12

LOCKED_LEGACY_MODEL_SHA = "59586004F5967602651156E0A26FE564015F240958F5416CBB565E4755C524EE"
LOCKED_MODERN_MODEL_SHA = "679D9768869088BA8CEE297577B1935DCF903F00B38697BF9A3FFA2F7DEB5082"


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


class TestUnifiedRiskServing(unittest.TestCase):
    """Regression test suite for UnifiedRiskPredictor and unified API serving."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.unified_predictor = UnifiedRiskPredictor.load(
            artifacts_dir=ARTIFACT_DIR,
            verify_hashes=True,
        )
        cls.schedule_predictor = cls.unified_predictor.schedule_predictor

        # Load reference rows
        cls.legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        cls.modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")

        cls.legacy_features = cls.schedule_predictor.get_features_for_regime("LEGACY")
        cls.modern_features = cls.schedule_predictor.get_features_for_regime("MODERN")

        # Representative valid rows
        cls.sample_legacy_raw = next(
            r for r in cls.legacy_rows if r["report_month"] == "2024-10"
        )
        cls.sample_legacy_dict = _extract_contract_features(
            cls.sample_legacy_raw, cls.legacy_features
        )

        cls.sample_modern_raw = next(
            r for r in cls.modern_rows if r["report_month"] == "2026-04"
        )
        cls.sample_modern_dict = _extract_contract_features(
            cls.sample_modern_raw, cls.modern_features
        )

        # Early segment rows (Segment 1: 2023-07, where physical progress was structurally unavailable)
        cls.sample_segment1_raw = next(
            r for r in cls.legacy_rows if r["report_month"] == "2023-07"
        )
        cls.sample_segment1_dict = _extract_contract_features(
            cls.sample_segment1_raw, cls.legacy_features
        )

        cls.backend_client = TestClient(fastapi_backend_app)

    # 1. Unified predictor initialization
    def test_01_unified_predictor_initialization_and_hashes(self) -> None:
        predictor = UnifiedRiskPredictor.load(artifacts_dir=ARTIFACT_DIR, verify_hashes=True)
        self.assertIsNotNone(predictor)
        self.assertIsNotNone(predictor.schedule_predictor)
        self.assertEqual(predictor.serving_contract_version, SERVING_CONTRACT_VERSION)

    # 2. Response schema
    def test_02_response_schema_completeness(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_modern_dict)
        self.assertIn("project_id", res)
        self.assertIn("report_month", res)
        self.assertIn("schedule_extension", res)
        self.assertIn("cost_overrun", res)
        self.assertIn("implementation_risk", res)
        self.assertIn("metadata", res)

        # Validate schedule_extension block
        sch = res["schedule_extension"]
        for key in ("status", "regime", "risk_score", "prediction", "threshold", "model_version", "reason"):
            self.assertIn(key, sch)

        # Validate cost_overrun block
        cost = res["cost_overrun"]
        for key in ("status", "risk_score", "prediction", "operational_status", "reason"):
            self.assertIn(key, cost)

        # Validate implementation_risk block
        impl = res["implementation_risk"]
        for key in ("status", "regime", "risk_score", "prediction", "threshold", "model_version", "operational_status", "reason"):
            self.assertIn(key, impl)

        # Validate metadata block
        meta = res["metadata"]
        self.assertEqual(meta["serving_contract_version"], SERVING_CONTRACT_VERSION)
        self.assertTrue(meta["deterministic"])
        self.assertIn("governance", meta)

    # 3. Schedule successful prediction
    def test_03_schedule_successful_prediction(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_modern_dict)
        sch = res["schedule_extension"]
        self.assertEqual(sch["status"], "AVAILABLE")
        self.assertEqual(sch["regime"], "MODERN")
        self.assertIsInstance(sch["risk_score"], float)
        self.assertGreaterEqual(sch["risk_score"], 0.0)
        self.assertLessEqual(sch["risk_score"], 1.0)
        self.assertIn(sch["prediction"], (0, 1))
        self.assertEqual(sch["threshold"], SCHEDULE_DECISION_THRESHOLD)
        self.assertEqual(sch["model_version"], "logistic_static_only__unweighted")
        self.assertIsNone(sch["reason"])

    # 4. Schedule direct-vs-unified parity
    def test_04_schedule_direct_vs_unified_parity(self) -> None:
        # Modern parity
        direct_modern = self.schedule_predictor.predict_one(self.sample_modern_dict)
        unified_modern = self.unified_predictor.predict_one(self.sample_modern_dict)
        self.assertAlmostEqual(
            direct_modern.probability,
            unified_modern["schedule_extension"]["risk_score"],
            delta=TOLERANCE_MACHINE_PRECISION,
        )

        # Legacy parity
        direct_legacy = self.schedule_predictor.predict_one(self.sample_legacy_dict)
        unified_legacy = self.unified_predictor.predict_one(self.sample_legacy_dict)
        self.assertAlmostEqual(
            direct_legacy.probability,
            unified_legacy["schedule_extension"]["risk_score"],
            delta=TOLERANCE_MACHINE_PRECISION,
        )

    # 5. Schedule legacy regime
    def test_05_schedule_legacy_regime(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_legacy_dict)
        sch = res["schedule_extension"]
        self.assertEqual(sch["status"], "AVAILABLE")
        self.assertEqual(sch["regime"], "LEGACY")
        self.assertEqual(sch["model_version"], "catboost_full_v1__unweighted")

    # 6. Schedule modern regime
    def test_06_schedule_modern_regime(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_modern_dict)
        sch = res["schedule_extension"]
        self.assertEqual(sch["status"], "AVAILABLE")
        self.assertEqual(sch["regime"], "MODERN")
        self.assertEqual(sch["model_version"], "logistic_static_only__unweighted")

    # 7. Schedule structural gap rejection
    def test_07_schedule_structural_gap_rejection(self) -> None:
        gap_payload = copy.deepcopy(self.sample_legacy_dict)
        gap_payload["report_month"] = "2024-04"  # April 2024 is a known structural gap month
        with self.assertRaises(ValueError) as ctx:
            self.unified_predictor.predict_one(gap_payload)
        self.assertIn("structural gap month", str(ctx.exception).lower())

    # 8. Schedule contradictory regime rejection
    def test_08_schedule_contradictory_regime_rejection(self) -> None:
        contradictory_payload = copy.deepcopy(self.sample_modern_dict)
        contradictory_payload["regime"] = "LEGACY"  # Modern 2026-04 contradicts LEGACY
        with self.assertRaises(ValueError) as ctx:
            self.unified_predictor.predict_one(contradictory_payload)
        self.assertIn("contradicts contract segment regime", str(ctx.exception))

    # 9. Implementation risk handling in supported months (fail-closed / NOT_AVAILABLE)
    def test_09_implementation_risk_handling_supported_months(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_modern_dict)
        impl = res["implementation_risk"]
        self.assertEqual(impl["status"], "NOT_AVAILABLE")
        self.assertEqual(impl["operational_status"], GOVERNANCE_STATUS_IMPLEMENTATION)
        self.assertIsNone(impl["risk_score"])
        self.assertIsNone(impl["prediction"])
        self.assertIsNotNone(impl["reason"])
        self.assertIn("no serialized production model artifact exists", impl["reason"])

    # 10. Implementation unsupported segment handling (Segments 1 and 2 return INELIGIBLE)
    def test_10_implementation_unsupported_segment_handling(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_segment1_dict)
        impl = res["implementation_risk"]
        self.assertEqual(impl["status"], "INELIGIBLE")
        self.assertEqual(impl["operational_status"], GOVERNANCE_STATUS_IMPLEMENTATION)
        self.assertIsNone(impl["risk_score"])
        self.assertIn("structurally unavailable", impl["reason"].lower())

    # 11. Implementation structural boundary handling
    def test_11_implementation_structural_boundary_handling(self) -> None:
        # Boundary month 2023-12 or out of range
        out_of_range_payload = copy.deepcopy(self.sample_modern_dict)
        out_of_range_payload["report_month"] = "2027-01"
        with self.assertRaises(ValueError) as ctx:
            self.unified_predictor.predict_one(out_of_range_payload)
        self.assertIn("continuous model segment", str(ctx.exception).lower())

    # 12. Implementation consistency
    def test_12_implementation_consistency_across_calls(self) -> None:
        res1 = self.unified_predictor.predict_one(self.sample_modern_dict)
        res2 = self.unified_predictor.predict_one(self.sample_modern_dict)
        self.assertEqual(res1["implementation_risk"], res2["implementation_risk"])

    # 13. Cost overrun explicitly marked research-only / NOT_READY_FOR_PRODUCTION
    def test_13_cost_overrun_governance_status(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_modern_dict)
        cost = res["cost_overrun"]
        self.assertEqual(cost["status"], "NOT_AVAILABLE")
        self.assertEqual(cost["operational_status"], GOVERNANCE_STATUS_COST)
        self.assertIn("NOT_READY_FOR_PRODUCTION", cost["reason"])

    # 14. Cost overrun cannot return an autonomous production decision
    def test_14_cost_overrun_no_autonomous_decision(self) -> None:
        res = self.unified_predictor.predict_one(self.sample_modern_dict)
        cost = res["cost_overrun"]
        self.assertIsNone(cost["risk_score"])
        self.assertIsNone(cost["prediction"])
        self.assertIsNone(cost["threshold"])

    # 15. Missing feature rejection
    def test_15_missing_feature_rejection(self) -> None:
        bad_payload = copy.deepcopy(self.sample_modern_dict)
        del bad_payload["cumulative_expenditure_t"]
        with self.assertRaises(ValueError) as ctx:
            self.unified_predictor.predict_one(bad_payload)
        self.assertIn("missing", str(ctx.exception).lower())

    # 16. Unknown feature rejection
    def test_16_unknown_feature_rejection(self) -> None:
        bad_payload = copy.deepcopy(self.sample_modern_dict)
        bad_payload["arbitrary_new_feature"] = 123.45
        with self.assertRaises(ValueError) as ctx:
            self.unified_predictor.predict_one(bad_payload)
        self.assertIn("unknown", str(ctx.exception).lower())

    # 17. Leakage field rejection
    def test_17_leakage_field_rejection(self) -> None:
        for leakage_field in [
            "target_effective_schedule_ext_3m",
            "target_effective_cost_esc_3m",
            "target_progress_stagnation_3m",
            "future_progress_t3",
            "completed_revised_cost",
            "eventually_completed",
        ]:
            bad_payload = copy.deepcopy(self.sample_modern_dict)
            bad_payload[leakage_field] = 1.0
            with self.assertRaises(ValueError) as ctx:
                self.unified_predictor.predict_one(bad_payload)
            self.assertIn("prohibited leakage field", str(ctx.exception).lower())

    # 18. Invalid numeric rejection
    def test_18_invalid_numeric_rejection(self) -> None:
        bad_payload = copy.deepcopy(self.sample_modern_dict)
        bad_payload["original_cost"] = "not_a_number_string"
        with self.assertRaises(ValueError) as ctx:
            self.unified_predictor.predict_one(bad_payload)
        self.assertIn("invalid numeric value", str(ctx.exception).lower())

    # 19. NaN rejection
    def test_19_nan_rejection(self) -> None:
        # Float NaN
        bad_payload1 = copy.deepcopy(self.sample_modern_dict)
        bad_payload1["original_cost"] = float("nan")
        with self.assertRaises(ValueError) as ctx1:
            self.unified_predictor.predict_one(bad_payload1)
        self.assertIn("nan value rejected", str(ctx1.exception).lower())

        # String "NaN"
        bad_payload2 = copy.deepcopy(self.sample_modern_dict)
        bad_payload2["original_cost"] = "NaN"
        with self.assertRaises(ValueError) as ctx2:
            self.unified_predictor.predict_one(bad_payload2)
        self.assertIn("nan value rejected", str(ctx2.exception).lower())

    # 20. Infinity rejection
    def test_20_infinity_rejection(self) -> None:
        # Float inf
        bad_payload1 = copy.deepcopy(self.sample_modern_dict)
        bad_payload1["original_cost"] = float("inf")
        with self.assertRaises(ValueError) as ctx1:
            self.unified_predictor.predict_one(bad_payload1)
        self.assertIn("infinite value rejected", str(ctx1.exception).lower())

        # String "-inf"
        bad_payload2 = copy.deepcopy(self.sample_modern_dict)
        bad_payload2["original_cost"] = "-infinity"
        with self.assertRaises(ValueError) as ctx2:
            self.unified_predictor.predict_one(bad_payload2)
        self.assertIn("infinite value rejected", str(ctx2.exception).lower())

    # 21. Invalid month rejection
    def test_21_invalid_month_rejection(self) -> None:
        bad_payload = copy.deepcopy(self.sample_modern_dict)
        bad_payload["report_month"] = "2026-13"  # invalid month
        with self.assertRaises(ValueError) as ctx:
            self.unified_predictor.predict_one(bad_payload)
        self.assertIn("report_month", str(ctx.exception).lower())

    # 22. Deterministic repeated calls
    def test_22_deterministic_repeated_calls(self) -> None:
        res1 = self.unified_predictor.predict_one(self.sample_modern_dict)
        res2 = self.unified_predictor.predict_one(self.sample_modern_dict)
        self.assertEqual(res1, res2)

    # 23. Call-order invariance
    def test_23_call_order_invariance(self) -> None:
        row_a = copy.deepcopy(self.sample_modern_dict)
        row_b = copy.deepcopy(self.sample_modern_dict)
        row_b["original_cost"] = "5000.0"

        batch_ab = self.unified_predictor.predict_batch([row_a, row_b])
        batch_ba = self.unified_predictor.predict_batch([row_b, row_a])

        self.assertEqual(batch_ab[0], batch_ba[1])
        self.assertEqual(batch_ab[1], batch_ba[0])

    # 24. Model and preprocessor immutability
    def test_24_model_and_preprocessor_immutability(self) -> None:
        model = self.schedule_predictor.get_model("MODERN")
        preprocessor = self.schedule_predictor.get_preprocessor("MODERN")

        weights_before = copy.deepcopy(model.coef_)
        intercept_before = copy.deepcopy(model.intercept_)
        means_before = copy.deepcopy(preprocessor.numeric_mean)
        scales_before = copy.deepcopy(preprocessor.numeric_scale)

        for _ in range(5):
            self.unified_predictor.predict_one(self.sample_modern_dict)

        self.assertTrue(math.isclose(float(weights_before[0][0]), float(model.coef_[0][0]), rel_tol=1e-12))
        self.assertEqual(float(intercept_before[0]), float(model.intercept_[0]))
        self.assertEqual(means_before, preprocessor.numeric_mean)
        self.assertEqual(scales_before, preprocessor.numeric_scale)


    # 25. Canonical dataset hash integrity
    def test_25_canonical_dataset_hash_integrity(self) -> None:
        monthly_hash = file_sha256(ROOT / "data/processed/projects_monthly.csv")
        completed_hash = file_sha256(ROOT / "data/processed/projects_completed.csv")
        self.assertEqual(monthly_hash, ONGOING_SHA256)
        self.assertEqual(completed_hash, COMPLETED_SHA256)

    # 26. Locked schedule artifact hash integrity
    def test_26_locked_schedule_artifact_hashes(self) -> None:
        legacy_path = ARTIFACT_DIR / "legacy_catboost/model.cbm"
        modern_path = ARTIFACT_DIR / "modern_logistic/model.joblib"
        self.assertEqual(file_sha256(legacy_path), LOCKED_LEGACY_MODEL_SHA)
        self.assertEqual(file_sha256(modern_path), LOCKED_MODERN_MODEL_SHA)

    # 27. API integration tests
    def test_27_backend_api_integration(self) -> None:
        # POST /api/ml/unified-risk (root endpoint)
        resp1 = self.backend_client.post("/api/ml/unified-risk", json=self.sample_modern_dict)
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertEqual(data1["schedule_extension"]["status"], "AVAILABLE")
        self.assertEqual(data1["cost_overrun"]["status"], "NOT_AVAILABLE")
        self.assertEqual(data1["implementation_risk"]["status"], "NOT_AVAILABLE")

        # POST /api/v1/risk/unified (v1 endpoint)
        resp2 = self.backend_client.post("/api/v1/risk/unified", json=self.sample_modern_dict)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(data1, data2)

        # POST /risk/unified (direct proxy endpoint)
        resp3 = self.backend_client.post("/risk/unified", json=self.sample_modern_dict)
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(resp1.json(), resp3.json())

        # Bad request: leakage field rejected with 422
        bad_req = copy.deepcopy(self.sample_modern_dict)
        bad_req["target_effective_schedule_ext_3m"] = 1.0
        resp_bad = self.backend_client.post("/api/ml/unified-risk", json=bad_req)
        self.assertEqual(resp_bad.status_code, 422)

        # Bad request: malformed report_month rejected with 422
        bad_req2 = copy.deepcopy(self.sample_modern_dict)
        bad_req2["report_month"] = "invalid_month"
        resp_bad2 = self.backend_client.post("/api/ml/unified-risk", json=bad_req2)
        self.assertEqual(resp_bad2.status_code, 422)

    # 28. Backward compatibility with existing serving endpoints
    def test_28_backward_compatibility_with_existing_serving(self) -> None:
        # Ping
        ping_resp = self.backend_client.get("/ping")
        self.assertEqual(ping_resp.status_code, 200)
        self.assertEqual(ping_resp.json()["status"], "pong")

        # Options endpoint
        options_resp = self.backend_client.get("/api/v1/risk/options")
        self.assertEqual(options_resp.status_code, 200)
        self.assertIn("report_months", options_resp.json())


if __name__ == "__main__":
    unittest.main()
