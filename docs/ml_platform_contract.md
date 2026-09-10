# ML ↔ Platform Integration Contract (v1.0.0)

Authoritative Integration Specification for the IRIS Infrastructure Risk Intelligence System.

---

## 1. Purpose

This document establishes the formal, deterministic, and versioned **ML ↔ Platform Integration Contract** between:
- **ARYAN (AI/ML + Data Intelligence)**: Model training, evaluation, validation, serialization, and registry governance.
- **SRINIVASH (Backend / Platform / Frontend)**: API routing, database persistence, dashboard rendering, client caching, and business orchestration.

The goal of this contract is complete encapsulation: the platform consumes ML outputs through stable, versioned schemas and envelopes **without needing to understand**:
- Model internals (CatBoost hyperplanes, Logistic Regression weights, tree depth, iterations).
- Feature engineering routines (delta calculations, ratio formulations, historical aggregations, indicator encodings).
- Artifact filesystem structure or joblib/cbm binaries.
- Training pipelines, walk-forward fold architectures, or embargo logic.

---

## 2. Architecture

The architectural flow decouples the client and backend from model mechanics:

```
+-------------------------------------------------------------------------+
|                              PLATFORM / UI                              |
|   (Provides project context: project_code, report_month, raw metadata)   |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                         ML SERVING INGESTION LAYER                      |
|                  (Validates request against Input Contract)             |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                       FEATURE ENGINEERING BUILDER                       |
|   (Constructs 36 or 25 frozen model features; checks embargo/leakage)    |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                         FROZEN MODEL ARTIFACT                           |
|        (CatBoost / Logistic Regression inference; TreeSHAP / Logit)     |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                      PLATFORM CONTRACT ENVELOPE                         |
|   (Enforces governance status, availability, non-causal explanations)   |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                            BACKEND & FRONTEND                           |
|            (Consumes standard JSON response; displays to users)         |
+-------------------------------------------------------------------------+
```

---

## 3. Aryan ↔ Srinivash Responsibility Boundary

| Dimension | Aryan (AI/ML) Responsibility | Srinivash (Platform) Responsibility |
| :--- | :--- | :--- |
| **Feature Extraction** | Formulates and derives all 36/25 engineered features. | Provides raw project observation (`project_code`, `report_month`). |
| **Model Execution** | Loads locked artifacts and computes raw margins/scores. | Dispatches requests to serving endpoints. |
| **Governance Enforcement** | Sets governance states (`LOCKED_PRODUCTION`, etc.). | Honors availability states (`AVAILABLE`, `NOT_AVAILABLE`). |
| **Risk Decisions** | Evaluates score against operational threshold (0.50). | Implements business workflow based on decision. |
| **Explanations** | Generates signed margin contributions (TreeSHAP/Logit). | Renders bar charts with non-causal disclaimers. |
| **Data Integrity** | Verifies sha256 hashes of datasets and models. | Maintains database schema and API service uptime. |

---

## 4. Contract Versioning

- **Contract Version**: `1.0.0` (frozen, semver compliant).
- **Contract ID**: `iris_ml_platform_contract_v1`.
- **JSON Schema Reference**: `schemas/ml_platform_contract_v1.contract.json` (Draft 2020-12).
- **Authoritative Artifact**: `artifacts/ml/ml_platform_contract_v1/contract.json`.
- **Breaking Changes**: Any modification to required payload keys, status enums, or threshold policies requires bumping the major version (`2.0.0`).

---

## 5. Prediction Input Contract

The platform is **never required** to compute complex statistical features.

### Platform-Visible Inputs
The platform provides a lightweight request payload:
```json
{
  "project_id": "201234",
  "report_month": "2026-04",
  "regime": "MODERN",
  "features": {
    "sector": "RAILWAYS",
    "agency": "NCRTC",
    "state": "DELHI",
    "original_cost": 30274.0,
    "revised_cost_t": 30274.0,
    "cumulative_expenditure_t": 12850.5,
    "physical_progress_t": 48.5,
    "approval_date": "2019-03",
    "start_date": null,
    "original_completion_date": "2025-06",
    "revised_completion_date": "2026-06"
  }
}
```

### Prohibited Leakage Fields
The platform must never pass future outcome fields. Any request containing any of the following 24 fields fails closed immediately with HTTP 422:
- Schedule leakage: `target_effective_schedule_ext_3m`, `target_extension_3m`, `extension_type`, `baseline_completion_date`, `target_event_revised_completion_date`.
- Cost leakage: `target_effective_cost_esc_3m`, `cost_revision_type`, `cost_diff`, `target_event_revised_cost`, `baseline_cost`, `baseline_cost_source`.
- Implementation leakage: `target_progress_stagnation_3m`, `progress_stagnation_subtype`, `delta_physical_progress_3m`, `baseline_progress`, `future_progress_t3`.
- Shared outcome leakage: `target_event_month`, `target_window_end_month`, `eventually_completed`, `completion_report_month`, `actual_completion_date`, `completed_revised_cost`, `completed_cumulative_expenditure`.

---

## 6. Prediction Output Contract

All single-domain predictions return a standardized platform envelope:

```json
{
  "contract_version": "1.0.0",
  "prediction": {
    "prediction_id": "pred-schedule_3m-modern",
    "domain": "schedule_3m",
    "regime": "MODERN",
    "target": "target_effective_schedule_ext_3m",
    "horizon_months": 3,
    "probability": 0.742,
    "prediction_status": "AVAILABLE",
    "operational_decision": 1,
    "decision_threshold": 0.50,
    "prediction_timestamp": "2026-09-10T10:15:00Z"
  },
  "model": {
    "model_id": "schedule_modern_logistic",
    "model_version": "1.0.0",
    "model_family": "LogisticRegression",
    "governance_status": "LOCKED_PRODUCTION",
    "production_availability": "AVAILABLE"
  },
  "calibration": {
    "status": "evaluated_uncalibrated_retained",
    "method": "uncalibrated_raw_probabilities",
    "limitations": "Platt scaling evaluated in PR-05; raw probabilities retained for operational consistency."
  },
  "explanation": {
    "available": true,
    "method": "StandardizedCoefficients",
    "contribution_space": "model_margin_or_logit",
    "non_causal": true,
    "disclaimer": "Explanations represent non-causal statistical associations based on reporting patterns and model margins. They do not imply causal mechanisms or guaranteed project outcomes.",
    "drivers": [
      {
        "feature": "schedule_revision_lag_months",
        "feature_group": "schedule",
        "contribution": 0.58,
        "direction": "risk_increasing",
        "contribution_space": "model_margin_or_logit"
      }
    ]
  },
  "limitations": [
    "Shorter longitudinal history in Segment 4 (July 2025 to July 2026).",
    "MoSPI administrative reporting changes after redesign.",
    "Non-causal statistical associations."
  ],
  "metadata": {}
}
```

---

## 7. Schedule Risk Contract (`schedule_3m`)

- **Domain ID**: `schedule_3m` (alias: `schedule_extension`, `schedule`).
- **Target**: `target_effective_schedule_ext_3m` (effective revision push-out within forward 3-month window).
- **Horizon**: 3 months ($H=3$).
- **Governance Status**: `LOCKED_PRODUCTION`.
- **Production Availability**: `AVAILABLE`.
- **Operational Threshold**: `0.50` (Score $\ge 0.50 \implies \text{decision} = 1$).
- **Regimes**:
  1. **Legacy Regime** (`LEGACY`): Projects observed before July 2025 redesign. Model: `schedule_legacy_catboost` (`CatBoostClassifier`, 36 features, TreeSHAP).
  2. **Modern Regime** (`MODERN`): Projects observed in 6-digit project code system (July 2025 onward). Model: `schedule_modern_logistic` (`LogisticRegression`, 25 static-only features, Standardized Coefficients).
- **Calibration Status**: `evaluated_uncalibrated_retained`. Production models output monotonic raw probabilities with lowest Brier scores.

---

## 8. Cost Overrun Contract (`cost_overrun`)

- **Domain ID**: `cost_overrun` (alias: `cost`).
- **Target**: `target_effective_cost_esc_3m`.
- **Horizon**: 3 months ($H=3$).
- **Governance Status**: `NOT_READY_FOR_PRODUCTION`.
- **Production Availability**: `NOT_AVAILABLE`.
- **Models**: `EVALUATION_ONLY` (`cost_overrun_baseline_logistic`, `cost_overrun_challenger_catboost`).
- **Operational Threshold**: `null`.
- **Serving Behavior**:
  - `probability`: `null`.
  - `operational_decision`: `null`.
  - `prediction_status`: `"NOT_AVAILABLE"`.
- **Safety Rule**: Platform code and UI must **never** interpret missing or null cost risk as evidence of zero or low cost risk. Cost revisions are administrative approvals occurring external to monthly telemetry.

---

## 9. Implementation Risk Contract (`implementation_risk`)

- **Domain ID**: `implementation_risk` (alias: `implementation`, `progress_stagnation`).
- **Target**: `target_progress_stagnation_3m` ($\Delta \text{progress} \le 10^{-6}$ over forward 3 months).
- **Horizon**: 3 months ($H=3$).
- **Governance Status**: `VIABLE_WITH_LIMITATIONS`.
- **Production Availability**: `NOT_AVAILABLE`.
- **Models**: `EVALUATION_ONLY` (`implementation_risk_baseline_logistic`, `implementation_risk_challenger_catboost`).
- **Operational Threshold**: `null`.
- **Segmentation Behavior**:
  - **Segments 1 & 2** (Legacy pre-June 2024): `INELIGIBLE` (physical progress is structurally absent from source tables). `probability: null`.
  - **Segments 3 & 4** (June 2024 onward): `NOT_AVAILABLE` (viable signal established under PR-09, but no production model artifact is deployed; live retraining is prohibited). `probability: null`.
- **Safety Rule**: Decision support only. Autonomous operational gating is strictly prohibited.

---

## 10. Unified Project Risk Profile Contract

The Unified Project Risk Profile synthesizes multiple domain evaluations for an infrastructure project:

### Strict Prohibition on Probability Fusion
> [!IMPORTANT]
> **NO PROBABILITY FUSION RULE**
> Under no circumstances may platform code or frontend scripts calculate:
> - Weighted average risk percentage
> - Arithmetic / geometric mean of probabilities
> - Composite mathematical risk score
> - Combined single probability
>
> The domains have fundamentally distinct statistical baselines, class prevalence rates (~9.4% schedule extension vs ~2.18% cost escalation vs ~30% progress stagnation), and disparate governance readiness. Merging them creates mathematically meaningless and hazardous indicators.

### Profile Structure
- `overall_status`: Categorical assessment (`FULL`, `PARTIAL`, `LIMITED`, `UNAVAILABLE`, `INELIGIBLE`).
- `coverage_status`: Level of predictive coverage (`COMPLETE_COVERAGE`, `PARTIAL_COVERAGE`, `LIMITED_COVERAGE`, `NO_PREDICTIVE_COVERAGE`).
- `priority_domains`: Deterministic domain ordering with priority levels:
  - `HIGH_PRIORITY`: Operational probability $\ge 0.50$.
  - `MEDIUM_PRIORITY`: Operational probability $\in [0.30, 0.50)$.
  - `UNAVAILABLE`: Unassessed domain (governed as not production-ready; must not be ignored).
  - `LOW_PRIORITY`: Operational probability $< 0.30$.
  - `INELIGIBLE`: Structurally omitted by source report layout.
- `attention_level`: Project-level operational classification (`HIGH_ATTENTION`, `MEDIUM_ATTENTION`, `LIMITED_ASSESSMENT`, `ROUTINE`, `NO_ASSESSMENT`).
- `recommendations`: Actionable human-in-the-loop engineering actions.
- `limitations`: Explicit operational boundaries.
- `governance_notes`: Domain governance audit trail.
- `summary`: Non-causal qualitative narrative.

---

## 11. Governance States

| Governance State | Definition | Operational Scoring Allowed? |
| :--- | :--- | :--- |
| `LOCKED_PRODUCTION` | Model locked, serialized, validated via walk-forward evaluation, and authorized for live inference. | **YES** (against 0.50 threshold). |
| `VIABLE_WITH_LIMITATIONS` | Research established viable predictive signal, but model requires human review and is not serialized for autonomous serving. | **NO** (`probability = null`). |
| `NOT_READY_FOR_PRODUCTION` | Model exhibits severe class imbalance or insufficient lift over prevalence. Not approved for production. | **NO** (`probability = null`). |

---

## 12. Production Availability States

| Availability State | Condition | Payload Representation |
| :--- | :--- | :--- |
| `AVAILABLE` | Production model artifact deployed and active. | Returns numeric `probability` and `operational_decision`. |
| `NOT_AVAILABLE` | Domain is evaluation-only or lacks serialized production artifact. | `probability = null`, `operational_decision = null`. |
| `EVALUATION_ONLY` | Candidate model evaluated in research folds only. | Not callable in production endpoints. |
| `INELIGIBLE` | Source reporting layout structurally omits telemetry required for evaluation. | `probability = null`, `prediction_status = "INELIGIBLE"`. |

---

## 13. Eligibility States

- **Eligible**: Actively ongoing project with continuous forward 3-month observation window in supported segment.
- **Ineligible — Structural Gap**: Observations during unreported months (e.g. 2023-12) or uncoded layout months (2024-04, 2024-05).
- **Ineligible — Boundary Month**: Observations within 3 months of June-July 2025 redesign boundary cannot cross the unbridged identifier redesign.
- **Ineligible — Structural Missingness**: Source tables omit required feature (e.g. physical progress in Segments 1 & 2).

---

## 14. Model Metadata

Platform endpoints expose comprehensive model metadata for UI inspection:
- `model_id`: Unique identifier (e.g. `schedule_modern_logistic`).
- `model_version`: Semver version (e.g. `1.0.0`).
- `model_family`: Algorithmic family (`CatBoostClassifier`, `LogisticRegression`).
- `candidate_type`: `production`, `baseline`, or `challenger`.
- `target`: Target variable name.
- `horizon_months`: Evaluation horizon (always 3).
- `performance_metrics`: Validation metrics from walk-forward expanding window evaluation (ROC-AUC, Average Precision, Brier Score).

---

## 15. Feature Contract Boundary

Feature engineering is strictly encapsulated within the ML layer:
1. **Raw Ingest**: Platform supplies `project_code`, `report_month`, and available source metadata.
2. **Feature Construction**: `src/ml/dataset_builder.py` transforms raw inputs into normalized, ordered vectors.
3. **Embargo Checks**: Strict walk-forward cutoff ($T + 3 < E$) ensures zero data leakage.
4. **Platform Isolation**: Frontend never handles categorical one-hot encoding, imputation, or feature scaling.

---

## 16. Calibration Metadata

- Models in production retain **uncalibrated raw probabilities** (`evaluated_uncalibrated_retained`).
- PR-05 empirical evaluation established that while Platt scaling improved calibration slope on isolated folds, raw probabilities minimized Brier score ($0.072$ in Legacy, $0.192$ in Modern) and preserved strict score monotonicity.
- The platform contract explicitly reports `calibration.status = "evaluated_uncalibrated_retained"` so users understand the score is a direct model output.

---

## 17. Explanation Contract

Explanations are exposed in a uniform platform schema:
```json
{
  "available": true,
  "method": "TreeSHAP",
  "contribution_space": "model_margin_or_logit",
  "non_causal": true,
  "disclaimer": "...",
  "drivers": [
    {
      "feature": "months_to_effective_schedule",
      "feature_group": "schedule",
      "contribution": 0.45,
      "direction": "risk_increasing",
      "contribution_space": "model_margin_or_logit"
    },
    {
      "feature": "expenditure_to_original_cost_ratio",
      "feature_group": "static_cost_financial",
      "contribution": -0.28,
      "direction": "risk_decreasing",
      "contribution_space": "model_margin_or_logit"
    }
  ]
}
```

---

## 18. Signed Contribution Semantics

- **Positive Contribution ($> 0$)**: Feature pushed model margin towards risk extension (`direction: "risk_increasing"`).
- **Negative Contribution ($< 0$)**: Feature pulled model margin away from risk extension (`direction: "risk_decreasing"`).
- **Zero Contribution ($= 0$)**: Feature had neutral effect (`direction: "neutral"`).
- **Contribution Space**: Stated explicitly as `model_margin_or_logit`. Contributions reflect shifts in log-odds margin, **not percentage probability shifts**.

---

## 19. Non-Causal Interpretation Rule

> [!WARNING]
> **CORRELATION != CAUSATION**
> All predictive contributions generated by TreeSHAP or Logistic coefficients reflect historical reporting patterns and statistical associations in MoSPI Flash Reports.
>
> They **must never be interpreted as root causes** or engineering recommendations (e.g. slowing expenditure will not inherently avert a schedule extension). Every explanation display must include the `non_causal: true` metadata flag and display the non-causal disclaimer.

---

## 20. Error Handling

Platform requests trigger standard, predictable HTTP status codes:
- **HTTP 200**: Successful prediction, profile, or contract metadata response.
- **HTTP 404**: Project code or evaluation month not found in evaluated population.
- **HTTP 422**: Unprocessable entity:
  - Prohibited leakage fields passed in payload.
  - Invalid date format (`report_month` not `YYYY-MM`).
  - Feature values containing `NaN`, `Infinity`, or unregistered categorical features.
  - Contradictory regime specifications.
- **HTTP 500**: Internal inference or verification error.
- **HTTP 503**: Serving database unavailable or corrupted.

---

## 21. Fail-Closed Behavior

The ML system strictly adheres to fail-closed design:
1. If an unknown feature is passed $\implies$ Fail closed (HTTP 422).
2. If prohibited leakage is detected $\implies$ Fail closed (HTTP 422).
3. If model artifact SHA-256 hash fails verification $\implies$ Refuse to boot (RuntimeError).
4. If a domain is `NOT_READY_FOR_PRODUCTION` $\implies$ Output `probability: null`.
5. If a domain is `INELIGIBLE` $\implies$ Output `probability: null` with machine-readable reason.

---

## 22. Registry Compatibility

The platform contract is automatically verified against:
- `artifacts/ml/model_registry_v1/registry.json`
- `src/ml/model_registry.py`

Verification guarantees:
- Domain IDs (`schedule_3m`, `cost_overrun`, `implementation_risk`) match exactly.
- Model IDs (`schedule_legacy_catboost`, `schedule_modern_logistic`, etc.) match exactly.
- Governance and availability states match byte-for-byte.
- Artifact hashes match canonical SHA-256 digests.
- Thresholds match registry policies.

---

## 23. Artifact Provenance

All serialized contract artifacts reside in:
- `artifacts/ml/ml_platform_contract_v1/contract.json`
- `artifacts/ml/ml_platform_contract_v1/manifest.json`
- `artifacts/ml/ml_platform_contract_v1/verification_report.json`

The manifest records the SHA-256 hashes of the underlying registry, canonical datasets, and locked model binaries.

---

## 24. API Integration

Read-only platform contract endpoints:
- `GET /api/ml/platform-contract`
- `GET /api/v1/ml/platform-contract`
- `GET /risk/platform-contract`

These endpoints return the complete platform contract dictionary with masked internal paths.

Inference endpoints:
- `POST /api/ml/unified-risk`: Evaluates multi-domain risk for a single project observation.
- `POST /api/ml/unified-risk-profile`: Generates the Unified Project Risk Profile.

---

## 25. Backend Integration Guidance

For backend engineers (Srinivash):
1. **Contract Ingestion**: Call `GET /api/ml/platform-contract` during service initialization or CI/CD to cache model IDs and thresholds.
2. **Serving Integration**: Use `src/ml/platform_contract.py`'s `MLPlatformContract` class to validate request payloads before inference and validate response shapes before delivery.
3. **Database Storage**: Store domain probabilities in separate columns (`schedule_risk_prob`, `cost_risk_prob`, `impl_risk_prob`). **Never store an averaged column.**
4. **Caching**: Cache platform contract metadata with a TTL of 24 hours (or invalidate on deployment).

---

## 26. Frontend Integration Guidance

For UI/UX engineers:
1. **Risk Cards**: Render individual cards for Schedule Extension, Cost Overrun, and Implementation Risk.
2. **Badges**:
   - Schedule Extension: Show probability gauge and binary badge (`HIGH RISK` if $\ge 0.50$, else `NORMAL`).
   - Cost Overrun: Display `UNASSESSED (RESEARCH STAGE)` badge. Show tooltip: *"Cost escalation models are currently evaluation-only due to extreme class imbalance (~2.18%)."*
   - Implementation Risk: Display `DECISION SUPPORT ONLY` or `INELIGIBLE` badge.
3. **Driver Charts**: Render signed contributions as horizontal bar charts (red for positive, green for negative). Display the non-causal disclaimer in the chart footer.
4. **No Combined Score**: Do not construct a circular progress meter showing "Total Risk: 65%". Display the `attention_level` (e.g. `HIGH_ATTENTION`) instead.

---

## 27. Versioning Policy

- **Patch (`1.0.x`)**: Clarifications in descriptions or documentation comments; no schema changes.
- **Minor (`1.x.0`)**: Adding optional fields or new research candidate models; backward compatible.
- **Major (`x.0.0`)**: Changing domain IDs, threshold values, required fields, or error codes; breaking change requiring coordinated deployment.

---

## 28. Backward Compatibility

- Existing prediction endpoints (`/risk/unified`, `/api/ml/unified-risk`) retain full backward compatibility.
- Existing dashboard endpoints (`/risk/projects`, `/risk/summary`, `/risk/options`) remain completely unchanged.
- Registry endpoints (`/api/ml/model-registry`) remain completely unchanged.

---

## 29. Security and Path Masking

The platform contract implements strict path masking:
- Absolute local filesystem paths (e.g. `D:\Coding\...` or `/home/...`) are stripped and replaced with relative repository paths (`artifacts/ml/...`).
- No binary weights, pickles, or model bytecode are exposed over HTTP.
- No environment variables, database credentials, or internal secrets are included in metadata.

---

## 30. Testing and Verification

To verify contract compliance:
```powershell
# Dedicated contract test suite
python -m unittest tests/test_ml_platform_contract.py -v

# Full ML regression suite
python -m unittest discover -s tests -p "test_ml_*.py"

# Backend pytest suite
python -m pytest backend/tests
```

All 40+ contract regression tests must pass before deployment.

---

## 31. Limitations

1. **Observational Flash Data**: Models are trained strictly on administrative MoSPI Flash Report PDFs, inheriting historical reporting lags and retrospective adjustments.
2. **Horizon Constraint**: All risk assessments operate on a strict 3-month forward window ($H=3$); predictions cannot be linearly extrapolated to multi-year horizons.
3. **Regime Boundary**: No direct project code bridges exist across the June-July 2025 redesign boundary; cross-regime tracking requires longitudinal analytical crosswalks.

---

## 32. Future Platform Integration

Future platform enhancements (PR-15+) will incorporate:
- Asynchronous batch portfolio evaluation crons.
- WebSocket streaming for multi-project risk scanning.
- Automated SLA monitoring for model inference latency.
- Analytical crosswalk lookup bridges between legacy and modern regimes.
