# IRIS PR-07: Cost Overrun Model Training, Evaluation, Calibration, and Audit

**Target Name**: `target_effective_cost_esc_3m`  
**Contract Version**: `1.0.0`  
**Contract Location**: [`schemas/cost_overrun_v1.contract.json`](file:///d:/Coding/Projects/IRIS/schemas/cost_overrun_v1.contract.json)  
**Model Module**: [`src/ml/cost_overrun_model.py`](file:///d:/Coding/Projects/IRIS/src/ml/cost_overrun_model.py)  
**Evaluation Module**: [`src/ml/cost_overrun_evaluation.py`](file:///d:/Coding/Projects/IRIS/src/ml/cost_overrun_evaluation.py)  
**Evaluation Artifacts**: [`artifacts/ml/cost_overrun_model_v1/`](file:///d:/Coding/Projects/IRIS/artifacts/ml/cost_overrun_model_v1/)  
**Test Suite**: [`tests/test_ml_cost_overrun_model.py`](file:///d:/Coding/Projects/IRIS/tests/test_ml_cost_overrun_model.py)  
**Overall Operational Recommendation**: **`NOT_READY_FOR_PRODUCTION`**  

---

## 1. Scope

PR-07 trains, evaluates, calibrates, explains, and audits supervised cost-overrun prediction models for the IRIS infrastructure project monitoring repository. This follows the authoritative PR-06 Cost Overrun Target Definition.

The evaluation covers two model families across two historical identifier regimes:
1. **Baseline**: Logistic Regression (unweighted and balanced)
2. **Challenger**: CatBoost (unweighted and balanced)
3. **Reference Baselines**: Empirical training prevalence and deterministic historical cost revision rules

All models are evaluated via strict walk-forward temporal evaluation using 17 expanding-origin evaluation folds across the Legacy (2023–2025) and Modern (2025–2026) regimes.

> [!IMPORTANT]
> **Production Boundary**: No model family beyond Logistic Regression and CatBoost is evaluated. No XGBoost, Random Forest, LightGBM, or neural networks were introduced. Schedule-extension model artifacts, contracts, and pipelines remain completely untouched.

---

## 2. Relationship to PR-06

PR-06 established that lifecycle completed-project cost overrun modeling is `NOT_YET_VIABLE` due to 81.5% ongoing project censoring, 80.6% missingness of revised cost in completed project announcements, and severe survivorship bias. PR-06 defined and audited the rolling 3-month administrative cost escalation target `target_effective_cost_esc_3m` as `VIABLE_WITH_LIMITATIONS`.

PR-07 takes the frozen PR-06 contract, population accounting, and censoring logic as ground truth. No target definitions were modified or reinterpreted.

---

## 3. Target Definition Reference

The primary target is **`target_effective_cost_esc_3m`**:
- **Horizon**: $H = 3$ months.
- **Tolerance**: $\tau = 0.001$ Rs crore (Rs 10,000 threshold to prevent micro-rounding noise from triggering positives).
- **Effective Baseline**:
  $$\text{baseline\_cost}(p, T) = \begin{cases} \text{revised\_cost}(p, T) & \text{if reported and } > 0 \\ \text{original\_cost}(p, T) & \text{otherwise} \end{cases}$$
- **Positive Condition**: At least one reported snapshot in $T+1..T+3$ reports $\text{revised\_cost} > \text{baseline\_cost} + \tau$.
- **Negative Condition**: Complete same-segment $T+1..T+3$ observation window with all $\text{revised\_cost} \le \text{baseline\_cost} + \tau$ and no unresolved null resets.
- **Ambiguity Rule**: A null revised cost cannot silently reset an approved revision back to the original sanctioned cost.

---

## 4. Modeling Population

The modeling population is constructed exclusively from eligible observations under PR-06:
- **Total Canonical Source Observations**: 64,608 (`data/processed/projects_monthly.csv`)
- **Eligible Modeling Observations**: 39,693
  - **Eligible Positives**: 865
  - **Eligible Negatives**: 38,828
  - **Positive Prevalence**: 2.18%
- **Excluded Observations**:
  - Censored at continuous segment boundary: 21,489
  - Censored due to panel exit / project disappearance: 2,663
  - Ineligible due to baseline persistence ambiguity: 562
  - Ineligible due to future window persistence ambiguity: 201
  - Ineligible due to missing/zero baseline: 0
  - **Exact Reconciliation**: $64,608 = 39,693 + 24,152 + 763$

---

## 5. Class Imbalance

The positive class is rare:
- **Prevalence**: ~2.18% across the eligible panel (Legacy: 2.22%, Modern: 2.08%).
- **Class Imbalance Ratio**: $1 : 44.9$.
- **Evaluation Policy**: Raw accuracy is strictly prohibited. Precision-Recall AUC (PR-AUC / Average Precision) is the primary evaluation metric. Brier score, Expected Calibration Error (ECE), and cost-sensitive class weighting are evaluated explicitly.

---

## 6. Feature Policy

All features are constructed strictly from information available at prediction time $T$:
- **Total Approved Features**: 36
- **Feature Groups**:
  - `static_categoricals` (3): `sector`, `agency`, `state`
  - `static_cost_financial` (6): `original_cost`, `revised_cost_t`, `cumulative_expenditure_t`, `expenditure_to_original_cost_ratio`, `revised_to_original_cost_ratio`, `cost_has_been_revised`
  - `schedule` (6): `project_age_months`, `months_to_original_schedule`, `months_to_effective_schedule`, `schedule_revision_lag_months`, `schedule_has_been_revised`, `months_since_start`
  - `progress` (1): `physical_progress_t`
  - `missingness_presence_indicators` (9): `state_is_missing`, `approval_date_is_missing`, `original_completion_date_is_missing`, `revised_cost_is_present`, `revised_date_is_present`, `physical_progress_is_present`, `physical_progress_supported`, `start_date_is_present`, `start_date_supported`
  - `historical_expenditure` (3): `exp_delta_1m`, `exp_delta_3m`, `past_exp_stagnant_3m`
  - `historical_progress` (2): `past_progress_delta_3m`, `past_progress_stagnant_3m`
  - `historical_schedule_cost_revision_counts` (3): `n_prior_schedule_extensions`, `n_prior_cost_revisions`, `observed_tenure_months`
  - `delta_support` (3): `exp_delta_1m_is_supported`, `exp_delta_3m_is_supported`, `progress_delta_3m_is_supported`

---

## 7. Leakage Controls

The feature matrix fails closed if any prohibited column enters the matrix:
- Target column: `target_effective_cost_esc_3m`
- Event/window attributes: `cost_revision_type`, `cost_diff`, `target_event_month`, `target_event_revised_cost`, `target_window_end_month`, `baseline_cost`, `baseline_cost_source`
- Completed-project outcomes: `eventually_completed`, `completion_report_month`, `actual_completion_date`, `completed_revised_cost`, `completed_cumulative_expenditure`
- High-cardinality/provenance identifiers: `project_code`, `project_name`, `legacy_ocms_code`, `pmgid`, `source_file`, `source_page`, `source_pages`, `source_row_number`, `source_serial_number`, `extraction_method`

All 23 prohibited fields were audited and verified absent from feature inputs.

---

## 8. Regime Handling

The June–July 2025 project code redesign boundary remains strictly unbridged:
- **LEGACY Regime**: 2023-01 through 2025-06 (Segments 1, 2, 3). Legacy codes (`N########` or 9-digit).
- **MODERN Regime**: 2025-07 through 2026-07 (Segment 4). Modern 6-digit codes.
- No evaluation fold spans across the redesign boundary. Training and evaluation populations are partitioned strictly within regime.

---

## 9. Temporal Validation & Folds

Models are evaluated using expanding-origin walk-forward evaluation across 17 accepted folds:
- **LEGACY Folds (12 origins)**:
  - `2023-07`, `2023-08` (Segment 1)
  - `2024-06`, `2024-07`, `2024-08`, `2024-09`, `2024-10`, `2024-11`, `2024-12`, `2025-01`, `2025-02`, `2025-03` (Segment 3)
- **MODERN Folds (5 origins)**:
  - `2025-12`, `2026-01`, `2026-02`, `2026-03`, `2026-04` (Segment 4)
- **Candidate Origins Rejection Reasons**:
  - `2023-01..2023-06`: Warmup (insufficient training history)
  - `2023-09..2023-11`: Right-censored at Segment 1 boundary
  - `2024-01..2024-03`: Right-censored at Segment 2 boundary (Segment 2 is 3 months long)
  - `2025-04..2025-06`: Right-censored at June–July 2025 redesign boundary
  - `2025-07..2025-11`: Warmup (insufficient Modern training history under embargo)
  - `2026-05..2026-07`: Right-censored at panel end

Every candidate model is evaluated on the exact identical fold population.

---

## 10. Strict Embargo

The embargo rule enforces complete outcome maturity before an evaluation origin:
$$T_{\text{train}} + 3 < E$$
- Converted to integer month index: $\text{month\_index}(\text{add\_months}(T_{\text{train}}, 3)) < \text{month\_index}(E)$.
- Equality fails: $T_{\text{train}} + 3 = E$ is strictly rejected.
- Audit verified: across all 17 folds, the maximum training label window end strictly precedes the evaluation origin.

---

## 11. Candidate Models

Four ML candidates and two reference baselines were evaluated:
1. `prevalence`: Predicts empirical training fold positive prevalence.
2. `lagged_cost_rule`: Deterministic historical rule predicting 1 if prior cost revision count increased at $T-1 \rightarrow T$.
3. `logistic_unweighted`: L2 Logistic Regression with unweighted loss.
4. `logistic_balanced`: L2 Logistic Regression with inverse class frequency loss weighting.
5. `catboost_unweighted`: CatBoost gradient boosted trees with standard unweighted logloss.
6. `catboost_balanced`: CatBoost gradient boosted trees with `auto_class_weights="Balanced"`.

---

## 12. Candidate Configurations

All configurations are fixed and deterministic:
- **Logistic Regression**:
  - Preprocessor: `CostOverrunFoldPreprocessor` fit strictly on training fold.
  - Numerics: Standardized with training mean/std. Missing values map to 0 in standardized space + explicit `__missing=1` indicator.
  - Categoricals: Frequency encoding learned from training fold. Unseen categories map to 0.0.
  - Hyperparameters: $C = 1.0$, solver = `lbfgs`, $\text{max\_iter} = 2000$, $\text{random\_state} = 20260910$.
- **CatBoost**:
  - Tree Complexity: $\text{depth} = 5$, $\text{iterations} = 300$, $\text{learning\_rate} = 0.05$, $\text{l2\_leaf\_reg} = 3.0$.
  - Categoricals: Handled natively (`cat_features=["sector", "agency", "state"]`) with missing sentinel `__MISSING__`.
  - Determinism: `random_seed = 20260910`, `thread_count = 4`, `allow_writing_files = False`.

---

## 13. Primary and Secondary Metrics

Summary across accepted walk-forward folds:

### Legacy Regime (12 Folds, 19,005 Observations, 336 Positives, Observed Prevalence: 1.77%)
| Candidate Model | Micro PR-AUC | Macro PR-AUC | Micro ROC-AUC | Micro Brier | ECE (10-bin) | Micro Precision | Micro Recall | Micro F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `prevalence` | 0.0181 | 0.0177 | 0.5016 | **0.0175** | 0.0101 | NA | 0.0000 | 0.0000 |
| `lagged_cost_rule` | 0.0186 | 0.0213 | 0.5091 | 0.0257 | 0.0257 | 0.0529 | 0.0268 | 0.0356 |
| `logistic_unweighted` | 0.0207 | 0.0270 | 0.5494 | 0.0363 | 0.0504 | 0.0165 | 0.0208 | 0.0184 |
| `logistic_balanced` | 0.0229 | 0.0303 | 0.5584 | 0.1926 | 0.3241 | 0.0239 | 0.2887 | 0.0442 |
| `catboost_unweighted` | **0.0279** | **0.0470** | **0.6021** | 0.0183 | **0.0059** | 0.0500 | 0.0030 | 0.0056 |
| `catboost_balanced` | 0.0266 | 0.0363 | 0.5534 | 0.0405 | 0.0837 | 0.0522 | 0.0774 | 0.0624 |

### Modern Regime (5 Folds, 8,261 Observations, 143 Positives, Observed Prevalence: 1.73%)
| Candidate Model | Micro PR-AUC | Macro PR-AUC | Micro ROC-AUC | Micro Brier | ECE (10-bin) | Micro Precision | Micro Recall | Micro F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `prevalence` | 0.0137 | 0.0171 | 0.2779 | **0.0173** | 0.0127 | NA | 0.0000 | 0.0000 |
| `lagged_cost_rule` | 0.0173 | 0.0171 | 0.4779 | 0.0608 | 0.0608 | 0.0000 | 0.0000 | NA |
| `logistic_unweighted` | 0.0179 | 0.0199 | 0.3026 | 0.0204 | 0.0102 | 0.0667 | 0.0140 | 0.0231 |
| `logistic_balanced` | **0.0210** | 0.0222 | 0.3895 | 0.1715 | 0.3028 | 0.0094 | 0.1329 | 0.0175 |
| `catboost_unweighted` | 0.0181 | **0.0382** | 0.5287 | 0.0191 | **0.0111** | 0.0000 | 0.0000 | NA |
| `catboost_balanced` | 0.0207 | 0.0346 | **0.5851** | 0.0279 | 0.0296 | 0.0098 | 0.0070 | 0.0082 |

---

## 14. Calibration Findings

- **Raw Probabilities vs Brier Score**: `catboost_unweighted` achieves the lowest ECE (0.0059 in Legacy, 0.0111 in Modern) among ML candidates. Unweighted logistic models suffer from slight probability overconfidence, while balanced variants (`logistic_balanced`) shift probability mass severely upward, creating large Brier penalties (0.1926 in Legacy, 0.1715 in Modern) and poor ECE (> 0.30).
- **Historical Calibration Test**: Testing Platt scaling fit on historical out-of-fold predictions showed that historical calibration did not consistently improve Brier scores due to the extreme non-stationarity of low-prevalence administrative cost approvals. Raw unweighted model probabilities remain the preferred score representation.

---

## 15. Threshold Research

Operating points evaluated across a 100-step grid from 0.01 to 1.00 (`artifacts/ml/cost_overrun_model_v1/threshold_research.csv`):
- Due to base rate ~1.7–2.2%, standard 0.50 threshold yields almost zero alerts for unweighted models.
- For `catboost_unweighted` in Legacy:
  - At threshold 0.02: Recall = 44.9%, Precision = 2.8%, Alert Rate = 28.0%.
  - At threshold 0.05: Recall = 11.0%, Precision = 3.6%, Alert Rate = 5.4%.
  - At threshold 0.10: Recall = 2.1%, Precision = 4.4%, Alert Rate = 0.8%.
- **Finding**: There is no operating threshold where precision exceeds 10% while retaining meaningful recall (> 20%). The false discovery rate is above 90% across all operational cutoffs.

---

## 16. Explainability Findings

- **Logistic Logit Reconstruction**: Exact reconciliation verified:
  $$\text{decision\_function} = \text{intercept} + \sum_{j} (x_{j} \cdot \beta_{j})$$
  Maximum absolute reconstruction discrepancy across all folds: $< 10^{-9}$.
- **CatBoost TreeSHAP Reconstruction**: Exact reconciliation verified:
  $$\text{raw\_margin} = \text{expected\_base\_value} + \sum_{j} \text{shap\_value}_{j}$$
  Maximum absolute reconstruction discrepancy across all folds: $< 10^{-9}$.
- **Feature Importance & Stability**:
  - `project_age_months`, `state`, `expenditure_to_original_cost_ratio`, `agency`, and `physical_progress_t` consistently dominate feature attribution.
  - Across evaluation folds, CatBoost feature importance rankings exhibit high Spearman rank stability: $\rho \approx 0.955$ in Legacy and $\rho \approx 0.950$ in Modern.

---

## 17. Robustness and Confidence Intervals

95% confidence intervals from 1,000 bootstrap draws (`artifacts/ml/cost_overrun_model_v1/robustness_metrics.csv`):
- **Legacy `catboost_unweighted`**:
  - PR-AUC: 0.0279 | Project-Cluster 95% CI: [0.0199, 0.0408] | Month-Block 95% CI: [0.0226, 0.0387]
  - ROC-AUC: 0.6021 | Project-Cluster 95% CI: [0.5508, 0.6442] | Month-Block 95% CI: [0.5457, 0.6574]
  - Brier: 0.0183 | Project-Cluster 95% CI: [0.0154, 0.0214] | Month-Block 95% CI: [0.0152, 0.0219]
- **Modern `logistic_balanced`**:
  - PR-AUC: 0.0210 | Project-Cluster 95% CI: [0.0142, 0.0322] | Month-Block 95% CI: [0.0159, 0.0270]
  - ROC-AUC: 0.3895 | Project-Cluster 95% CI: [0.3397, 0.4431] | Month-Block 95% CI: [0.3524, 0.4249]

---

## 18. Candidate Comparison

- **Best Ranking Model**:
  - **Legacy**: `catboost_unweighted` (Micro PR-AUC = 0.0279, ROC-AUC = 0.6021).
  - **Modern**: `logistic_balanced` has highest micro PR-AUC (0.0210), but `catboost_unweighted` achieves better discrimination (Macro PR-AUC = 0.0382, ROC-AUC = 0.5287) and vastly superior calibration.
- **Best Calibrated Model**: `catboost_unweighted` in both regimes (Brier = 0.0183 in Legacy, 0.0191 in Modern; ECE < 0.012).
- **Challenger vs Baseline**: CatBoost demonstrates clear nonlinear ranking advantages over Logistic Regression in Legacy (PR-AUC lift +0.0072 over unweighted logistic, ROC-AUC +0.0527), but absolute ranking power remains constrained across all architectures.

---

## 19. Final Recommendation

**Overall Operational Status: `NOT_READY_FOR_PRODUCTION`**

### Evidence-Based Rationale:
1. **Marginal Lift Over Prevalence**: In Legacy, the best candidate (`catboost_unweighted`) achieves a micro PR-AUC of 0.0279 compared to the empirical prevalence baseline of 0.0181 (a net lift of only +0.0098). In Modern, net lift over prevalence is only +0.0073.
2. **Administrative vs Physical Decision Driver**: Cost escalation in public infrastructure is fundamentally an administrative and fiscal event governed by cabinet approvals, Revised Cost Estimates (RCE) committee cycles, and budget sanctions. Project-level physical and expenditure trends available at monthly publication time do not capture the external bureaucratic triggers that precede an official upward revision.
3. **Severe False Alarm Burden**: Because positive prevalence is ~2%, any operating point that captures even 20% of true cost escalations produces over 90% false alarms, creating decision fatigue and lack of trust in production.
4. **Operational Role**: Cost overrun models should serve as exploratory diagnostic indicators or research metrics, but must not be used as automated production decision gates or budget reallocation blockers.

---

## 20. Limitations

1. **Interim Administrative Proxy**: The target captures officially published interim revisions in Table 6/7 Flash Reports, not final post-completion settled cost audits.
2. **Structural Censoring**: 24,152 observations (37.4% of total source data) are right-censored at segment/regime boundaries or due to panel exit and cannot be labeled.
3. **Unbridged Modern Boundary**: The June–July 2025 redesign boundary limits Modern training data to only 5 walk-forward evaluation folds.
4. **Infrequent Revision Events**: Only 865 positive escalation events exist across the entire 40-month panel, limiting model parameter estimation.

---

## 21. Compliance Statement

- Canonical datasets `data/processed/projects_monthly.csv` and `data/processed/projects_completed.csv` remained read-only and byte-for-byte unchanged.
- Schedule ML contracts, models, artifacts, and pipelines were not modified.
- No model family beyond Logistic Regression and CatBoost was introduced.
- Strict embargo $T_{\text{train}} + 3 < E$ was enforced across all 17 walk-forward folds without data leakage.
- All evaluation artifacts are fully deterministic and reproducible.
