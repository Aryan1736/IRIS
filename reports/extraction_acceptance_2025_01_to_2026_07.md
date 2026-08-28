# PAIMANA ongoing-project extraction acceptance: January 2025-July 2026

## Outcome

January, February, and March 2025 passed fail-closed extraction and individual validation. All three use the existing `legacy-all-ongoing-nine-column-v1` adapter and call the all-ongoing project list Table 7. No new table adapter was required.

January and March have a character-spaced embedded PDF text layer for some dates, including values such as `2 - 2 0 1 8`, `J u n -24`, and `May-23`. A narrowly scoped legacy-date parser update compacts whitespace only for parsing and supports the report's abbreviated `Mon-YY` form. The exact extracted strings remain in the `*_raw` fields. Character-spaced `N . A .` remains missing. No date, day, or absent field was inferred.

## Monthly results

| Month | Table pages | Rows | Rejected | Warnings | Layout |
|---|---:|---:|---:|---:|---|
| 2025-01 | 42-239 | 1,719 | 0 | 228 | `legacy-all-ongoing-nine-column-v1` |
| 2025-02 | 42-246 | 1,682 | 0 | 210 | `legacy-all-ongoing-nine-column-v1` |
| 2025-03 | 40-239 | 1,677 | 0 | 222 | `legacy-all-ongoing-nine-column-v1` |
| 2025-04 | 43-268 | 1,670 | 0 | 253 | `legacy-all-ongoing-nine-column-v1` |
| 2025-05 | 43-207 | 1,637 | 0 | 242 | `legacy-all-ongoing-nine-column-v1` |
| 2025-06 | 41-229 | 1,595 | 0 | 228 | `legacy-all-ongoing-nine-column-v1` |
| 2025-07 | 37-66 | 791 | 0 | 99 | `table6-eight-column-approval-only-v1` |
| 2025-08 | 37-66 | 800 | 0 | 112 | `table6-eight-column-v1` |
| 2025-09 | 42-71 | 794 | 0 | 125 | `table6-eight-column-v1` |
| 2025-10 | 42-72 | 820 | 3 | 130 | `table6-eight-column-v1` |
| 2025-11 | 42-72 | 823 | 1 | 104 | `table6-eight-column-v1` |
| 2025-12 | 50-107 | 1,392 | 2 | 406 | `table6-eight-column-v1` |
| 2026-01 | 62-133 | 1,702 | 3 | 573 | `table6-eight-column-v1` |
| 2026-02 | 65-167 | 1,948 | 2 | 717 | `table6-eight-column-v1` |
| 2026-03 | 55-156 | 1,941 | 1 | 711 | `table6-eight-column-v1` |
| 2026-04 | 55-162 | 1,981 | 1 | 723 | `table6-eight-column-v1` |
| 2026-05 | 54-162 | 1,987 | 1 | 756 | `table6-eight-column-v1` |
| 2026-06 | 59-159 | 1,847 | 0 | 675 | `table6-eight-column-v1` |
| 2026-07 | 55-152 | 1,775 | 0 | 554 | `table6-eight-column-v1` |

The 14 rejected rows in the accepted range are unchanged and all have reason `empty_table_row`. January-June 2025 have no rejected rows.

For January-March, printed serials are continuous from 1 through the monthly row count; project identifiers are complete and unique within each report; all source-present dates, costs, expenditures, and physical-progress values parse successfully; and every cleaned row has file/page/row/serial provenance. Start Date and Ministry are absent from these legacy reports and remain missing.

## New-month warning counts by rule

| Rule | Jan | Feb | Mar |
|---|---:|---:|---:|
| `EXTREME_EXPENDITURE_COST_MISMATCH` | 5 | 5 | 5 |
| `FULL_PROGRESS_STILL_ONGOING` | 129 | 110 | 122 |
| `REVISED_COST_BELOW_ORIGINAL` | 76 | 74 | 75 |
| `ZERO_EXPENDITURE_POSITIVE_PROGRESS` | 18 | 21 | 20 |
| All other existing cross-field rules | 0 | 0 | 0 |
| **Total** | **228** | **210** | **222** |

These are source-quality warnings only. No warned value was corrected, normalized, rejected, or imputed.

## Manual source verification

Rendered PDF pages were compared with cleaned rows for each newly added report:

- January: first project serial 1 on page 42; page boundary 93/94 on pages 52/53; multiline serial 516 on page 101; ₹108,000.00 crore serial 1,111 on page 168; last serial 1,719 on page 239.
- February: first project serial 1 on page 42; page boundary 89/90 on pages 52/53; multiline serial 793 on page 139; ₹108,000.00 crore serial 1,096 on page 171; last serial 1,682 on page 246.
- March: first project serial 1 on page 40; page boundary 90/91 on pages 50/51; ₹108,000.00 crore serial 1,082 on page 166; multiline serial 1,505 on page 217; last serial 1,677 on page 239.

The comparisons covered exact project codes, project/agency cells, state/sector labels, approval and completion dates, parenthesized revised values, braced anticipated values, missing revised values, expenditure, progress, first/last records, and continuation boundaries. All checked canonical values and provenance matched the printed source. Anticipated values were not promoted to revised values.

## Combined dataset

The combined source-faithful dataset now explicitly covers January 2025 through July 2026:

- Project-month observations: **28,581**
- Unique source project codes: **4,029**
- Missing project codes: **0**
- Duplicate `(project_code, report_month)` keys: **0**
- Projects with at least 3 observations: **3,830**
- Projects with at least 6 observations: **3,444**
- Projects with at least 12 observations: **629**
- Projects with at least 19 observations: **0**
- Combined SHA-256: `A366C2BA57055BE107EF687373477F1704242E00D64ABECFEC59AFD93CC1BB91`

The zero 19-month count is expected because the source identifier system changes between June and July 2025. The diagnostic crosswalk was not integrated.

## Continuity by identifier era

| Statistic | Legacy-ID era, Jan-Jun 2025 | Six-digit-ID era, Jul 2025-Jul 2026 |
|---|---:|---:|
| Months | 6 | 13 |
| Project-month rows | 9,980 | 18,601 |
| Unique source codes | 1,786 | 2,243 |
| Projects with at least 3 observations | 1,704 | 2,126 |
| Projects with at least 6 observations | 1,527 | 1,917 |
| Projects with at least 12 observations | 0 | 629 |
| Projects present in every era month | 1,527 | 552 |
| Adjacent overlap range | 1,590-1,673 | 760-1,951 |
| Mean adjacent overlap | 1,638.6 | 1,359.6 |

These statistics use exact source-reported codes within each era. They do not bridge June-July 2025.

## New adjacent-month transitions

| Transition | Overlap | Earlier only | Later only | Revised cost down | Expenditure down | Progress down | Positive-to-zero | Name changed | Agency changed | Ministry changed | Sector changed | State changed | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Jan-Feb 2025 | 1,673 | 46 | 9 | 2 | 15 | 40 | 0 | 262 | 0 | 0 | 6 | 269 | 594 |
| Feb-Mar 2025 | 1,665 | 17 | 12 | 2 | 5 | 42 | 0 | 43 | 0 | 0 | 6 | 0 | 98 |
| Mar-Apr 2025 | 1,643 | 34 | 27 | 0 | 108 | 32 | 0 | 90 | 0 | 0 | 6 | 0 | 236 |

Across all 18 adjacent transitions, longitudinal warning totals are:

- `AGENCY_CHANGED`: 967
- `PROJECT_NAME_CHANGED`: 1,061
- `MINISTRY_CHANGED`: 0
- `SECTOR_CHANGED`: 90
- `STATE_CHANGED`: 798
- `CUMULATIVE_EXPENDITURE_DECREASED`: 626
- `PHYSICAL_PROGRESS_DECREASED`: 419
- `REVISED_COST_DECREASED`: 103
- positive cumulative expenditure to exactly zero: 15
- total: 4,079

All previously accepted later-transition diagnostics remain in the new 19-month longitudinal summary and their source monthly files are unchanged.

## Integrity

- Full regression suite: **62/62 tests passing**.
- All 16 previously accepted monthly CSV SHA-256 hashes matched their baseline after the parser update and new extraction.
- The previously accepted combined SHA-256 before the explicit rebuild was `73E47AA487E70A28FE3C984E532A6E23D21897B60C176BEEA80FB1C06F73E191`.
- New monthly CSV SHA-256 values: January `214444FF39AEC6C8017F6B4B1A864989E094758291EF28B17278BF201A5CD72E`; February `00D5185600DB5EEF893CECA001CD51DFED1338373117C82F468A7E29D82CAAF3`; March `2697C4C9601EC94B3DE42CAAEB78ED92FA645916439522CE0EF727F917209722`.
- The June-July 2025 proposed identifier crosswalk remains diagnostic only and is not present in the canonical data.
- No source field normalization, feature engineering, target creation, imputation, or machine learning was performed.
