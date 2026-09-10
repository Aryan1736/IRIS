# IRIS PR-10: Unified Risk Serving Documentation

## 1. Scope and PR-10 Objective

The objective of PR-10 is to establish a unified, auditable, and deterministic production-serving layer for the Infrastructure Risk Intelligence System (IRIS). Prior PRs developed and validated models and evaluations across three distinct risk domains:
1. **Schedule Extension Risk (3-Month Horizon)**: Validated and locked production inference models (PR-03, PR-04, PR-05).
2. **Cost Overrun Risk (3-Month Horizon)**: Walk-forward evaluation and governance research (PR-06, PR-07).
3. **Implementation Risk (3-Month Physical Progress Stagnation)**: Walk-forward evaluation and governance research (PR-08, PR-09).

PR-10 does **not** retrain, tune, or alter any model artifacts or scientific conclusions. Instead, it provides an auditable, deterministic, fail-closed multi-domain serving interface (`UnifiedRiskPredictor`) and REST API endpoints (`POST /api/ml/unified-risk` and `POST /api/v1/risk/unified`) that surface the three domains under their authoritative governance rules.

---

## 2. Architecture Overview

The unified risk serving layer is structured around the `UnifiedRiskPredictor` class located in `src/ml/unified_risk_predictor.py`. It coordinates request validation, continuous segment resolution, domain dispatch, and structured response assembly:

```
                      Client Request (JSON payload)
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │             UnifiedRiskPredictor.predict_one()          │
       │                                                        │
       │  1. Top-Level Validation (Leakage, Types, YYYY-MM)     │
       │  2. Numeric Sanity (Reject NaN, Inf, non-numerics)     │
       │  3. Continuous Segment & Regime Resolution             │
       │     (Fail-closed on structural gaps / contradictions)   │
       └───────────────────┬────────────────┬───────────────────┘
                           │                │
            ┌──────────────┴──────────┐     │
            │                         │     │
            ▼                         ▼     ▼
┌───────────────────────┐ ┌──────────────────────┐ ┌────────────────────────┐
│  Schedule Extension   │ │     Cost Overrun     │ │  Implementation Risk   │
│  Domain Serving       │ │  Governance Handler  │ │   Governance Handler   │
│                       │ │                      │ │                        │
│ Status: AVAILABLE     │ │ Status: NOT_AVAILABLE│ │ Seg 1-2: INELIGIBLE    │
│ Predictor:            │ │ Status:              │ │ Seg 3-4: NOT_AVAILABLE │
│ ScheduleExtension-    │ │ NOT_READY_FOR_       │ │ Status:                │
│ Predictor             │ │ PRODUCTION           │ │ VIABLE_WITH_           │
│ Parity: < 1e-12       │ │ Autonomous gate:     │ │ LIMITATIONS            │
│ Threshold: 0.50       │ │ PROHIBITED           │ │ Human review required  │
└───────────┬───────────┘ └──────────┬───────────┘ └───────────┬────────────┘
            │                        │                         │
            └────────────────────────┼─────────────────────────┘
                                     │
                                     ▼
                      Unified Structured Response
```

---

## 3. Unified Serving Contract

The serving layer returns a deterministic JSON dictionary conforming to `UnifiedRiskResponse`:

```json
{
  "project_id": "020100044",
  "report_month": "2026-04",
  "schedule_extension": {
    "status": "AVAILABLE",
    "regime": "MODERN",
    "risk_score": 0.412,
    "prediction": 0,
    "threshold": 0.50,
    "model_version": "logistic_static_only__unweighted",
    "operational_status": "LOCKED_PRODUCTION",
    "reason": null
  },
  "cost_overrun": {
    "status": "NOT_AVAILABLE",
    "regime": "MODERN",
    "risk_score": null,
    "prediction": null,
    "threshold": null,
    "model_version": null,
    "operational_status": "NOT_READY_FOR_PRODUCTION",
    "reason": "Cost overrun modeling is research-only and classified as NOT_READY_FOR_PRODUCTION under PR-07. Due to severe class imbalance (~2.18%) and low precision lift, no autonomous production model artifact is deployed for live scoring."
  },
  "implementation_risk": {
    "status": "NOT_AVAILABLE",
    "regime": "MODERN",
    "risk_score": null,
    "prediction": null,
    "threshold": null,
    "model_version": null,
    "operational_status": "VIABLE_WITH_LIMITATIONS",
    "reason": "Implementation risk is classified as VIABLE_WITH_LIMITATIONS for decision support with human review under PR-09. However, no serialized production model artifact exists in artifacts/ml/implementation_risk_model_v1/ (evaluation artifacts only). Inference-time retraining is prohibited; serving fails closed until model serialization."
  },
  "metadata": {
    "serving_contract_version": "1.0.0",
    "deterministic": true,
    "continuous_segment": "SEGMENT_4",
    "governance": {
      "schedule_extension": "LOCKED_PRODUCTION",
      "cost_overrun": "NOT_READY_FOR_PRODUCTION",
      "implementation_risk": "VIABLE_WITH_LIMITATIONS"
    }
  }
}
```

---

## 4. Schedule Extension Integration

The Schedule Extension domain delegates directly to `ScheduleExtensionPredictor` (`src/ml/predict_schedule.py`), which loads the locked model artifacts:
- **LEGACY**: CatBoost (`artifacts/ml/schedule_extension_3m/legacy_catboost/model.cbm`, SHA-256: `59586004F5967602651156E0A26FE564015F240958F5416CBB565E4755C524EE`).
- **MODERN**: Logistic Regression (`artifacts/ml/schedule_extension_3m/modern_logistic/model.joblib`, SHA-256: `679D9768869088BA8CEE297577B1935DCF903F00B38697BF9A3FFA2F7DEB5082`).

### Parity Guarantees
- Single-row and batch-forward inference produce identical results.
- Standalone `ScheduleExtensionPredictor` probabilities and raw margins reconcile with `UnifiedRiskPredictor` to within $< 10^{-12}$ (machine precision).

---

## 5. Cost-Overrun Governance Status

PR-07 concluded that cost overrun models are:
```
NOT_READY_FOR_PRODUCTION
```
### Key Governance Guardrails
1. **No Autonomous Decisions**: The cost overrun domain must **never** return an autonomous binary prediction, risk gate, or pass/fail decision.
2. **No Production Threshold**: No production decision threshold is defined or exposed.
3. **No Dynamic Training**: The system does not fit, calibrate, or retrain models at request time.
4. **Explicit Rationale**: Returns `status: "NOT_AVAILABLE"`, `risk_score: null`, and `prediction: null`, clearly identifying that cost revisions in the canonical records are administrative decisions with severe class imbalance (~2.18%) and low precision lift over prevalence.

---

## 6. Implementation-Risk Integration

PR-09 evaluated candidate models on physical progress stagnation (`target_progress_stagnation_3m`) and concluded:
```
VIABLE_WITH_LIMITATIONS
```
### Decision Support and Fail-Closed Serving
- **Decision Support Only**: When deployed, the implementation risk model is intended strictly for decision support with human-in-the-loop review.
- **Artifact Status**: PR-09 generated walk-forward evaluation artifacts (`calibration_metrics.csv`, `fold_metrics.csv`, `threshold_research.csv`, `candidate_recommendation.json`) but did not serialize a locked production predictor artifact.
- **Fail-Closed Policy**: In accordance with PR-10 instructions, the system does not dynamically train or invent model weights. For supported segments (Segments 3 and 4), it returns `status: "NOT_AVAILABLE"`, `operational_status: "VIABLE_WITH_LIMITATIONS"`, with an explicit explanatory reason.
- **Unsupported Segments**: For continuous Segments 1 and 2 (where physical progress was structurally unrecorded in the source PDFs), it returns `status: "INELIGIBLE"`.

---

## 7. Regime Handling

The repository enforces strict regime boundaries:
- **LEGACY (`SEGMENT_1`, `SEGMENT_2`, `SEGMENT_3`)**: Covers observations up to `2025-06`. Uses legacy project identifiers, 36 contract features, and CatBoost unweighted inference.
- **MODERN (`SEGMENT_4`)**: Covers observations from `2025-07` onwards following the Ministry's six-digit project code redesign. Uses 25 static-at-T contract features, frequency/standardization preprocessing, and Logistic Regression inference.
- **Redesign Boundary**: The boundary between `2025-06` and `2025-07` is absolute. No cross-regime inference, identifier translation, or surrogate bridging is permitted.

---

## 8. Structural Gap Handling

Certain historical months are structural reporting gaps where no ongoing project data could be reliably parsed from monthly Flash Reports:
- `2023-12` (Structural gap between Segment 1 and Segment 2)
- `2024-04` and `2024-05` (Structural gap between Segment 2 and Segment 3)
- Months outside the contract range ($< 2023-01$ or $> 2026-07$)

When an input request specifies a report month that falls within a structural gap or out-of-range period:
- `UnifiedRiskPredictor` immediately rejects the request with a fail-closed `ValueError`.
- In REST API calls, this returns an HTTP 422 Unprocessable Entity error.

---

## 9. Feature Validation

Strict feature contract validation is enforced:
1. **Completeness**: All required features for the resolved regime must be present in the request payload.
2. **Prohibition of Unknowns**: Any key not in the required regime feature catalog (or allowed routing metadata) causes immediate fail-closed rejection.
3. **Numeric Robustness**: Numeric features must be finite, valid numbers or valid numeric strings.
4. **Explicit Rejection of NaN & Infinity**: Passing `NaN`, `+Infinity`, `-Infinity` (as floats or case-insensitive string representations like `"nan"` or `"-infinity"`) fails closed immediately.

---

## 10. Leakage Protection

The unified serving layer isolates and prevents target, future, or completion leakage. The unified prohibited leakage set includes:

| Category | Prohibited Fields |
|---|---|
| **Schedule Target & Future** | `target_effective_schedule_ext_3m`, `target_extension_3m`, `extension_type`, `baseline_completion_date`, `target_event_revised_completion_date` |
| **Cost Overrun Target & Future** | `target_effective_cost_esc_3m`, `cost_revision_type`, `cost_diff`, `target_event_revised_cost`, `baseline_cost`, `baseline_cost_source` |
| **Implementation Risk Target & Future** | `target_progress_stagnation_3m`, `progress_stagnation_subtype`, `delta_physical_progress_3m`, `baseline_progress`, `future_progress_t3` |
| **Outcomes & Completions** | `target_event_month`, `target_window_end_month`, `eventually_completed`, `completion_report_month`, `actual_completion_date`, `completed_revised_cost`, `completed_cumulative_expenditure` |

If any of these fields appear in the request, inference is rejected with an informative error.

---

## 11. Fail-Closed Behavior

The serving layer adheres to strict fail-closed principles:
- It never silently coerces malformed strings into numerics.
- It never imputes missing required features at request time.
- It never falls back to an unverified default regime.
- It never bridges gaps across unassigned months.
- When an error occurs, it emits an explicit, deterministic diagnostic message.

---

## 12. Determinism

Inference is 100% deterministic:
- **Repeated Calls**: Repeated calls with identical inputs produce identical probabilities, predictions, and metadata down to floating-point bit equivalence.
- **Call-Order Invariance**: The order in which requests are evaluated within a batch or sequence does not alter individual predictions.

---

## 13. Immutability

The inference engine does not mutate any underlying model weights, coefficients, intercepts, or preprocessor scalers:
- Evaluated and verified via unit tests checking `model.coef_`, `model.intercept_`, `preprocessor.numeric_mean`, and `preprocessor.numeric_scale` before and after repetitive scoring.

---

## 14. Numerical Parity

Unified serving maintains exact numerical parity:
- Tested against standalone `ScheduleExtensionPredictor` on both Legacy and Modern representative populations.
- Discrepancy between direct prediction probability and unified response risk score is bounded by $< 10^{-12}$.

---

## 15. Artifact Integrity

All canonical datasets and locked model artifacts remain byte-for-byte unchanged:

| Artifact | Locked SHA-256 Digest | Verification Status |
|---|---|---|
| `data/processed/projects_monthly.csv` | `9512A9881E17DFDED6E182D87A8DFB1C4EDBD36C0D9B8A7DA9FD1ABB7E002FBF` | VERIFIED UNCHANGED |
| `data/processed/projects_completed.csv` | `89BEA84FD68A22E327090C1E4E4533F5BCD745ADCA61EB4E66172EE9023BB910` | VERIFIED UNCHANGED |
| `artifacts/ml/schedule_extension_3m/legacy_catboost/model.cbm` | `59586004F5967602651156E0A26FE564015F240958F5416CBB565E4755C524EE` | VERIFIED UNCHANGED |
| `artifacts/ml/schedule_extension_3m/modern_logistic/model.joblib` | `679D9768869088BA8CEE297577B1935DCF903F00B38697BF9A3FFA2F7DEB5082` | VERIFIED UNCHANGED |

---

## 16. API Integration

Unified risk prediction is exposed across both direct root paths and API v1 routes:
- `POST /api/ml/unified-risk` (Direct machine-learning serving route)
- `POST /api/v1/ml/unified-risk` (Versioned machine-learning route)
- `POST /api/v1/risk/unified` (Risk router route)
- `POST /risk/unified` (Direct proxy route)

### Request Payload Formats
The API supports both structured and flat payloads:
- **Structured Payload**:
  ```json
  {
    "project_id": "020100044",
    "report_month": "2026-04",
    "regime": "MODERN",
    "features": {
      "sector": "RAILWAYS",
      "agency": "NCRTC",
      "state": "DELHI",
      "original_cost": 30274.0,
      ...
    }
  }
  ```
- **Flat Payload**:
  ```json
  {
    "project_id": "020100044",
    "report_month": "2026-04",
    "sector": "RAILWAYS",
    "agency": "NCRTC",
    "state": "DELHI",
    "original_cost": 30274.0,
    ...
  }
  ```

### HTTP Status Codes
- `200 OK`: Valid request; returns unified multi-domain risk evaluation.
- `422 Unprocessable Entity`: Request validation failure (missing feature, unknown feature, prohibited leakage field, invalid numeric/NaN/Inf, invalid month, or structural gap).
- `500 Internal Server Error`: Unhandled server or inference exception.

---

## 17. Response Interpretation

When interpreting responses:
1. Check `schedule_extension.status`:
   - If `"AVAILABLE"`: `risk_score` represents the estimated probability of schedule extension within 3 months. `prediction` is 1 if score $\ge 0.50$, else 0.
   - If `"INELIGIBLE"`: The observation falls in a structural gap month.
2. Check `cost_overrun.status`:
   - Always `"NOT_AVAILABLE"`. Do **not** attempt to extract a cost overrun prediction or threshold.
3. Check `implementation_risk.status`:
   - If `"INELIGIBLE"`: Physical progress was not recorded for the observation's continuous segment.
   - If `"NOT_AVAILABLE"`: PR-09 evaluation recommends the model for decision support (`VIABLE_WITH_LIMITATIONS`), but production model weights are not serialized.

---

## 18. Governance Status of Each Domain

| Risk Domain | Target | Horizon | Governance Status | Operational Usage |
|---|---|---|---|---|
| **Schedule Extension** | `target_effective_schedule_ext_3m` | 3 Months | `LOCKED_PRODUCTION` | Production scoring with locked CatBoost (Legacy) and Logistic (Modern) |
| **Cost Overrun** | `target_effective_cost_esc_3m` | 3 Months | `NOT_READY_FOR_PRODUCTION` | Research only. Prohibited from autonomous production gates |
| **Implementation Risk** | `target_progress_stagnation_3m` | 3 Months | `VIABLE_WITH_LIMITATIONS` | Decision support requiring human review. Fails closed pending model serialization |

---

## 19. Known Limitations

1. **Physical Progress Absence**: Physical progress is unavailable in continuous Segments 1 and 2 (prior to June 2024).
2. **Administrative Cost Revisions**: Cost revisions occur through administrative cabinet and ministry approvals rather than purely endogenous project progress, limiting predictability from internal metrics.
3. **Identifier Boundary**: Models cannot cross the June-to-July 2025 boundary without explicit regime separation.

---

## 20. Operational Usage Guidance

- **Automated Alerts**: Use only the `schedule_extension` domain for automated notifications or ranking.
- **Auditing**: Review the `metadata` block to ensure `serving_contract_version` and `deterministic` flags are logged with all downstream decisions.
- **Human Oversight**: Never automate portfolio decisions using Cost Overrun or Implementation Risk without explicit human analyst verification.

---

## 21. Compliance Statement

PR-10 strictly complies with all repository rules in `AGENTS.md` and prior PR contracts:
- Canonical datasets `projects_monthly.csv` and `projects_completed.csv` were preserved byte-for-byte.
- Locked schedule model artifacts `model.cbm` and `model.joblib` were preserved byte-for-byte.
- No dynamic retraining, tuning, or imputation was introduced.
- Strict leakage controls, regime separation, and structural gap fail-closed behaviors remain fully enforced.
