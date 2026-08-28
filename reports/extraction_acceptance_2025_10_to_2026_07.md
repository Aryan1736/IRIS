# PAIMANA ongoing-project extraction acceptance

Scope: October–December 2025 newly processed reports plus the accepted January–July 2026 baseline. July–September 2025 were not processed.

## Outcome

- Status: **PASS**
- Combined observations: **16,216**
- Unique projects: **2,186**
- Duplicate `(project_code, report_month)` keys: **0**
- Missing project codes: **0**
- Combined CSV SHA-256: `040B31461623BCBB8FED1F676600587B08CE161320E3B2245EB16C5AA2AECCA4`
- Regression suite: **43 tests passed** (`python -m unittest discover -s tests -v`)

## Monthly acceptance results

| Report month | Table 6 pages | Project rows | Missing codes | Duplicate codes | Rejected rows | Warning count |
|---|---:|---:|---:|---:|---:|---:|
| 2025-10 | 42–72 | 820 | 0 | 0 | 3 | 130 |
| 2025-11 | 42–72 | 823 | 0 | 0 | 1 | 104 |
| 2025-12 | 50–107 | 1,392 | 0 | 0 | 2 | 406 |
| 2026-01 | 62–133 | 1,702 | 0 | 0 | 3 | 573 |
| 2026-02 | 65–167 | 1,948 | 0 | 0 | 2 | 717 |
| 2026-03 | 55–156 | 1,941 | 0 | 0 | 1 | 711 |
| 2026-04 | 55–162 | 1,981 | 0 | 0 | 1 | 723 |
| 2026-05 | 54–162 | 1,987 | 0 | 0 | 1 | 756 |
| 2026-06 | 59–159 | 1,847 | 0 | 0 | 0 | 675 |
| 2026-07 | 55–152 | 1,775 | 0 | 0 | 0 | 554 |
| **Total** |  | **16,216** | **0** | **0** | **14** | **5,349** |

All 14 rejected records were `empty_table_row`: October 2025 pages 48, 49, and 50; November page 42; December pages 78 and 84; January 2026 had 3; February 2; March 1; April 1; May 1. June and July had none.

Serial continuity, identifier uniqueness, date parsing, cost parsing, expenditure parsing, physical-progress parsing, and existing cross-field rules passed for each new report. All four numeric parse rates and the date parse rate were 100% for October, November, and December 2025.

## Schema and layout

- Extraction method: `pdfplumber-lines-v1` for all ten months.
- New-report semantic selector: `semantic-table6-header-v1`.
- Canonical Table 6 layout encountered: the accepted 8-column project table. No new adapter was required and no report produced `SCHEMA_CHANGE`.
- Canonical cleaned schema: the existing 31-field ongoing-project CSV header. The manifests do not encode a separate schema-version identifier.
- April–July are preserved baseline outputs whose older manifests predate the selector-method field; the existing regression suite confirms a normal April Table 6 page remains compatible with the semantic selector.

## Observation coverage

| Metric | Projects |
|---|---:|
| At least 3 observations | 2,069 |
| At least 6 observations | 1,887 |
| At least 10 observations | 611 |
| Present in all 10 months | 611 |

## New longitudinal transitions

| Transition | In both | Earlier only | Later only | Total warnings |
|---|---:|---:|---:|---:|
| Oct→Nov | 800 | 20 | 23 | 58 |
| Nov→Dec | 788 | 35 | 604 | 50 |
| Dec→Jan | 1,388 | 4 | 314 | 53 |

| Rule | Oct→Nov | Nov→Dec | Dec→Jan |
|---|---:|---:|---:|
| `REVISED_COST_DECREASED` | 4 | 7 | 1 |
| `CUMULATIVE_EXPENDITURE_DECREASED` | 37 | 17 | 36 |
| `PHYSICAL_PROGRESS_DECREASED` | 4 | 5 | 7 |
| Positive expenditure → zero | 0 | 0 | 0 |
| `PROJECT_NAME_CHANGED` | 2 | 2 | 3 |
| `AGENCY_CHANGED` | 10 | 15 | 5 |
| `MINISTRY_CHANGED` | 0 | 0 | 0 |
| `SECTOR_CHANGED` | 0 | 1 | 0 |
| `STATE_CHANGED` | 1 | 3 | 1 |

Existing later-transition diagnostics were preserved in the rebuilt summary: Jan→Feb 76 warnings, Feb→Mar 46, Mar→Apr 66, Apr→May 88, May→Jun 654, and Jun→Jul 629. Across all nine transitions there are 1,720 longitudinal warnings.

## January–July 2026 hash verification

| Month | SHA-256 | Result |
|---|---|---|
| 2026-01 | `B48F69745B4BD97253761825F5BF143B0FAD7C51AF326C1A1F73D394F05DA4D6` | unchanged |
| 2026-02 | `E6D2EA35AB40EAF8B2DCB091760EFCA0F3847EACC9C904D8CEEB366EA6511E3B` | unchanged |
| 2026-03 | `8A99484E353FBF50437B92C6842DDE8FE0BBC9112A5331B2637600873DF4C512` | unchanged |
| 2026-04 | `EDD50D32FC179611D217BEFADE8B5903AE17ABFE014F164199F37C2DDF02AB3A` | unchanged |
| 2026-05 | `85C04A73B7978935B47244351E52382C6A96F7DE41CB5863557085BD4787C802` | unchanged |
| 2026-06 | `829E7B8A7A6C9611AB7C3A228CCA97C25A0FE7E4AF043FAFF27C560D77ACE289` | unchanged |
| 2026-07 | `05BF807B4C4E8C0A93D5952EC963141F4AC246A22C9BCD5BF0A70C68544DDC17` | unchanged |

The October–December cleaned CSVs and the 10-month combined CSV were also imported and inspected with the spreadsheet validation runtime; canonical headers and non-empty first/last project codes were confirmed.
