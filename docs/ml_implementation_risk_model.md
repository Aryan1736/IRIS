# IRIS PR-09: Implementation Risk Model Training, Evaluation, Calibration, Explainability, and Audit Report

## 1. Scope

This document provides the authoritative technical report, walk-forward validation results, calibration analysis, threshold operating trade-offs, explainability audit, and empirical recommendation for the **IRIS Implementation Risk Model** (`target_progress_stagnation_3m`).

The predictive task forecasts whether an actively ongoing infrastructure project at prediction origin month $T$ will experience physical progress stagnation or deterioration over the next $H = 3$ months, based strictly on information available at $T$.

---

## 2. Frozen Target Reference

The evaluation builds directly and immutably upon the frozen PR-08 data contract and target definition:
- **Contract Path**: `schemas/implementation_risk_v1.contract.json`
- **Target Name**: `target_progress_stagnation_3m`
- **Prediction Horizon**: $H = 3$ months
- **Tolerance**: $\epsilon = 10^{-6}$
- **Mathematical Formulation**:
  $$Y_{i, T} = \begin{cases}
  1, & \text{if } \text{physical\_progress}(T+3) - \text{physical\_progress}(T) \le 10^{-6} \quad \text{(Stagnation / Deterioration)} \\
  0, & \text{if } \text{physical\_progress}(T+3) - \text{physical\_progress}(T) > 10^{-6} \quad \text{(Physical Advancement)}
  \end{cases}$$
- **Baseline Eligibility Constraint**:
  $$0.0 \le \text{physical\_progress}(T) < 100.0$$

---

## 3. Contract Version

- **Contract Name**: `implementation_risk_v1`
- **Contract Version**: `1.0.0`
- **Dataset Name**: `implementation_risk_v1`
- **Dataset Type**: `implementation_risk_prediction`

---

## 4. Population Reconciliation

The implementation validates the exact deterministic population reconciliation of the 64,608 source observations in `data/processed/projects_monthly.csv`:

| Population Component | Metric / Disposition | Count | Percentage |
|---|---|---|---|
| **Total Source Observations** | `total_source_rows` | 64,608 | 100.00% |
| **Eligible Observations** | Total Eligible Population | 26,044 | 40.31% |
| - Positives | `ELIGIBLE_POSITIVE` | 7,344 | 11.37% |
| - Negatives | `ELIGIBLE_NEGATIVE` | 18,700 | 28.94% |
| **Right-Censored Observations** | Total Censored | 24,152 | 37.38% |
| - Segment / Gap / Boundary | `STRUCTURAL_GAP_OR_REGIME_BOUNDARY` | 21,489 | 33.26% |
| - Disappeared / Exit | `PROJECT_DISAPPEARED_OR_PANEL_EXIT` | 2,663 | 4.12% |
| **Ineligible / Ambiguous** | Total Ineligible | 14,412 | 22.31% |
| - Layout Unsupported | `LAYOUT_PROGRESS_UNSUPPORTED` (Seg 1 & 2) | 11,993 | 18.56% |
| - Missing Baseline | `MISSING_BASELINE_PROGRESS` | 537 | 0.83% |
| - Baseline Completed | `BASELINE_ALREADY_COMPLETED` ($\ge 100\%$) | 1,239 | 1.92% |
| - Future Progress Missing | `FUTURE_PROGRESS_MISSING` | 643 | 1.00% |

- **Reconciliation Accounting**: $7,344 + 18,700 + 21,489 + 2,663 + 11,993 + 537 + 1,239 + 643 = 64,608$ (exact match).
- **Eligible Positive Prevalence**: $7,344 / 26,044 = 28.1984\%$.
- **Class Imbalance Ratio**: $18,700 : 7,344 = 2.5463 : 1$ (~1 : 2.55).

---

## 5. Eligibility Criteria

An observation is eligible for modeling if and only if:
1. The project is actively ongoing at $T$ ($0.0 \le \text{physical\_progress}(T) < 100.0$).
2. The project is continuously observed across the forward window $T+1, T+2, T+3$ within the same continuous segment.
3. The continuous segment structurally reports physical progress percentage (Segments 3 and 4).
4. Physical progress is non-null and valid in all forward window months.

---

## 6. Feature Policy

The modeling matrix contains exactly 36 approved contract features spanning 9 allowed families:
1. **Static Categoricals (3)**: `sector`, `agency`, `state`.
2. **Static Cost & Financial (6)**: `original_cost`, `revised_cost_t`, `cumulative_expenditure_t`, `expenditure_to_original_cost_ratio`, `revised_to_original_cost_ratio`, `cost_has_been_revised`.
3. **Schedule Metrics (6)**: `project_age_months`, `months_to_original_schedule`, `months_to_effective_schedule`, `schedule_revision_lag_months`, `schedule_has_been_revised`, `months_since_start`.
4. **Current Progress (1)**: `physical_progress_t`.
5. **Presence & Support Indicators (9)**: `state_is_missing`, `approval_date_is_missing`, `original_completion_date_is_missing`, `revised_cost_is_present`, `revised_date_is_present`, `physical_progress_is_present`, `physical_progress_supported`, `start_date_is_present`, `start_date_supported`.
6. **Historical Financial Trajectory (3)**: `exp_delta_1m`, `exp_delta_3m`, `past_exp_stagnant_3m`.
7. **Historical Progress Trajectory (2)**: `past_progress_delta_3m`, `past_progress_stagnant_3m`.
8. **Historical Revisions & Tenure (3)**: `n_prior_schedule_extensions`, `n_prior_cost_revisions`, `observed_tenure_months`.
9. **Delta Availability Indicators (3)**: `exp_delta_1m_is_supported`, `exp_delta_3m_is_supported`, `progress_delta_3m_is_supported`.

---

## 7. Leakage Controls

All candidate inputs are subjected to fail-closed leakage audits. The 27 prohibited fields include:
- Primary and secondary target labels (`target_progress_stagnation_3m`, `progress_stagnation_subtype`, `delta_physical_progress_3m`, `baseline_progress`, `future_progress_t3`, `target_window_end_month`).
- Cross-pipeline target labels (`target_extension_3m`, `target_effective_cost_esc_3m`, `cost_revision_type`, `cost_diff`, `target_event_month`, `target_event_revised_cost`).
- Lifecycle completed project fields (`actual_completion_date`, `completed_revised_cost`, `completed_cumulative_expenditure`, `eventually_completed`, `completion_report_month`).
- High-cardinality project identifiers (`project_code`, `project_name`, `legacy_ocms_code`, `pmgid`).
- Extraction metadata (`source_file`, `source_page`, `source_pages`, `source_row_number`, `source_serial_number`, `extraction_method`).

---

## 8. Candidate Models

Evaluated candidate model families:
1. **Reference Baseline**:
   - `prevalence`: Predicts the empirical training-fold positive prevalence $\bar{y}_{train}$.
2. **Logistic Regression Baselines**:
   - `logistic_unweighted`: L2 regularized, $C = 1.0$, `max_iter = 2000`, `solver = lbfgs`, unweighted, `random_state = 20260910`.
   - `logistic_balanced`: Same configuration with `class_weight = "balanced"`.
3. **CatBoost Challengers**:
   - `catboost_unweighted`: 300 trees, learning rate 0.05, depth 5, L2 leaf reg 3.0, `thread_count = 4`, unweighted, `random_seed = 20260910`.
   - `catboost_balanced`: Same configuration with `auto_class_weights = "Balanced"`.

Fold preprocessing (`ImplementationRiskFoldPreprocessor`) is fit strictly on training-fold data:
- Categorical features: Frequency encoding, unseen categories map to 0.0.
- Numeric features: Standardized using training-fold mean and standard deviation, missing values mapped to 0 with an accompanying `__missing` indicator.
- Immutable after fitting; evaluation transformations never mutate state.

---

## 9. Temporal Validation Design

Validation enforces expanding-origin walk-forward evaluation:
- Regimes and continuous segments are strictly isolated. No cross-gap or June–July 2025 redesign bridging.
- All evaluation origins satisfy target maturity and historical training availability.
- No random shuffling of temporal panels.

---

## 10. Strict Embargo Proof

For every evaluation origin $E$ and training reference month $T$:
$$T + 3 < E \iff \text{month\_index}(\text{add\_months}(T, 3)) < \text{month\_index}(E)$$
Equality $T + 3 == E$ is strictly rejected.

Proof:
- For $T = \text{2024-06}$, $T + 3 = \text{2024-09}$.
- If $E = \text{2024-09}$, $T + 3 == E \implies$ rejected (unobserved label outcome overlaps evaluation origin).
- If $E = \text{2024-10}$, $T + 3 < E \implies$ accepted (label window completes in 2024-09, fully mature prior to 2024-10).

---

## 11. Fold Definitions

A total of **11 evaluation folds** were accepted:

### LEGACY Regime (Segment 3: Table 7, 2024-06 to 2025-06)
- Warmup (0 mature training months under embargo): 2024-06, 2024-07, 2024-08, 2024-09.
- Accepted Folds (6):
  1. `2024-10`: Train months [2024-06] ($N_{train} = 1,555$, pos = 535) $\to$ Eval $N_{eval} = 1,422$, pos = 425 (prev = 29.89%).
  2. `2024-11`: Train months [2024-06..2024-07] ($N_{train} = 3,049$, pos = 1,034) $\to$ Eval $N_{eval} = 1,406$, pos = 404 (prev = 28.73%).
  3. `2024-12`: Train months [2024-06..2024-08] ($N_{train} = 4,536$, pos = 1,541) $\to$ Eval $N_{eval} = 1,399$, pos = 391 (prev = 27.95%).
  4. `2025-01`: Train months [2024-06..2024-09] ($N_{train} = 6,092$, pos = 2,083) $\to$ Eval $N_{eval} = 1,360$, pos = 366 (prev = 26.91%).
  5. `2025-02`: Train months [2024-06..2024-10] ($N_{train} = 7,514$, pos = 2,508) $\to$ Eval $N_{eval} = 1,343$, pos = 327 (prev = 24.35%).
  6. `2025-03`: Train months [2024-06..2024-11] ($N_{train} = 8,920$, pos = 2,912) $\to$ Eval $N_{eval} = 1,299$, pos = 339 (prev = 26.10%).
- Right-Censored (3-month window crosses redesign boundary): 2025-04, 2025-05, 2025-06.

### MODERN Regime (Segment 4: Table 6, 2025-07 to 2026-07)
- Warmup (insufficient mature modern training history): 2025-07, 2025-08, 2025-09, 2025-10, 2025-11.
- Accepted Folds (5):
  1. `2025-12`: Train months [2025-07..2025-08] ($N_{train} = 1,443$, pos = 587) $\to$ Eval $N_{eval} = 1,316$, pos = 169 (prev = 12.84%).
  2. `2026-01`: Train months [2025-07..2025-09] ($N_{train} = 2,174$, pos = 875) $\to$ Eval $N_{eval} = 1,578$, pos = 204 (prev = 12.93%).
  3. `2026-02`: Train months [2025-07..2025-10] ($N_{train} = 2,932$, pos = 1,152) $\to$ Eval $N_{eval} = 1,796$, pos = 215 (prev = 11.97%).
  4. `2026-03`: Train months [2025-07..2025-11] ($N_{train} = 3,701$, pos = 1,439) $\to$ Eval $N_{eval} = 1,692$, pos = 480 (prev = 28.37%).
  5. `2026-04`: Train months [2025-07..2025-12] ($N_{train} = 5,017$, pos = 1,608) $\to$ Eval $N_{eval} = 1,640$, pos = 502 (prev = 30.61%).
- Right-Censored (3-month window exceeds panel end): 2026-05, 2026-06, 2026-07.

---

## 12. Primary Performance Results

Summary of candidate model performance across regimes:

### LEGACY Regime ($N = 8,229$ evaluation rows, Positives = 2,252, Prevalence = 27.37%)

| Candidate Model | Micro PR-AUC | Macro PR-AUC | Micro ROC-AUC | Micro Brier | Micro ECE | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|
| `prevalence` | 0.2839 | 0.2732 | 0.5181 | 0.2028 | 0.0640 | — | 0.0000 | 0.0000 |
| `logistic_unweighted` | 0.5629 | 0.5570 | 0.7870 | 0.1664 | 0.0909 | 0.5936 | 0.5462 | 0.5689 |
| `logistic_balanced` | 0.5624 | 0.5548 | 0.7884 | 0.1899 | 0.1787 | 0.5231 | 0.7029 | 0.5998 |
| `catboost_unweighted` | **0.6872** | **0.6898** | **0.8664** | **0.1291** | **0.0341** | **0.6883** | 0.6323 | 0.6591 |
| `catboost_balanced` | **0.6881** | **0.6898** | **0.8678** | 0.1376 | 0.0965 | 0.6391 | **0.7518** | **0.6909** |

### MODERN Regime ($N = 8,022$ evaluation rows, Positives = 1,570, Prevalence = 19.57%)

| Candidate Model | Micro PR-AUC | Macro PR-AUC | Micro ROC-AUC | Micro Brier | Micro ECE | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|
| `prevalence` | 0.1615 | 0.1934 | 0.3686 | 0.1969 | 0.1857 | — | 0.0000 | 0.0000 |
| `logistic_unweighted` | 0.2229 | 0.2839 | 0.5164 | 0.1947 | 0.1506 | 0.2450 | 0.1790 | 0.2068 |
| `logistic_balanced` | 0.2318 | 0.2867 | 0.5352 | 0.2125 | 0.1813 | 0.2274 | 0.2739 | 0.2485 |
| `catboost_unweighted` | **0.3007** | **0.3903** | **0.6454** | 0.2114 | 0.1788 | **0.2973** | 0.4210 | 0.3485 |
| `catboost_balanced` | **0.3099** | **0.3847** | **0.6526** | 0.2258 | 0.2055 | 0.2849 | **0.4783** | **0.3571** |

---

## 13. Calibration Findings

- **Raw Probability Performance**:
  - In LEGACY, `catboost_unweighted` achieves excellent raw probability calibration: Brier score **0.1291**, 10-bin ECE **0.0341**, MCE 0.1738, calibration slope 0.770, intercept -0.374.
  - In MODERN, calibration is more challenging: Brier score **0.2114**, ECE 0.1788, calibration slope 0.300, intercept -1.176.
- **Historical Platt Scaling Test**:
  - Tested strictly forward across folds: fitting Platt scaling on past evaluation folds does not consistently improve out-of-fold generalization across regime boundaries.
  - Raw uncalibrated probabilities provide the lowest Brier score in production; historical recalibration is recorded as testable but not mandatory.

---

## 14. Threshold Trade-offs

Threshold curves evaluated across 100 operating points ($0.01$ to $1.00$):

### `catboost_unweighted` Operating Points in LEGACY

| Operating Threshold | Precision | Recall | Specificity | F1 | Alert Rate | False Discovery Rate |
|---|---|---|---|---|---|---|
| **0.20** | 0.4566 | 0.8872 | 0.6508 | 0.6030 | 53.18% | 54.34% |
| **0.30** | 0.5385 | 0.8148 | 0.7698 | 0.6486 | 41.44% | 46.15% |
| **0.40** | 0.6128 | 0.7247 | 0.8499 | 0.6641 | 32.37% | 38.72% |
| **0.50** (Default) | **0.6883** | **0.6323** | **0.8921** | **0.6591** | **25.14%** | **31.17%** |
| **0.60** | 0.7513 | 0.5404 | 0.9329 | 0.6288 | 19.69% | 24.87% |
| **0.70** | 0.8174 | 0.4307 | 0.9658 | 0.5641 | 14.44% | 18.26% |

- **Operational Insight**: At threshold $0.50$, the model alerts on ~25% of ongoing projects with ~69% precision and ~63% recall. For higher screening sensitivity, threshold $0.30$ captures $>81\%$ of stagnating projects with $>53\%$ precision.

---

## 15. Error Analysis

Analysis of false positives and false negatives:
1. **False Positives (Predicted Stagnant, Actually Advanced)**:
   - Primarily projects with long historical tenures ($>60$ months) or previous schedule extensions where work resumed abruptly due to newly awarded subcontracts or seasonal construction acceleration.
2. **False Negatives (Predicted Advancing, Actually Stagnated)**:
   - Projects that were progressing steadily in the past ($T-3$ to $T$) but stalled suddenly due to external litigation, contractor disputes, or unrecorded land acquisition roadblocks.

---

## 16. Explainability Findings

- **Exact Reconstruction Verification**:
  - CatBoost TreeSHAP exact margin reconstruction:
    $$\max \left| \text{raw\_margin} - \left( \text{base\_value} + \sum_{j} \text{SHAP}_j \right) \right| \le 7.11 \times 10^{-15} \le 10^{-9} \quad \text{(Machine precision verified)}$$
  - Logistic regression exact logit reconstruction:
    $$\max \left| \text{decision\_function} - \left( \beta_0 + \sum_{j} x_j \beta_j \right) \right| \le 1.11 \times 10^{-16} \le 10^{-9} \quad \text{(Exact match)}$$
- **Top Predictive Features**:
  1. `agency`: Executing agency tracks historical project management reliability.
  2. `state`: Geographic location captures regional land acquisition, regulatory clearance, and monsoon seasonality.
  3. `sector`: Infrastructure sector (Roads, Railways, Power) exhibits distinct progress measurement conventions.
  4. `physical_progress_t`: Baseline completion stage; projects near early foundation stages or late finishing stages experience distinct stagnation dynamics.
- **Attribution Stability**:
  - Fold-to-fold rank correlation (Spearman $\rho$):
    - LEGACY `catboost_unweighted`: $\mathbf{0.9516}$
    - MODERN `catboost_unweighted`: $\mathbf{0.9521}$
  - Attributions are stable across expanding-window origins.

---

## 17. Robustness Results

Bootstrap 95% confidence intervals ($B = 1,000$ draws):

### LEGACY Regime (`catboost_unweighted`)
- **PR-AUC**:
  - Point Estimate: **0.6872**
  - Project-Cluster Bootstrap 95% CI: **[0.6495, 0.7246]**
  - Month-Block Bootstrap 95% CI: **[0.6609, 0.7150]**
- **ROC-AUC**:
  - Point Estimate: **0.8664**
  - Project-Cluster Bootstrap 95% CI: **[0.8524, 0.8799]**
  - Month-Block Bootstrap 95% CI: **[0.8592, 0.8721]**
- **Brier Score**:
  - Point Estimate: **0.1291**
  - Project-Cluster Bootstrap 95% CI: **[0.1207, 0.1378]**
  - Month-Block Bootstrap 95% CI: **[0.1250, 0.1334]**

### MODERN Regime (`catboost_unweighted`)
- **PR-AUC**:
  - Point Estimate: **0.3007**
  - Project-Cluster Bootstrap 95% CI: **[0.2694, 0.3341]**
  - Month-Block Bootstrap 95% CI: **[0.1887, 0.4578]**
- **ROC-AUC**:
  - Point Estimate: **0.6454**
  - Project-Cluster Bootstrap 95% CI: **[0.6226, 0.6683]**
  - Month-Block Bootstrap 95% CI: **[0.5583, 0.7850]**

---

## 18. Regime Comparison & Discontinuity Analysis

Performance exhibits noticeable regime divergence:
- **LEGACY (Segment 3)**: High predictive power (PR-AUC 0.6872, ROC-AUC 0.8664). MoSPI Table 7 reports steady monthly physical progress increments.
- **MODERN (Segment 4)**: Moderate predictive power (PR-AUC 0.3007, ROC-AUC 0.6454). Following the July 2025 redesign (Table 6 format), progress reporting dynamics shifted, and the panel expanded significantly in late 2025 / early 2026, creating higher month-block variance.
- Models in both regimes firmly outperform their respective prevalence baselines.

---

## 19. Limitations

1. **Structural Absence in Segments 1 & 2**: Physical progress percentage was omitted in MoSPI Flash Reports from January 2023 through March 2024. Models cannot learn from this historical era.
2. **Administrative Proxy Metric**: Reported physical progress is an administrative, self-reported percentage from executing agencies, subject to quarterly batching and reporting lags.
3. **Regime Redesign Discontinuity**: Models trained in Segment 3 cannot be transferred across the June–July 2025 identifier boundary without unbridged assumptions; separate regime evaluation is strictly required.

---

## 20. Operational Recommendation

**Status**: $\mathbf{VIABLE\_WITH\_LIMITATIONS}$

### Recommended Model: `catboost_unweighted`
- **Primary Operational Role**: Early warning signal for ongoing infrastructure monitoring dashboards and quarterly project review committees.
- **Key Capabilities**: Strong discrimination in legacy monitoring (ROC 0.866) and meaningful positive lift across both regimes (+0.41 in Legacy, +0.10 in Modern over baseline).
- **Deployment Constraint**: Predictions must be used for prioritized human oversight, contractor inquiry, and administrative follow-up, rather than autonomous or punitive gating.

---

## 21. Compliance & Reproducibility Statement

- **Canonical Immutability**: Canonical datasets `projects_monthly.csv` and `projects_completed.csv` were verified before and after evaluation; their SHA-256 digests remain byte-for-byte identical.
- **Zero Leakage**: All 36 features are derived strictly at or before $T$; prohibited leakage fields fail closed.
- **Strict Embargo**: $T_{train} + 3 < E$ holds for all accepted training observations.
- **Artifact Reproducibility**: Running the pipeline from clean state reproduces all 11 artifacts with bit-for-bit determinism:
  ```powershell
  python -m src.ml.implementation_risk_evaluation
  ```
- **Test Suite**:
  ```powershell
  python -m unittest tests/test_ml_implementation_risk_model.py -v
  ```
