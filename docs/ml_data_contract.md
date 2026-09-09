# IRIS Machine Learning Data Contract (v1.0.0)

**Dataset**: `schedule_extension_3m_v1`  
**Authoritative Contract Path**: [`schemas/schedule_extension_3m_v1.contract.json`](file:///d:/Coding/Projects/IRIS/schemas/schedule_extension_3m_v1.contract.json)  
**Contract Validator Module**: [`src.ml.data_contract`](file:///d:/Coding/Projects/IRIS/src/ml/data_contract.py)  
**Dataset Builder Module**: [`src.ml.dataset_builder`](file:///d:/Coding/Projects/IRIS/src/ml/dataset_builder.py)  
**Status**: Formally frozen, code-enforced, reproducible.

---

## 1. What the ML Contract Freezes

The ML data contract establishes an immutable, code-enforced boundary for IRIS predictive modeling:

1. **Canonical Input Checksums & Counts**:
   - `data/processed/projects_monthly.csv`: 64,608 rows, SHA-256 `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF`
   - `data/processed/projects_completed.csv`: 876 rows, SHA-256 `89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910`
2. **Prediction Target**: Flagship target `target_effective_schedule_ext_3m` over horizon $H=3$.
3. **Feature Contract**: Exactly 36 prediction-time features in fixed deterministic order across 9 families.
4. **Leakage Boundary**: Explicitly prohibited metadata, identifiers, and future outcome fields.
5. **Continuous Reporting Segments**: 4 continuous segments with strict structural gap isolation.
6. **Embargo Policy**: Non-negotiable walk-forward maturity rule: $T + 3 < E$.
7. **Zero Whole-Dataset Imputation or Fitting**: Raw categoricals and structural missingness preserved; transformations and encodings are training-fold-only.

---

## 2. Why the Target is $H=3$

The flagship target `target_effective_schedule_ext_3m` predicts whether an ongoing project will report an outward revision to its operational completion commitment within the forward 3-month window:

- **Operational Early Warning**: A 3-month horizon provides actionable lead time for administrative interventions before schedule slippage compounds.
- **Tractable Class Balance**: Across continuous segments, $H=3$ provides well-behaved class distributions (~1:4.1 in legacy, ~1:1.7 in modern; total 6,961 positive events / 37,305 eligible rows = 18.66% positive rate). Shorter horizons ($H=1$) suffer from event sparsity, whereas longer horizons ($H \ge 6$) reduce eligible historical tenure and suffer from panel attrition.
- **Effective Commitment Semantics**:
  $$\text{eff\_date}(p, T) = \begin{cases} \text{revised\_completion\_date}(p, T) & \text{if non-empty} \\ \text{original\_completion\_date}(p, T) & \text{otherwise} \end{cases}$$
  A positive event ($Y=1$) requires an actually reported revised date in $T+1 \dots T+3$ that is strictly later than $\text{eff\_date}(p, T)$. A negative ($Y=0$) requires complete same-segment presence without extension, and without unresolved nulls following earlier revisions.

---

## 3. Why Strict Embargo ($T + 3 < E$) is Required

When evaluating a model at reference month $E$, using training labels that overlap or touch $E$ causes label lookahead leakage:
- A training observation at $T = E - 3$ has its label determined by events occurring in $[T+1, T+3]$, which includes month $E$. Publishing delays mean information about month $E$ is not available when making predictions at $E$.
- The strict rule:
  $$T + 3 < E \iff \text{month\_index}(T + 3) < \text{month\_index}(E)$$
  guarantees that every training outcome was fully finalized and published strictly before evaluation snapshot month $E$.
- Training windows ending at $T+3 = E$ or $T+3 > E$ are strictly rejected by `validate_embargo_rule()`.

---

## 4. The 36 Prediction-Time Features

The contract organizes all 36 features into 9 distinct families. Order and names are frozen:

| # | Family | Features | Description |
|---|---|---|---|
| 1 | **Static Categoricals** (3) | `sector`, `agency`, `state` | Source administrative labels; frequency-encoded on training fold only. |
| 2 | **Static Cost / Financial** (6) | `original_cost`, `revised_cost_t`, `cumulative_expenditure_t`, `expenditure_to_original_cost_ratio`, `revised_to_original_cost_ratio`, `cost_has_been_revised` | Financial baseline, latest cost revision, and expenditure ratios at $T$. |
| 3 | **Schedule** (6) | `project_age_months`, `months_to_original_schedule`, `months_to_effective_schedule`, `schedule_revision_lag_months`, `schedule_has_been_revised`, `months_since_start` | Elapsed and remaining schedule durations relative to $T$. |
| 4 | **Progress** (1) | `physical_progress_t` | Reported physical completion percentage at $T$. |
| 5 | **Missingness / Presence Indicators** (9) | `state_is_missing`, `approval_date_is_missing`, `original_completion_date_is_missing`, `revised_cost_is_present`, `revised_date_is_present`, `physical_progress_is_present`, `physical_progress_supported`, `start_date_is_present`, `start_date_supported` | Explicit binary flags for structural and source-level missing values. |
| 6 | **Historical Expenditure** (3) | `exp_delta_1m`, `exp_delta_3m`, `past_exp_stagnant_3m` | Trajectory of cumulative expenditure strictly backward ($T-1$, $T-3$). |
| 7 | **Historical Progress** (2) | `past_progress_delta_3m`, `past_progress_stagnant_3m` | Trajectory of physical progress strictly backward ($T-3$). |
| 8 | **Historical Revisions / Tenure** (3) | `n_prior_schedule_extensions`, `n_prior_cost_revisions`, `observed_tenure_months` | Historical revision counts and observed tenure within the current segment. |
| 9 | **Delta Support** (3) | `exp_delta_1m_is_supported`, `exp_delta_3m_is_supported`, `progress_delta_3m_is_supported` | Binary indicators distinguishing zero delta from unobserved/unsupported history. |

### Excluded Candidate Drift Features
The following features are intentionally excluded from the v1 feature contract:
- `month_of_fiscal_year`
- `is_fiscal_yearend`
- `report_month_index`
- `identifier_regime` (as a feature)

---

## 5. Prohibited Leakage Metadata

The contract specifies metadata fields that must **never** enter the feature matrix ($X$). Models ingesting any of these fields fail contract validation:

- **Target Variable**: `target_effective_schedule_ext_3m`
- **Future Outcome Metadata**: `target_event_month`, `target_event_revised_completion_date`, `target_window_end_month`, `extension_type`
- **Completion Dataset Boundary**: `eventually_completed`, `completion_report_month`, `actual_completion_date` (completion records are published post-exit)
- **Entity Memorization Identifiers**: `project_code`, `project_name`
- **Baseline Metadata**: `baseline_completion_date`, `baseline_completion_source`

---

## 6. Structural Gaps Excluded From Continuous Segments

The 4 continuous reporting segments are frozen without cross-segment longitudinal bridging:

1. **SEGMENT_1** (`LEGACY`): `2023-01` $\to$ `2023-11` (11 months)
2. **SEGMENT_2** (`LEGACY`): `2024-01` $\to$ `2024-03` (3 months)
3. **SEGMENT_3** (`LEGACY`): `2024-06` $\to$ `2025-06` (13 months)
4. **SEGMENT_4** (`MODERN`): `2025-07` $\to$ `2026-07` (13 months)

### Unbridged Boundaries:
- **`2023-12`**: Flash report gap; no projects are linked across this month.
- **`2024-04` and `2024-05`**: Uncoded Annexure XVIII layout; omitted from canonical longitudinal linking.
- **June $\to$ July 2025**: Identifier redesign from legacy (`N########` / 9-digit) to modern 6-digit codes. Crosswalk proposals remain strictly diagnostic and are never used to bridge segments.

---

## 7. Verifying the Dataset Before Training

Before fitting any baseline or candidate model, execute contract validation:

```powershell
python -m src.ml.data_contract --root .
```

To run the full automated contract and ML test suite:

```powershell
python -m unittest tests/test_ml_data_contract.py tests/test_ml_dataset_builder.py tests/test_ml_evaluate_baselines.py tests/test_ml_refine_logistic.py tests/test_ml_robustness_audit.py -v
```

If canonical file hashes, row counts, feature names, feature ordering, leakage exclusions, or segment boundaries deviate, the validator raises a typed exception and halts execution immediately.
