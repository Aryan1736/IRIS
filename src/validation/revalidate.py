"""Re-run validation from clean monthly CSVs without re-extracting PDFs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src.validation.core import build_quality_control_rows, validate_records

NUMERIC_FIELDS = ("original_cost", "revised_cost", "cumulative_expenditure", "physical_progress")
INTEGER_FIELDS = ("source_page", "source_row_number", "source_serial_number")


def _read_records(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for field in NUMERIC_FIELDS:
            row[field] = None if row[field] == "" else float(row[field])
        for field in INTEGER_FIELDS:
            row[field] = None if row[field] == "" else int(row[field])
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(root: Path, tag: str) -> Path:
    validation_dir = root / "data" / "validation"
    summaries = {}
    warning_fields = [
        "project_code", "report_month", "source_file", "source_page", "source_row_number",
        "field", "rule", "severity", "priority", "category", "message",
    ]
    qc_fields = [
        "project_code", "report_month", "start_date", "original_completion_date",
        "revised_completion_date", "original_cost", "revised_cost", "cumulative_expenditure",
        "physical_progress", "financial_progress", "physical_financial_gap", "warning_rules",
        "source_file", "source_page", "source_row_number",
    ]
    for token in ("2026_06", "2026_07"):
        records = _read_records(root / "data" / "cleaned" / f"projects_{token}.csv")
        warnings, _, metrics = validate_records(records)
        qc_rows = build_quality_control_rows(records, warnings)
        _write_csv(validation_dir / f"warnings_{token}_{tag}.csv", warnings, warning_fields)
        _write_csv(validation_dir / f"qc_metrics_{token}_{tag}.csv", qc_rows, qc_fields)
        summaries[token.replace("_", "-")] = metrics
    summary_path = validation_dir / f"validation_summary_{tag}.json"
    summary_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--tag", default="revised")
    args = parser.parse_args()
    print(run(args.root.resolve(), args.tag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
