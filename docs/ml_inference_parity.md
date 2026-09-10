# Live Inference Parity Validation Guide

## 1. Overview & Objective

This document defines the deterministic parity validation between the live inference engine (`ScheduleExtensionPredictor` in `src/ml/predict_schedule.py` using serialized artifacts under `artifacts/ml/schedule_extension_3m/`) and the authoritative locked evaluation references.

The purpose of PR-04 is to prove that:

$$\text{live inference prediction} \equiv \text{locked evaluation prediction}$$

for the exact same project-month observation inputs under explicit numerical tolerances, without training any new model, modifying canonical datasets, tuning hyperparameters, or altering the frozen ML data contract.

---

## 2. Authoritative Locked Evaluation References

The repository establishes two authoritative evaluation references:

### Reference 1: Primary Serialized Production Model & Direct Evaluation Pipeline
- **Legacy Regime (`LEGACY`)**:
  - **Model Winner**: `catboost_full_v1__unweighted` (`CatBoostClassifier`).
  - **Training Subset**: All matured historical observations up to cutoff $T=\text{2025-03}$ (25,406 observations).
  - **Direct Evaluation Reference**: Raw feature formatting via `prepare_catboost_df` from `src.ml.challenger_catboost`, conversion into native `cb.Pool` preserving string categoricals (`sector`, `agency`, `state`) with `__MISSING__` sentinels and `NaN` numerics, followed by `predict(prediction_type="RawFormulaVal")` and `predict_proba`.
- **Modern Regime (`MODERN`)**:
  - **Model Winner**: `logistic_static_only__unweighted` (`LogisticRegression` with `FoldPreprocessor`).
  - **Training Subset**: All matured historical observations up to cutoff $T=\text{2026-04}$ (11,899 observations).
  - **Direct Evaluation Reference**: 47-dimension training frequency and standardization transformation via `FoldPreprocessor.transform` from `src.ml.evaluate_baselines`, followed by `LogisticRegression.decision_function` and `predict_proba`.

### Reference 2: Historical Walk-Forward Evaluation Folds
- **Evaluation Artifact**: `data/ml/schedule_extension_3m/evaluation/operational_policy/predictions.csv` (25,189 observations across 17 evaluation origins: 12 Legacy, 5 Modern).
- **Validation Role**: Validates that when `ScheduleExtensionPredictor` is configured for any walk-forward evaluation fold (e.g. Modern `2026-04`), its predictions match `raw_probability` and `raw_logit` in the locked evaluation artifact within machine precision ($10^{-12}$).

---

## 3. Compared Outputs & Explicit Numerical Tolerances

The parity suite compares the following outputs for identical input rows:

| Output | Type | Semantic Meaning | Tolerance | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `probability` | `float` | Predicted probability of 3-month schedule extension ($P \in [0, 1]$) | $\text{atol} = 10^{-9}$ | Exact mathematical equivalence across serialization and inference boundaries. |
| `raw_score` | `float` | Raw decision margin: CatBoost raw margin (Legacy) or logit (Modern) | $\text{atol} = 10^{-9}$ | Exact raw score reconciliation before sigmoid / probability transformation. |
| `regime` | `str` | Resolved regime identifier (`LEGACY` or `MODERN`) | Exact (`==`) | Strict deterministic adherence to frozen contract continuous segments. |
| `model_identifier` | `str` | Authoritative model identity string | Exact (`==`) | Must match `LOCKED_MODELS` exactly (`catboost_full_v1__unweighted` / `logistic_static_only__unweighted`). |
| `features_used` | `list[str]` | Ordered list of feature names used | Exact (`==`) | Exact 36-feature (Legacy) and 25-feature (Modern) contract ordering. |

---

## 4. Representative Population Selection

Deterministic, reproducible row selections from `eligible_legacy.csv` and `eligible_modern.csv` are used for validation:

1. **Legacy Representative Set (16 rows)**:
   - Spans Segments 1, 2, and 3 (`2023-01` through `2025-06`).
   - Includes both positive ($Y=1$) and negative ($Y=0$) actual target events.
   - Covers diverse sectors: Roads, Railways, Power, Coal, Petroleum, Atomic Energy.
   - Includes rows with source-missing categoricals and missing numerics to exercise `__MISSING__` and `NaN` handling.
2. **Modern Representative Set (16 rows)**:
   - Spans Segment 4 (`2025-07` through `2026-07`).
   - Includes evaluation fold origins (`2025-12` through `2026-04`).
   - Includes positive and negative target events.
   - Exercises `FoldPreprocessor` frequency encoding, standardization, and missingness indicators.
3. **Population Slices (50 rows per regime)**:
   - Strided deterministic samples (`[::500]` for Legacy, `[::230]` for Modern) testing large-scale batch reconciliation.

---

## 5. Single-Row vs Batch Equivalence & Determinism

1. **Batch Equivalence**:
   $$\text{predict\_one}(x_i) \equiv \text{predict\_batch}([x_1, \dots, x_N])[i]$$
   Reconciles within $\text{atol} = 10^{-12}$ (machine precision).
2. **Call-Order Invariance**:
   Predictions for observation $x_i$ are invariant under arbitrary permutations of the input batch.
3. **Parameter Immutability**:
   Inference is strictly stateless. Preprocessor statistics (`numeric_mean`, `numeric_scale`, `category_frequency`) and model weights/intercepts do not mutate across repeated inference calls.
4. **Fresh-Process Parity**:
   Loading serialized artifacts from disk in an isolated Python subprocess produces predictions identical to in-process evaluation within $10^{-9}$.

---

## 6. Meaning of a Parity Failure

A test failure in `tests/test_ml_inference_parity.py` indicates one of the following critical defects:

1. **Model Divergence**: The serialized artifact weights do not match the locked evaluation training fold, or model hyperparameter drift occurred.
2. **Preprocessing Incompatibility**: Feature scaling, frequency encoding, or missingness indicators in the inference path diverged from training-time preprocessing.
3. **Feature Misalignment**: The column order or names passed into the CatBoost `Pool` or Logistic matrix do not match the locked feature contract.
4. **Regime Leakage**: An observation was routed to the wrong model family, crossed a continuous segment boundary, or accepted an unassigned structural gap month.
5. **Mutation / Dynamic Retraining**: Inference modified internal state or fitted statistics on incoming request payloads.

Any parity failure blocks deployment and requires immediate investigation before serving live predictions.
