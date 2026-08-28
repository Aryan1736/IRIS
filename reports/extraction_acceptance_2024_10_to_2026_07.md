# PAIMANA ongoing-project extraction acceptance: 2024-10 to 2026-07

## Outcome

October, November, and December 2024 were processed individually and accepted before the combined rebuild. The rebuilt source-faithful dataset covers 22 ordered months from October 2024 through July 2026.

- Project-month rows: **33,794**
- Unique source project codes: **4,104**
- Missing project codes: **0**
- Duplicate `(project_code, report_month)` keys: **0**
- Projects with at least 3 observations: **3,914**
- Projects with at least 6 observations: **3,574**
- Projects with at least 12 observations: **629**
- Projects with at least 18 observations: **0**
- Combined SHA-256: `A3DC4F46C3B382AC2A36DDAF8BE70162F6D1D8857795CF39294F63D2E0310F2B`

The June-July 2025 identifier redesign remains untouched. The diagnostic crosswalk was not integrated, and exact source `project_code` values remain canonical.

## Monthly coverage

| Month | Rows | Warnings | Rejected | Layout |
|---|---:|---:|---:|---|
| 2024-10 | 1,747 | 343 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2024-11 | 1,742 | 342 | 0 | `legacy-all-ongoing-nine-column-progress-only-v1` |
| 2024-12 | 1,724 | 327 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2025-01 | 1,719 | 228 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2025-02 | 1,682 | 210 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2025-03 | 1,677 | 222 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2025-04 | 1,670 | 253 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2025-05 | 1,637 | 242 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2025-06 | 1,595 | 228 | 0 | `legacy-all-ongoing-nine-column-v1` |
| 2025-07 | 791 | 99 | 0 | `table6-eight-column-approval-only-v1` |
| 2025-08 | 800 | 112 | 0 | `table6-eight-column-v1` |
| 2025-09 | 794 | 125 | 0 | `table6-eight-column-v1` |
| 2025-10 | 820 | 130 | 3 | `table6-eight-column-v1` |
| 2025-11 | 823 | 104 | 1 | `table6-eight-column-v1` |
| 2025-12 | 1,392 | 406 | 2 | `table6-eight-column-v1` |
| 2026-01 | 1,702 | 573 | 3 | `table6-eight-column-v1` |
| 2026-02 | 1,948 | 717 | 2 | `table6-eight-column-v1` |
| 2026-03 | 1,941 | 711 | 1 | `table6-eight-column-v1` |
| 2026-04 | 1,981 | 723 | 1 | `table6-eight-column-v1` |
| 2026-05 | 1,987 | 756 | 1 | `table6-eight-column-v1` |
| 2026-06 | 1,847 | 675 | 0 | `table6-eight-column-v1` |
| 2026-07 | 1,775 | 554 | 0 | `table6-eight-column-v1` |

Across the accepted range, all 14 rejected rows have the exact reason `empty_table_row`; none are project records. The three new months have zero rejected rows.

## New-month structural and semantic validation

| Month | Ongoing-table pages | Serial continuity | Missing IDs | Duplicate IDs | Numeric parse | Date parse |
|---|---|---|---:|---:|---:|---:|
| 2024-10 | 51-273 | complete, 1-1747 | 0 | 0 | 100% of source-present values | 100% (4,096/4,096) |
| 2024-11 | 46-277 | complete, 1-1742 | 0 | 0 | 100% of source-present values | 100% (4,076/4,076) |
| 2024-12 | 44-214 | complete, 1-1724 | 0 | 0 | 100% of source-present values | 100% (4,040/4,040) |

October and December match the existing legacy nine-column signature. November is structurally the same legacy project table, but its final column header is printed `Progress (%)`, not `Physical Progress (%)`. The selector therefore uses a separate exact semantic signature, `legacy-all-ongoing-nine-column-progress-only-v1`. It still requires the full positional State, Sector, Sl No, Project Name, approval, commissioning/completion, cost, cumulative expenditure, and progress structure. No fixed table index, table-size rule, or broad header relaxation was introduced.

### New-month warning counts by rule

| Rule | 2024-10 | 2024-11 | 2024-12 |
|---|---:|---:|---:|
| `ZERO_EXPENDITURE_POSITIVE_PROGRESS` | 26 | 24 | 23 |
| `EXPENDITURE_WITH_ZERO_PROGRESS` | 100 | 102 | 94 |
| `FULL_PROGRESS_STILL_ONGOING` | 138 | 137 | 129 |
| `EXTREME_EXPENDITURE_COST_MISMATCH` | 4 | 4 | 5 |
| `REVISED_COST_BELOW_ORIGINAL` | 75 | 75 | 76 |
| `PHYSICAL_PROGRESS_ABOVE_100` | 0 | 0 | 0 |
| `NEGATIVE_EXPENDITURE` | 0 | 0 | 0 |
| `COMPLETION_DATE_BEFORE_START_DATE` | 0 | 0 | 0 |
| `PROGRESS_REPORTED_BEFORE_START` | 0 | 0 | 0 |

Warnings retain source values and do not mutate or reject project rows.

## New longitudinal checks

| Transition | In both | Earlier only | Later only | Longitudinal warnings |
|---|---:|---:|---:|---:|
| 2024-10 to 2024-11 | 1,727 | 20 | 15 | 471 |
| 2024-11 to 2024-12 | 1,709 | 33 | 15 | 610 |
| 2024-12 to 2025-01 | 1,702 | 22 | 17 | 544 |

| Rule | Oct-Nov | Nov-Dec | Dec-Jan | Three-transition total |
|---|---:|---:|---:|---:|
| `AGENCY_CHANGED` | 2 | 4 | 0 | 6 |
| `PROJECT_NAME_CHANGED` | 159 | 257 | 222 | 638 |
| `MINISTRY_CHANGED` | 0 | 0 | 0 | 0 |
| `SECTOR_CHANGED` | 6 | 6 | 0 | 12 |
| `STATE_CHANGED` | 275 | 273 | 277 | 825 |
| `CUMULATIVE_EXPENDITURE_DECREASED` | 4 | 30 | 14 | 48 |
| `PHYSICAL_PROGRESS_DECREASED` | 23 | 39 | 29 | 91 |
| `REVISED_COST_DECREASED` | 2 | 0 | 2 | 4 |
| Positive expenditure to zero | 0 | 1 | 0 | 1 |
| **Total** | **471** | **610** | **544** | **1,625** |

All 21 adjacent transitions remain in `data/validation/longitudinal_summary_2024_10_2026_07.json`. Their aggregate warning count is **5,704**: agency 973, project name 1,699, ministry 0, sector 102, state 1,623, cumulative expenditure decreases 674, physical-progress decreases 510, revised-cost decreases 107, and positive-to-zero expenditure 16.

## Manual PDF verification

Rendered source comparisons covered seven pages per new report: the first table page, its next-page boundary, a multiline project-name page, a second page boundary, the unusual Rs 108,000 crore high-speed-rail record, and the final table page.

- First records: serial 1, `N04000073`, Port Blair terminal, including original/revised costs and revised completion date.
- Missing-value records: serial 2, `N22000584`, whose `N.A.` revised cost and revised completion date remain empty in canonical fields.
- First boundaries: October 7/8 on pages 51/52; November 7/8 on pages 46/47; December 11/12 on pages 44/45.
- Second boundaries: October 894/895 on pages 162/163; November 890/891 on pages 162/163; December 884/885 on pages 129/130.
- Multiline names: October serial 357, November serial 165, and December serial 510.
- Paired values: October serial 895 preserves original cost 1,142.62 and revised cost 1,907.03; source-printed revised dates/costs in other samples also match.
- Unusual numeric: `N22000463`, Mumbai-Ahmedabad High Speed Rail, preserves original cost `108,000.00`; expenditures/progress match each monthly source page.
- Final records: serials 1,747, 1,742, and 1,724 are `N30000049` in October, November, and December respectively.

No ambiguous case was silently corrected. Source grouping labels, including visually surprising state propagation in early legacy pages, remain exactly as reported.

## Regression and hash protection

- Pre-change accepted suite: **65/65 passed**.
- Selector/adapter suite after implementation: **66/66 passed**.
- Final suite with generated Q4 acceptance coverage: **70/70 passed**.
- All 19 previously accepted monthly CSV SHA-256 hashes remained unchanged before and after the rebuild.
- The previously accepted combined hash `A366C2BA57055BE107EF687373477F1704242E00D64ABECFEC59AFD93CC1BB91` changed only through the explicitly authorized addition of the three new months.
- Artifact-tool inspection confirmed all four CSVs have 31 canonical columns, expected row boundaries, intact provenance in the final rows, and no spreadsheet error tokens.

New monthly SHA-256 hashes:

- 2024-10: `D4D7EAA80466A5B3C6678431798AA6641B4E125E47FEBEB9FD0F15BCA44D6A95`
- 2024-11: `01825CE3633833B93DFEE0F68DBF981DB7DB2D8DB850655F7F09F3C73213B345`
- 2024-12: `267CE9D8A7706A4C0D94B210B56C120F287134B488BFAE9442927C90C153FE06`
