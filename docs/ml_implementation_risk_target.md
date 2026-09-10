# IRIS PR-08: Implementation Risk Target Definition & Audit Report

## 1. Scope

This document specifies the authoritative, machine-readable data contract, target definition, eligibility logic, temporal feasibility audit, right-censoring accounting, and modeling viability analysis for the **IRIS Implementation Risk Target** (`implementation_risk_v1`).

The working unit is one ongoing infrastructure project in one report month ($T$). The implementation-risk prediction pipeline forecasts whether an actively ongoing project will suffer implementation stagnation or deterioration over a forward 3-month horizon ($H = 3$).

---

## 2. PR Boundaries

In strict compliance with PR-08 governance:
- **No Predictive Models**: Zero machine learning models (Logistic Regression, CatBoost, XGBoost, Random Forest, neural networks, or baseline heuristics) are trained or evaluated in this PR.
- **Data Immutability**: Canonical datasets (`data/processed/projects_monthly.csv` and `data/processed/projects_completed.csv`) are immutable; their SHA-256 digests remain byte-for-byte identical.
- **Separation of Concerns**: PR-08 strictly defines, audits, reconciles, and proves the viability of the target. Production model training and evaluation are reserved for PR-09.

---

## 3. Dataset Sources

Target definition and auditing are derived from the canonical, source-faithful IRIS processed datasets:

| Dataset | Path | Row Count | Unique Projects | Authoritative SHA-256 Digest |
|---|---|---|---|---|
| Monthly Panel | `data/processed/projects_monthly.csv` | 64,608 | 4,738 | `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF` |
| Completed Projects | `data/processed/projects_completed.csv` | 876 | 876 | `89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910` |

---

## 4. Candidate Outcome Audit

Before selecting the primary target, five candidate implementation-risk outcomes were empirically investigated across the canonical data:

### Candidate 1: Rolling 3-Month Physical Progress Stagnation (`target_progress_stagnation_3m`)
- **Scope**: `projects_monthly.csv` (Segments 3 & 4, 2024-06 to 2026-07).
- **Definition**: For an ongoing project with reported $0.0 \le \text{physical\_progress}(T) < 100.0$, the change over $H=3$ months satisfies $\Delta \text{progress}_{T \to T+3} \le 0.0$.
- **Eligible Observations**: 26,044.
- **Positive Events**: 7,344 (28.20% prevalence).
- **Class Ratio**: 1 : 2.55 (balanced).
- **Viability**: **`VIABLE_WITH_LIMITATIONS`**.
- **Rationale**: Highly observable in official MoSPI Flash Reports, well-balanced positive prevalence, stable across time, and directly captures on-the-ground physical stalled execution.

### Candidate 2: Dual Implementation Stagnation (`target_dual_stagnation_3m`)
- **Scope**: `projects_monthly.csv` (Segments 3 & 4).
- **Definition**: Both physical progress and financial expenditure fail to advance ($\Delta \text{progress}_{T \to T+3} \le 0.0$ AND $\Delta \text{expenditure}_{T \to T+3} \le 0.0$).
- **Eligible Observations**: 26,044.
- **Positive Events**: 3,745 (14.38% prevalence).
- **Viability**: **`VIABLE_WITH_LIMITATIONS`**.
- **Rationale**: Strong signal of complete project paralysis, but omits projects experiencing "hollow spending" (funds disbursed on paper while physical work is frozen).

### Candidate 3: Physical Progress Deterioration (`target_progress_deterioration_3m`)
- **Scope**: `projects_monthly.csv` (Segments 3 & 4).
- **Definition**: Downward revision of reported physical progress ($\Delta \text{progress}_{T \to T+3} < 0.0$).
- **Eligible Observations**: 26,044.
- **Positive Events**: 608 (2.33% prevalence).
- **Viability**: **`NOT_YET_VIABLE`**.
- **Rationale**: Severe class rarity (2.3%) and sparse monthly distribution prevent robust expanding-origin walk-forward model evaluation.

### Candidate 4: Rolling 3-Month Expenditure Stagnation (`target_expenditure_stagnation_3m`)
- **Scope**: `projects_monthly.csv` (All Segments, 2023-01 to 2026-07).
- **Definition**: Cumulative expenditure fails to increase ($\Delta \text{expenditure}_{T \to T+3} \le 0.0$).
- **Complete Window Observations**: 40,456.
- **Positive Events**: 11,504 (28.44% prevalence).
- **Viability**: **`VIABLE_WITH_LIMITATIONS`**.
- **Rationale**: While available across all 4 segments, expenditure stagnation reflects accounting and billing disbursement cycles rather than physical site execution, and is susceptible to documented MoSPI source anomalies (`EXPENDITURE_WITH_ZERO_PROGRESS`).

### Candidate 5: Lifecycle Completed Project Implementation Overrun (`target_completed_implementation_overrun`)
- **Scope**: `projects_completed.csv` ($N = 876$).
- **Viability**: **`NOT_YET_VIABLE`**.
- **Bottlenecks**:
  1. `physical_progress` is structurally absent from `projects_completed.csv`.
  2. Severe survivorship bias: 81.5% of unique projects in the repository remain ongoing and are never completed.
  3. Severe temporal clustering: 50.7% of completed projects appear in just two months (June 2026 and October 2024).

---

## 5. Final Selected Target

The authoritative primary implementation-risk target selected for IRIS is:

$$\mathbf{target\_progress\_stagnation\_3m}$$

This target measures observable on-the-ground project execution stalls over a rolling short horizon ($H = 3$ months) for actively ongoing infrastructure projects.

---

## 6. Mathematical Definition

Let:
- $T$ denote the prediction origin month.
- $H = 3$ denote the forward prediction horizon.
- $P(t) \in [0.0, 100.0]$ denote the reported `physical_progress` of project $i$ at month $t$.
- $\epsilon = 10^{-6}$ denote the floating-point tolerance threshold.

The target label $Y_{i, T} \in \{0, 1\}$ is defined as:

$$Y_{i, T} = \begin{cases}
1, & \text{if } P(T+3) - P(T) \le \epsilon \quad \text{(Stagnation / Deterioration)} \\
0, & \text{if } P(T+3) - P(T) > \epsilon \quad \text{(Positive Physical Advancement)}
\end{cases}$$

Subject to baseline eligibility:
$$0.0 \le P(T) < 100.0$$

---

## 7. Prediction Horizon ($H = 3$) Justification

A forward horizon of $H = 3$ months is selected for three reasons:
1. **Consistency across Pipelines**: Aligns with the 3-month horizon frozen in Schedule Extension (`target_extension_3m`, PR-01) and Cost Escalation (`target_effective_cost_esc_3m`, PR-06), creating a unified tri-pillar predictive risk suite.
2. **Operational Meaningfulness**: Infrastructure construction in India operates on quarterly reporting and contractor billing cycles. A project failing to advance over an entire quarter represents an actionable management intervention signal.
3. **Minimization of Censoring**: Longer horizons ($H = 6$ or $12$) would censor a substantially larger portion of the panel at segment boundaries and the dataset boundary (July 2026).

---

## 8. Positive Definition

An observation is classified as an **Eligible Positive** ($Y = 1$) when:
1. The project is actively ongoing at $T$ ($0.0 \le P(T) < 100.0$).
2. The project is continuously observed in the panel across $T+1, T+2, T+3$ within the same continuous segment.
3. Physical progress is fully reported across the forward window.
4. $P(T+3) - P(T) \le 10^{-6}$.

Subtypes recorded in metadata:
- `ZERO_ADVANCE` ($6,736$ events): $P(T+3) == P(T)$ (complete freeze in physical works).
- `DETERIORATION` ($608$ events): $P(T+3) < P(T)$ (administrative downward revision).

---

## 9. Negative Definition

An observation is classified as an **Eligible Negative** ($Y = 0$) when:
1. The project is actively ongoing at $T$ ($0.0 \le P(T) < 100.0$).
2. The project is continuously observed in the panel across $T+1, T+2, T+3$ within the same continuous segment.
3. Physical progress is fully reported across the forward window.
4. $P(T+3) - P(T) > 10^{-6}$.
- Total Eligible Negatives: $18,700$ observations (`ADVANCE`).

---

## 10. Right-Censoring Rules

Observations whose forward 3-month window cannot be fully observed are treated as censored and excluded from supervised training/evaluation. They are **never** silently classified as negatives:

1. **`STRUCTURAL_GAP_OR_REGIME_BOUNDARY`** ($21,489$ rows):
   - $T$ and $T+3$ belong to different continuous segments, cross unbridged publication gaps (e.g. 2023-11 to 2024-01, 2024-03 to 2024-06), cross the June-July 2025 identifier redesign boundary, or extend beyond the dataset boundary (July 2026).
2. **`PROJECT_DISAPPEARED_OR_PANEL_EXIT`** ($2,663$ rows):
   - The project is dropped, completed, or omitted from one or more intermediate months $T+1..T+3$ within the same continuous segment.

---

## 11. Ambiguity & Ineligibility Rules

Observations that cannot be cleanly labeled due to missing or non-ongoing state at baseline or window:

1. **`LAYOUT_PROGRESS_UNSUPPORTED`** ($11,993$ rows):
   - Prediction months in Segments 1 and 2 (2023-01 through 2024-03) where the MoSPI Flash Report layout structurally omitted physical progress percentage.
2. **`MISSING_BASELINE_PROGRESS`** ($537$ rows):
   - $P(T)$ is null or unrecorded in Segments 3 or 4.
3. **`BASELINE_ALREADY_COMPLETED`** ($1,239$ rows):
   - $P(T) \ge 100.0$. The project is already physically complete on the ground. Non-advancement is expected completion, not stagnation.
4. **`FUTURE_PROGRESS_MISSING`** ($643$ rows):
   - The project is observed in $T+1..T+3$, but $P(t)$ is null in one or more forward window months.

---

## 12. Continuous Segments & Structural Gaps

IRIS enforces strict temporal segmentation. Prediction windows are strictly forbidden from crossing segment boundaries:

| Segment | Identifier Regime | Start Month | End Month | Physical Progress Supported | Total Rows |
|---|---|---|---|---|---|
| `SEGMENT_1` | LEGACY | 2023-01 | 2023-11 | No (Layout Omission) | 18,040 |
| `SEGMENT_2` | LEGACY | 2024-01 | 2024-03 | No (Layout Omission) | 5,596 |
| `SEGMENT_3` | LEGACY | 2024-06 | 2025-06 | Yes (Table 7) | 22,371 |
| `SEGMENT_4` | MODERN | 2025-07 | 2026-07 | Yes (Table 6) | 18,601 |

---

## 13. Population Reconciliation

Deterministic accounting reconciles all 64,608 observations in `projects_monthly.csv`:

$$\text{Total Observations } (64,608) = \text{Eligible } (26,044) + \text{Censored } (24,152) + \text{Ineligible } (14,412)$$

### Exact Disposition Breakdown

| Category | Disposition Reason | Row Count | Percentage of Total |
|---|---|---|---|
| **Eligible** | `ELIGIBLE_POSITIVE` | 7,344 | 11.37% |
| **Eligible** | `ELIGIBLE_NEGATIVE` | 18,700 | 28.94% |
| **Censored** | `STRUCTURAL_GAP_OR_REGIME_BOUNDARY` | 21,489 | 33.26% |
| **Censored** | `PROJECT_DISAPPEARED_OR_PANEL_EXIT` | 2,663 | 4.12% |
| **Ineligible** | `LAYOUT_PROGRESS_UNSUPPORTED` | 11,993 | 18.56% |
| **Ineligible** | `MISSING_BASELINE_PROGRESS` | 537 | 0.83% |
| **Ineligible** | `BASELINE_ALREADY_COMPLETED` | 1,239 | 1.92% |
| **Ineligible** | `FUTURE_PROGRESS_MISSING` | 643 | 1.00% |
| **Total** | **Reconciled Deterministically** | **64,608** | **100.00%** |

---

## 14. Temporal Feasibility

The target supports expanding-origin walk-forward evaluation under the strict embargo rule:

$$T + 3 < E$$

Equality $T + 3 == E$ is strictly rejected.

### Summary by Segment

| Identifier Regime | Continuous Segment | Total Rows | Eligible Rows | Positives | Negatives | Positive Rate | Censored Rows | Ineligible Rows |
|---|---|---|---|---|---|---|---|---|
| LEGACY | `SEGMENT_1` | 18,040 | 0 | 0 | 0 | 0.00% | 6,047 | 11,993 |
| LEGACY | `SEGMENT_2` | 5,596 | 0 | 0 | 0 | 0.00% | 5,596 | 0 |
| LEGACY | `SEGMENT_3` | 22,371 | 14,321 | 4,335 | 9,986 | 30.27% | 5,893 | 2,157 |
| MODERN | `SEGMENT_4` | 18,601 | 11,723 | 3,009 | 8,714 | 25.67% | 6,616 | 262 |
| **Total** | | **64,608** | **26,044** | **7,344** | **18,700** | **28.20%** | **24,152** | **14,412** |

---

## 15. Event Prevalence & Class Balance

- **Eligible Population**: 26,044
- **Positive Events**: 7,344
- **Positive Prevalence**: 28.20% ($0.281984$)
- **Negative Events**: 18,700
- **Negative Prevalence**: 71.80% ($0.718016$)
- **Class Imbalance Ratio**: $2.55 : 1$ ($18,700 / 7,344 = 2.5463$)

Unlike cost overrun (which suffered an extreme 1 : 44.9 class imbalance), implementation risk has a balanced class ratio of ~1 : 2.55, enabling standard loss functions and evaluation metrics without extreme rebalancing.

---

## 16. Leakage Policy

The leakage policy separates fields into allowed prediction-time inputs and strictly prohibited outcome/future columns:

### Prohibited Leakage Fields (27 Fields)
1. Target outcome fields: `target_progress_stagnation_3m`, `progress_stagnation_subtype`, `delta_physical_progress_3m`, `baseline_progress`, `future_progress_t3`, `target_window_end_month`.
2. Cross-pipeline outcome labels: `target_extension_3m`, `target_effective_cost_esc_3m`, `cost_revision_type`, `cost_diff`, `target_event_month`, `target_event_revised_cost`.
3. Completed project fields: `actual_completion_date`, `completed_revised_cost`, `completed_cumulative_expenditure`, `eventually_completed`, `completion_report_month`.
4. High-cardinality project identifiers: `project_code`, `project_name`, `legacy_ocms_code`, `pmgid`.
5. Provenance metadata: `source_file`, `source_page`, `source_pages`, `source_row_number`, `source_serial_number`, `extraction_method`.

---

## 17. Feature Availability Rules

The model input space is strictly restricted to 36 ordered features available at prediction origin $T$, spanning 8 allowed families:
1. `static_categoricals`: `sector`, `agency`, `state`
2. `static_cost_financial`: `original_cost`, `revised_cost_t`, `cumulative_expenditure_t`, `expenditure_to_original_cost_ratio`, `revised_to_original_cost_ratio`, `cost_has_been_revised`
3. `schedule`: `project_age_months`, `months_to_original_schedule`, `months_to_effective_schedule`, `schedule_revision_lag_months`, `schedule_has_been_revised`, `months_since_start`
4. `progress`: `physical_progress_t`
5. `missingness_presence_indicators`: `state_is_missing`, `approval_date_is_missing`, `original_completion_date_is_missing`, `revised_cost_is_present`, `revised_date_is_present`, `physical_progress_is_present`, `physical_progress_supported`, `start_date_is_present`, `start_date_supported`
6. `historical_expenditure`: `exp_delta_1m`, `exp_delta_3m`, `past_exp_stagnant_3m`
7. `historical_progress`: `past_progress_delta_3m`, `past_progress_stagnant_3m`
8. `historical_schedule_cost_revision_counts`: `n_prior_schedule_extensions`, `n_prior_cost_revisions`, `observed_tenure_months`
9. `delta_support`: `exp_delta_1m_is_supported`, `exp_delta_3m_is_supported`, `progress_delta_3m_is_supported`

All 36 features are derived strictly from snapshots at or prior to $T$.

---

## 18. Modeling Viability Analysis

Evaluating the 9 required viability dimensions:

1. **Eligible Observations ($26,044$)**: High statistical power across Segments 3 and 4.
2. **Positive Events ($7,344$)**: Substantial positive event volume across all eligible prediction months.
3. **Class Balance ($28.2\%$)**: Well-balanced distribution (~1 : 2.55).
4. **Temporal Distribution**: Positives occur steadily in every single eligible month ($320$ to $611$ per month in Segment 3; $169$ to $502$ per month in Segment 4).
5. **Walk-Forward Folds**: Supports multiple expanding-window folds in Segment 3 (Legacy) and Segment 4 (Modern).
6. **Right-Censoring**: Explicitly audited and quarantined ($24,152$ rows).
7. **Leakage Risk**: Zero leakage; candidate feature set passes audit.
8. **Structural Discontinuities**: Respected; windows never bridge across gaps.
9. **Outcome Observability**: Derived directly from reported `physical_progress`.

---

## 19. Limitations

The target carries three important limitations:
1. **Segment 1 & 2 Omission**: Physical progress was structurally omitted from the MoSPI Flash Report layout from January 2023 through March 2024. Therefore, models cannot train on these historical months.
2. **Right-Censoring Volume**: $24,152$ observations ($37.38\%$) are censored by segment boundaries, publication gaps, or panel exits.
3. **Administrative Self-Reporting Proxy**: Physical progress is self-reported by executing agencies to MoSPI, subject to occasional reporting batching or lag.

---

## 20. Formal PR-09 Recommendation

The formal, evidence-based recommendation for PR-09 model training is:

$$\mathbf{VIABLE\_WITH\_LIMITATIONS}$$

### Decision Rationale
The target is scientifically and empirically viable for machine learning modeling under clearly documented limitations. With 26,044 eligible observations, 7,344 positive events, a balanced class ratio of ~1 : 2.55, and robust monthly positive coverage across Segments 3 and 4, PR-09 can proceed with expanding-origin walk-forward model training.

---

## 21. Reproducibility & Determinism Statement

All calculations, classifications, reconciliations, and artifact generations are 100% deterministic with zero randomness:
- Generated artifacts in `artifacts/ml/implementation_risk_target_v1/` are byte-for-byte reproducible upon repeated execution.
- Canonical dataset SHA-256 digests are verified and unchanged.
- Command to reproduce:
  ```powershell
  python -m src.ml.implementation_risk_target
  ```
- Command to execute test suite:
  ```powershell
  python -m unittest discover -s tests -p "test_ml_implementation_risk_target.py" -v
  ```
