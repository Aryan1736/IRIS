# June-July 2025 Project Identifier Crosswalk Investigation

## Conclusion

A defensible **partial, proposed analytical bridge** can be constructed, but a complete old-ID-to-new-ID crosswalk cannot be supported from the reports alone.

- Neither report prints an explicit old-to-new identifier relationship.
- The conservative investigation proposes 137 `HIGH_CONFIDENCE` one-to-one links.
- 346 June projects have one or more unresolved candidate relationships (`AMBIGUOUS`).
- 1,112 June projects have no retained July candidate (`UNMATCHED`).
- No proposed mapping has been integrated into `projects_monthly.csv`, and no source-reported `project_code` has been changed.

These proposals are suitable for review in a separate analytical identity layer. They are not source crosswalks and must not be represented as such.

## Source identifier inspection

| Check | June 2025 | July 2025 |
|---|---:|---:|
| Unique projects | 1,595 | 791 |
| Rows with legacy `N########` or nine-digit-style ID | 1,595 | 0 |
| Rows with six-digit ID | 0 | 791 |
| Rows printing both ID styles | 0 | 0 |
| Populated extracted `legacy_ocms_code` | 0 | 0 |
| Populated extracted `pmgid` | 0 | 0 |
| Explicit source crosswalks | 0 | 0 |

The June report mentions OCMS only as a report/data-source context and prints a single legacy-style project code in each Table 7 project cell. The July `All Ongoing Projects` table prints a single six-digit project code. No row in either report prints both identifiers, a legacy-ID label, or a PMGID that could act as an explicit bridge.

The compared source attributes were project name, agency, ministry where available, sector, state, approval date, original cost, revised cost, original completion date, and revised completion date. June does not provide a populated ministry field in the canonical extraction. Missing fields were treated as unavailable evidence, never inferred.

## Matching criteria actually used

Name similarity was used only to retrieve candidates. It never created a mapping by itself.

A pair entered the candidate set only when at least one of the following held:

1. Project names were equal after comparison-only normalization.
2. Name similarity was at least 0.68 and at least two independent attributes agreed.
3. Name similarity was at least 0.50 and at least four independent attributes agreed.

A candidate was proposed as `HIGH_CONFIDENCE` only when all of these conditions held:

- it was the only high-eligible July candidate for the June project;
- it was the only high-eligible June candidate for the July project;
- state, approval date, and original cost had no material conflict;
- agency or state agreed; and
- project-name evidence was supported by multiple independent attributes: exact normalized name plus at least three agreeing attributes, similarity at least 0.80 plus at least four, or similarity at least 0.65 plus at least five.

Agreement and conflict columns in the CSV record evidence for project name, agency, sector, state, approval date, original cost, revised cost, and original/revised completion dates. Revised cost and completion-date differences are recorded as changes; they do not automatically disqualify identity when the stable fields are strong and conflict-free. Missing comparisons are recorded separately.

`AMBIGUOUS` means that candidate evidence exists but the conservative high-confidence rules were not satisfied. `UNMATCHED` means no retained candidate relationship was found; it does not prove that the project disappeared.

## Results

### June project outcomes

| Outcome | June projects |
|---|---:|
| `EXACT_SOURCE_CROSSWALK` | 0 |
| `HIGH_CONFIDENCE` | 137 |
| `AMBIGUOUS` | 346 |
| `UNMATCHED` | 1,112 |
| **Total** | **1,595** |

The ambiguous file contains 408 candidate edges involving 346 distinct June projects and 347 distinct July projects. On the July side, 137 projects have a high-confidence proposed link, 347 participate only in ambiguous relationships, and 307 have no retained June candidate, totaling 791 July projects.

### Relationship ambiguity

- 41 unresolved one-June-to-multiple-July candidate structures were detected. These are **possible split patterns**, not confirmed project splits.
- 44 unresolved multiple-June-to-one-July candidate structures were detected. These are **possible merger patterns**, not confirmed project mergers.
- Similar-name families are especially risky. For example, June `N18000391` through `N18000394` and July `615332` through `615346` include several Rajasthan REZ transmission packages with overlapping wording and some agreeing dates. The pairings remain unresolved because the candidate graph is many-to-many and contains state/original-cost conflicts.
- June `N22000574` has four retained July railway candidates. Although July `709815` has the closest project wording, approval/completion evidence conflicts and the relationship remains unresolved.
- June `N30000036` (Munger sewer project) and July `616616` (Hajipur sewer project) share a generic name pattern, state, and approval month, but refer to different locations and conflict on agency, sector, cost, and completion dates. The pair is retained only as a diagnostic `AMBIGUOUS` example and is not mapped.

## Representative high-confidence evidence

| Legacy ID -> New ID | Project-name comparison | Agency comparison | State | Approval | Original cost | Completion evidence | Recorded changes |
|---|---|---|---|---|---:|---|---|
| `N16000484` -> `709754` | Same LPG facilities project at Kamardanga, case only | `HPCL` -> `Hindustan Petroleum Corporation Limited` | Assam agrees | 2023-03 agrees | 156.36 agrees | Original and revised 2027-07 agree | Sector label changed |
| `N16000535` -> `709761` | `HP TRIJET UNIT IN VR` -> expanded Visakh Refinery name | `HPCL` -> `Hindustan Petroleum Corporation Limited` | Andhra Pradesh agrees | 2024-07 agrees | 193.00 agrees | Original 2027-07 agrees | July prints revised cost/date where June is blank; sector changed |
| `N16000485` -> `709766` | CGD acronym expanded; same three districts | `IOCL` -> `MinistryofPetroleumNaturalGas` | Andhra Pradesh agrees | 2022-03 agrees | 1,420.00 agrees | Original 2030-03 agrees | Agency/group label and sector changed; July revised fields populated |
| `N16000386` -> `701324` | Same Barauni refinery 6.0-to-9.0 MMTPA expansion | `IOCL` -> `Ministry of Petroleum & Natural Gas` | Bihar agrees | 2020-01 agrees | 14,810.00 agrees | Original 2023-04 and revised 2026-08 agree | Revised cost changed 18,113 -> 16,724; agency/sector labels changed |

The third and fourth examples demonstrate why agency, sector, revised cost, or revised completion changes were recorded rather than made automatic identity vetoes. High confidence still required unique bidirectional eligibility and no conflict in state, approval date, or original cost.

## Manual PDF verification

The following cases were visually checked in both source PDFs against the extracted provenance:

| Case | June page | July page | Result |
|---|---:|---:|---|
| Obvious same project: `N16000484` -> `709754` | 57 | 49 | Name, location, approval, cost, dates, and state match; agency is acronym versus full name. |
| Renamed/expanded project: `N16000535` -> `709761` | 43 | 49 | Abbreviated `VR` expands to Visakh Refinery; independent stable fields agree. |
| Changed agency/group label: `N16000485` -> `709766` | 43 | 49 | Project, districts, approval, cost, date, and state agree; July agency-like value differs and is preserved as printed. |
| Changed revised cost: `N16000386` -> `701324` | 64 | 50 | Stable fields and completion dates agree; revised cost change is recorded, not silently corrected. |
| Similar wording but different projects: `N30000036` vs `616616` | 73 | 64 | Munger versus Hajipur plus multiple attribute conflicts; remains unresolved. |
| Ambiguous multi-candidate family: Rajasthan REZ transmission packages | reviewed in source tables | reviewed in source tables | Repeated package wording and many-to-many candidates prevent a unique mapping. |

The visual checks confirmed that the compared values and identifiers are genuinely printed in the reports. No hidden second identifier or footnote-based crosswalk was found in these cases.

## Proposed future analytical representation

The canonical source layer should remain unchanged. A separate reviewed analytical layer could add:

| Field | Proposed meaning |
|---|---|
| `project_code` | Exact source-reported code for that report month. |
| `stable_project_id` | A separate internal surrogate assigned only after a mapping is approved; do not overwrite or reuse the source code. |
| `id_mapping_status` | `SOURCE_NATIVE`, `HIGH_CONFIDENCE_PROPOSED`, `AMBIGUOUS`, or `UNMATCHED`. |
| `id_mapping_method` | For example `EXPLICIT_SOURCE_CROSSWALK` or `MULTI_ATTRIBUTE_BIDIRECTIONAL_UNIQUE`; retain the evidence version. |

The relationship table should retain both source codes, the matching-rule version, evidence fields, conflicting fields, source files/pages, and review status. The 137 high-confidence proposals should remain proposals until explicitly accepted; ambiguous relationships should have no stable identity assigned.

## Limitations

- There is no source-issued crosswalk, so even strong attribute agreement is inferential.
- July contains fewer projects than June, and report scope or publication conventions may have changed alongside the identifier redesign.
- Agency, sector, revised cost, and completion-date conventions can change between reports.
- Generic or templated project names create false similarity, especially for transmission, railway, airport, coal, and water projects.
- Splits and mergers cannot be confirmed from candidate graph shape alone.
- `UNMATCHED` includes both genuinely absent projects and projects for which available attributes were insufficient or changed too substantially.

No January-March 2025 report was processed, no machine learning was used, and no canonical project-month file was modified by this investigation.
