# PAIMANA historical project-month extraction

This repository converts machine-readable PAIMANA monthly Flash Report PDFs into auditable project-level monthly data. It does not create modelling features, targets, or models.

## Run

Install `requirements.txt`, place reports anywhere below `data/raw/`, and run from the repository root:

```powershell
python -m src.extraction --input data/raw
```

The command discovers PDFs recursively, detects the report month and the contiguous **All Ongoing Projects (Table 6)** page range, preserves raw page/row extraction, standardizes project fields, validates each report, and creates monthly plus combined CSV files.

## Data flow

`data/raw/*.pdf` -> `data/extracted/YYYY-MM/*.jsonl` -> `data/cleaned/projects_YYYY_MM.csv` -> `data/processed/projects_monthly.csv`

Validation manifests and warning/rejection/duplicate files are written to `data/validation/`. Generated data and source PDFs are intentionally ignored by Git.

Validation-only `qc_metrics_YYYY_MM.csv` files contain financial progress and the physical-financial gap for anomaly analysis. These derived values are deliberately excluded from the clean monthly and combined project-month datasets. Cross-field warning definitions are documented in `reports/validation_rules.md`.

Dates reported as `MM/YYYY` are stored as `YYYY-MM`; no day is invented. Missing values remain empty and are never converted to zero. The combined dataset retains one row per project per report month and performs no backfilling across months.

## Tests

```powershell
python -m unittest discover -v
```

See `reports/data_dictionary.md`, `reports/extraction_comparison.md`, and `reports/manual_validation.md` for schema, method-selection evidence, and checked source fixtures.
