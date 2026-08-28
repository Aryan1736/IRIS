# PAIMANA ongoing-project extraction acceptance: April 2025–July 2026

## Outcome

April, May, and June 2025 passed fail-closed extraction and validation. The source uses a distinct nine-column legacy project-list layout and calls the all-ongoing table Table 7. A semantic adapter named `legacy-all-ongoing-nine-column-v1` was added; it does not select by table index or size.

The legacy reports explicitly provide State and Sector but not Start Date or Ministry. Those absent fields remain missing. Original, parenthesized revised, and braced anticipated values remain intact in raw extraction; only explicitly parenthesized values populate canonical revised fields. No anticipated value is promoted to revised.

## Monthly results

| Month | Source PDF pages | Rows | Missing codes | Duplicate codes | Rejected rows | Warnings | Layout |
|---|---:|---:|---:|---:|---:|---:|---|
| 2025-04 | 43–268 | 1,670 | 0 | 0 | 0 | 253 | legacy-all-ongoing-nine-column-v1 |
| 2025-05 | 43–207 | 1,637 | 0 | 0 | 0 | 242 | legacy-all-ongoing-nine-column-v1 |
| 2025-06 | 41–229 | 1,595 | 0 | 0 | 0 | 228 | legacy-all-ongoing-nine-column-v1 |
| 2025-07 | 37–66 | 791 | 0 | 0 | 0 | 99 | table6-eight-column-approval-only-v1 |
| 2025-08 | 37–66 | 800 | 0 | 0 | 0 | 112 | table6-eight-column-v1 |
| 2025-09 | 42–71 | 794 | 0 | 0 | 0 | 125 | table6-eight-column-v1 |
| 2025-10 | 42–72 | 820 | 0 | 0 | 3 | 130 | table6-eight-column-v1 |
| 2025-11 | 42–72 | 823 | 0 | 0 | 1 | 104 | table6-eight-column-v1 |
| 2025-12 | 50–107 | 1,392 | 0 | 0 | 2 | 406 | table6-eight-column-v1 |
| 2026-01 | 62–133 | 1,702 | 0 | 0 | 3 | 573 | table6-eight-column-v1 |
| 2026-02 | 65–167 | 1,948 | 0 | 0 | 2 | 717 | table6-eight-column-v1 |
| 2026-03 | 55–156 | 1,941 | 0 | 0 | 1 | 711 | table6-eight-column-v1 |
| 2026-04 | 55–162 | 1,981 | 0 | 0 | 1 | 723 | table6-eight-column-v1 |
| 2026-05 | 54–162 | 1,987 | 0 | 0 | 1 | 756 | table6-eight-column-v1 |
| 2026-06 | 59–159 | 1,847 | 0 | 0 | 0 | 675 | table6-eight-column-v1 |
| 2026-07 | 55–152 | 1,775 | 0 | 0 | 0 | 554 | table6-eight-column-v1 |

The 14 previously accepted rejected rows are unchanged and all have reason `empty_table_row`. April–June 2025 have no rejected rows.

For each new month, serials are continuous from 1 through the monthly row count, identifiers are unique and complete, all source-present dates parse successfully, and all source-present cost, expenditure, and physical-progress values parse successfully.

## Manual source comparison

Rendered source pages were compared against the cleaned rows, including first and last records, page boundaries, multiline names, parenthesized revised values, missing revised values, large numeric values, and the nested agency name `HPCLRRL(JV)`.

- April: serials 1, 2, 8, 9, 842, 1,078, 1,245, and 1,670 on PDF pages 43, 44, 156, 186, 209, and 268.
- May: serials 1, 2, 11, 12, 825, 1,065, 1,223, and 1,637 on PDF pages 43, 44, 125, 146, 162, and 207.
- June: serials 1, 2, 8, 9, 801, 1,033, 1,188, and 1,595 on PDF pages 41, 42, 135, 161, 180, and 229.

All 24 representative comparisons matched the source. Raw page and row provenance is present for every cleaned record.

## Combined dataset

- Project-month observations: 23,503
- Unique project identifiers: 3,933
- Missing project codes: 0
- Duplicate `(project_code, report_month)` keys: 0
- Projects with at least 3 observations: 3,701
- Projects with at least 6 observations: 1,917
- Projects with at least 12 observations: 629
- Projects with at least 16 observations: 0
- Projects present in all 16 months: 0
- Combined SHA-256: `73E47AA487E70A28FE3C984E532A6E23D21897B60C176BEEA80FB1C06F73E191`

The zero all-month count is caused by the documented June-to-July identifier-system change: the legacy reports use `N########` or nine-digit source codes, while July uses the redesigned six-digit project IDs. No inferred crosswalk was introduced.

## New longitudinal transitions

| Transition | Overlap | Revised cost down | Expenditure down | Progress down | Positive→zero | Name changed | Agency changed | Ministry changed | Sector changed | State changed | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Apr→May | 1,622 | 1 | 49 | 39 | 0 | 262 | 0 | 0 | 33 | 258 | 642 |
| May→Jun | 1,590 | 2 | 6 | 26 | 0 | 196 | 0 | 0 | 30 | 235 | 495 |
| Jun→Jul | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

All later accepted transitions remain in `data/validation/longitudinal_summary_2025_04_2026_07.json`. Across all 15 transitions, rule totals are: agency changed 967; project name changed 666; state changed 529; cumulative expenditure decreased 498; physical progress decreased 305; revised cost decreased 99; sector changed 72; positive expenditure to zero 15; ministry changed 0; total 3,151.

## Integrity and tests

- Full regression suite: 51/51 passing.
- Previously accepted monthly CSV hashes: 13/13 exact matches.
- Previously accepted July 2025–July 2026 combined SHA-256 was confirmed as `C833EE52AEEE92D9350B584BB385A9E6305266CCD0C26C9964429214EF66FACB` before rebuilding.
- Artifact-level CSV inspection found 23,504 spreadsheet rows including the header and 31 columns, matching 23,503 project-month data rows.
- No feature engineering, normalization, imputation, target creation, or ML was performed.
