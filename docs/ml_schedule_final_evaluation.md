# IRIS v1 Schedule Extension Prediction: Final Model Evaluation & Calibration Report

**Version**: 1.0  
**Date**: 2026-09-10  
**Status**: Authoritative Final Evaluation Evidence (PR-05)  
**Target**: `target_effective_schedule_ext_3m` (Horizon $H = 3$ months)  
**Machine-Readable Evaluation Artifacts**: `artifacts/ml/schedule_extension_3m/final_evaluation/`  

---

## 1. Scope and Executive Summary

This report delivers the authoritative, reproducible, and auditable final evaluation evidence and calibration audit for the locked IRIS v1 schedule-extension prediction models.

The evaluation covers:
1. **Walk-Forward Evaluation Performance**: 17 accepted temporal walk-forward evaluation folds.
2. **Calibration Analysis & Diagnostics**: 10-bin reliability analysis, Brier scores, calibration slopes, intercepts, and Platt scaling behavior.
3. **Threshold Research**: Empirical trade-off curves across a fine grid ($\tau \in [0.01, 0.99]$) and history-only operational policy thresholds.
4. **Error Analysis**: Quantitative and qualitative profiling of false positives and false negatives, temporal distribution, feature profiles across confusion quadrants, and project-level repeat error clustering.
5. **Subgroup Analysis**: Segment-faithful performance across sectors, cost brackets, project maturity brackets, revision status, and continuous segments.
6. **Robustness & Uncertainty Auditing**: Clustered project bootstrap (1,000 draws), temporal month-block bootstrap (1,000 draws), cross-fold stability, and multi-view aggregation comparisons.

---

## 2. Locked Models Evaluated

Model-family selection for IRIS v1 is formally closed. No challenger models, tree ensembles, neural networks, or hyperparameter changes were introduced.

| Identifier Regime | Locked Model Identifier | Family & Preprocessing | Feature Count & Families | Operational Scoring Policy |
|---|---|---|---|---|
| **LEGACY** (2023-01 to 2025-06) | `catboost_full_v1__unweighted` | CatBoostClassifier (300 trees, depth 5, lr 0.05, l2 3.0, unweighted) | 36 features (`FULL_V1_FEATURES`): static categoricals, cost/financial, schedule, progress, trajectory, missingness indicators | Uncalibrated native risk probabilities ($P \in [0, 1]$). |
| **MODERN** (2025-07 to 2026-07) | `logistic_static_only__unweighted` | LogisticRegression (L2, $C=1.0$, unweighted) + `FoldPreprocessor` (standardization + missing indicators + train frequency) | 25 features (`STATIC_AT_T_FEATURES`): static categoricals, static cost/financial, static schedule, missingness indicators | Platt calibrated on raw logits where mature historical OOF history is available (Fold M5 / `2026-04`); raw logistic probabilities on early folds (M1–M4). |

---

## 3. Frozen Contract Reference & Canonical Inputs

All evaluation data, feature definitions, and target rules conform to the frozen ML data contract (`schemas/schedule_extension_3m_v1.contract.json`, `src/ml/data_contract.py`).

### Canonical Datasets
- `data/processed/projects_monthly.csv`: **64,608 rows**, SHA-256: `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF`
- `data/processed/projects_completed.csv`: **876 rows**, SHA-256: `89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910`

### Serialized Model Artifacts
- `artifacts/ml/schedule_extension_3m/legacy_catboost/model.cbm`: SHA-256: `59586004F5967602651156E0A26FE564015F240958F5416CBB565E4755C524EE`
- `artifacts/ml/schedule_extension_3m/modern_logistic/model.joblib`: SHA-256: `679D9768869088BA8CEE297577B1935DCF903F00B38697BF9A3FFA2F7DEB5082`

Both canonical datasets and serialized model binaries remain byte-for-byte unchanged.

---

## 4. Evaluation Population & Fold Reconciliation

The evaluation strictly reconciles against the canonical datasets and authoritative ML dataset manifest:

```
Total Canonical Monthly Observations: 64,608 rows
├── Eligible Observations (Contract Satisfied): 37,305 rows
│   ├── Legacy Eligible: 25,406 rows (2,634 positives, 10.37% prevalence)
│   │   ├── Evaluated in Accepted Walk-Forward Folds: 16,999 rows (1,606 positives, 9.45% prevalence)
│   │   └── Pre-Evaluation / Training-Only History: 8,407 rows
│   └── Modern Eligible: 11,899 rows (4,327 positives, 36.36% prevalence)
│       ├── Evaluated in Accepted Walk-Forward Folds: 8,190 rows (3,680 positives, 44.93% prevalence)
│       └── Pre-Evaluation / Training-Only History: 3,709 rows
└── Ineligible Observations (Structural Exclusions): 27,303 rows
    ├── Legacy Ineligible: 20,601 rows
    │   ├── STRUCTURAL_GAP_OR_REGIME_BOUNDARY: 15,880 rows
    │   ├── PROJECT_DISAPPEARED_OR_MONTH_MISSING: 1,656 rows
    │   ├── FUTURE_REVISION_PERSISTENCE_AMBIGUOUS: 1,653 rows
    │   ├── BASELINE_REVISION_PERSISTENCE_AMBIGUOUS: 888 rows
    │   └── MISSING_BASELINE_COMPLETION_COMMITMENT: 524 rows
    └── Modern Ineligible: 6,702 rows
        ├── STRUCTURAL_GAP_OR_REGIME_BOUNDARY: 5,609 rows
        ├── PROJECT_DISAPPEARED_OR_MONTH_MISSING: 1,007 rows
        ├── FUTURE_REVISION_PERSISTENCE_AMBIGUOUS: 57 rows
        └── BASELINE_REVISION_PERSISTENCE_AMBIGUOUS: 29 rows
```

Total evaluation observations evaluated across the 17 walk-forward origins: **25,189 rows** (16,999 Legacy + 8,190 Modern).

---

## 5. Temporal Validation Methodology & Embargo Enforcement

### Strict Embargo Arithmetic: $T_{\text{train}} + H < E$
To prevent look-ahead bias and forward window leakage at horizon $H = 3$:
$$\text{month\_index}(T_{\text{train}}) + 3 < \text{month\_index}(E)$$

- **Strict Inequality Enforced**: For any training observation month $T$, its forward 3-month label verification window ends at $T + 3$. If $T + 3 = E$, the label event window overlaps into evaluation month $E$; therefore, equality is strictly forbidden and rejected.
- **Fail-Closed Verification**: A test confirming that $T + 3 == E$ fails validation was executed and verified for all 17 folds.
- **Temporally Ordered Folds**: Folds are evaluated in chronological sequence without random shuffling or train/test splits.

### Accepted Walk-Forward Folds:
- **Legacy (12 folds)**: `2023-07`, `2023-08`, `2024-06`, `2024-07`, `2024-08`, `2024-09`, `2024-10`, `2024-11`, `2024-12`, `2025-01`, `2025-02`, `2025-03`
- **Modern (5 folds)**: `2025-12`, `2026-01`, `2026-02`, `2026-03`, `2026-04`

Structural gap months (`2023-12`, `2024-04`, `2024-05`, and unbridged months) remain fail-closed.

---

## 6. Primary Performance Metrics

Metrics are evaluated independently across both regimes.

### Regime Summary:
| Metric | Legacy CatBoost (Operational) | Modern Logistic (Raw Baseline) | Modern Logistic (Operational Platt) |
|---|---|---|---|
| **Evaluation Folds** | 12 | 5 | 5 |
| **Evaluation Observations** | 16,999 | 8,190 | 8,190 |
| **Observed Positives** | 1,606 | 3,680 | 3,680 |
| **Empirical Prevalence** | 9.45% | 44.93% | 44.93% |
| **Pooled Average Precision (AP)** | **0.4071** | **0.7587** | **0.7487** |
| **Pooled ROC-AUC** | **0.8064** | **0.8419** | **0.8345** |
| **Brier Score** | **0.0720** | **0.1916** | **0.1890** |
| **Expected Calibration Error (ECE, 10-bin)** | **0.0287** | **0.1405** | **0.1297** |
| **Precision ($\tau = 0.5$)** | 0.5426 | 0.8083 | 0.7719 |
| **Recall ($\tau = 0.5$)** | 0.2540 | 0.3620 | 0.5057 |
| **F1 Score ($\tau = 0.5$)** | 0.3461 | 0.5000 | 0.6111 |
| **Macro Fold AP Mean** | 0.4184 | 0.7516 | 0.7516 |
| **Row-Weighted Fold AP Mean** | 0.4093 | 0.7523 | 0.7523 |

### Walk-Forward Granular Results (`fold_metrics.csv`):
- **Legacy CatBoost**: AP ranges from 0.0711 (in anomalous low-volume month `2025-02`) to 0.6328 (`2024-11`), with a macro mean of 0.4184 (std: 0.1628).
- **Modern Logistic**: AP is stable across all 5 evaluation origins, ranging from 0.6916 (`2026-03`) to 0.8010 (`2026-02`), with a macro mean of 0.7516 (std: 0.0467).

---

## 7. Calibration Findings & Diagnostics

Calibration evaluates how closely predicted probabilities reflect actual empirical delay frequencies.

### Calibration Summary (`calibration_metrics.csv`):
- **Legacy Regime**:
  - CatBoost native predictions exhibit high calibration fidelity out-of-the-box on the low-prevalence portfolio: mean predicted probability is **0.1020** vs empirical prevalence **0.0945**.
  - ECE is exceptionally low at **0.0287**; Brier score is **0.0720**.
  - Logistic calibration regression yields a slope of **0.6878** and intercept of **-0.6029**.
  - **Decision**: Legacy CatBoost operates uncalibrated; post-hoc scaling is unnecessary and would risk overfitting.
- **Modern Regime**:
  - Raw unweighted Logistic Regression exhibits systematic underprediction: mean predicted probability is **0.3174** against an empirical prevalence of **0.4493** (net bias of -0.1319).
  - Raw ECE is elevated at **0.1405**; calibration intercept is **+0.8794** (indicating systematic negative log-odds shift).
  - **Leakage-Safe Platt Calibration**: Under strict sub-embargo ($T' + 3 < T$), chronological out-of-fold calibration pools are structurally unavailable for folds M1–M3 and provisional for M4 (772 rows < 1,000 threshold). On fold M5 (`2026-04`), a 2,110-row pool across two mature months (`2025-11`, `2025-12`) is unlocked, yielding fitted Platt parameters:
    $$\text{slope} = 1.2063, \quad \text{intercept} = 0.4551$$
  - Applying Platt calibration to M5 reduces its fold ECE from **0.1122** to **0.0854** and improves Brier score from **0.1802** to **0.1671**.
  - Across the pooled Modern regime, operational calibration reduces pooled ECE from **0.1405** to **0.1297** and improves Brier score from **0.1916** to **0.1890**.

---

## 8. Threshold Research Findings

Threshold research analyzes trade-offs across operating points separately from scoring.

### Operating Curve Highlights (`threshold_research.csv`):

#### Legacy Regime (Prevalence ~9.45%):
- At default $\tau = 0.50$: Precision = 0.5426, Recall = 0.2540, Alert Rate = 4.42% (752 alerts).
- At $\tau = 0.20$: Precision = 0.3204, Recall = 0.6389, Alert Rate = 18.84% (3,203 alerts).
- At $\tau = 0.10$ (~prevalence): Precision = 0.2185, Recall = 0.8144, Alert Rate = 35.19% (5,982 alerts).
- At $\tau \ge 0.90$: High precision (0.7692 at $\tau=0.90$) with very low alert volume (39 alerts).

#### Modern Regime (Prevalence ~44.93%):
- At default $\tau = 0.50$: Precision = 0.7719, Recall = 0.5057, Alert Rate = 29.43% (2,410 alerts).
- At $\tau = 0.40$: Precision = 0.6729, Recall = 0.7495, Alert Rate = 50.05% (4,099 alerts).
- At $\tau = 0.30$: Precision = 0.5693, Recall = 0.9141, Alert Rate = 72.15% (5,909 alerts).
- At $\tau = 0.70$: Precision = 0.8845, Recall = 0.2223, Alert Rate = 11.29% (925 alerts).

### Handling of Undefined Precision:
For extreme thresholds where alert count is zero (e.g. $\tau \ge 0.96$ in Modern where max score is 0.957), precision is undefined. The pipeline records `precision = None` (serialized as empty string) without coercing to zero.

---

## 9. Error Analysis

Error analysis evaluates False Positives (FP) and False Negatives (FN) across feature distributions, temporal origins, and project repeat-error clustering (`error_analysis.csv`).

### Confusion Matrix at $\tau = 0.50$:
- **Legacy**:
  - TP: 408 (2.40%), FP: 344 (2.02%), FN: 1,198 (7.05%), TN: 15,049 (88.53%).
  - False Positive Rate (FPR): 2.23%; False Negative Rate (FNR): 74.60%.
- **Modern**:
  - TP: 1,861 (22.72%), FP: 549 (6.70%), FN: 1,819 (22.21%), TN: 3,961 (48.36%).
  - False Positive Rate (FPR): 12.17%; False Negative Rate (FNR): 49.43%.

### Feature Profile Contrasts Across Quadrants:
1. **Physical Progress**:
   - In both regimes, True Negatives and False Positives show substantially higher physical progress (~50–65%) than False Negatives (~25–35%). False Negatives represent early/mid-stage projects where physical progress is modest, but extension risk was not sufficiently flagged by static features.
2. **Project Maturity (Age)**:
   - False Positives tend to have longer project tenure / age (mean ~90–110 months in Legacy) and higher prior schedule extensions (~1.5–2.2 extensions), causing the model to anticipate further extensions that did not occur in the 3-month window.
3. **Expenditure Ratio**:
   - False Positives exhibit higher expenditure-to-cost ratios (~0.55–0.70) than True Negatives (~0.30–0.45).

### Project-Level Repeat Error Clustering:
- **Legacy Regime**:
  - 344 FPs were generated by **178 unique projects**. Of these, 64 projects generated $\ge 2$ false alarms, accounting for **66.86%** of all false alarms.
  - 1,198 FNs were generated by **567 unique projects**. 327 projects missed extensions in $\ge 2$ months, accounting for **79.80%** of all false negatives.
- **Modern Regime**:
  - 549 FPs were generated by **355 unique projects**. 126 projects generated $\ge 2$ false alarms, accounting for **58.29%** of all false alarms.
  - 1,819 FNs were generated by **947 unique projects**. 504 projects had missed extensions in $\ge 2$ months, accounting for **75.54%** of all false negatives.
- **Takeaway**: Errors are heavily clustered in repeat projects with chronic slow-burn execution patterns.

---

## 10. Subgroup Analysis

Subgroup performance was audited across valid metadata dimensions (`subgroup_metrics.csv`). Small groups ($N < 50$ or positives $< 5$) are marked with `statistically_insufficient = True`.

### Key Subgroup Findings:
1. **Sectors**:
   - **Road Transport & Highways**: Consistently the largest sector (Legacy $N=7,078$, Modern $N=3,506$). Legacy AP = **0.3701**, Modern AP = **0.7818**.
   - **Railways**: Legacy $N=4,342$ (AP = **0.4285**), Modern $N=2,323$ (AP = **0.7410**).
   - **Petroleum**: Lower base-rate in Legacy (prev 5.25%, AP = **0.3800**); higher base-rate in Modern (prev 38.38%, AP = **0.7028**).
   - **Power**: Legacy $N=1,467$ (AP = **0.4253**), Modern $N=586$ (AP = **0.7180**).
2. **Project Scale / Cost Brackets**:
   - Mega-projects ($\ge 5,000$ cr) exhibit higher extension prevalence (~15% Legacy, ~52% Modern) and higher AP (**0.5186** in Legacy, **0.8037** in Modern).
   - Small projects ($< 500$ cr) have lower base rates and lower AP (**0.3392** in Legacy, **0.6729** in Modern).
3. **Project Maturity (Age Brackets)**:
   - Mature projects ($\ge 5$ years old) show higher prevalence and stronger model discrimination (Legacy AP = **0.4371**, Modern AP = **0.7891**).
   - Young projects ($< 2$ years old) have fewer historical indicators (Legacy AP = **0.2646**).
4. **Prior Schedule Revision Status**:
   - Projects that have already experienced a schedule revision at baseline $T$ have substantially higher push-out rates (~15.8% vs 4.7% in Legacy) and higher AP (**0.4851** vs **0.2562** in Legacy; **0.8252** vs **0.6381** in Modern).

---

## 11. Robustness Findings & Bootstrap Confidence Intervals

Robustness was quantified using 1,000-iteration cluster and block resampling (`robustness_metrics.csv`):

### Project-Cluster vs Month-Block 95% Confidence Intervals:
| Regime | Model | Metric | Point Estimate | Project-Cluster 95% CI | Month-Block 95% CI |
|---|---|---|---|---|---|
| **LEGACY** | CatBoost (full_v1) | **Average Precision** | **0.4071** | [0.3515, 0.4594] | [0.3456, 0.4905] |
| **LEGACY** | CatBoost (full_v1) | **ROC-AUC** | **0.8064** | [0.7857, 0.8271] | [0.7766, 0.8351] |
| **LEGACY** | CatBoost (full_v1) | **Brier Score** | **0.0720** | [0.0667, 0.0772] | [0.0634, 0.0805] |
| **MODERN** | Logistic (static_only, op) | **Average Precision** | **0.7487** | [0.7225, 0.7770] | [0.7092, 0.7869] |
| **MODERN** | Logistic (static_only, op) | **ROC-AUC** | **0.8345** | [0.8202, 0.8490] | [0.8122, 0.8524] |
| **MODERN** | Logistic (static_only, op) | **Brier Score** | **0.1890** | [0.1818, 0.1963] | [0.1706, 0.2078] |

- **Cluster Stability**: Project-cluster intervals strictly exclude zero and confirm strong discriminative capability.
- **Month-Block Variance**: Month-block bootstrap intervals are wider than project-cluster intervals, reflecting macro-level temporal co-movements and seasonal reporting patterns across ministries.

---

## 12. Known Limitations

1. **Uncalibrated Early Modern Folds (M1–M3)**:
   - Under strict nested sub-embargo ($T' + 3 < T$), Modern folds M1–M3 lack sufficient mature chronological history for out-of-fold calibration. Manufacturing calibration data by relaxing the label embargo was strictly rejected to preserve temporal integrity.
2. **Legacy Regime Code Shift**:
   - January–June 2025 use legacy $N\#\#\#\#\#\#\#\#$ identifiers; July 2025 onward uses 6-digit codes. Direct project-code overlap across the June–July boundary is zero. The two regimes must remain strictly separated.
3. **Historical Structural Gaps**:
   - Months `2023-12`, `2024-04`, and `2024-05` structurally lack continuous reporting and remain excluded from evaluation.
4. **Asymmetric Error Trade-offs**:
   - At $\tau = 0.50$, Legacy CatBoost achieves high precision (0.5426) but low recall (0.2540). Operational users requiring high recall ($\ge 60\%$) should operate at historical recall-floor thresholds ($\tau \approx 0.20–0.25$).

---

## 13. Compliance Statement

- **No New Model Family**: No challenger models (XGBoost, Random Forest, LightGBM, Neural Networks) were trained or evaluated.
- **No Hyperparameter Tuning**: Model architectures, tree depths, learning rates, and regularization penalties are locked.
- **No Dynamic Retraining**: Serialized model binaries were evaluated as-is.
- **No In-Sample Threshold Selection**: All operational thresholds are derived strictly from historical out-of-fold curves.
- **No Evaluation Leakage**: No calibration parameters or thresholds were fit using test fold labels.
- **Byte-for-Byte Integrity**: Canonical datasets and serialized model binaries remain unmodified.
