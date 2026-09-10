# IRIS PR-06: Cost Overrun Target Definition, Eligibility Logic, and Audit

**Target Name**: `target_effective_cost_esc_3m`  
**Contract Version**: `1.0.0`  
**Contract Location**: [`schemas/cost_overrun_v1.contract.json`](file:///d:/Coding/Projects/IRIS/schemas/cost_overrun_v1.contract.json)  
**Target Module**: [`src/ml/cost_overrun_target.py`](file:///d:/Coding/Projects/IRIS/src/ml/cost_overrun_target.py)  
**Audit Artifacts**: [`artifacts/ml/cost_overrun_target_v1/`](file:///d:/Coding/Projects/IRIS/artifacts/ml/cost_overrun_target_v1/)  
**Status**: Contract, eligibility, censoring, temporal feasibility, leakage audit, and regression tests complete. **No predictive models were trained.**

---

## 1. Scope and Objective

The objective of PR-06 is to define, audit, and mathematically substantiate a scientifically defensible cost-overrun prediction target for the IRIS infrastructure project monitoring repository.

This work establishes the ground-truth definition, right-censoring rules, temporal walk-forward embargoes, and feature-leakage boundaries before any predictive modeling is attempted in PR-07.

### Explicit Model Training Boundary
> [!IMPORTANT]
> **No machine learning models are trained in PR-06.**  
> No Logistic Regression, CatBoost, XGBoost, Random Forest, neural networks, or heuristics were fitted. Existing schedule-extension model binaries, frozen data contracts, and inference implementations remain strictly untouched.

---

## 2. Why Target Definition Precedes Modeling

In infrastructure analytics, modeling often fails due to ill-defined target concepts:
1. **Conflating Interim Revisions with Final Settlement**: An ongoing project that has not experienced a cost revision is not necessarily "within budget"; it is right-censored. Calling it a negative outcome introduces massive label corruption.
2. **Survivorship Bias**: Conditioning lifecycle cost overrun labels strictly on completed projects restricts the population to projects that finished within the historical monitoring window, biasing the sample toward shorter, simpler, or specific sectors (e.g. roads).
3. **Target Leakage**: Using post-outcome information, future expenditures, or completion statuses as prediction features yields artificially inflated model metrics that collapse during live monitoring.

By separating target definition, eligibility auditing, and leakage prevention into PR-06, we guarantee that PR-07 operates on a frozen, validated, and leak-free foundation.

---

## 3. Available Source Data and Field Discovery

Empirical analysis of the two canonical processed datasets in IRIS established the following:

### 3.1 Ongoing Monthly Dataset (`data/processed/projects_monthly.csv`)
- **Total Rows**: 64,608 observations across 4,738 unique projects.
- **Reporting Period**: January 2023 through July 2026 (40 monthly reports, spanning 4 continuous reporting segments).
- **Available Cost Fields**:
  - `original_cost`: 64,608 / 64,608 present (100.0%). Minimum: 48.44 crore; Median: 615.78 crore; Maximum: 150,000.0 crore. Represents the official sanctioned project cost at inception.
  - `revised_cost`: 29,268 / 64,608 present (45.3%). Minimum: 0.10 crore; Median: 760.16 crore; Maximum: 188,000.0 crore. Represents the officially approved revised cost when published in Flash Report Table 6/7.
  - `cumulative_expenditure`: 64,608 / 64,608 present (100.0%). Represents interim disbursements reported at publication time.
- **Cost Fields Structurally Absent**:
  - No `actual_cost` or `final_settled_cost` field exists in the ongoing panel.

### 3.2 Completed Projects Dataset (`data/processed/projects_completed.csv`)
- **Total Rows**: 876 projects announced as completed between April 2023 and July 2026.
- **Linkage**: All 876 completed projects match ongoing records by exact `project_code` (100.0% linkable).
- **Field Completeness in Completed Table**:
  - `original_cost`: 851 / 876 present (97.1%).
  - `revised_cost`: Only 170 / 876 present (19.4%). 706 records (80.6%) omit `revised_cost`.
  - `cumulative_expenditure`: 876 / 876 present (100.0%).
  - `actual_completion_date`: Only 107 / 876 present (12.2%), structurally absent from all legacy layouts.

---

## 4. Evaluation of Candidate Target Formulations

Three candidate target formulations were evaluated against data availability, censoring, and operational utility:

### Candidate A: Lifecycle Completed-Project Cost Overrun (`target_completed_cost_overrun_v1`)
- **Conceptual Definition**: Final realized cost of a completed project exceeds its initial approved/sanctioned cost.
- **Findings & Bottlenecks**:
  1. **Extreme Right-Censoring**: 3,862 out of 4,738 projects (81.5% of unique projects, accounting for 54,106 of 64,608 monthly observations) have never completed. Their lifecycle cost outcome is unobservable.
  2. **Severe Outcome Missingness**: `revised_cost` is missing in 80.6% of records in `projects_completed.csv`. While 300 of these 706 unrevised completed records had a `revised_cost` in their terminal monthly snapshot, 406 records never had a revision recorded.
  3. **Interim Disbursement vs. Final Cost**: In completed tables, 72.15% of projects report `cumulative_expenditure < original_cost` (median ratio 0.8353). Expenditure at completion publication reflects interim disbursements, not audited final settled financial closures.
  4. **Survivorship & Sector Skew**: >50% of completed projects belong to Road Transport and Highways. Completions are heavily clustered in May/June 2026 (130) and October 2024 (62).
  5. **Prediction-Time Inapplicability**: At monthly prediction time $T$, completed status is an unobserved future event.
- **Viability**: **`NOT_YET_VIABLE`** for supervised training of ongoing project early warning.

### Candidate B: Rolling Effective Cost Escalation (`target_effective_cost_esc_3m`) — **SELECTED PRIMARY TARGET**
- **Conceptual Definition**: Does an ongoing project report an administrative upward cost revision exceeding its official approved baseline within a forward 3-month monitoring window ($H=3$)?
- **Findings & Feasibility**:
  1. **Direct Operational Alignment**: Provides actionable early warning for monitoring authorities that a project is about to report an approved cost escalation.
  2. **Panel Coverage**: Evaluated across all 64,608 monthly observations within continuous segments.
  3. **Reconciled Sample**: 39,693 eligible observations, 865 positive events (2.18%), and 38,828 negative events.
  4. **Stable Temporal Distribution**: Positive events occur across all historical reporting periods from 2023 through 2026 (prevalence: Legacy 2.22%, Modern 2.08%).
  5. **Limitation**: Severe class imbalance (1 : 44.9), requiring precision-recall evaluation and cost-sensitive methods.
- **Viability**: **`VIABLE_WITH_LIMITATIONS`**.

### Candidate C: Lifecycle Cost Growth Threshold ($\text{cost\_growth} > \theta$)
- **Conceptual Definition**: Project cost growth from inception to terminal state exceeds a threshold $\theta$.
- **Findings**: For ongoing projects with no cost growth, labeling them as negatives is invalid because they are right-censored (may experience cost revisions before completion). Restricting the analysis to completed projects collapses to Candidate A.
- **Viability**: **`NOT_YET_VIABLE`**.

---

## 5. Mathematical Target Definition

The primary target is formalized as **`target_effective_cost_esc_3m`**.

### 5.1 Effective Cost Commitment
For any project $p$ at reference month $T$:
$$\text{eff\_cost}(p, T) = \begin{cases} \text{revised\_cost}(p, T) & \text{if non-null, parsed, and } > 0 \\ \text{original\_cost}(p, T) & \text{otherwise} \end{cases}$$

- Baseline source is recorded as `REVISED` if `revised_cost` is present, or `ORIGINAL` if using `original_cost`.
- Tolerance parameter: $\epsilon = 0.001$ Rs crore (Rs 10,000) to filter out negligible floating-point/rounding noise.

### 5.2 Positive Rule ($Y = 1$)
An observation $(p, T)$ receives label $Y = 1$ if and only if:
1. $T$ and $T+3$ belong to the same continuous segment ($\text{Segment}(T) = \text{Segment}(T+3)$).
2. Project $p$ is observed in all forward months $t \in \{T+1, T+2, T+3\}$.
3. $\text{original\_cost}(p, T)$ is present and $> 0$.
4. There is no unresolved baseline revision persistence ambiguity (a null at $T$ after a prior revision).
5. $\exists t \in \{T+1, T+2, T+3\}$ such that:
   $$\text{revised\_cost}(p, t) > \text{eff\_cost}(p, T) + \epsilon$$

**Revision Types**:
- `FIRST_COST_REVISION`: $\text{revised\_cost}(p, T)$ was absent; first revision appears in forward window.
- `SUBSEQUENT_COST_REVISION`: $\text{revised\_cost}(p, T)$ was already present; higher revision appears in forward window.

### 5.3 Negative Rule ($Y = 0$)
An observation $(p, T)$ receives label $Y = 0$ if and only if:
1. $T$ and $T+3$ belong to the same continuous segment.
2. Project $p$ is observed in all forward months $t \in \{T+1, T+2, T+3\}$.
3. $\text{original\_cost}(p, T)$ is present and $> 0$.
4. No upward revision occurs: $\forall t \in \{T+1, T+2, T+3\}$, $\text{revised\_cost}(p, t) \le \text{eff\_cost}(p, T) + \epsilon$ (or is null).
5. **No unresolved future revision persistence ambiguity**: If a revision was present at $T$ or appeared in the window, no subsequent month in the window exhibits a null reset.

---

## 6. Right-Censoring and Fail-Closed Eligibility Logic

Any observation that does not satisfy both positive and negative criteria is classified into a deterministic non-eligible category:

```
Total Observations (64,608)
├── Eligible Observations (39,693) [61.44%]
│   ├── Eligible Positives (865) [2.18% of eligible]
│   └── Eligible Negatives (38,828) [97.82% of eligible]
├── Right-Censored Observations (24,152) [37.38%]
│   ├── Structural Gap or Regime Boundary (21,489)
│   └── Project Disappeared / Panel Exit before T+3 (2,663)
└── Ineligible Ambiguous Observations (763) [1.18%]
    ├── Baseline Revision Persistence Ambiguous (562)
    └── Future Revision Persistence Ambiguous (201)
```

### Deterministic Exclusion Reasons
1. `STRUCTURAL_GAP_OR_REGIME_BOUNDARY` (21,489 rows):
   Forward 3-month window crosses a known reporting gap (2023-12, 2024-04, 2024-05), the unbridged June–July 2025 identifier boundary, or the panel endpoint (May–July 2026).
2. `PROJECT_DISAPPEARED_OR_PANEL_EXIT` (2,663 rows):
   Project exits the ongoing table before completing the forward 3-month window (e.g. project completed, dropped, or paused).
3. `BASELINE_REVISION_PERSISTENCE_AMBIGUOUS` (562 rows):
   Project had an approved revision in a prior month, but report $T$ prints null for `revised_cost`. A null cannot reset approved commitments to the original baseline.
4. `FUTURE_REVISION_PERSISTENCE_AMBIGUOUS` (201 rows):
   Project had an approved revision at $T$ or early in the window, but a subsequent window month prints null without proving an upward escalation.
5. `MISSING_OR_NONPOSITIVE_BASELINE_COST` (0 rows in canonical data):
   Rejects missing, zero, or negative `original_cost` values.

---

## 7. Population Reconciliation

Deterministic accounting reconciles every single observation in `projects_monthly.csv`:

| Category | Disposition Reason | Count | % of Total |
|---|---|---:|---:|
| **Eligible Negatives** | `ELIGIBLE_NEGATIVE` | 38,828 | 60.10% |
| **Eligible Positives** | `ELIGIBLE_POSITIVE` | 865 | 1.34% |
| **Censored Boundary** | `STRUCTURAL_GAP_OR_REGIME_BOUNDARY` | 21,489 | 33.26% |
| **Censored Panel Exit** | `PROJECT_DISAPPEARED_OR_PANEL_EXIT` | 2,663 | 4.12% |
| **Ambiguous Baseline** | `BASELINE_REVISION_PERSISTENCE_AMBIGUOUS` | 562 | 0.87% |
| **Ambiguous Future** | `FUTURE_REVISION_PERSISTENCE_AMBIGUOUS` | 201 | 0.31% |
| **Missing Baseline** | `MISSING_OR_NONPOSITIVE_BASELINE_COST` | 0 | 0.00% |
| **Total Reconciled** | **Exact match to source** | **64,608** | **100.00%** |

### Breakdown by Identifier Regime and Continuous Segment

| Identifier Regime | Continuous Segment | Total Rows | Eligible Rows | Positives | Negatives | Positive Rate | Censored | Ambiguous |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **LEGACY** | `SEGMENT_1` (2023-01 to 2023-11) | 18,040 | 11,864 | 346 | 11,518 | 2.92% | 6,047 | 129 |
| **LEGACY** | `SEGMENT_2` (2024-01 to 2024-03) | 5,596 | 0 | 0 | 0 | 0.00% | 5,596 | 0 |
| **LEGACY** | `SEGMENT_3` (2024-06 to 2025-06) | 22,371 | 15,844 | 270 | 15,574 | 1.70% | 5,893 | 634 |
| **MODERN** | `SEGMENT_4` (2025-07 to 2026-07) | 18,601 | 11,985 | 249 | 11,736 | 2.08% | 6,616 | 0 |
| **TOTAL** | **All 4 Segments** | **64,608** | **39,693** | **865** | **38,828** | **2.18%** | **24,152** | **763** |

*Note on Segment 2*: Segment 2 comprises 3 calendar months (Jan–Mar 2024). Because $H=3$, any prediction window extends into April 2024 (an unbridged uncoded Annexure XVIII month). Therefore, all 5,596 observations in Segment 2 are legitimately censored by the segment boundary.

---

## 8. Temporal Feasibility and Walk-Forward Embargo

To support leak-free expanding-origin walk-forward validation in PR-07:
1. **Origin Time $T$**: Prediction is generated using information available up to month $T$.
2. **Outcome Window**: Revisions are observed strictly in months $T+1, T+2, T+3$.
3. **Walk-Forward Embargo Rule**:
   $$\text{MonthIndex}(T + 3) < \text{MonthIndex}(E)$$
   For evaluation reference month $E$, a historical training snapshot $T$ is usable only if its 3-month forward outcome window strictly closes before $E$.
4. **Stable Monthly Incidence**: The monthly temporal feasibility audit confirms positive events occur in every eligible month across 2023–2026, ranging from 1.3% to 4.5% positive rate per month.

---

## 9. Feature Leakage Audit

A comprehensive leakage boundary is defined in `schemas/cost_overrun_v1.contract.json`.

### Prohibited Leakage Fields (Strictly Excluded from Feature Matrix)
- **Target and Outcome Identifiers**:
  `target_effective_cost_esc_3m`, `cost_revision_type`, `cost_diff`, `target_event_month`, `target_event_revised_cost`, `target_window_end_month`, `baseline_cost`, `baseline_cost_source`.
- **Completed-Project Information**:
  `eventually_completed`, `completion_report_month`, `actual_completion_date`, `completed_revised_cost`, `completed_cumulative_expenditure`.
- **Non-Generalizable Identifiers**:
  `project_code`, `project_name`, `legacy_ocms_code`, `pmgid`.
- **Source Provenance Attributes**:
  `source_file`, `source_page`, `source_pages`, `source_row_number`, `source_serial_number`, `extraction_method`.
- **Future Trajectory Values**:
  Any financial, progress, or schedule revision reported at $t > T$.

### Permitted Feature Families (At Origin Time $T$)
1. **Static Categoricals**: `sector`, `agency`, `state`.
2. **Static & Snapshot Financials**: `original_cost`, `revised_cost_t`, `cumulative_expenditure_t`, `expenditure_to_original_cost_ratio`, `revised_to_original_cost_ratio`, `cost_has_been_revised`.
3. **Schedule Features**: `project_age_months`, `months_to_original_schedule`, `months_to_effective_schedule`, `schedule_revision_lag_months`, `schedule_has_been_revised`, `months_since_start`.
4. **Physical Progress**: `physical_progress_t` (where supported).
5. **Historical Lagged Deltas**: `exp_delta_1m`, `exp_delta_3m`, `past_exp_stagnant_3m`, `past_progress_delta_3m`, `past_progress_stagnant_3m`.
6. **Revision Counts & Tenure**: `n_prior_schedule_extensions`, `n_prior_cost_revisions`, `observed_tenure_months`.
7. **Presence Indicators**: `state_is_missing`, `approval_date_is_missing`, `revised_cost_is_present`, `revised_date_is_present`, etc.

The leakage audit tool confirmed zero overlap between candidate feature sets and prohibited columns (`is_leak_free: True`).

---

## 10. Viability Recommendation and Modeling Guidelines for PR-07

### Formal Recommendation: **`VIABLE_WITH_LIMITATIONS`**

Supervised machine learning model development for cost escalation in PR-07 is viable, subject to the following explicit operational boundaries:

### What PR-07 MAY Do:
1. Train supervised models on `target_effective_cost_esc_3m` across the 39,693 eligible observations.
2. Implement expanding-origin walk-forward temporal cross-validation respecting the $T+3 < E$ embargo.
3. Optimize models using **Precision-Recall AUC (PR-AUC)** as the primary discriminative metric.
4. Apply class-imbalance adaptations (e.g. class weights, focal loss, precision-recall threshold tuning).
5. Evaluate probability calibration using Brier score and Expected Calibration Error (ECE).
6. Evaluate separate models or regime indicators across Legacy (Segments 1 & 3) and Modern (Segment 4) eras.

### What PR-07 MAY NOT Do:
1. **Do NOT use raw classification accuracy or uncalibrated ROC-AUC** as the primary success metric. Under 1:44.9 imbalance, a naive dummy model predicting all negatives achieves 97.82% accuracy.
2. **Do NOT train models on `projects_completed.csv`** as ground-truth lifecycle cost overrun labels.
3. **Do NOT apply completed-project status retroactively** to ongoing monthly records.
4. **Do NOT impute unobserved cost outcomes** for right-censored ongoing projects.
5. **Do NOT allow prohibited leakage fields** into the training matrix.
6. **Do NOT cross continuous segment boundaries** (specifically June–July 2025) without an authoritative crosswalk.

---

## 11. Canonical Dataset Integrity Verification

Before, during, and after execution of PR-06, canonical dataset integrity was verified byte-for-byte:

| Dataset | Expected SHA-256 | Verified SHA-256 | Status |
|---|---|---|---|
| `data/processed/projects_monthly.csv` | `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF` | `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF` | Match (Byte-for-byte unchanged) |
| `data/processed/projects_completed.csv` | `89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910` | `89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910` | Match (Byte-for-byte unchanged) |

No canonical data files were modified.
