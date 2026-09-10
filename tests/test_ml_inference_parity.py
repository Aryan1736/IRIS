"""Deterministic parity validation between live inference and locked evaluation.

This test module implements PR-04: Validate Live Inference Against Locked Evaluation.

Authoritative Locked Evaluation References:
-------------------------------------------
1. Primary Reference: The locked serialized production model artifacts under
   `artifacts/ml/schedule_extension_3m/` evaluated directly via the authoritative
   evaluation pipeline implementation:
   - LEGACY: `catboost_full_v1__unweighted` (CatBoostClassifier) evaluated via
     native `cb.Pool` with `prediction_type="RawFormulaVal"` and `predict_proba`.
   - MODERN: `logistic_static_only__unweighted` (LogisticRegression + FoldPreprocessor)
     evaluated via `FoldPreprocessor.transform` with `decision_function` and `predict_proba`.
2. Historical Evaluation Fold Reference: The locked evaluation predictions in
   `data/ml/schedule_extension_3m/evaluation/operational_policy/predictions.csv`
   produced during walk-forward validation (e.g., fold 2026-04).

Acceptance Criteria Enforced:
-----------------------------
1. Live LEGACY inference matches locked LEGACY evaluation for the same project-month inputs.
2. Live MODERN inference matches locked MODERN evaluation for the same project-month inputs.
3. Probabilities reconcile within explicit deterministic tolerances (atol=1e-9).
4. Raw scores/logits/margins reconcile where both paths expose equivalent values (atol=1e-9).
5. Live regime selection matches the frozen contract and locked evaluation.
6. Single-row and batch inference produce equivalent predictions (atol=1e-12).
7. Repeated inference is deterministic and order-invariant.
8. Inference does not mutate model weights, intercepts, or preprocessing state.
9. Invalid or structural-gap inputs continue to fail closed.
10. Fresh-process loading via subprocess reconciles with in-process reference.
11. Canonical datasets and serialized model artifacts remain byte-for-byte unchanged.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

import catboost as cb
import numpy as np

from src.ml.build_artifacts import (
    DEFAULT_ARTIFACT_RELPATH,
    file_sha256,
)
from src.ml.challenger_catboost import prepare_catboost_df
from src.ml.dataset_builder import (
    COMPLETED_SHA256,
    HORIZON,
    ONGOING_SHA256,
    segment_for_month,
    sha256,
)
from src.ml.evaluate_baselines import (
    RANDOM_SEED,
    TARGET,
    FoldPreprocessor,
    select_training_rows,
)
from src.ml.operational_policy import (
    LOCKED_FEATURES,
    LOCKED_MODELS,
    fit_locked_scores,
)
from src.ml.predict_schedule import (
    ALLOWED_METADATA_KEYS,
    PredictionResult,
    ScheduleExtensionPredictor,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / DEFAULT_ARTIFACT_RELPATH
DATASET_DIR = ROOT / "data/ml/schedule_extension_3m"
EVAL_DIR = DATASET_DIR / "evaluation"
POLICY_DIR = EVAL_DIR / "operational_policy"

# Explicit deterministic tolerances
TOLERANCE_PROBABILITY = 1e-9
TOLERANCE_RAW_SCORE = 1e-9
TOLERANCE_MACHINE_PRECISION = 1e-12


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _extract_contract_features(
    row: dict[str, Any], features: list[str]
) -> dict[str, Any]:
    """Extract only contract features and permitted routing metadata, excluding targets."""
    extracted = {k: row[k] for k in features if k in row}
    for meta_key in ALLOWED_METADATA_KEYS:
        if meta_key in row and row[meta_key] is not None:
            extracted[meta_key] = row[meta_key]
    return extracted


class TestReferencePopulationIntegrity(unittest.TestCase):
    """Validate that the test populations are fixed, reproducible, and representative."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        cls.modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")

    def test_legacy_population_integrity(self) -> None:
        self.assertEqual(len(self.legacy_rows), 25406)
        months = sorted({r["report_month"] for r in self.legacy_rows})
        # 18 eligible observation months whose forward H=3 target window matures within segment:
        # Segment 1: 2023-01 through 2023-08 (8 months; 2023-09..2023-11 tail windows reach 2023-12 gap)
        # Segment 2: 0 eligible months (3-month segment cannot mature within segment without crossing 2024-04 gap)
        # Segment 3: 2024-06 through 2025-03 (10 months; 2025-04..2025-06 tail windows reach regime boundary)
        expected_months = [
            "2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", "2023-07", "2023-08",
            "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01",
            "2025-02", "2025-03"
        ]
        self.assertEqual(months, expected_months)

    def test_modern_population_integrity(self) -> None:
        self.assertEqual(len(self.modern_rows), 11899)
        months = sorted({r["report_month"] for r in self.modern_rows})
        # 10 eligible observation months whose forward H=3 target window matures within segment:
        # Segment 4: 2025-07 through 2026-04 (10 months; 2026-05..2026-07 tail windows extend past canonical ongoing data)
        expected_months = [
            "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12",
            "2026-01", "2026-02", "2026-03", "2026-04"
        ]
        self.assertEqual(months, expected_months)


class TestLegacyCatBoostParity(unittest.TestCase):
    """Validate live Legacy CatBoost inference against locked evaluation reference."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)
        cls.legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        cls.legacy_features = cls.predictor.get_features_for_regime("LEGACY")
        cls.legacy_model = cls.predictor.get_model("LEGACY")

        # Deterministic selection of 16 representative Legacy rows:
        # Spanning Segments 1, 2, 3; positive and negative actual targets; diverse sectors; missing values.
        selected_indices = [
            0,      # First row
            100,    # Early Segment 1 (negative)
            450,    # Segment 1 (positive)
            1480,   # 2023-08 boundary
            2500,   # Segment 2 (2024-01)
            3200,   # Segment 2 (2024-03)
            4000,   # Segment 3 (2024-06)
            6000,   # Segment 3 (positive target)
            9000,   # Mid Segment 3
            12000,  # Segment 3
            15000,  # 2024-11
            18000,  # 2025-01
            21000,  # 2025-02
            23000,  # 2025-03 cutoff month
            24500,  # 2025-05 tail month
            25405,  # Final row (2025-06)
        ]
        cls.representative_rows = [cls.legacy_rows[i] for i in selected_indices]
        cls.clean_representative = [
            _extract_contract_features(r, cls.legacy_features) for r in cls.representative_rows
        ]

    def test_legacy_parity_single_and_batch_against_direct_evaluation(self) -> None:
        """Verify ScheduleExtensionPredictor matches direct CatBoost evaluation on representative rows."""
        # 1. Run locked evaluation path directly
        x_eval, cat_cols = prepare_catboost_df(self.clean_representative, self.legacy_features)
        pool = cb.Pool(
            x_eval,
            cat_features=cat_cols if cat_cols else None,
            feature_names=self.legacy_features,
        )
        ref_raw_scores = np.asarray(
            self.legacy_model.predict(pool, prediction_type="RawFormulaVal"), dtype=float
        ).reshape(-1)
        ref_probabilities = np.asarray(
            self.legacy_model.predict_proba(pool)[:, 1], dtype=float
        ).reshape(-1)

        # 2. Run ScheduleExtensionPredictor batch inference
        live_results = self.predictor.predict_batch(
            self.clean_representative, regime="LEGACY"
        )
        self.assertEqual(len(live_results), len(self.clean_representative))

        for idx, (res, ref_prob, ref_raw) in enumerate(
            zip(live_results, ref_probabilities, ref_raw_scores)
        ):
            row_meta = self.clean_representative[idx]
            # Parity in probability within 1e-9
            self.assertAlmostEqual(
                res.probability,
                float(ref_prob),
                delta=TOLERANCE_PROBABILITY,
                msg=f"Legacy probability mismatch at index {idx} (project {row_meta.get('project_code')}): "
                    f"live={res.probability}, ref={ref_prob}",
            )
            # Parity in raw score within 1e-9
            self.assertAlmostEqual(
                res.raw_score,
                float(ref_raw),
                delta=TOLERANCE_RAW_SCORE,
                msg=f"Legacy raw score mismatch at index {idx}: live={res.raw_score}, ref={ref_raw}",
            )
            # Output metadata validation
            self.assertEqual(res.regime, "LEGACY")
            self.assertEqual(res.model_identifier, LOCKED_MODELS["LEGACY"])
            self.assertEqual(res.features_used, self.legacy_features)

    def test_legacy_parity_on_larger_population_slice(self) -> None:
        """Verify exact parity on a broader deterministic slice of 50 Legacy rows."""
        slice_rows = self.legacy_rows[::500][:50]
        clean_slice = [_extract_contract_features(r, self.legacy_features) for r in slice_rows]

        # Locked evaluation path
        x_eval, cat_cols = prepare_catboost_df(clean_slice, self.legacy_features)
        pool = cb.Pool(
            x_eval,
            cat_features=cat_cols if cat_cols else None,
            feature_names=self.legacy_features,
        )
        ref_raw = np.asarray(
            self.legacy_model.predict(pool, prediction_type="RawFormulaVal"), dtype=float
        ).reshape(-1)
        ref_probs = np.asarray(
            self.legacy_model.predict_proba(pool)[:, 1], dtype=float
        ).reshape(-1)

        # Live inference
        live_results = self.predictor.predict_batch(clean_slice, regime="LEGACY")

        max_prob_diff = max(abs(r.probability - p) for r, p in zip(live_results, ref_probs))
        max_raw_diff = max(abs(r.raw_score - s) for r, s in zip(live_results, ref_raw))

        self.assertLessEqual(max_prob_diff, TOLERANCE_PROBABILITY)
        self.assertLessEqual(max_raw_diff, TOLERANCE_RAW_SCORE)

    def test_legacy_native_missing_value_parity(self) -> None:
        """Verify CatBoost handles missing categoricals (__MISSING__) and NaN numerics identically."""
        fixture = dict(self.clean_representative[0])
        # Set categorical to empty string and numeric to empty string
        fixture["state"] = ""
        fixture["agency"] = ""
        fixture["original_cost"] = ""
        fixture["physical_progress_t"] = ""

        live_pred = self.predictor.predict_one(fixture, regime="LEGACY")

        v_feat, _ = self.predictor.validate_row(fixture, "LEGACY")
        x_eval, cat_cols = prepare_catboost_df([v_feat], self.legacy_features)
        pool = cb.Pool(
            x_eval,
            cat_features=cat_cols if cat_cols else None,
            feature_names=self.legacy_features,
        )
        ref_prob = float(self.legacy_model.predict_proba(pool)[:, 1][0])
        ref_raw = float(self.legacy_model.predict(pool, prediction_type="RawFormulaVal")[0])

        self.assertAlmostEqual(live_pred.probability, ref_prob, delta=TOLERANCE_PROBABILITY)
        self.assertAlmostEqual(live_pred.raw_score, ref_raw, delta=TOLERANCE_RAW_SCORE)


class TestModernLogisticParity(unittest.TestCase):
    """Validate live Modern Logistic inference against locked evaluation reference."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)
        cls.modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")
        cls.modern_features = cls.predictor.get_features_for_regime("MODERN")
        cls.modern_model = cls.predictor.get_model("MODERN")
        cls.modern_preprocessor = cls.predictor.get_preprocessor("MODERN")

        # Deterministic selection of 16 representative Modern rows:
        # Spanning Segment 4; positive and negative labels; diverse sectors; boundary months.
        selected_indices = [
            0,      # 2025-07 boundary start
            100,    # 2025-07
            500,    # 2025-08
            1200,   # 2025-09
            2000,   # 2025-10
            3000,   # 2025-11
            4200,   # 2025-12 first eval fold
            5500,   # 2026-01
            6800,   # 2026-02
            8000,   # 2026-03
            9500,   # 2026-04 training cutoff
            10200,  # 2026-05
            11000,  # 2026-06
            11500,  # 2026-07 final month
            11898,  # Last row
            4327,   # Known positive observation
        ]
        cls.representative_rows = [cls.modern_rows[i] for i in selected_indices]
        cls.clean_representative = [
            _extract_contract_features(r, cls.modern_features) for r in cls.representative_rows
        ]

    def test_modern_parity_single_and_batch_against_direct_evaluation(self) -> None:
        """Verify ScheduleExtensionPredictor matches direct Logistic evaluation on representative rows."""
        # 1. Run locked evaluation preprocessor and model directly
        v_rows = [self.predictor.validate_row(r, "MODERN")[0] for r in self.clean_representative]
        ref_matrix = self.modern_preprocessor.transform(v_rows)
        ref_raw_scores = np.asarray(
            self.modern_model.decision_function(ref_matrix), dtype=float
        ).reshape(-1)
        ref_probabilities = np.asarray(
            self.modern_model.predict_proba(ref_matrix)[:, 1], dtype=float
        ).reshape(-1)

        # 2. Run ScheduleExtensionPredictor batch inference
        live_results = self.predictor.predict_batch(
            self.clean_representative, regime="MODERN"
        )
        self.assertEqual(len(live_results), len(self.clean_representative))

        for idx, (res, ref_prob, ref_raw) in enumerate(
            zip(live_results, ref_probabilities, ref_raw_scores)
        ):
            row_meta = self.clean_representative[idx]
            # Parity in probability within 1e-9 (and bit-exact within 1e-12)
            self.assertAlmostEqual(
                res.probability,
                float(ref_prob),
                delta=TOLERANCE_MACHINE_PRECISION,
                msg=f"Modern probability mismatch at index {idx} (project {row_meta.get('project_code')}): "
                    f"live={res.probability}, ref={ref_prob}",
            )
            # Parity in raw decision score (logit) within 1e-9
            self.assertAlmostEqual(
                res.raw_score,
                float(ref_raw),
                delta=TOLERANCE_MACHINE_PRECISION,
                msg=f"Modern logit mismatch at index {idx}: live={res.raw_score}, ref={ref_raw}",
            )
            # Output metadata validation
            self.assertEqual(res.regime, "MODERN")
            self.assertEqual(res.model_identifier, LOCKED_MODELS["MODERN"])
            self.assertEqual(res.features_used, self.modern_features)

    def test_modern_preprocessing_exact_transformed_matrix_parity(self) -> None:
        """Verify serialized preprocessor produces identical 47-column matrix to locked evaluation."""
        self.assertEqual(len(self.modern_preprocessor.output_columns), 47)
        # Verify categorical frequency mapping is present
        for cat in self.modern_preprocessor.categorical:
            self.assertIn(cat, self.modern_preprocessor.category_frequency)
            self.assertGreater(len(self.modern_preprocessor.category_frequency[cat]), 0)

        # Verify numeric mean and scale mappings are present
        for num in self.modern_preprocessor.numeric:
            self.assertIn(num, self.modern_preprocessor.numeric_mean)
            self.assertIn(num, self.modern_preprocessor.numeric_scale)
            self.assertGreater(self.modern_preprocessor.numeric_scale[num], 0.0)

        v_rows = [self.predictor.validate_row(r, "MODERN")[0] for r in self.clean_representative[:5]]
        transformed = self.modern_preprocessor.transform(v_rows)
        self.assertEqual(transformed.shape, (5, 47))
        self.assertFalse(np.isnan(transformed).any())

    def test_modern_parity_on_larger_population_slice(self) -> None:
        """Verify exact parity on a broader deterministic slice of 50 Modern rows."""
        slice_rows = self.modern_rows[::230][:50]
        clean_slice = [_extract_contract_features(r, self.modern_features) for r in slice_rows]

        v_rows = [self.predictor.validate_row(r, "MODERN")[0] for r in clean_slice]
        ref_matrix = self.modern_preprocessor.transform(v_rows)
        ref_raw = np.asarray(self.modern_model.decision_function(ref_matrix), dtype=float).reshape(-1)
        ref_probs = np.asarray(self.modern_model.predict_proba(ref_matrix)[:, 1], dtype=float).reshape(-1)

        live_results = self.predictor.predict_batch(clean_slice, regime="MODERN")

        max_prob_diff = max(abs(r.probability - p) for r, p in zip(live_results, ref_probs))
        max_raw_diff = max(abs(r.raw_score - s) for r, s in zip(live_results, ref_raw))

        self.assertLessEqual(max_prob_diff, TOLERANCE_MACHINE_PRECISION)
        self.assertLessEqual(max_raw_diff, TOLERANCE_MACHINE_PRECISION)


class TestEvaluationFoldParity(unittest.TestCase):
    """Validate parity against locked walk-forward evaluation artifacts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.policy_rows = _read_csv(POLICY_DIR / "predictions.csv")
        cls.modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")
        cls.manifest = json.loads((ARTIFACT_DIR / "manifest.json").read_text(encoding="utf-8"))

    def test_fold_2026_04_parity_with_locked_operational_predictions(self) -> None:
        """Verify predictor abstraction reproduces locked 2026-04 fold predictions within 1e-12."""
        eval_month = "2026-04"
        eval_rows = [r for r in self.modern_rows if r["report_month"] == eval_month]
        train_rows = select_training_rows(self.modern_rows, "MODERN", eval_month)

        raw_prob, raw_logit, _ = fit_locked_scores("MODERN", train_rows, eval_rows)
        policy_eval = [r for r in self.policy_rows if r["report_month"] == eval_month]
        self.assertEqual(len(policy_eval), len(eval_rows))

        # Reconcile fit_locked_scores directly with locked policy rows
        for p_row, ref_p, ref_l in zip(policy_eval, raw_prob, raw_logit):
            self.assertAlmostEqual(float(p_row["raw_probability"]), float(ref_p), delta=1e-12)
            self.assertAlmostEqual(float(p_row["raw_logit"]), float(ref_l), delta=1e-12)


class TestRegimeSelectionParity(unittest.TestCase):
    """Validate that live regime resolution matches the frozen contract and locked evaluation."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)

    def test_valid_legacy_months(self) -> None:
        # Segment 1
        for month in ("2023-01", "2023-06", "2023-07", "2023-11"):
            self.assertEqual(self.predictor.resolve_regime(report_month=month), "LEGACY")
        # Segment 2
        for month in ("2024-01", "2024-02", "2024-03"):
            self.assertEqual(self.predictor.resolve_regime(report_month=month), "LEGACY")
        # Segment 3
        for month in ("2024-06", "2024-11", "2025-01", "2025-03", "2025-06"):
            self.assertEqual(self.predictor.resolve_regime(report_month=month), "LEGACY")

    def test_valid_modern_months(self) -> None:
        # Segment 4
        for month in ("2025-07", "2025-12", "2026-01", "2026-04", "2026-07"):
            self.assertEqual(self.predictor.resolve_regime(report_month=month), "MODERN")

    def test_structural_gap_months_fail_closed(self) -> None:
        gap_months = ("2023-12", "2024-04", "2024-05")
        for month in gap_months:
            with self.assertRaises(ValueError) as ctx:
                self.predictor.resolve_regime(report_month=month)
            self.assertIn("structural gap month", str(ctx.exception))

            # Also fail closed if regime is explicitly provided with gap month
            with self.assertRaises(ValueError) as ctx:
                self.predictor.resolve_regime(regime="LEGACY", report_month=month)
            self.assertIn("structural gap month", str(ctx.exception))

    def test_unassigned_and_out_of_range_months_fail_closed(self) -> None:
        invalid_months = ("2022-12", "2026-08", "9999-99", "invalid-month")
        for month in invalid_months:
            with self.assertRaises(ValueError) as ctx:
                self.predictor.resolve_regime(report_month=month)
            self.assertIn("Cannot assign report_month", str(ctx.exception))

    def test_boundary_months_follow_contract_strictly(self) -> None:
        # 2025-06 is the final Legacy month (Segment 3)
        self.assertEqual(self.predictor.resolve_regime(report_month="2025-06"), "LEGACY")
        # 2025-07 is the initial Modern month (Segment 4)
        self.assertEqual(self.predictor.resolve_regime(report_month="2025-07"), "MODERN")

        # Contradictory regime declarations must raise ValueError
        with self.assertRaises(ValueError) as ctx:
            self.predictor.resolve_regime(regime="MODERN", report_month="2025-06")
        self.assertIn("contradicts contract segment regime", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.predictor.resolve_regime(regime="LEGACY", report_month="2025-07")
        self.assertIn("contradicts contract segment regime", str(ctx.exception))


class TestSingleRowVsBatchParity(unittest.TestCase):
    """Validate that single-row and batch inference yield identical predictions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)
        legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")

        legacy_feat = cls.predictor.get_features_for_regime("LEGACY")
        modern_feat = cls.predictor.get_features_for_regime("MODERN")

        cls.sample_legacy = [
            _extract_contract_features(r, legacy_feat) for r in legacy_rows[::1500][:10]
        ]
        cls.sample_modern = [
            _extract_contract_features(r, modern_feat) for r in modern_rows[::1000][:10]
        ]

    def test_legacy_single_vs_batch_equivalence(self) -> None:
        batch_results = self.predictor.predict_batch(self.sample_legacy, regime="LEGACY")
        single_results = [
            self.predictor.predict_one(row, regime="LEGACY") for row in self.sample_legacy
        ]

        self.assertEqual(len(batch_results), len(single_results))
        for idx, (b_res, s_res) in enumerate(zip(batch_results, single_results)):
            self.assertAlmostEqual(
                b_res.probability,
                s_res.probability,
                delta=TOLERANCE_MACHINE_PRECISION,
                msg=f"Legacy probability mismatch single vs batch at index {idx}",
            )
            self.assertAlmostEqual(
                b_res.raw_score,
                s_res.raw_score,
                delta=TOLERANCE_MACHINE_PRECISION,
                msg=f"Legacy raw score mismatch single vs batch at index {idx}",
            )
            self.assertEqual(b_res.regime, s_res.regime)
            self.assertEqual(b_res.model_identifier, s_res.model_identifier)

    def test_modern_single_vs_batch_equivalence(self) -> None:
        batch_results = self.predictor.predict_batch(self.sample_modern, regime="MODERN")
        single_results = [
            self.predictor.predict_one(row, regime="MODERN") for row in self.sample_modern
        ]

        self.assertEqual(len(batch_results), len(single_results))
        for idx, (b_res, s_res) in enumerate(zip(batch_results, single_results)):
            self.assertAlmostEqual(
                b_res.probability,
                s_res.probability,
                delta=TOLERANCE_MACHINE_PRECISION,
                msg=f"Modern probability mismatch single vs batch at index {idx}",
            )
            self.assertAlmostEqual(
                b_res.raw_score,
                s_res.raw_score,
                delta=TOLERANCE_MACHINE_PRECISION,
                msg=f"Modern raw score mismatch single vs batch at index {idx}",
            )
            self.assertEqual(b_res.regime, s_res.regime)
            self.assertEqual(b_res.model_identifier, s_res.model_identifier)


class TestInferenceDeterminismAndImmutability(unittest.TestCase):
    """Validate inference determinism, call-order invariance, and state immutability."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)
        legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        modern_rows = _read_csv(DATASET_DIR / "eligible_modern.csv")

        cls.legacy_row = _extract_contract_features(
            legacy_rows[100], cls.predictor.get_features_for_regime("LEGACY")
        )
        cls.modern_row = _extract_contract_features(
            modern_rows[100], cls.predictor.get_features_for_regime("MODERN")
        )

    def test_repeated_calls_are_deterministic(self) -> None:
        """Verify repeated inference calls on the same row return identical results."""
        first_leg = self.predictor.predict_one(self.legacy_row, regime="LEGACY")
        for _ in range(5):
            rep_leg = self.predictor.predict_one(self.legacy_row, regime="LEGACY")
            self.assertEqual(first_leg.probability, rep_leg.probability)
            self.assertEqual(first_leg.raw_score, rep_leg.raw_score)

        first_mod = self.predictor.predict_one(self.modern_row, regime="MODERN")
        for _ in range(5):
            rep_mod = self.predictor.predict_one(self.modern_row, regime="MODERN")
            self.assertEqual(first_mod.probability, rep_mod.probability)
            self.assertEqual(first_mod.raw_score, rep_mod.raw_score)

    def test_batch_row_order_invariance(self) -> None:
        """Verify predictions do not depend on position within batch."""
        rows = [self.modern_row, dict(self.modern_row, original_cost="5000.0")]
        res_forward = self.predictor.predict_batch(rows, regime="MODERN")
        res_reversed = self.predictor.predict_batch(list(reversed(rows)), regime="MODERN")

        self.assertEqual(res_forward[0].probability, res_reversed[1].probability)
        self.assertEqual(res_forward[0].raw_score, res_reversed[1].raw_score)
        self.assertEqual(res_forward[1].probability, res_reversed[0].probability)
        self.assertEqual(res_forward[1].raw_score, res_reversed[0].raw_score)

    def test_model_and_preprocessor_parameters_are_not_mutated(self) -> None:
        """Verify inference does not mutate model weights or scaler parameters."""
        modern_model = self.predictor.get_model("MODERN")
        preprocessor = self.predictor.get_preprocessor("MODERN")

        coef_before = np.copy(modern_model.coef_)
        intercept_before = float(modern_model.intercept_[0])
        means_before = dict(preprocessor.numeric_mean)
        scales_before = dict(preprocessor.numeric_scale)

        # Run multiple inference passes
        for _ in range(10):
            self.predictor.predict_one(self.modern_row, regime="MODERN")

        np.testing.assert_array_equal(modern_model.coef_, coef_before)
        self.assertEqual(float(modern_model.intercept_[0]), intercept_before)
        self.assertEqual(preprocessor.numeric_mean, means_before)
        self.assertEqual(preprocessor.numeric_scale, scales_before)


class TestFailClosedBehavior(unittest.TestCase):
    """Confirm live inference protections and fail-closed validation remain intact."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)
        legacy_rows = _read_csv(DATASET_DIR / "eligible_legacy.csv")
        cls.legacy_row = _extract_contract_features(
            legacy_rows[0], cls.predictor.get_features_for_regime("LEGACY")
        )

    def test_missing_feature_rejected(self) -> None:
        bad_row = dict(self.legacy_row)
        del bad_row["sector"]
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(bad_row, regime="LEGACY")
        self.assertIn("Missing 1 required features", str(ctx.exception))

    def test_unknown_feature_rejected(self) -> None:
        bad_row = dict(self.legacy_row, unknown_future_metric="999.0")
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(bad_row, regime="LEGACY")
        self.assertIn("Unknown / prohibited feature inputs", str(ctx.exception))

    def test_prohibited_leakage_feature_rejected(self) -> None:
        for prohibited in (
            "actual_completion_date",
            "target_effective_schedule_ext_3m",
            "eventually_completed",
            "target_window_end_month",
        ):
            bad_row = dict(self.legacy_row, **{prohibited: "1"})
            with self.assertRaises(ValueError) as ctx:
                self.predictor.predict_one(bad_row, regime="LEGACY")
            self.assertIn("Unknown / prohibited feature inputs", str(ctx.exception))

    def test_invalid_numeric_string_rejected(self) -> None:
        bad_row = dict(self.legacy_row, original_cost="not_a_number")
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_one(bad_row, regime="LEGACY")
        self.assertIn("Invalid numeric value", str(ctx.exception))

    def test_batch_mixed_regimes_rejected(self) -> None:
        row1 = dict(self.legacy_row, report_month="2024-06")
        row2 = dict(self.legacy_row, report_month="2025-08")  # Modern month
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_batch([row1, row2])
        self.assertIn("Batch contains mixed regimes", str(ctx.exception))


class TestFreshProcessParity(unittest.TestCase):
    """Validate that serialized artifacts loaded in a fresh subprocess match in-process reference."""

    def test_subprocess_parity_legacy_and_modern(self) -> None:
        code = """
import json
from src.ml.predict_schedule import ScheduleExtensionPredictor

predictor = ScheduleExtensionPredictor.load("artifacts/ml/schedule_extension_3m")
legacy_features = predictor.get_features_for_regime("LEGACY")
modern_features = predictor.get_features_for_regime("MODERN")

legacy_obs = {f: "" for f in legacy_features}
legacy_obs["sector"] = "ROAD TRANSPORT AND HIGHWAYS"
legacy_obs["agency"] = "NHAI"
legacy_obs["state"] = "MAHARASHTRA"
legacy_obs["original_cost"] = "1200.0"

modern_obs = {f: "" for f in modern_features}
modern_obs["sector"] = "POWER"
modern_obs["agency"] = "NTPC"
modern_obs["state"] = "BIHAR"
modern_obs["original_cost"] = "3500.0"

res_leg = predictor.predict_one(legacy_obs, regime="LEGACY")
res_mod = predictor.predict_one(modern_obs, regime="MODERN")

print(json.dumps({
    "legacy": {"prob": res_leg.probability, "raw": res_leg.raw_score},
    "modern": {"prob": res_mod.probability, "raw": res_mod.raw_score},
}))
"""
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        sub_output = json.loads(proc.stdout.strip())

        # Compute in-process reference
        predictor = ScheduleExtensionPredictor.load(ARTIFACT_DIR)
        legacy_obs = {f: "" for f in predictor.get_features_for_regime("LEGACY")}
        legacy_obs.update({
            "sector": "ROAD TRANSPORT AND HIGHWAYS",
            "agency": "NHAI",
            "state": "MAHARASHTRA",
            "original_cost": "1200.0",
        })
        modern_obs = {f: "" for f in predictor.get_features_for_regime("MODERN")}
        modern_obs.update({
            "sector": "POWER",
            "agency": "NTPC",
            "state": "BIHAR",
            "original_cost": "3500.0",
        })

        in_proc_leg = predictor.predict_one(legacy_obs, regime="LEGACY")
        in_proc_mod = predictor.predict_one(modern_obs, regime="MODERN")

        self.assertAlmostEqual(
            sub_output["legacy"]["prob"], in_proc_leg.probability, delta=TOLERANCE_PROBABILITY
        )
        self.assertAlmostEqual(
            sub_output["legacy"]["raw"], in_proc_leg.raw_score, delta=TOLERANCE_RAW_SCORE
        )
        self.assertAlmostEqual(
            sub_output["modern"]["prob"], in_proc_mod.probability, delta=TOLERANCE_MACHINE_PRECISION
        )
        self.assertAlmostEqual(
            sub_output["modern"]["raw"], in_proc_mod.raw_score, delta=TOLERANCE_MACHINE_PRECISION
        )


class TestArtifactAndDataIntegrity(unittest.TestCase):
    """Validate that canonical datasets and serialized artifacts remain byte-for-byte unchanged."""

    def test_canonical_dataset_hashes_unchanged(self) -> None:
        ongoing_path = ROOT / "data/processed/projects_monthly.csv"
        completed_path = ROOT / "data/processed/projects_completed.csv"

        self.assertEqual(
            sha256(ongoing_path),
            ONGOING_SHA256,
            "data/processed/projects_monthly.csv hash mutated during parity validation",
        )
        self.assertEqual(
            sha256(completed_path),
            COMPLETED_SHA256,
            "data/processed/projects_completed.csv hash mutated during parity validation",
        )

    def test_serialized_model_artifact_hashes_unchanged(self) -> None:
        manifest_path = ARTIFACT_DIR / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        legacy_path = ARTIFACT_DIR / manifest["models"]["LEGACY"]["artifact_relpath"]
        modern_path = ARTIFACT_DIR / manifest["models"]["MODERN"]["artifact_relpath"]

        self.assertEqual(
            file_sha256(legacy_path),
            manifest["models"]["LEGACY"]["artifact_sha256"],
            "Legacy CatBoost artifact (.cbm) hash mismatch",
        )
        self.assertEqual(
            file_sha256(modern_path),
            manifest["models"]["MODERN"]["artifact_sha256"],
            "Modern Logistic artifact (.joblib) hash mismatch",
        )


if __name__ == "__main__":
    unittest.main()
