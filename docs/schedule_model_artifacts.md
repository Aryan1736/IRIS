# Schedule Model Artifacts & Reusable Inference Guide

## Overview

This document describes the serialized, versioned model artifacts and reusable inference abstraction for the IRIS 3-month schedule-extension prediction pipeline (`target_effective_schedule_ext_3m`).

The implementation turns the locked schedule-extension models into portable, deterministic model artifacts that can be loaded in fresh processes for forward-pass inference without modifying canonical datasets, refitting models, recalculating threshold policies, or altering the existing SQLite serving layer.

---

## Authoritative Model Decisions & Parameters

The locked model decisions are regime-specific:

### 1. Legacy Regime
- **Model Winner**: `catboost_full_v1__unweighted`
- **Model Family**: CatBoost Classifier (`CatBoostClassifier`)
- **Target**: `target_effective_schedule_ext_3m`
- **Horizon ($H$)**: 3 months within continuous segment
- **Embargo**: Strict walk-forward ($T + 3 < E$)
- **Feature Set**: `FULL_V1_FEATURES` (36 features):
  - 3 static categoricals: `sector`, `agency`, `state`
  - 6 static cost/financial features: `original_cost`, `revised_cost_t`, `cumulative_expenditure_t`, `expenditure_to_original_cost_ratio`, `revised_to_original_cost_ratio`, `cost_has_been_revised`
  - 6 schedule features: `project_age_months`, `months_to_original_schedule`, `months_to_effective_schedule`, `schedule_revision_lag_months`, `schedule_has_been_revised`, `months_since_start`
  - 1 progress feature: `physical_progress_t`
  - 9 missingness/presence indicators: `state_is_missing`, `approval_date_is_missing`, `original_completion_date_is_missing`, `revised_cost_is_present`, `revised_date_is_present`, `physical_progress_is_present`, `physical_progress_supported`, `start_date_is_present`, `start_date_supported`
  - 3 historical expenditure features: `exp_delta_1m`, `exp_delta_3m`, `past_exp_stagnant_3m`
  - 2 historical progress features: `past_progress_delta_3m`, `past_progress_stagnant_3m`
  - 3 historical revision count features: `n_prior_schedule_extensions`, `n_prior_cost_revisions`, `observed_tenure_months`
  - 3 delta support indicators: `exp_delta_1m_is_supported`, `exp_delta_3m_is_supported`, `progress_delta_3m_is_supported`
- **Hyperparameters**:
  - `iterations = 300`
  - `learning_rate = 0.05`
  - `depth = 5`
  - `l2_leaf_reg = 3.0`
  - `random_seed = 20260829`
  - `thread_count = 4`
  - `verbose = False`
  - `allow_writing_files = False`
  - `auto_class_weights = None` (unweighted)
- **Categorical & Numeric Handling**: Native CatBoost string categoricals with `__MISSING__` sentinel; missing numerics preserved as `NaN`.
- **Serialization Format**: Native CatBoost binary format (`.cbm`).

### 2. Modern Regime
- **Model Winner**: `logistic_static_only__unweighted`
- **Model Family**: Scikit-learn Logistic Regression (`LogisticRegression`)
- **Target**: `target_effective_schedule_ext_3m`
- **Horizon ($H$)**: 3 months within continuous segment
- **Embargo**: Strict walk-forward ($T + 3 < E$)
- **Feature Set**: `STATIC_AT_T_FEATURES` (25 features):
  - 3 static categoricals: `sector`, `agency`, `state`
  - 13 static numeric features: `original_cost`, `cumulative_expenditure_t`, `revised_cost_t`, `physical_progress_t`, `project_age_months`, `months_to_original_schedule`, `months_to_effective_schedule`, `schedule_revision_lag_months`, `schedule_has_been_revised`, `months_since_start`, `expenditure_to_original_cost_ratio`, `revised_to_original_cost_ratio`, `cost_has_been_revised`
  - 9 missingness/presence indicators: `state_is_missing`, `approval_date_is_missing`, `original_completion_date_is_missing`, `revised_cost_is_present`, `revised_date_is_present`, `physical_progress_is_present`, `physical_progress_supported`, `start_date_is_present`, `start_date_supported`
- **Preprocessing**: `FoldPreprocessor` fitted strictly on the production training fold:
  - Categoricals: Learned training frequencies (`<feature>__train_frequency`).
  - Numerics: Standardized with training mean and standard deviation (`<feature>__standardized`), with explicit missingness indicators (`<feature>__missing`).
  - Total transformed feature dimensions: 47 columns.
- **Hyperparameters**:
  - `penalty = "l2"` (`l1_ratio = 0.0`)
  - `C = 1.0`
  - `solver = "lbfgs"`
  - `max_iter = 2000`
  - `class_weight = None` (unweighted)
  - `random_state = 20260829`
- **Serialization Format**: Scikit-learn joblib archive (`.joblib`) bundling the fitted preprocessor and model.

---

## Artifact Directory & File Structure

Model artifacts are stored under `artifacts/ml/schedule_extension_3m/`:

```
artifacts/ml/schedule_extension_3m/
├── manifest.json
├── legacy_catboost/
│   └── model.cbm
└── modern_logistic/
    └── model.joblib
```

### Artifact Manifest (`manifest.json`)
The manifest is a machine-readable JSON document recording:
- `manifest_version`: Schema version (`1.0.0`)
- `contract_version`: Frozen data contract version (`1.0.0`)
- `dataset_name`: `schedule_extension_3m_v1`
- `target`: `target_effective_schedule_ext_3m`
- `horizon_months`: 3
- `embargo_rule`: `strict_walk_forward (T + 3 < E)`
- `canonical_inputs`: Exact SHA-256 digests for `projects_monthly.csv` and `projects_completed.csv`
- `environment`: Python, CatBoost, scikit-learn, NumPy, and Joblib versions
- `models`: Regime specifications for `LEGACY` and `MODERN`, including relative paths, SHA-256 digests, feature counts, exact feature orderings, hyperparameters, and production training boundaries.

---

## Production-Fit Training Boundaries

The production artifacts are trained only on historical observations whose target labels are fully observable and matured under the contract ($H=3$):

| Regime | Segments Included | Start Month | Cutoff Month ($T$) | Target Matures By | Training Rows | Positive / Negative | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LEGACY** | Segments 1, 2, 3 | `2023-01` | `2025-03` | `2025-06` | 25,406 | 2,634 / 22,772 | Latest month in Segment 3 with a full 3-month window before the June–July 2025 unbridged identifier redesign boundary. |
| **MODERN** | Segment 4 | `2025-07` | `2026-04` | `2026-07` | 11,899 | 4,327 / 7,572 | Latest month in Segment 4 with a full 3-month window before the end of canonical processed data. |

Tail months ($2025-04..2025-06$ and $2026-05..2026-07$) have incomplete forward windows and are strictly excluded from training to prevent label ambiguity and leakage.

---

## Building and Validating Artifacts

Artifacts are built deterministically using `src/ml/build_artifacts.py`:

```powershell
python -m src.ml.build_artifacts --root . --output artifacts/ml/schedule_extension_3m
```

### Verification Steps
1. The builder computes and verifies SHA-256 digests of the canonical inputs:
   - `data/processed/projects_monthly.csv`: `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF`
   - `data/processed/projects_completed.csv`: `89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910`
2. It validates the data contract against `schemas/schedule_extension_3m_v1.contract.json`.
3. It fits both models on the approved production training subsets.
4. It serializes the models and writes `manifest.json`.
5. It validates that the serialized file SHA-256 digests match the recorded manifest digests.

---

## Reusable Inference Interface

Inference is performed through `ScheduleExtensionPredictor` in `src/ml/predict_schedule.py`.

### Basic Usage

```python
from src.ml.predict_schedule import ScheduleExtensionPredictor

# Load artifacts from disk with SHA-256 integrity verification
predictor = ScheduleExtensionPredictor.load()

# Example input observation (Modern regime)
observation = {
    "project_code": "000123",
    "report_month": "2026-01",
    "sector": "ROAD TRANSPORT AND HIGHWAYS",
    "agency": "NHAI",
    "state": "UTTAR PRADESH",
    "original_cost": 1500.0,
    "cumulative_expenditure_t": 850.0,
    "revised_cost_t": 1750.0,
    "physical_progress_t": 65.0,
    # ... other required static features ...
}

# Run forward-pass inference (regime automatically resolved from report_month)
result = predictor.predict_one(observation)

print(f"Regime: {result.regime}")
print(f"Model ID: {result.model_identifier}")
print(f"Raw Score (logit): {result.raw_score:.4f}")
print(f"Probability: {result.probability:.4f}")
```

### Batch Scoring

```python
results = predictor.predict_batch(observations, regime="MODERN")
for r in results:
    print(r.metadata.get("project_code"), r.probability)
```

---

## Safety & Validation Guarantees

1. **Strict Input Validation**:
   - **Missing features**: Raises `ValueError` listing exact missing features.
   - **Unknown features**: Raises `ValueError` listing unrecognized fields. Never silently dropped.
   - **Non-numeric strings**: Parsing errors in numeric columns raise `ValueError`.
2. **Safe Regime Assignment**:
   - Resolved either via explicit parameter (`LEGACY` or `MODERN`) or automatically from `report_month` using contract continuous segment definitions.
   - Unassigned months or structural gap months (`2023-12`, `2024-04`, `2024-05`) fail closed with clear error messages.
   - Conflicting regime and report month (e.g. `regime="LEGACY"` with `report_month="2026-01"`) fail closed.
   - No silent boundary crossing across June–July 2025.
3. **No Dynamic Retraining**:
   - The inference engine is strictly read-only. It performs zero fitting, zero parameter updating, and zero request-time imputation.
4. **Explainability Compatibility**:
   - Legacy CatBoost artifact preserves the exact feature ordering and Pool structure required for native TreeSHAP decomposition ($raw\_margin = \sum contributions + base\_value$).
   - Modern Logistic artifact preserves exact preprocessor scales and coefficients required for linear logit decomposition ($raw\_score = \sum (x \cdot w) + b$).

---

## Testing & Verification

Run the dedicated artifact test suite:

```powershell
python -m unittest tests/test_ml_artifacts.py -v
```

Run the combined ML regression test suite:

```powershell
python -m unittest tests/test_ml_data_contract.py tests/test_ml_dataset_builder.py tests/test_ml_evaluate_baselines.py tests/test_ml_refine_logistic.py tests/test_ml_robustness_audit.py tests/test_ml_challenger_catboost.py tests/test_ml_operational_policy.py tests/test_ml_explain_locked_models.py tests/test_ml_readiness_audit.py tests/test_ml_artifacts.py -v
```
