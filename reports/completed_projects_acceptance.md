# Table 3: Completed Projects Extraction Acceptance Report

## 1. Executive Summary

This report documents the standalone extraction pipeline and validated output dataset for **Table 3: Completed Projects** across all 16 Flash Report PDFs in `data/raw/` (covering April 2025 through July 2026).

The extraction strictly enforces source-faithfulness, positional header matching, fail-closed candidate selection, and exact source-issued project code preservation. Existing monthly extraction pipelines, schemas, validation outputs, and canonical monthly datasets remain completely untouched and byte-identical.

- **Output dataset**: `data/processed/projects_completed.csv`
- **Output SHA-256**: `CDE695898623FAEE380B834DCE764BE1A79F7681760B99A18F2C911C4C045456`
- **Total completed project records**: **375**
- **Unique completed projects**: **375** (zero duplicates across reports)
- **Missing project codes**: **0**
- **Duplicate `(project_code, report_month)` keys**: **0**
- **Serial continuity**: **100% continuous (1..N)** within each report month with **0 gaps** and **0 duplicates**
- **Parse rate for present values**: **100%** across dates and numerics
- **Dedicated test suite**: **27/27 passing** (`tests/test_completed_projects.py`, `tests/test_parsers.py`, `tests/test_validation.py`, `tests/test_manual_fixtures.py`)
- **Combined monthly dataset integrity**: `data/processed/projects_monthly.csv` and all 16 monthly CSVs are **byte-for-byte identical** to pre-implementation baselines.

---

## 2. PDFs Processed & Table 3 Presence

| Report Month | PDF Filename | Table 3 Completed Projects Present? | Table 3 Page Range | Layout Type | Project Rows Extracted |
|---|---|---|---|---|---:|
| **2025-04** | `2025/FR_April_2025.pdf` | **Yes** | Pages 11–14 | `table3-completed-legacy-six-column-v1` | 34 |
| **2025-05** | `2025/FR_May2025.pdf` | **Yes** | Pages 11–15 | `table3-completed-legacy-six-column-v1` | 40 |
| **2025-06** | `2025/FR_JUNE_2025.pdf` | **Yes** | Pages 11–15 | `table3-completed-legacy-six-column-v1` | 42 |
| **2025-07** | `2025/FlashReport_July_2025.pdf` | **No** (Table 3 is *North-East Ongoing*) | N/A | Absent | 0 |
| **2025-08** | `2025/FlashReport_August_2025.pdf` | **No** (Table 3 is *North-East Ongoing*) | N/A | Absent | 0 |
| **2025-09** | `2025/FlashReport_September_2025.pdf` | **Yes** | Pages 32–33 (p. 33 data) | `table3-completed-seven-column-v1` | 6 |
| **2025-10** | `2025/FlashReport_October_2025.pdf` | **Yes** | Pages 32–33 (p. 33 data) | `table3-completed-seven-column-v1` | 6 |
| **2025-11** | `2025/FlashReport_November_2025.pdf` | **Yes** | Pages 32–33 (p. 33 data) | `table3-completed-seven-column-v1` | 13 |
| **2025-12** | `2025/FlashReport_December_2025.pdf` | **Yes** | Pages 34–36 (pp. 35–36 data) | `table3-completed-seven-column-v1` | 17 |
| **2026-01** | `FlashReport_January_2026.pdf` | **Yes** | Pages 35–36 (p. 36 data) | `table3-completed-seven-column-v1` | 3 |
| **2026-02** | `FlashReport_February_2026.pdf` | **Yes** | Pages 35–36 (p. 36 data) | `table3-completed-seven-column-v1` | 9 |
| **2026-03** | `FlashReport_March_2026.pdf` | **Yes** | Pages 35–37 (pp. 36–37 data) | `table3-completed-seven-column-v1` | 25 |
| **2026-04** | `FlashReport_April2026.pdf` | **Yes** | Pages 34–35 (p. 35 data) | `table3-completed-seven-column-v1` | 9 |
| **2026-05** | `FlashReport_May2026.pdf` | **Yes** | Pages 34–35 (p. 35 data) | `table3-completed-seven-column-v1` | 16 |
| **2026-06** | `FlashReport_June_2026.pdf` | **Yes** | Pages 35–42 (pp. 36–42 data) | `table3-completed-seven-column-v1` | 130 |
| **2026-07** | `FlashReport_July_2026.pdf` | **Yes** | Pages 35–37 (pp. 36–37 data) | `table3-completed-seven-column-v1` | 25 |
| **TOTAL** | | | | | **375** |

### July & August 2025 Absence Note
In July and August 2025, the reports publish no Completed Projects table. Table 3 in those months is titled *"Table 3: Ongoing Projects of North Eastern Region"*. The semantic selector explicitly checks for `"ongoing projects"` and `"north eastern region"` and rejects those pages, recording `table3_present = False` and extracting 0 records.

---

## 3. Layout Specifications

### Layout 1: `table3-completed-legacy-six-column-v1` (April–June 2025)
* **Header text**: `Table:-3. Project List: Completed during <Month> <Year>`
* **Columns (6)**:
  1. `Sector`
  2. `Sl. No.`
  3. `Project Name / (Agency Name) / (Project Code) / (State Name)` (Composite cell)
  4. `Original Cost in Rs. Crore`
  5. `Date of Commissioning Original (MM/YYYY)`
  6. `Cumulative Expenditure in Rs. Crore`
* **Sector context**: Captured from Sector band rows or Col 0.
* **Fields absent from source**: `ministry`, `approval_date`, `start_date`, `actual_completion_date`, `revised_completion_date`, `revised_cost`. These remain `None` / empty to preserve source fidelity.

### Layout 2: `table3-completed-seven-column-v1` (September 2025–July 2026)
* **Header text**: `Completed Projects During Month <MONTH> <YEAR>` (Divider: `Table 3: Completed Projects`)
* **Columns (7)**:
  1. `Sl.No`
  2. `Project Name / (Agency) / Project Code` (Composite cell)
  3. `State`
  4. `Date of Approval / (Start Date) MM/YYYY`
  5. `Actual Date of Completion / (Orignal/Target DoC) / (Revised DoC) MM/YYYY` (June 2026 variant omits actual DoC header)
  6. `Orignal Cost / Revised Cost in Rs. Crore`
  7. `Cumulative Expenditure in Rs. Crore`
* **Ministry & Sector context**: Extracted from section band rows (e.g. `['', 'Ministry of ...', ...]`, `['', 'Sector Name', ...]`).

---

## 4. Final CSV Schema (`projects_completed.csv`)

The output schema follows the repository's standard ordering and convention:

1. **Identity & Source Labels**:
   - `project_code`: Source-issued project identifier (`N########` or 9-digit in legacy; 6 digits in 7-column). Preserved exactly as printed.
   - `project_name`: Extracted from composite cell.
   - `agency`: Extracted from composite cell.
   - `ministry`: Extracted from band rows (seven-column layout) or empty (legacy).
   - `sector`: Extracted from band rows or Sector column.
   - `state`: Extracted from composite cell (legacy) or separate State column (seven-column).
2. **Parsed Dates** (`YYYY-MM`):
   - `approval_date`: Approval date where printed.
   - `start_date`: Start date where printed.
   - `original_completion_date`: Original or target completion date.
   - `revised_completion_date`: Revised completion date where printed.
   - `actual_completion_date`: Actual completion date where printed.
3. **Parsed Numerics** (Rs. crore, float):
   - `original_cost`: Parsed original cost.
   - `revised_cost`: Parsed revised cost where printed.
   - `cumulative_expenditure`: Parsed cumulative expenditure.
4. **Time**:
   - `report_month`: Report month in `YYYY-MM` format.
5. **Source Raw Representations**:
   - `approval_date_raw`
   - `start_date_raw`
   - `original_completion_date_raw`
   - `revised_completion_date_raw`
   - `actual_completion_date_raw`
   - `original_cost_raw`
   - `revised_cost_raw`
   - `cumulative_expenditure_raw`
6. **Provenance**:
   - `source_file`: PDF basename.
   - `source_page`: Physical 1-indexed PDF page.
   - `source_row_number`: 1-indexed row number in the detected table.
   - `source_serial_number`: Source-printed integer serial number (`1..N`).
   - `extraction_method`: `"pdfplumber-table3-v1"`.

---

## 5. Non-Project Row Exclusions

Across the 14 reports containing Table 3, all non-project rows were identified and excluded deterministically:
- **Repeated headers**: On multi-page continuation pages (e.g. June 2026, Dec 2025, Mar 2026, July 2026), repeated header rows are detected and excluded.
- **Section band rows**: Ministry and Sector band rows are consumed for hierarchical context and excluded from project rows.
- **Group total rows**: Summary rows such as `['', 'Total (1)', '', '', '', '287.2', '310']` are recognized and excluded.
- **Empty / whitespace rows**: Blank padding rows are cleanly dropped.
- **Enclosing page-frame tables**: Enclosing 1-column tables (e.g. 3x1 layout frames) fail the semantic project table signature and are excluded.

---

## 6. Dataset Integrity & Hash Verification

### Baseline & Re-Verification of Monthly Dataset Files

Before and after the Completed Projects implementation, SHA-256 hashes of all existing files were captured. All files are **byte-for-byte identical**:

| File | Status | SHA-256 Hash |
|---|---|---|
| `data/processed/projects_monthly.csv` | **MATCH** | `73E47AA487E70A28FE3C984E532A6E23D21897B60C176BEEA80FB1C06F73E191` |
| `data/cleaned/projects_2025_04.csv` | **MATCH** | `9870B39CB353B4DDF870566908E21BC000322FED65B2DB1E94E50C3A78A000FD` |
| `data/cleaned/projects_2025_05.csv` | **MATCH** | `ED45BC78FE9B12E00A9EC9D914D38A347F7A6CBB29F0264F85F1ADE14982B843` |
| `data/cleaned/projects_2025_06.csv` | **MATCH** | `987459F23C0E479B80F7E647F4062BE1B73FA3BA9451BFECFB9DFA29A4B4334F` |
| `data/cleaned/projects_2025_07.csv` | **MATCH** | `AFEDC251C8F55CB27034938FA9681E823BC00F8ECD062E50E44E9B802A9A1A58` |
| `data/cleaned/projects_2025_08.csv` | **MATCH** | `FB9296DCD192FB591B726717BF83DCF78269DF86E797FC85B5FFD6296F9FBD61` |
| `data/cleaned/projects_2025_09.csv` | **MATCH** | `6045C5274077A7CBE7EC948F3C966BFF12BA089C3924434FB4E3CB487F8AA5D3` |
| `data/cleaned/projects_2025_10.csv` | **MATCH** | `241F26EA0FA3465DD83AA2E3BDEA3548BB40EE8457ED3BFADD5B396B40A1F01E` |
| `data/cleaned/projects_2025_11.csv` | **MATCH** | `E07EBD3630C34F6795BCCA0FD269DCAF11E944EBE7F14410A790B9FE34111016` |
| `data/cleaned/projects_2025_12.csv` | **MATCH** | `1195FBB10AFB31E68A3B13B7FDDE953FEA4771301ABBF76D361233F85A1A36FB` |
| `data/cleaned/projects_2026_01.csv` | **MATCH** | `B48F69745B4BD97253761825F5BF143B0FAD7C51AF326C1A1F73D394F05DA4D6` |
| `data/cleaned/projects_2026_02.csv` | **MATCH** | `E6D2EA35AB40EAF8B2DCB091760EFCA0F3847EACC9C904D8CEEB366EA6511E3B` |
| `data/cleaned/projects_2026_03.csv` | **MATCH** | `8A99484E353FBF50437B92C6842DDE8FE0BBC9112A5331B2637600873DF4C512` |
| `data/cleaned/projects_2026_04.csv` | **MATCH** | `EDD50D32FC179611D217BEFADE8B5903AE17ABFE014F164199F37C2DDF02AB3A` |
| `data/cleaned/projects_2026_05.csv` | **MATCH** | `85C04A73B7978935B47244351E52382C6A96F7DE41CB5863557085BD4787C802` |
| `data/cleaned/projects_2026_06.csv` | **MATCH** | `829E7B8A7A6C9611AB7C3A228CCA97C25A0FE7E4AF043FAFF27C560D77ACE289` |
| `data/cleaned/projects_2026_07.csv` | **MATCH** | `05BF807B4C4E8C0A93D5952EC963141F4AC246A22C9BCD5BF0A70C68544DDC17` |

---

## 7. Files Changed / Created

### New Self-Contained Files Created:
1. `src/extraction/completed_projects.py`: Dedicated Table 3 extraction pipeline, semantic table selector, layout adapters, and row parsers.
2. `src/validation/completed_projects.py`: Dedicated Table 3 validation module for structural integrity, serial continuity, parse rates, and provenance completeness.
3. `tests/test_completed_projects.py`: Dedicated regression and unit test suite covering semantic detection, header matching, composite cell parsing, date/cost parsing, July/August 2025 absence, and dataset integrity.
4. `reports/completed_projects_acceptance.md`: This acceptance report.
5. `data/processed/projects_completed.csv`: The target canonical completed projects dataset (ignored by git per repository rules).

### Shared Files Modified:
- **Zero**. No existing shared files were modified.

---

## 8. Summary of Validation Checks

- `total_records`: **375**
- `unique_projects`: **375**
- `missing_project_codes`: **0**
- `duplicate_keys`: **0**
- `serial_continuity_all_months`: **True** (1..N in every month)
- `warnings_count`: **0**
- `test_results`: **27/27 OK** (Ran 27 tests in 22.988s)
