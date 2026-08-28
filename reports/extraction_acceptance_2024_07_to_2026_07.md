# Extraction Acceptance: 2024-07 to 2026-07 (Corrected August Reconstruction)

This report documents the extraction acceptance of the **July 2024, August 2024, and September 2024** reports into the canonical PAIMANA dataset, which now covers 25 consecutive months (July 2024 through July 2026 inclusive).

## August 2024 Reconstruction Investigation and Resolution

An earlier draft extraction of August 2024 had two structural defects:
1. **Misalignment of Margin Text:** On 8-column and 7-column continuation pages, arbitrary table cell index slicing and unaligned margin crops misassociated State and Sector group headings with unrelated rows (e.g. projecting urban development and railway sectors onto coal projects).
2. **False North-East Banner Exclusion:** A full-string regex match for `"north east"` caused Pages 164 and 165 to be dropped because project names on those pages contained `"NORTH EAST GAS GRID"` and `"NORTH EASTERN REGION"`.

### Corrected Spatial Reconstruction Architecture
- **Unified Spatial Grid:** The August PDF layout maintains exact physical column coordinates across all 202 Table 7 pages (Pages 39 to 240): State column at `x ∈ [30.0, 81.5]`, Sector column at `x ∈ [81.5, 132.0]`, and project fields from `x ≥ 131.8`.
- **Row-Relative Group Association:** Word extraction in the State and Sector margin bands is bound to the exact unmerged vertical boundaries of each project row (`Sl No` and `Project Name`).
- **Fragment Merging:** Non-project fragment rows merge group label fragments (e.g. `HEALTH AND` + `FAMILY WELFARE` → `HEALTH AND FAMILY WELFARE`) across visual line breaks without fabricating or guessing.
- **Fail-Closed Isolation:** If a continuation page lacks established context, extraction fails closed. No adjacent-month data is ever used to backfill or populate August.

## Verification Checklist

1. **Hashes Unchanged:** All 24 non-August monthly CSV hashes (July 2024, September 2024, and October 2024 through July 2026) are byte-for-byte identical to their accepted baselines.
2. **Monthly Hashes:**
   - `projects_2024_07.csv`: `1F2A215E6FBB407064A0D139537916C337DF673EE84132934DC536EDADC1A3AB` (Accepted)
   - `projects_2024_08.csv`: `2D49E70600AF7555133FC9BE7074854CC498169BC9B313C9ACC5D27B61B05DB8` (Accepted; supersedes previous `E87414B0...`)
   - `projects_2024_09.csv`: `D1566B44491736C89961C36C514D1EA34799785DD00540DFF30FBB3B62704FDA` (Accepted)
3. **Combined SHA-256 Check:** `projects_monthly.csv` was rebuilt across all 25 months:
   - **Combined Hash:** `16147C02F8C67F35CF814E4ACDE03F0B777B205D7B50B589CEB5BFA67C58BB99` (supersedes previous `847E5071...`)
   - **Total Records:** **39,162** rows (exactly 1,783 rows in August 2024).
   - **Unique Projects:** **4,217** unique source project codes.
   - **Duplicate Keys:** **0** duplicate `(project_code, report_month)` keys.
   - **Missing Project IDs:** **0**.
4. **Serial Continuity:** August 2024 serial numbers span continuously from `1` to `1783` with zero gaps and zero duplicates across all 202 pages.
5. **Regression Integrity:** The full test suite passes (**76/76 passing tests**).

## Longitudinal Transition Metrics

### July 2024 → August 2024
- **Projects in both:** 1,765
- **Earlier only (July only):** 28
- **Later only (August only):** 18
- **Warnings Breakdown (789 total, down from 2,481):**
  - `sector_changed`: **36** (Exact source: 36, Collapsed whitespace diffs: **0**)
  - `state_changed`: **429** (Exact source: 429, Collapsed whitespace diffs: **58**, where all 58 are the literal printed source difference `MULTI` on August Page 163 vs `MULTI STATE` in July)
  - `project_name_changed`: 286
  - `physical_progress_decreased`: 28
  - `cumulative_expenditure_decreased`: 9
  - `agency_changed`: 1

### August 2024 → September 2024
- **Projects in both:** 1,770
- **Earlier only (August only):** 13
- **Later only (September only):** 22
- **Warnings Breakdown (619 total, down from 2,370):**
  - `sector_changed`: **56** (Exact source: 56, Collapsed whitespace diffs: **0**)
  - `state_changed`: **374** (Exact source: 374, Collapsed whitespace diffs: **58**, representing `MULTI` on August Page 163 vs `MULTI STATE` in September)
  - `project_name_changed`: 129
  - `physical_progress_decreased`: 45
  - `cumulative_expenditure_decreased`: 11
  - `revised_cost_decreased`: 2
  - `positive_to_zero_expenditure`: 1
  - `agency_changed`: 1

### September 2024 → October 2024
- **Projects in both:** 1,720
- **Earlier only (September only):** 72
- **Later only (October only):** 27
- **Warnings Breakdown (467 total):**
  - `project_name_changed`: 301
  - `sector_changed`: 56
  - `state_changed`: 53
  - `physical_progress_decreased`: 47
  - `cumulative_expenditure_decreased`: 9
  - `revised_cost_decreased`: 1
