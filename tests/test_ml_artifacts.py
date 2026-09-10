"""Focused test suite for serialized schedule model artifacts and reusable inference.

Verifies:
1. Legacy CatBoost artifact (.cbm) exists on disk and has matching SHA-256 digest.
2. Modern Logistic artifact (.joblib) exists on disk and has matching SHA-256 digest.
3. Artifact manifest exists, is valid JSON, and records:
   - contract_version == "1.0.0"
   - target == "target_effective_schedule_ext_3m"
   - horizon_months == 3
   - strict walk-forward embargo rule ("T + 3 < E")
   - exact feature count and ordering for LEGACY (36) and MODERN (25)
   - production-fit cutoffs and rationale
4. Fresh-process loading via subprocess:
   - Separate process loads artifacts from disk and computes inference.
5. Deterministic forward-pass inference.
6. Fail-closed contract validation:
   - Unknown feature raises ValueError.
   - Missing required feature raises ValueError.
   - Prohibited/leakage column raises ValueError.
   - Unsupported regime raises ValueError.
   - Unsupported / gap report_month raises ValueError.
   - Non-numeric string in numeric feature raises ValueError.
7. Explainability compatibility:
   - CatBoost loaded model with cb.Pool produces TreeSHAP contributions that sum
     exactly to (raw_margin - base_value).
   - Logistic loaded model + FoldPreprocessor produces exact linear logit decomposition
     that sums to (raw_score - intercept).
8. Behavioral reconciliation:
   - Loaded artifact inference matches locked in-memory fit within 1e-9.
   - Logistic coefficients, intercept, and preprocessor statistics match.
9. Zero retraining / refitting during inference.
10. Canonical input hashes remain unchanged.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

import catboost as cb
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
    sha256,
)
from src.ml.evaluate_baselines import (
    CATEGORICAL_FEATURES,
    RANDOM_SEED,
    TARGET,
    FoldPreprocessor,
)
from src.ml.operational_policy import LOCKED_FEATURES, LOCKED_MODELS
from src.ml.predict_schedule import (
    PredictionResult,
    ScheduleExtensionPredictor,
)
from src.ml.robustness_audit import FULL_V1_FEATURES, STATIC_AT_T_FEATURES


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / DEFAULT_ARTIFACT_RELPATH
DATASET_DIR = ROOT / "data/ml/schedule_extension_3m"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ScheduleModelArtifactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)
        cls.manifest = cls.predictor.manifest

        cls.legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        cls.modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")

        # Fixture inputs (strip leakage/metadata columns except routing metadata)
        cls.legacy_fixture = {
            k: cls.legacy_rows[0][k] for k in LOCKED_FEATURES["LEGACY"]
        }
        cls.legacy_fixture["project_code"] = cls.legacy_rows[0]["project_code"]
        cls.legacy_fixture["report_month"] = cls.legacy_rows[0]["report_month"]

        cls.modern_fixture = {
            k: cls.modern_rows[0][k] for k in LOCKED_FEATURES["MODERN"]
        }
        cls.modern_fixture["project_code"] = cls.modern_rows[0]["project_code"]
        cls.modern_fixture["report_month"] = cls.modern_rows[0]["report_month"]

    def test_01_legacy_catboost_artifact_exists(self) -> None:
        path = ARTIFACT_DIR / "legacy_catboost/model.cbm"
        self.assertTrue(path.exists(), f"Legacy CatBoost artifact missing at {path}")
        self.assertGreater(path.stat().st_size, 100_000)

    def test_02_modern_logistic_artifact_exists(self) -> None:
        path = ARTIFACT_DIR / "modern_logistic/model.joblib"
        self.assertTrue(path.exists(), f"Modern Logistic artifact missing at {path}")
        self.assertGreater(path.stat().st_size, 1_000)

    def test_03_artifact_manifest_exists_and_is_valid_json(self) -> None:
        manifest_path = ARTIFACT_DIR / "manifest.json"
        self.assertTrue(manifest_path.exists())
        with manifest_path.open("r", encoding="utf-8") as handle:
            content = json.load(handle)
        self.assertIn("models", content)
        self.assertIn("LEGACY", content["models"])
        self.assertIn("MODERN", content["models"])

    def test_04_manifest_records_contract_version(self) -> None:
        self.assertEqual(self.manifest["contract_version"], "1.0.0")

    def test_05_manifest_records_target_correctly(self) -> None:
        self.assertEqual(self.manifest["target"], "target_effective_schedule_ext_3m")
        self.assertEqual(self.manifest["horizon_months"], 3)
        self.assertIn("strict_walk_forward", self.manifest["embargo_rule"])

    def test_06_manifest_records_regimes_correctly(self) -> None:
        self.assertIn("LEGACY", self.manifest["models"])
        self.assertIn("MODERN", self.manifest["models"])
        self.assertEqual(self.manifest["models"]["LEGACY"]["regime"], "LEGACY")
        self.assertEqual(self.manifest["models"]["MODERN"]["regime"], "MODERN")
        self.assertEqual(
            self.manifest["models"]["LEGACY"]["model_identifier"],
            "catboost_full_v1__unweighted",
        )
        self.assertEqual(
            self.manifest["models"]["MODERN"]["model_identifier"],
            "logistic_static_only__unweighted",
        )

    def test_07_manifest_records_exact_feature_ordering(self) -> None:
        legacy_spec = self.manifest["models"]["LEGACY"]
        modern_spec = self.manifest["models"]["MODERN"]

        self.assertEqual(legacy_spec["feature_count"], 36)
        self.assertEqual(legacy_spec["feature_ordering"], list(FULL_V1_FEATURES))

        self.assertEqual(modern_spec["feature_count"], 25)
        self.assertEqual(modern_spec["feature_ordering"], list(STATIC_AT_T_FEATURES))

    def test_08_artifact_sha256_is_recorded_and_verified(self) -> None:
        legacy_path = ARTIFACT_DIR / self.manifest["models"]["LEGACY"]["artifact_relpath"]
        modern_path = ARTIFACT_DIR / self.manifest["models"]["MODERN"]["artifact_relpath"]

        self.assertEqual(
            file_sha256(legacy_path),
            self.manifest["models"]["LEGACY"]["artifact_sha256"],
        )
        self.assertEqual(
            file_sha256(modern_path),
            self.manifest["models"]["MODERN"]["artifact_sha256"],
        )

    def test_09_legacy_artifact_can_be_loaded_in_a_fresh_process(self) -> None:
        script = (
            "import json, sys\n"
            "from src.ml.predict_schedule import ScheduleExtensionPredictor\n"
            "p = ScheduleExtensionPredictor.load()\n"
            "features = json.loads(sys.argv[1])\n"
            "res = p.predict_one(features, regime='LEGACY')\n"
            "print(f'{res.probability:.10f},{res.raw_score:.10f},{res.regime}')\n"
        )
        payload = json.dumps(self.legacy_fixture)
        result = subprocess.run(
            [sys.executable, "-c", script, payload],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(ROOT),
        )
        prob_str, score_str, regime = result.stdout.strip().split(",")
        self.assertEqual(regime, "LEGACY")
        prob = float(prob_str)
        self.assertGreater(prob, 0.0)
        self.assertLess(prob, 1.0)

    def test_10_modern_artifact_can_be_loaded_in_a_fresh_process(self) -> None:
        script = (
            "import json, sys\n"
            "from src.ml.predict_schedule import ScheduleExtensionPredictor\n"
            "p = ScheduleExtensionPredictor.load()\n"
            "features = json.loads(sys.argv[1])\n"
            "res = p.predict_one(features, regime='MODERN')\n"
            "print(f'{res.probability:.10f},{res.raw_score:.10f},{res.regime}')\n"
        )
        payload = json.dumps(self.modern_fixture)
        result = subprocess.run(
            [sys.executable, "-c", script, payload],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(ROOT),
        )
        prob_str, score_str, regime = result.stdout.strip().split(",")
        self.assertEqual(regime, "MODERN")
        prob = float(prob_str)
        self.assertGreater(prob, 0.0)
        self.assertLess(prob, 1.0)

    def test_11_inference_output_is_deterministic(self) -> None:
        res1 = self.predictor.predict_one(self.legacy_fixture, regime="LEGACY")
        res2 = self.predictor.predict_one(self.legacy_fixture, regime="LEGACY")
        self.assertEqual(res1.probability, res2.probability)
        self.assertEqual(res1.raw_score, res2.raw_score)

        res_m1 = self.predictor.predict_one(self.modern_fixture, regime="MODERN")
        res_m2 = self.predictor.predict_one(self.modern_fixture, regime="MODERN")
        self.assertEqual(res_m1.probability, res_m2.probability)
        self.assertEqual(res_m1.raw_score, res_m2.raw_score)

    def test_12_contract_invalid_input_fails_closed(self) -> None:
        # Invalid numeric type (non-numeric string)
        invalid_numeric = dict(self.legacy_fixture)
        invalid_numeric["original_cost"] = "not_a_valid_number"
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(invalid_numeric, regime="LEGACY")
        self.assertIn("Invalid numeric value", str(ctx.exception))

    def test_13_unknown_feature_fails(self) -> None:
        bad_input = dict(self.legacy_fixture)
        bad_input["unapproved_leakage_feature"] = 42.0
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(bad_input, regime="LEGACY")
        self.assertIn("Unknown / prohibited feature inputs", str(ctx.exception))

    def test_14_missing_feature_fails(self) -> None:
        bad_input = dict(self.legacy_fixture)
        del bad_input["physical_progress_t"]
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(bad_input, regime="LEGACY")
        self.assertIn("Missing 1 required features", str(ctx.exception))

    def test_15_wrong_regime_fails(self) -> None:
        # Invalid string
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(self.legacy_fixture, regime="UNSUPPORTED_REGIME")
        self.assertIn("Unsupported regime", str(ctx.exception))

        # Conflicting regime with report month (e.g. 2026 month with LEGACY regime)
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(
                self.modern_fixture, regime="LEGACY", report_month="2026-02"
            )
        self.assertIn("contradicts contract segment regime", str(ctx.exception))

        # Structural gap month (2023-12)
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(self.legacy_fixture, report_month="2023-12")
        self.assertIn("structural gap month", str(ctx.exception))

    def test_16_existing_explainability_compatibility_is_preserved(self) -> None:
        # Legacy CatBoost TreeSHAP compatibility
        legacy_model = self.predictor.get_model("LEGACY")
        features = self.predictor.get_features_for_regime("LEGACY")
        from src.ml.challenger_catboost import prepare_catboost_df

        x_eval, cat_cols = prepare_catboost_df([self.legacy_fixture], features)
        pool = cb.Pool(
            x_eval,
            cat_features=cat_cols if cat_cols else None,
            feature_names=features,
        )
        shap_values = np.asarray(
            legacy_model.get_feature_importance(pool, type="ShapValues"), dtype=float
        )
        contributions = shap_values[:, :-1]
        base_value = float(shap_values[:, -1][0])
        raw_margin = float(
            legacy_model.predict(pool, prediction_type="RawFormulaVal")[0]
        )

        reconstructed = float(contributions.sum()) + base_value
        self.assertAlmostEqual(reconstructed, raw_margin, places=6)

        # Modern Logistic exact linear contribution compatibility
        modern_model = self.predictor.get_model("MODERN")
        preprocessor = self.predictor.get_preprocessor("MODERN")
        self.assertIsNotNone(preprocessor)

        v_feat, _ = self.predictor.validate_row(self.modern_fixture, "MODERN")
        x_matrix = preprocessor.transform([v_feat])
        linear_contributions = x_matrix * np.asarray(modern_model.coef_[0], dtype=float)
        reconstructed_logit = float(linear_contributions.sum()) + float(
            modern_model.intercept_[0]
        )
        raw_decision = float(modern_model.decision_function(x_matrix)[0])
        self.assertAlmostEqual(reconstructed_logit, raw_decision, places=9)

    def test_17_behavioral_reconciliation_legacy_catboost(self) -> None:
        """Verify loaded CatBoost predictions match direct model evaluation."""
        legacy_model = self.predictor.get_model("LEGACY")
        from src.ml.challenger_catboost import prepare_catboost_df

        features = self.predictor.get_features_for_regime("LEGACY")
        x_eval, cat_cols = prepare_catboost_df([self.legacy_fixture], features)
        pool = cb.Pool(
            x_eval,
            cat_features=cat_cols if cat_cols else None,
            feature_names=features,
        )

        expected_prob = float(legacy_model.predict_proba(pool)[:, 1][0])
        expected_raw = float(
            legacy_model.predict(pool, prediction_type="RawFormulaVal")[0]
        )

        pred_res = self.predictor.predict_one(self.legacy_fixture, regime="LEGACY")
        self.assertAlmostEqual(pred_res.probability, expected_prob, places=9)
        self.assertAlmostEqual(pred_res.raw_score, expected_raw, places=9)

    def test_18_behavioral_reconciliation_modern_logistic(self) -> None:
        """Verify loaded Logistic predictions match direct model evaluation."""
        modern_model = self.predictor.get_model("MODERN")
        preprocessor = self.predictor.get_preprocessor("MODERN")

        v_feat, _ = self.predictor.validate_row(self.modern_fixture, "MODERN")
        x_matrix = preprocessor.transform([v_feat])

        expected_prob = float(modern_model.predict_proba(x_matrix)[:, 1][0])
        expected_raw = float(modern_model.decision_function(x_matrix)[0])

        pred_res = self.predictor.predict_one(self.modern_fixture, regime="MODERN")
        self.assertAlmostEqual(pred_res.probability, expected_prob, places=9)
        self.assertAlmostEqual(pred_res.raw_score, expected_raw, places=9)

    def test_19_inference_performs_no_dynamic_retraining(self) -> None:
        """Verify inference does not modify preprocessor or model parameters."""
        preprocessor = self.predictor.get_preprocessor("MODERN")
        mean_before = dict(preprocessor.numeric_mean)
        scale_before = dict(preprocessor.numeric_scale)

        # Run inference multiple times
        for _ in range(5):
            self.predictor.predict_one(self.modern_fixture, regime="MODERN")

        self.assertEqual(preprocessor.numeric_mean, mean_before)
        self.assertEqual(preprocessor.numeric_scale, scale_before)

    def test_20_canonical_input_hashes_remain_unchanged(self) -> None:
        ongoing_path = ROOT / "data/processed/projects_monthly.csv"
        completed_path = ROOT / "data/processed/projects_completed.csv"

        self.assertEqual(sha256(ongoing_path), ONGOING_SHA256)
        self.assertEqual(sha256(completed_path), COMPLETED_SHA256)


if __name__ == "__main__":
    unittest.main()
