# PAIMANA extraction handoff

## Current exact state

The accepted ongoing-project extraction covers **2025-04 through 2026-07**, inclusive: 16 monthly reports.

- Project-month observations: **23,503**
- Unique source-reported project identifiers: **3,933**
- Missing project codes: **0**
- Duplicate `(project_code, report_month)` keys: **0**
- Projects with at least 3 observations: **3,701**
- Projects with at least 6 observations: **1,917**
- Projects with at least 10 observations: **719**
- Projects with at least 12 observations: **629**
- Projects with all 16 months: **0**, because the identifier system changes between June and July 2025
- Combined file: `data/processed/projects_monthly.csv`
- Accepted combined SHA-256: `73E47AA487E70A28FE3C984E532A6E23D21897B60C176BEEA80FB1C06F73E191`
- Current regression suite: **57/57 passing**

Monthly row counts are:

| Month | Rows | Layout |
|---|---:|---|
| 2025-04 | 1,670 | `legacy-all-ongoing-nine-column-v1` |
| 2025-05 | 1,637 | `legacy-all-ongoing-nine-column-v1` |
| 2025-06 | 1,595 | `legacy-all-ongoing-nine-column-v1` |
| 2025-07 | 791 | `table6-eight-column-approval-only-v1` |
| 2025-08 | 800 | `table6-eight-column-v1` |
| 2025-09 | 794 | `table6-eight-column-v1` |
| 2025-10 | 820 | `table6-eight-column-v1` |
| 2025-11 | 823 | `table6-eight-column-v1` |
| 2025-12 | 1,392 | `table6-eight-column-v1` |
| 2026-01 | 1,702 | `table6-eight-column-v1` |
| 2026-02 | 1,948 | `table6-eight-column-v1` |
| 2026-03 | 1,941 | `table6-eight-column-v1` |
| 2026-04 | 1,981 | `table6-eight-column-v1` |
| 2026-05 | 1,987 | `table6-eight-column-v1` |
| 2026-06 | 1,847 | `table6-eight-column-v1` |
| 2026-07 | 1,775 | `table6-eight-column-v1` |

The authoritative machine-readable current summaries are `data/validation/combined_summary.json` and `data/validation/longitudinal_summary_2025_04_2026_07.json`.

## Layouts and adapters

Three layouts are accepted:

1. `legacy-all-ongoing-nine-column-v1` - April-June 2025. These reports call the project list Table 7 and provide State and Sector separately. They do not provide Ministry or Start Date. Project cells use legacy `N########` or nine-digit-style identifiers. Original/revised/anticipated triplets are parsed without promoting anticipated values to revised fields.
2. `table6-eight-column-approval-only-v1` - July 2025. This report legitimately omits Start Date; `start_date` must remain missing.
3. `table6-eight-column-v1` - August 2025-July 2026. This is the standard accepted eight-column Table 6 layout.

All layouts use `pdfplumber-lines-v1` extraction and the fail-closed `semantic-table6-header-v1` selector. Multiple detected tables on a page are allowed, but exactly one must match the verified positional project-table signature. The enclosing two-column `pdfplumber` detections seen in supported reports are ignored only after a logged semantic rejection; no fixed table index or size heuristic is used.

## June-July 2025 identifier redesign

June 2025 uses 1,595 legacy `N########`/nine-digit identifiers. July 2025 uses 791 six-digit project codes. Exact code overlap is zero, and neither report prints both identifier styles or an explicit OCMS/PMGID bridge.

The completed crosswalk investigation found:

- Explicit source mappings: **0**
- High-confidence analytical proposals: **137**
- Ambiguous June projects: **346** across 408 candidate edges
- Unmatched June projects: **1,112**
- Ambiguous July projects: **347**
- Unmatched July projects: **307**
- Possible one-to-many/split-shaped candidate structures: **41**
- Possible many-to-one/merger-shaped candidate structures: **44**

These relationships are **diagnostic only and are not integrated** into monthly CSVs or `projects_monthly.csv`. No stable ID has been assigned. Do not rewrite source `project_code`, automatically fuzzy-match, or use the proposals for ordinary exact-code longitudinal validation without explicit user authorization.

Detailed evidence and manual comparisons are in `reports/id_crosswalk_june_july_2025.md`. Candidate data are in `data/validation/id_crosswalk_june_july_2025.csv`, `data/validation/id_crosswalk_ambiguous_june_july_2025.csv`, and `data/validation/id_crosswalk_summary_june_july_2025.json`.

## Last completed task

The last completed task was the conservative June-July 2025 identifier-crosswalk investigation. It resumed an interrupted diagnostic run, regenerated the candidate outputs after a raw-row filter fix, classified every June project, documented manual PDF verification, added six crosswalk regression tests, and confirmed that canonical dataset hashes were unchanged. The suite then passed 57/57 tests.

## Next planned task

Process **January, February, and March 2025 only**, but only after those PDFs are supplied and the user explicitly authorizes processing. Those PDFs are not currently present under `data/raw/2025/`.

Do not process any new report merely because it appears in `data/raw/`. First confirm the exact user scope, snapshot hashes, and run the existing suite. January-March 2025 may introduce another historical layout; preserve fail-closed behavior and add a narrow adapter only if source inspection justifies it.

## Read these files first

Recommended order for a new agent with no chat history:

1. `AGENTS.md` - durable repository rules and safe commands.
2. `README.md` - short pipeline overview.
3. `reports/extraction_acceptance_2025_04_to_2026_07.md` - accepted 16-month extraction, row counts, warnings, layout, manual checks, and hash.
4. `reports/id_crosswalk_june_july_2025.md` - identifier redesign investigation and limitations.
5. `reports/data_dictionary.md` and `schemas/project_month.schema.json` - canonical fields. Note that the JSON schema's six-digit `project_code` regex predates the accepted legacy IDs; production validation in `src/validation/core.py` accepts all source formats.
6. `reports/validation_rules.md` - cross-field warning meanings and QC-only metrics.
7. `reports/manual_validation.md` and `tests/fixtures/manual_verified_records.csv` - source-checked records.
8. `reports/extraction_comparison.md` - why native `pdfplumber` extraction was selected.
9. `reports/longitudinal_warning_diagnostic_2026_01_07.md` and `data/validation/diagnostics/longitudinal_warning_diagnostic_2026_01_07.json` - diagnosis of later warning spikes.
10. `reports/zero_expenditure_positive_progress_diagnostic_2026_06_07.md` - the focused zero-expenditure diagnostic.
11. `src/extraction/pipeline.py`, `src/cleaning/parsers.py`, `src/validation/core.py`, and `src/build_dataset/monthly.py` - production implementation.
12. The relevant `data/validation/manifest_YYYY_MM.json`, `quality_YYYY_MM.json`, `warnings_YYYY_MM.csv`, `rejected_YYYY_MM.csv`, `duplicates_YYYY_MM.csv`, and `qc_metrics_YYYY_MM.csv` before changing any accepted month.

Earlier acceptance reports remain useful for incremental history:

- `reports/extraction_acceptance_2025_07_to_2026_07.md`
- `reports/extraction_acceptance_2025_10_to_2026_07.md`
- `reports/longitudinal_warning_diagnostic_2026_01_07.md`

Do not copy their large tables into new reports; link to them and record only new deltas.

## Known source and implementation quirks

- April-June 2025 are legacy Table 7 reports, not the later Table 6 layout.
- Legacy reports omit Start Date and Ministry. Missing values are intentional and must not be inferred.
- Legacy cells can contain original, parenthesized revised, and braced anticipated values. Anticipated is not revised.
- July 2025 is an approval-only layout and legitimately lacks Start Date.
- June-July 2025 has a source identifier redesign, so ordinary exact-code overlap is zero.
- Some pages produce an extra enclosing two-column table with implausible geometry. It is logged and ignored only because it fails the semantic header signature.
- Fourteen accepted non-project rows from October 2025-May 2026 are rejected as `empty_table_row`; these counts are stable. April-June 2025 have zero rejected rows.
- Project names, agency labels, sector labels, state strings, revised costs, expenditure, progress, and dates can change between reports. Preserve them and emit warnings; do not normalize the source layer.
- May-June and June-July 2026 have large longitudinal warning counts, particularly agency/name label changes. These were diagnosed rather than corrected; read the longitudinal diagnostic report.
- Positive expenditure can become zero and physical progress can decrease in later reports. These are retained source states, not imputation/correction requests.
- A project at 100% progress may still appear in the ongoing table; the validator flags but retains it.
- `qc_metrics` contains derived financial progress and physical-financial gap only for validation. Those fields are deliberately absent from canonical data.
- `src/build_dataset/monthly.py` has an old default month list of January-July 2026. Always pass the complete explicit ordered month list.
- The extraction CLI combines only PDFs processed in that invocation. Running it against a single PDF would replace `projects_monthly.csv` with that invocation's rows; use `process_pdf` directly for single-month acceptance work.
- The repository has an unrelated untracked archive `IRIS_data_2025_2026.7z`. Preserve it and do not stage, modify, or delete it without instruction.

## First health checks

From the repository root:

```powershell
git status --short
python -m unittest discover -v
Get-FileHash data/processed/projects_monthly.csv -Algorithm SHA256
Get-Content -Raw data/validation/combined_summary.json
Get-Content -Raw data/validation/id_crosswalk_summary_june_july_2025.json
```

Expected test result: **57 tests, OK**.

Expected combined SHA-256:

```text
73E47AA487E70A28FE3C984E532A6E23D21897B60C176BEEA80FB1C06F73E191
```

Before any new extraction, also capture all accepted monthly CSV hashes:

```powershell
Get-FileHash data/cleaned/projects_*.csv -Algorithm SHA256 | Sort-Object Path
```

To rebuild only after every new month has passed individual acceptance, use the complete explicit month list, extending it at the beginning as authorized:

```powershell
python -m src.build_dataset.monthly --months 2025-04 2025-05 2025-06 2025-07 2025-08 2025-09 2025-10 2025-11 2025-12 2026-01 2026-02 2026-03 2026-04 2026-05 2026-06 2026-07
```

Do not run this rebuild merely as a health check because it writes generated data. Tests and hashes are the non-mutating health checks.

## Safety boundary

The current phase prohibits ML, normalization, feature engineering, target creation, imputation, dashboard work, and canonical integration of the diagnostic identifier crosswalk. Preserve exact source values and provenance. Stop on unsupported schemas. Do not process January-March 2025 until the files exist and the user supplies the next extraction instruction.
