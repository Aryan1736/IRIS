# PAIMANA ongoing-project extraction acceptance

Scope: July–September 2025 newly processed reports plus the accepted October 2025–July 2026 baseline. January–June 2025 were not processed.

## Outcome

- Status: **PASS**
- Combined observations: **18,601**
- Unique projects: **2,243**
- Duplicate `(project_code, report_month)` keys: **0**
- Missing project codes: **0**
- Combined CSV SHA-256: `C833EE52AEEE92D9350B584BB385A9E6305266CCD0C26C9964429214EF66FACB`
- Regression suite: **46 tests passed** (`python -m unittest discover -s tests -v`)

## Monthly results

| Month | Table 6 pages | Rows | Missing codes | Rejected | Warnings |
|---|---:|---:|---:|---:|---:|
| 2025-07 | 37–66 | 791 | 0 | 0 | 99 |
| 2025-08 | 37–66 | 800 | 0 | 0 | 112 |
| 2025-09 | 42–71 | 794 | 0 | 0 | 125 |
| 2025-10 | 42–72 | 820 | 0 | 3 | 130 |
| 2025-11 | 42–72 | 823 | 0 | 1 | 104 |
| 2025-12 | 50–107 | 1,392 | 0 | 2 | 406 |
| 2026-01 | 62–133 | 1,702 | 0 | 3 | 573 |
| 2026-02 | 65–167 | 1,948 | 0 | 2 | 717 |
| 2026-03 | 55–156 | 1,941 | 0 | 1 | 711 |
| 2026-04 | 55–162 | 1,981 | 0 | 1 | 723 |
| 2026-05 | 54–162 | 1,987 | 0 | 1 | 756 |
| 2026-06 | 59–159 | 1,847 | 0 | 0 | 675 |
| 2026-07 | 55–152 | 1,775 | 0 | 0 | 554 |
| **Total** |  | **18,601** | **0** | **14** | **5,685** |

The three new reports rejected no rows. All 14 preserved historical rejections are `empty_table_row` records from October 2025 through May 2026; June and July 2026 had none.

July–September each passed serial continuity, project-code completeness and uniqueness, numeric/date parsing, provenance, and existing semantic/cross-field validation. Numeric and date parse success was 100% for each new report.

## Schema and layout

- Extraction method: `pdfplumber-lines-v1`.
- Selection method: `semantic-table6-header-v1`, requiring exactly one matching candidate per Table 6 page.
- `table6-eight-column-v1`: August and September 2025 and the accepted later reports.
- `table6-eight-column-approval-only-v1`: July 2025. This verified source layout omits Start Date and spells the source headers `Orignal/Target DoC` and `Orignal Cost`. The adapter preserves the approval-date cell and leaves start date missing; it does not infer or copy a value.
- No report remained in `SCHEMA_CHANGE` after the format-specific semantic signature was implemented and tested.

## Observation coverage

| Metric | Projects |
|---|---:|
| At least 3 observations | 2,126 |
| At least 6 observations | 1,917 |
| At least 10 observations | 719 |
| Present in all 13 months | 552 |

## New longitudinal transitions

| Transition | In both | Earlier only | Later only | Warnings |
|---|---:|---:|---:|---:|
| Jul→Aug | 765 | 26 | 35 | 151 |
| Aug→Sep | 760 | 40 | 34 | 77 |
| Sep→Oct | 785 | 9 | 35 | 66 |

| Rule | Jul→Aug | Aug→Sep | Sep→Oct |
|---|---:|---:|---:|
| `REVISED_COST_DECREASED` | 16 | 2 | 2 |
| `CUMULATIVE_EXPENDITURE_DECREASED` | 44 | 22 | 22 |
| `PHYSICAL_PROGRESS_DECREASED` | 21 | 18 | 6 |
| Positive expenditure → zero | 0 | 0 | 2 |
| `PROJECT_NAME_CHANGED` | 25 | 3 | 7 |
| `AGENCY_CHANGED` | 37 | 31 | 25 |
| `MINISTRY_CHANGED` | 0 | 0 | 0 |
| `SECTOR_CHANGED` | 5 | 1 | 2 |
| `STATE_CHANGED` | 3 | 0 | 0 |

All previously validated transitions remain in the rebuilt summary. The complete 12-transition range contains **2,014** longitudinal warnings.

## Manual source checks

Representative visual comparisons covered first and last projects, the first page boundary, multiline names, revised cost, revised completion date, missing values, and unusual numeric values. Examples included Kadapa Airport (`612786`), Jamrani Dam (`613787`), BharatNet (`706775`, cost `61109 (188000)`), and Western Dedicated Freight Corridor (`705237`, cumulative expenditure `124623`). Extracted source values and page provenance matched the visible PDFs.

## Hash verification

All ten previously accepted monthly CSV hashes remained unchanged:

| File | SHA-256 |
|---|---|
| `projects_2025_10.csv` | `241F26EA0FA3465DD83AA2E3BDEA3548BB40EE8457ED3BFADD5B396B40A1F01E` |
| `projects_2025_11.csv` | `E07EBD3630C34F6795BCCA0FD269DCAF11E944EBE7F14410A790B9FE34111016` |
| `projects_2025_12.csv` | `1195FBB10AFB31E68A3B13B7FDDE953FEA4771301ABBF76D361233F85A1A36FB` |
| `projects_2026_01.csv` | `B48F69745B4BD97253761825F5BF143B0FAD7C51AF326C1A1F73D394F05DA4D6` |
| `projects_2026_02.csv` | `E6D2EA35AB40EAF8B2DCB091760EFCA0F3847EACC9C904D8CEEB366EA6511E3B` |
| `projects_2026_03.csv` | `8A99484E353FBF50437B92C6842DDE8FE0BBC9112A5331B2637600873DF4C512` |
| `projects_2026_04.csv` | `EDD50D32FC179611D217BEFADE8B5903AE17ABFE014F164199F37C2DDF02AB3A` |
| `projects_2026_05.csv` | `85C04A73B7978935B47244351E52382C6A96F7DE41CB5863557085BD4787C802` |
| `projects_2026_06.csv` | `829E7B8A7A6C9611AB7C3A228CCA97C25A0FE7E4AF043FAFF27C560D77ACE289` |
| `projects_2026_07.csv` | `05BF807B4C4E8C0A93D5952EC963141F4AC246A22C9BCD5BF0A70C68544DDC17` |

New monthly hashes:

- July 2025: `AFEDC251C8F55CB27034938FA9681E823BC00F8ECD062E50E44E9B802A9A1A58`
- August 2025: `FB9296DCD192FB591B726717BF83DCF78269DF86E797FC85B5FFD6296F9FBD61`
- September 2025: `6045C5274077A7CBE7EC948F3C966BFF12BA089C3924434FB4E3CB487F8AA5D3`

The three new cleaned CSVs and the combined CSV were also imported with the spreadsheet validation runtime. Canonical headers, expected row endpoints, and first/last project identifiers were confirmed.
