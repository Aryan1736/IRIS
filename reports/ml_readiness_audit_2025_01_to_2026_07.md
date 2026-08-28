# PAIMANA 19-month ML-readiness and data-coverage audit

## Decision

**Recommendation: `EXTRACT_2024_AND_2023_BEFORE_MODELLING`.**

The accepted Table 6/Table 7 history is already sufficient for exploratory prototypes of future schedule revision and future progress stagnation, but it is not yet a defensible general training base for the harder future cost-escalation problem. Only 180 upward revised-cost changes are observed across 18,175 comparable adjacent-month pairs (0.99%), only 244 projects have any upward or downward revised-cost change, and just 34 projects change revised cost more than once. The 13-month six-digit era supplies only 552 complete 12-month project-history windows; the six-month legacy era supplies no 6- or 12-month windows.

Two additional years are recommended because event rarity, horizon coverage, reporting-regime effects, and temporal validation matter more here than the raw 28,581-row count. Extracting 2024 and 2023 should be staged and validated in the existing fail-closed pipeline. Their identifier continuity and field semantics must be established from the sources; this recommendation does not assume that either year will bridge the June-July 2025 redesign.

No feature, label, target, normalization, imputation, stable ID, or model was created in this audit. The June-July 2025 diagnostic crosswalk was not used.

## Audit scope and definitions

- Source: accepted `data/processed/projects_monthly.csv`, January 2025-July 2026.
- Identifier eras are analysed independently: legacy IDs from January-June 2025 and six-digit IDs from July 2025-July 2026.
- June-July 2025 is an identifier-system boundary, not project churn. It is excluded from new/disappearing, event-transition, run, and horizon calculations.
- A change event requires the same exact source `project_code` in adjacent report months within one era and source-present values in both months.
- A complete H-month history requires the project to appear in every report from T through T+H. The separately reported calendar ceiling only requires H future report months to exist, irrespective of project attrition.
- Quantiles use linear interpolation over sorted observations. Cost magnitudes are Rs crore. Schedule magnitudes are calendar months.
- `structurally absent` means the source layout has no such field. `source missing` means the layout supports the field but the source-faithful canonical value is empty.
- Category statistics use exact source values. Apparent casing, punctuation, acronym, spelling, and wrapping variants are not merged.

## Accepted baseline

- 28,581 project-month observations
- 4,029 unique source project codes
- 0 missing project codes
- 0 duplicate `(project_code, report_month)` keys
- Combined SHA-256: `A366C2BA57055BE107EF687373477F1704242E00D64ABECFEC59AFD93CC1BB91`

## Monthly coverage and churn within identifier era

The first month of each era is an initial stock, not a count of new projects. June disappearance and July appearance are deliberately not calculated across the redesign. July 2026 disappearance is right-censored.

| Month | Rows / unique codes | New vs prior same-era month | Disappearing before next same-era month | Layout |
|---|---:|---:|---:|---|
| 2025-01 | 1,719 | N/A: initial stock | 46 | legacy nine-column |
| 2025-02 | 1,682 | 9 | 17 | legacy nine-column |
| 2025-03 | 1,677 | 12 | 34 | legacy nine-column |
| 2025-04 | 1,670 | 27 | 48 | legacy nine-column |
| 2025-05 | 1,637 | 15 | 47 | legacy nine-column |
| 2025-06 | 1,595 | 5 | N/A: ID-era boundary | legacy nine-column |
| 2025-07 | 791 | N/A: initial stock after redesign | 26 | approval-only eight-column |
| 2025-08 | 800 | 35 | 40 | standard eight-column |
| 2025-09 | 794 | 34 | 9 | standard eight-column |
| 2025-10 | 820 | 35 | 20 | standard eight-column |
| 2025-11 | 823 | 23 | 35 | standard eight-column |
| 2025-12 | 1,392 | 604 | 4 | standard eight-column |
| 2026-01 | 1,702 | 314 | 24 | standard eight-column |
| 2026-02 | 1,948 | 270 | 29 | standard eight-column |
| 2026-03 | 1,941 | 22 | 17 | standard eight-column |
| 2026-04 | 1,981 | 57 | 30 | standard eight-column |
| 2026-05 | 1,987 | 36 | 162 | standard eight-column |
| 2026-06 | 1,847 | 22 | 115 | standard eight-column |
| 2026-07 | 1,775 | 43 | N/A: endpoint | standard eight-column |

The December 2025-February 2026 additions are real source-code appearances within the six-digit era, but should not automatically be interpreted as project starts; they may also reflect changes in reporting coverage.

## Observation depth by identifier era

| Statistic | Legacy Jan-Jun 2025 | Six-digit Jul 2025-Jul 2026 |
|---|---:|---:|
| Project-month rows | 9,980 | 18,601 |
| Unique source codes | 1,786 | 2,243 |
| Minimum observations/project | 1 | 1 |
| 25th percentile | 6 | 6 |
| Median | 6 | 8 |
| Mean | 5.588 | 8.293 |
| 75th percentile | 6 | 12 |
| Maximum | 6 | 13 |
| Projects with ≥3 observations | 1,704 | 2,126 |
| Projects with ≥6 observations | 1,527 | 1,917 |
| Projects with ≥9 observations | 0 | 751 |
| Projects with ≥12 observations | 0 | 629 |
| Present in every era month | 1,527 | 552 |

The legacy era has excellent six-month continuity but cannot support a six-month *future* horizon because six future reports after T would require at least seven months. The six-digit era has useful depth for 1-6 month questions but limited 12-month coverage.

## Field completeness

### Overall

| Field | Present | Structural absence | Source missing | Completeness across all rows | Source completeness when applicable |
|---|---:|---:|---:|---:|---:|
| `project_code` | 28,581 | 0 | 0 | 100.00% | 100.00% |
| `project_name` | 28,581 | 0 | 0 | 100.00% | 100.00% |
| `agency` | 28,581 | 0 | 0 | 100.00% | 100.00% |
| `ministry` | 18,601 | 9,980 | 0 | 65.08% | 100.00% |
| `sector` | 28,581 | 0 | 0 | 100.00% | 100.00% |
| `state` | 28,575 | 0 | 6 | 99.98% | 99.98% |
| `approval_date` | 27,970 | 0 | 611 | 97.86% | 97.86% |
| `start_date` | 17,789 | 10,771 | 21 | 62.24% | 99.88% |
| `original_completion_date` | 28,466 | 0 | 115 | 99.60% | 99.60% |
| `revised_completion_date` | 16,206 | 0 | 12,375 | 56.70% | 56.70% |
| `original_cost` | 28,581 | 0 | 0 | 100.00% | 100.00% |
| `revised_cost` | 20,901 | 0 | 7,680 | 73.13% | 73.13% |
| `cumulative_expenditure` | 28,581 | 0 | 0 | 100.00% | 100.00% |
| `physical_progress` | 27,659 | 0 | 922 | 96.77% | 96.77% |

The strongest general inputs are the exact identifier/grouping fields, `original_cost`, `cumulative_expenditure`, and—subject to reported corrections—`physical_progress`. Revised fields are materially selective: their absence can mean that no revision is printed, not simply a data-quality failure.

### By layout

| Layout | Rows | Structural absence | Important source completeness |
|---|---:|---|---|
| Legacy nine-column | 9,980 | `ministry`, `start_date` | original completion 98.96%; revised completion 28.30%; revised cost 23.05%; progress 90.76% |
| Approval-only eight-column | 791 | `start_date` | state 99.87%; approval 99.62%; revised completion 66.75%; revised cost/expenditure/progress 100% |
| Standard eight-column | 17,810 | none | state 99.97%; approval 96.59%; start 99.88%; original completion 99.94%; revised completion 72.17%; revised cost/expenditure/progress 100% |

Start Date is therefore not missing at random: all 9,980 legacy rows and all 791 July 2025 rows lack the column structurally. Ministry is likewise structurally unavailable for all 9,980 legacy rows. These absences must be represented as schema availability, not imputed values.

### By month: structural/source-missing counts

Each cell is `S/M`, where S is structurally absent and M is source missing. Fields not shown—project code/name, agency, sector, original cost, and expenditure—are complete in every month.

| Month | Ministry | State | Approval | Start | Original completion | Revised completion | Revised cost | Progress |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-01 | 1,719/0 | 0/0 | 0/0 | 1,719/0 | 0/27 | 0/1,111 | 0/1,313 | 0/170 |
| 2025-02 | 1,682/0 | 0/0 | 0/0 | 1,682/0 | 0/27 | 0/1,682 | 0/1,294 | 0/147 |
| 2025-03 | 1,677/0 | 0/0 | 0/0 | 1,677/0 | 0/27 | 0/1,105 | 0/1,291 | 0/147 |
| 2025-04 | 1,670/0 | 0/0 | 0/0 | 1,670/0 | 0/8 | 0/1,115 | 0/1,289 | 0/150 |
| 2025-05 | 1,637/0 | 0/0 | 0/0 | 1,637/0 | 0/8 | 0/1,084 | 0/1,259 | 0/149 |
| 2025-06 | 1,595/0 | 0/0 | 0/0 | 1,595/0 | 0/7 | 0/1,059 | 0/1,234 | 0/159 |
| 2025-07 | 0/0 | 0/1 | 0/3 | 791/0 | 0/0 | 0/263 | 0/0 | 0/0 |
| 2025-08 | 0/0 | 0/0 | 0/280 | 0/5 | 0/0 | 0/250 | 0/0 | 0/0 |
| 2025-09 | 0/0 | 0/1 | 0/94 | 0/3 | 0/0 | 0/239 | 0/0 | 0/0 |
| 2025-10 | 0/0 | 0/1 | 0/24 | 0/1 | 0/0 | 0/251 | 0/0 | 0/0 |
| 2025-11 | 0/0 | 0/0 | 0/12 | 0/1 | 0/0 | 0/251 | 0/0 | 0/0 |
| 2025-12 | 0/0 | 0/0 | 0/19 | 0/0 | 0/0 | 0/525 | 0/0 | 0/0 |
| 2026-01 | 0/0 | 0/1 | 0/44 | 0/0 | 0/0 | 0/768 | 0/0 | 0/0 |
| 2026-02 | 0/0 | 0/1 | 0/54 | 0/0 | 0/0 | 0/963 | 0/0 | 0/0 |
| 2026-03 | 0/0 | 0/1 | 0/17 | 0/0 | 0/0 | 0/347 | 0/0 | 0/0 |
| 2026-04 | 0/0 | 0/0 | 0/11 | 0/0 | 0/0 | 0/354 | 0/0 | 0/0 |
| 2026-05 | 0/0 | 0/0 | 0/22 | 0/11 | 0/11 | 0/352 | 0/0 | 0/0 |
| 2026-06 | 0/0 | 0/0 | 0/19 | 0/0 | 0/0 | 0/308 | 0/0 | 0/0 |
| 2026-07 | 0/0 | 0/0 | 0/12 | 0/0 | 0/0 | 0/348 | 0/0 | 0/0 |

February 2025 has no reported revised completion values despite the legacy layout supporting the original/revised/anticipated structure. It remains source missing rather than being filled from original or anticipated dates.

### Sector and agency effects

The full machine-readable breakdown contains all fields for every exact sector and agency. Useful high-volume examples show that missingness is tied to source regime and reporting practice:

- Among exact sectors with at least 50 rows, approval-date missingness is highest for `Shipping` (15.38%), `Waste & Water` (14.68%), `Energy Storage` (11.54%), and `Healthcare` (10.60%).
- Legacy uppercase sectors have high revised-cost missingness: `COAL` 95.16%, `POWER` 89.09%, `ROAD TRANSPORT AND HIGHWAYS` 78.59%, and `RAILWAYS` 63.51%. This reflects legacy source semantics, not values to impute.
- Exact agencies with ≥50 rows and wholly absent revised completion dates include `ECR`, `CCL`, `SWR`, `Maharashtra Metro Rail Corporation Limited [MMRCL]`, `SCCL`, `Mahanadi Coalfields Limited [MCL]`, `NER`, and `SCR`.
- Progress missingness is concentrated in several legacy agency labels, including `SCR` 75.93%, `RVNL` 75.76%, and `ECOR` 37.50%.

## Revised-cost event audit

| Era | Comparable adjacent pairs | Projects changed | Projects with multiple changes | Upward changes | Downward changes |
|---|---:|---:|---:|---:|---:|
| Legacy | 1,860 | 24 | 3 | 20 | 7 |
| Six-digit | 16,315 | 220 | 31 | 160 | 96 |
| Overall | 18,175 | 244 | 34 | 180 | 103 |

| Direction | P25 | Median | Mean | P75 | Maximum | Unit |
|---|---:|---:|---:|---:|---:|---|
| Upward | 38.89 | 199.83 | 695.72 | 688.53 | 13,334.00 | Rs crore |
| Downward/correction, absolute | 0.41 | 36.21 | 2,124.97 | 295.67 | 175,291.00 | Rs crore |

The extreme downward maximum shows why a decrease cannot automatically be treated as a genuine cost saving; it may be a source correction or a change in reporting convention. The 180 upward events establish that a future-escalation target is conceptually observable from Table history, but the event base is small and highly imbalanced. A later target must define whether any upward change, a material threshold, or cumulative net escalation within H months is intended; none is defined here.

## Revised-completion event audit

| Era | Comparable adjacent pairs | Projects changed | Projects with multiple changes | Extensions | Reductions |
|---|---:|---:|---:|---:|---:|
| Legacy | 1,607 | 145 | 37 | 185 | 10 |
| Six-digit | 11,506 | 1,106 | 602 | 2,096 | 84 |
| Overall | 13,113 | 1,251 | 639 | 2,281 | 94 |

Extensions have a median magnitude of 3 months, P25/P75 of 1/7 months, mean 6.19 months, and maximum 135 months. Reductions have a median absolute magnitude of 3.5 months, P25/P75 of 2/8.75 months, mean 8.19 months, and maximum 96 months.

Future schedule revision is therefore the best-supported candidate Table-history target. However, 43.30% of all revised-completion values are missing, including 71.70% in the legacy layout, so target observability depends on explicit source semantics and cannot treat a missing revised date as proof of “no revision.”

## Physical-progress history

| Scope | Projects with ≥3 reported months | ≥6 | ≥9 | ≥12 |
|---|---:|---:|---:|---:|
| Legacy | 1,555 | 1,340 | 0 | 0 |
| Six-digit | 2,126 | 1,917 | 751 | 629 |
| Overall | 3,681 | 3,257 | 751 | 629 |

Across 23,711 comparable adjacent pairs:

- increases: 11,878
- unchanged: 11,414
- reported decreases/corrections: 419

There are 4,688 maximal unchanged-progress runs affecting 2,920 projects. Of these, 2,597 last at least 3 consecutive months, 670 at least 6, 81 at least 9, and 36 at least 12. Median run length is 3 months; the maximum is 13 months.

Future stagnation can be audited from Table history, but a later target must distinguish true lack of progress from rounding, reporting cadence, agency behaviour, missing reports, and corrections. The 419 decreases must remain reported corrections/anomalies rather than being clamped.

## Cumulative-expenditure history

All 28,581 rows contain a reported cumulative-expenditure value. Projects with usable reported histories are:

- at least 2 months: 3,911
- at least 3 months: 3,830
- at least 6 months: 3,444
- at least 9 months: 751
- at least 12 months: 629

Across 24,508 comparable adjacent pairs:

- increases: 14,055
- unchanged: 9,827
- reported decreases/corrections: 626
- positive-to-zero resets: 15

Zero reporting is substantial and must not be converted to missing:

- 2,787 zero-expenditure project-month rows
- 625 projects report zero at least once
- 274 projects report zero in every available expenditure observation
- 1,747 zero-expenditure rows nevertheless report positive physical progress, affecting 373 projects

The dominant exact agency labels for zero expenditure with positive progress are:

| Exact source agency | Expenditure rows | Zero rows | Zero + positive-progress rows | Affected projects |
|---|---:|---:|---:|---:|
| `MoRTH` | 4,571 | 1,400 | 1,152 | 206 |
| `NHIDCL` | 2,403 | 570 | 403 | 101 |
| `PGCIL` | 348 | 83 | 34 | 10 |
| `ministry of housing and urban affairs` | 77 | 18 | 18 | 2 |
| `NHAI` | 3,821 | 71 | 17 | 6 |
| `Western Coalfields Limited [WCL]` | 345 | 37 | 15 | 3 |

The labels `NHAI` and `National Highways Authority of India [NHAI]` remain separate exact categories; the latter has 13 zero rows and 5 zero-plus-positive-progress rows. Any future comparison-only agency normalization must preserve both raw values and be versioned outside the canonical dataset.

## Category coverage and sparsity

“Extremely sparse” is an audit flag defined as fewer than 10 project-month rows or fewer than 3 unique source codes. It is not a modelling cutoff.

| Dimension | Exact nonmissing categories | Extremely sparse categories | Missing rows |
|---|---:|---:|---:|
| Ministry | 17 | 1 | 9,980 structural |
| Sector | 45 | 10 | 0 |
| Agency | 356 | 192 | 0 |
| State | 152 | 52 | 6 source missing |

Largest exact categories include:

- Ministries: `Ministry of Road Transport & Highways` 7,976 rows/1,187 projects; `Ministry of Railways` 3,236/319; `Ministry of Coal` 1,616/137.
- Sectors: `Roads & Highways` 7,976/1,187; `ROAD TRANSPORT AND HIGHWAYS` 5,861/1,042; `Railways` 3,257/321.
- Agencies: `MoRTH` 4,571/736; `NHAI` 3,821/1,012; `National Highways Authority of India [NHAI]` 2,952/586; `NHIDCL` 2,403/379.
- States: `Maharashtra` 1,806/213; `Uttar Pradesh` 1,228/164; `Gujarat` 1,092/128. The separate legacy label `UTTAR PRADESH` has 768 rows/142 projects.

Sparse categories and superficial label variants will make unpooled categorical estimates unstable. A future analytical representation may map exact values to versioned normalized categories, but the source fields must remain unchanged and available.

## Hypothetical horizon eligibility—no labels built

Primary counts require a complete project history from T through T+H. The calendar ceiling shows the maximum possible observations based only on dataset endpoints.

| Era | Horizon | Complete project histories | Calendar coverage ceiling |
|---|---:|---:|---:|
| Legacy | 1 month | 8,193 | 8,385 |
| Legacy | 3 months | 4,753 | 5,078 |
| Legacy | 6 months | 0 | 0 |
| Legacy | 12 months | 0 | 0 |
| Six-digit | 1 month | 16,315 | 16,826 |
| Six-digit | 3 months | 11,985 | 12,992 |
| Six-digit | 6 months | 6,038 | 7,122 |
| Six-digit | 12 months | 552 | 791 |

These counts do not prove label observability. A project that disappears before T+H may have completed, left reporting coverage, changed identifier, or become censored; absence cannot automatically be labelled as no event.

## Preliminary leakage-risk table

| Field | Classification | Rationale |
|---|---|---|
| `project_code` | `IDENTIFIER_ONLY` | Grouping/split key, not predictive signal; era redesign remains unbridged. |
| `project_name` | `IDENTIFIER_ONLY` | Near-unique text can memorize identity; text use would need project-grouped temporal evaluation. |
| `legacy_ocms_code`, `pmgid` | `IDENTIFIER_ONLY` | Identifier/provenance only. |
| `agency` | `SAFE_BASE_FEATURE` | Known at T, but label drift and sparse exact levels require care. |
| `ministry` | `CONDITIONALLY_SAFE` | Known where present; structural legacy absence strongly encodes era/layout. |
| `sector` | `SAFE_BASE_FEATURE` | Known at T; exact labels must remain available. |
| `state` | `SAFE_BASE_FEATURE` | Known at T; multi-state and source-label conventions need explicit treatment. |
| `approval_date` | `SAFE_BASE_FEATURE` | Historical date known at T. |
| `start_date` | `CONDITIONALLY_SAFE` | Historical where present, but structurally absent through July 2025. |
| `original_completion_date` | `SAFE_BASE_FEATURE` | Baseline schedule known at T. |
| `revised_completion_date` | `LIKELY_LEAKAGE_FOR_CERTAIN_TARGETS` | Valid state at T for predicting later revision; direct leakage for current-revision/current-delay targets. |
| `original_cost` | `SAFE_BASE_FEATURE` | Baseline cost known at T. |
| `revised_cost` | `LIKELY_LEAKAGE_FOR_CERTAIN_TARGETS` | Valid T-state for future escalation; direct leakage for current escalation or “ever revised by T.” |
| `cumulative_expenditure` | `CONDITIONALLY_SAFE` | T value may be used; future values/deltas leak. Zero reporting is agency dependent. |
| `physical_progress` | `CONDITIONALLY_SAFE` | T value may be used; values from the target stagnation window leak. |
| `report_month` | `CONDITIONALLY_SAFE` | Required for temporal splits; also encodes reporting/schema regime. |
| Raw fields and provenance | `IDENTIFIER_ONLY` | Retain for audit; do not model PDF layout, page order, or source formatting. |

All feature decisions must enforce an as-of-T snapshot. Random project-month row splits would leak the same project across train and test and are inappropriate.

## Potential target availability

### Future cost revision

Table history can reveal later reported revised-cost changes. It cannot establish final cost. The 180 observed upward changes show conceptual feasibility, but the low event rate, only 34 multiply revised projects, selective legacy revised-cost reporting, and extreme downward corrections make the present history too thin for a final cost-escalation model. A prototype could test mechanics only.

### Future schedule revision

Table history contains 2,281 extensions across 1,251 changed projects, with 639 projects changing revised completion more than once. This is the strongest candidate for a prototype, provided missing revised dates are handled as “not observable” rather than “no extension.” It still predicts later reported schedule revision, not actual completion or final delay.

### Future stagnation

Table history contains 11,414 unchanged adjacent progress pairs and 2,597 runs of at least three months. This supports a prototype future-stagnation question. The eventual target definition must specify horizon, tolerance/rounding, required reporting completeness, and treatment of corrections.

## Outcomes requiring Completed Projects data

Ongoing-project tables alone cannot defensibly supply:

- actual completion date
- final delay relative to original or revised schedule
- final project cost
- completion status at the end of an observation window when a project disappears

These outcomes require a separately validated Completed Projects history and a defensible source identifier relationship. Revised completion and revised cost in ongoing reports are planning/status values, not terminal outcomes. No Completed Projects data was extracted or integrated in this audit.

## What to obtain before training

1. Extract and validate 2024 and 2023 ongoing-project histories using the accepted fail-closed pipeline, without assuming identifier continuity.
2. Re-run this audit per discovered identifier era/layout. More history should increase 6- and 12-month windows and reveal whether the low cost-revision count is stable.
3. Before terminal delay/final-cost modelling, separately inspect and extract Completed Projects tables and establish source-supported linkage rules.
4. Define one target at a time with explicit as-of date, horizon, observability/censoring policy, revision threshold, and temporal/project-grouped evaluation.
5. Build any normalization only as a separate, versioned analytical layer retaining all exact source values.

## Machine-readable outputs

Detailed audit results are under `data/validation/audit/`:

- `audit_manifest.json`
- `coverage_summary.json`
- `field_missingness.json`
- `event_audit.json`
- `category_coverage.json`
- `horizon_eligibility.json`
- `leakage_risk.json`

## Final integrity verification

- Expanded regression suite: **65/65 tests passing** (the original 62 plus three audit regressions).
- All 19 accepted monthly CSV SHA-256 hashes are unchanged.
- Combined CSV SHA-256 remains `A366C2BA57055BE107EF687373477F1704242E00D64ABECFEC59AFD93CC1BB91`.
- The audit read 28,581 canonical rows and wrote only validation/report artifacts.
- No source value, canonical CSV, identifier, crosswalk status, or extraction output was altered.
