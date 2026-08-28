# PAIMANA longitudinal-warning diagnosis: January–July 2026

## Scope

This is a read-only diagnosis of the accepted January–July 2026 project-month baseline. No source, cleaned, or combined canonical value was modified. No normalization, imputation, feature engineering, target creation, or ML was performed. `POSITIVE_EXPENDITURE_TO_ZERO` is a separately reported subset of `CUMULATIVE_EXPENDITURE_DECREASED`.

## Rule-level counts

| Transition | Agency changed | Project name changed | State changed | Cum. expenditure decreased | Physical progress decreased | Revised cost decreased | Positive expenditure → zero | Recorded events* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Jan→Feb | 21 | 2 | 1 | 42 | 6 | 0 | 4 | 76 |
| Feb→Mar | 0 | 6 | 2 | 24 | 13 | 0 | 1 | 46 |
| Mar→Apr | 4 | 3 | 1 | 37 | 15 | 6 | 0 | 66 |
| Apr→May | 5 | 1 | 0 | 39 | 35 | 8 | 0 | 88 |
| May→Jun | 578 | 7 | 0 | 38 | 19 | 6 | 6 | 654 |
| Jun→Jul | 236 | 147 | 24 | 85 | 91 | 44 | 2 | 629 |
| **All** | **844** | **166** | **28** | **265** | **179** | **64** | **13** | **1,559** |

\* Recorded events include the 13 positive→zero cases both in their parent rule and as a separately requested subset.

## Agency-change classification

| Classification | Jan→Feb | Feb→Mar | Mar→Apr | Apr→May | May→Jun | Jun→Jul | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Exact genuine different agency names | 0 | 0 | 1 | 0 | 5 | 148 | 154 |
| Abbreviation/acronym differences | 2 | 0 | 0 | 3 | 557 | 12 | 574 |
| Whitespace/punctuation/casing differences | 17 | 0 | 0 | 1 | 2 | 1 | 21 |
| Apparent source spelling changes | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Likely extraction/group-heading propagation issue | 2 | 0 | 3 | 1 | 14 | 75 | 95 |

Representative examples:

- Genuine different labels: `WPO/Patna` → `South Central Railway [SCR] - II`; `MIS MoCoal Integration Logins` → `INVALID CO.`; `East Coast Railway [ECoR] - II` → `CAO/C/ECOR ECoR mor`; `NHIDCL` → `NICDC`.
- Abbreviation/acronym: `National Highways Authority of India [NHAI]` → `NHAI`; `Western Coalfields Limited [WCL]` → `WCL - CIL`; `National Mission for Clean Ganga` → `NMCG1`.
- Whitespace/punctuation/case: parenthesis-to-bracket variants such as `(NHPC)` → `[NHPC]`; `Ministry of Petroleum & Natural Gas` → `MinistryofPetroleumNaturalGas`.
- Apparent source spelling changes: none could be isolated confidently as spelling-only.
- Group-label propagation: `Ministry of Coal` → `CCL - CIL`; `Oil and Natural Gas Corporation Limited [ONGC]` → `MinistryofPetroleumNaturalGas`; `GAIL Gas` → `Ministry of Petroleum & Natural Gas`.

Preserved raw cells and PDF pages show the group-level labels in the source rows. They are therefore apparent **source group-label propagation**, not parser-invented substitutions.

## Top 20 exact agency transitions

| Previous agency | Current agency | Count |
|---|---|---:|
| National Highways Authority of India [NHAI] | NHAI | 497 |
| Western Coalfields Limited [WCL] | WCL - CIL | 32 |
| East Coast Railway [ECoR] - II | CAO/C/ECOR ECoR mor | 14 |
| MinistryofPetroleumNaturalGas | Indian Oil Corporation Limited [IOCL] | 14 |
| South Eastern Coalfields Limited [SECL] | SECL - CIL | 13 |
| Ministry of Petroleum & Natural Gas | Indian Oil Corporation Limited [IOCL] | 11 |
| South Western Railway [SWR] - II | CAOC/SWR SWR mor | 10 |
| Eastern Coal Fields Limited [ECL] | ECL - CIL | 9 |
| Ministry of Coal | CCL - CIL | 9 |
| North Western Railway [NWR] | CAOC/NWR NWR mor | 9 |
| East Central Railway [ECR] - I | CAO/Con/North/MHX ECR mor | 8 |
| East Central Railway [ECR] - I | CAO/Con/South/MHX ECR mor | 8 |
| Ministry of Petroleum & Natural Gas | Gas Authority of India Limited [GAIL] | 8 |
| Ministry of Petroleum & Natural Gas | Oil and Natural Gas Corporation Limited [ONGC] | 8 |
| MinistryofPetroleumNaturalGas | Bharat Petroleum Corporation Limited [BPCL] | 8 |
| South Central Railway [SCR] - II | CAO/C/SCoR SCoR mor | 8 |
| Western Railway [WR] - II | CAOCWR WR mor | 8 |
| Central Railway [CR] - II | CAOC/CR CR mor | 6 |
| Northern Coalfields Limited [NCL] | NCL - CIL | 5 |
| SECR | CAOC/SECR SECR mor | 5 |

## Project-name changes

| Transition | Superficial only | Substantive text change |
|---|---:|---:|
| Jan→Feb | 0 | 2 |
| Feb→Mar | 2 | 4 |
| Mar→Apr | 2 | 1 |
| Apr→May | 1 | 0 |
| May→Jun | 3 | 4 |
| Jun→Jul | 7 | 140 |
| **All** | **15** | **151** |

Superficial equivalence uses Unicode-to-ASCII, lowercase, and non-alphanumeric removal solely for comparison. The source strings remain intact. The June→July substantive cases include large title expansions and rewordings, especially railway projects; for example project `400273` changes from `Tarakeshwar-Bishnupur New Line [82.47 km]` to a much longer title adding extensions and material modifications.

## Cumulative-expenditure decreases

There are 265 cases. The workbook's **Exp Decreases** sheet shows, for every case, previous value, current value, absolute and percentage decrease, agency, ministry, project code, project name, and both PDF pages.

The 13 positive→zero cases are:

| Transition | Project code | Previous | Current | Absolute decrease | Agency | Ministry |
|---|---:|---:|---:|---:|---|---|
| Jan→Feb | 617960 | 7.40 | 0 | 7.40 | MoRTH | Ministry of Road Transport & Highways |
| Jan→Feb | 617995 | 2.08 | 0 | 2.08 | MoRTH | Ministry of Road Transport & Highways |
| Jan→Feb | 618092 | 437.05 | 0 | 437.05 | MoRTH | Ministry of Road Transport & Highways |
| Jan→Feb | 618986 | 0.24 | 0 | 0.24 | Northeast Frontier Railway [NFR] | Ministry of Railways |
| Feb→Mar | 617967 | 43.83 | 0 | 43.83 | MoRTH | Ministry of Road Transport & Highways |
| May→Jun | 617968 | 422.72 | 0 | 422.72 | MoRTH | Ministry of Road Transport & Highways |
| May→Jun | 617972 | 14.99 | 0 | 14.99 | MoRTH | Ministry of Road Transport & Highways |
| May→Jun | 618125 | 44.45 | 0 | 44.45 | MoRTH | Ministry of Road Transport & Highways |
| May→Jun | 618431 | 0.39 | 0 | 0.39 | NHIDCL | Ministry of Road Transport & Highways |
| May→Jun | 618441 | 72.13 | 0 | 72.13 | NHIDCL | Ministry of Road Transport & Highways |
| May→Jun | 619326 | 0.01 | 0 | 0.01 | South Central Railway [SCR] - II | Ministry of Railways |
| Jun→Jul | 617210 | 62.20 | 0 | 62.20 | CAO/C/SCoR SCoR mor | Ministry of Railways |
| Jun→Jul | 708687 | 183.16 | 0 | 183.16 | Department of Telecommunications | Department of Telecommunications |

Every one is a 100% decrease because the current value is exactly zero.

## Physical-progress decrease distribution

| Transition | <1 pp | 1–5 pp | >5–10 pp | >10 pp |
|---|---:|---:|---:|---:|
| Jan→Feb | 0 | 5 | 0 | 1 |
| Feb→Mar | 2 | 6 | 2 | 3 |
| Mar→Apr | 5 | 5 | 2 | 3 |
| Apr→May | 8 | 22 | 2 | 3 |
| May→Jun | 6 | 11 | 1 | 1 |
| Jun→Jul | 11 | 42 | 13 | 25 |
| **All** | **32** | **91** | **20** | **36** |

Bands are non-overlapping: `<1`; `1–5` inclusive; `>5–10` inclusive; `>10` percentage points.

## Spike diagnosis and recommendation

- **May→June:** 578 of 654 recorded warning events are agency changes. Of those, 557 are abbreviation/acronym differences; the single pair `National Highways Authority of India [NHAI]` → `NHAI` accounts for 494 May→June records (497 across all transitions). This is primarily a mass agency-label convention change, with smaller coal and petroleum group-label updates.
- **June→July:** the spike is broader: 236 agency changes, 147 name changes (140 substantive), 24 state changes, 85 expenditure decreases, 91 physical-progress decreases, and 44 revised-cost decreases. Railway rows commonly switch from zone-level labels to `CAO/...` organizational units while project titles and numeric values are also revised.
- All seven cleaned CSVs have the same header schema and use `pdfplumber-lines-v1`; inspected Table 6 pages retain the same eight columns. Representative May, June, and July rows match the preserved raw cells and visible PDFs. This rules against a parser column-shift or report-table schema break as the primary cause.
- The evidence supports a source-data update convention: May→June is mostly label compression/aliasing; June→July is a broader agency/title/state/numeric refresh. Some changes may reflect genuine project updates, but no automatic correction is justified.

For analysis, build a **separate normalized representation** containing comparison-only text keys and a reviewed agency alias/organizational hierarchy map. Retain the exact canonical source fields alongside every normalized field, and do not overwrite historical values.
