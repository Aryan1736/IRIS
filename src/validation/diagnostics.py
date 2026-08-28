"""Diagnostic analysis for ZERO_EXPENDITURE_POSITIVE_PROGRESS.

This module reads clean monthly CSVs and validation warnings without modifying
either. It writes JSON and Markdown diagnostic artifacts only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

RULE = "ZERO_EXPENDITURE_POSITIVE_PROGRESS"
MONTH_TOKENS = ("2026_06", "2026_07")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _number(value: str) -> float | None:
    return None if value == "" else float(value)


def _month_index(value: str) -> int:
    year, month = map(int, value.split("-"))
    return year * 12 + month - 1


def _age_months(row: dict[str, str]) -> int | None:
    if not row["start_date"]:
        return None
    return _month_index(row["report_month"]) - _month_index(row["start_date"])


def _age_band(row: dict[str, str]) -> str:
    age = _age_months(row)
    if age is None:
        return "START_DATE_MISSING"
    if age < 0:
        return "STARTS_AFTER_REPORT"
    if age < 12:
        return "[0,1 year)"
    if age < 24:
        return "[1,2 years)"
    if age < 36:
        return "[2,3 years)"
    if age < 60:
        return "[3,5 years)"
    if age < 120:
        return "[5,10 years)"
    return "[10+ years)"


def _progress_band(row: dict[str, str]) -> str:
    value = _number(row["physical_progress"])
    if value is None:
        return "MISSING"
    if 0 < value <= 25:
        return "(0,25]"
    if 25 < value <= 50:
        return "(25,50]"
    if 50 < value <= 75:
        return "(50,75]"
    if 75 < value <= 100:
        return "(75,100]"
    if value == 0:
        return "ZERO"
    return "OUTSIDE_RANGE"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _aggregate(rows: list[dict[str, str]], flagged_keys: set[tuple[str, str]], dimension: str) -> list[dict[str, Any]]:
    totals: Counter[str] = Counter()
    flagged: Counter[str] = Counter()
    month_counts: dict[str, Counter[str]] = defaultdict(Counter)
    unique_codes: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        value = row[dimension] or "MISSING"
        totals[value] += 1
        key = (row["project_code"], row["report_month"])
        if key in flagged_keys:
            flagged[value] += 1
            month_counts[value][row["report_month"]] += 1
            unique_codes[value].add(row["project_code"])
    total_flags = sum(flagged.values())
    result = []
    for value, count in flagged.items():
        denominator = totals[value]
        result.append(
            {
                "value": value,
                "flagged_project_months": count,
                "unique_flagged_projects": len(unique_codes[value]),
                "total_project_months": denominator,
                "flag_rate_pct": round(count / denominator * 100, 2),
                "share_of_all_flags_pct": round(count / total_flags * 100, 2) if total_flags else 0,
                "june_flags": month_counts[value]["2026-06"],
                "july_flags": month_counts[value]["2026-07"],
            }
        )
    return sorted(result, key=lambda item: (-item["flagged_project_months"], item["value"]))


def _transition_analysis(rows: list[dict[str, str]]) -> dict[str, Any]:
    by_month: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_month[row["report_month"]][row["project_code"]] = row
    june, july = by_month["2026-06"], by_month["2026-07"]
    shared = sorted(set(june) & set(july))
    transitions = Counter()
    zero_zero_change = Counter()
    increased_cases = []

    def state(value: float | None) -> str:
        if value is None:
            return "missing"
        if value == 0:
            return "zero"
        if value > 0:
            return "positive"
        return "negative"

    for code in shared:
        left, right = june[code], july[code]
        june_exp = _number(left["cumulative_expenditure"])
        july_exp = _number(right["cumulative_expenditure"])
        transition = f"{state(june_exp)}_to_{state(july_exp)}"
        transitions[transition] += 1
        if transition != "zero_to_zero":
            continue
        june_progress = _number(left["physical_progress"])
        july_progress = _number(right["physical_progress"])
        if june_progress is None or july_progress is None:
            zero_zero_change["missing_progress"] += 1
        elif july_progress > june_progress:
            zero_zero_change["increased"] += 1
            increased_cases.append(
                {
                    "project_code": code,
                    "project_name": right["project_name"],
                    "ministry": right["ministry"],
                    "sector": right["sector"],
                    "agency": right["agency"],
                    "state": right["state"],
                    "june_expenditure": june_exp,
                    "july_expenditure": july_exp,
                    "june_physical_progress": june_progress,
                    "july_physical_progress": july_progress,
                    "physical_progress_change": round(july_progress - june_progress, 6),
                    "june_source_page": int(left["source_page"]),
                    "july_source_page": int(right["source_page"]),
                }
            )
        elif july_progress < june_progress:
            zero_zero_change["decreased"] += 1
        else:
            zero_zero_change["unchanged"] += 1
    increased_cases.sort(key=lambda item: (-item["physical_progress_change"], item["project_code"]))
    return {
        "projects_present_in_both_months": len(shared),
        "expenditure_transitions": dict(sorted(transitions.items())),
        "zero_expenditure_both_months_physical_progress_change": {
            key: zero_zero_change.get(key, 0)
            for key in ("increased", "decreased", "unchanged", "missing_progress")
        },
        "zero_expenditure_both_months_with_any_physical_progress_change": zero_zero_change.get("increased", 0) + zero_zero_change.get("decreased", 0),
        "zero_expenditure_both_months_with_increased_physical_progress": len(increased_cases),
        "increased_physical_progress_cases": increased_cases,
    }


def _markdown_table(rows: list[dict[str, Any]], limit: int | None = None) -> str:
    rows = rows if limit is None else rows[:limit]
    if not rows:
        return "_No records._"
    columns = list(rows[0])
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join("---" for _ in columns) + "|"
    body = ["| " + " | ".join(str(row[column]).replace("|", "/") for column in columns) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def run(root: Path) -> tuple[Path, Path]:
    source_paths = {token: root / "data" / "cleaned" / f"projects_{token}.csv" for token in MONTH_TOKENS}
    rows = [row for token in MONTH_TOKENS for row in _read_csv(source_paths[token])]
    warning_paths = {
        token: (
            root / "data" / "validation" / f"warnings_{token}_revised.csv"
            if (root / "data" / "validation" / f"warnings_{token}_revised.csv").exists()
            else root / "data" / "validation" / f"warnings_{token}.csv"
        )
        for token in MONTH_TOKENS
    }
    warning_rows = [
        row
        for token in MONTH_TOKENS
        for row in _read_csv(warning_paths[token])
        if row["rule"] == RULE
    ]
    flagged_keys = {(row["project_code"], row["report_month"]) for row in warning_rows}

    # Add analysis-only dimensions to copies. Source rows and source CSVs remain untouched.
    analysis_rows = []
    for source in rows:
        row = dict(source)
        row["physical_progress_band"] = _progress_band(row)
        row["project_age_band"] = _age_band(row)
        analysis_rows.append(row)

    flagged_rows = [row for row in analysis_rows if (row["project_code"], row["report_month"]) in flagged_keys]
    ages = [age for row in flagged_rows if (age := _age_months(row)) is not None and age >= 0]
    breakdowns = {
        dimension: _aggregate(analysis_rows, flagged_keys, dimension)
        for dimension in (
            "ministry",
            "sector",
            "agency",
            "state",
            "physical_progress_band",
            "project_age_band",
        )
    }
    transitions = _transition_analysis(analysis_rows)
    flagged_by_month = Counter(row["report_month"] for row in flagged_rows)
    june_flagged_codes = {row["project_code"] for row in flagged_rows if row["report_month"] == "2026-06"}
    july_flagged_codes = {row["project_code"] for row in flagged_rows if row["report_month"] == "2026-07"}
    unique_by_month = {
        month: len({row["project_code"] for row in flagged_rows if row["report_month"] == month})
        for month in ("2026-06", "2026-07")
    }
    result = {
        "diagnostic_rule": RULE,
        "source_files": {str(path.resolve()): _sha256(path) for path in source_paths.values()},
        "validation_warning_files": [str(path.resolve()) for path in warning_paths.values()],
        "definitions": {
            "flag": "cumulative_expenditure == 0 AND physical_progress > 0, with start_date <= report_month or start_date missing",
            "observation_unit": "project-month",
            "project_age_months": "whole calendar months from start_date to report_month",
            "source_values_modified": False,
        },
        "flagged_project_months": len(flagged_rows),
        "flagged_by_month": dict(sorted(flagged_by_month.items())),
        "unique_flagged_projects_by_month": unique_by_month,
        "unique_flagged_projects_across_months": len({row["project_code"] for row in flagged_rows}),
        "flagged_project_cross_month_presence": {
            "flagged_in_both_months": len(june_flagged_codes & july_flagged_codes),
            "flagged_in_june_only": len(june_flagged_codes - july_flagged_codes),
            "flagged_in_july_only": len(july_flagged_codes - june_flagged_codes),
        },
        "flagged_project_age_months": {
            "count": len(ages),
            "minimum": min(ages) if ages else None,
            "median": statistics.median(ages) if ages else None,
            "mean": round(statistics.mean(ages), 2) if ages else None,
            "maximum": max(ages) if ages else None,
        },
        "breakdowns": breakdowns,
        "cross_month_transitions": transitions,
    }
    result["cross_month_transitions"]["increased_cases_by_agency"] = dict(
        Counter(item["agency"] for item in transitions["increased_physical_progress_cases"]).most_common()
    )
    result["cross_month_transitions"]["increased_cases_by_sector"] = dict(
        Counter(item["sector"] for item in transitions["increased_physical_progress_cases"]).most_common()
    )

    output_dir = root / "data" / "validation" / "diagnostics"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "zero_expenditure_positive_progress_2026_06_07.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    transition_rows = [
        {"transition": key, "projects": value}
        for key, value in transitions["expenditure_transitions"].items()
    ]
    change_rows = [
        {"physical_progress_change": key, "projects": value}
        for key, value in transitions["zero_expenditure_both_months_physical_progress_change"].items()
    ]
    case_rows = [
        {
            "project_code": item["project_code"],
            "agency": item["agency"],
            "sector": item["sector"],
            "state": item["state"],
            "June %": item["june_physical_progress"],
            "July %": item["july_physical_progress"],
            "change": item["physical_progress_change"],
        }
        for item in transitions["increased_physical_progress_cases"]
    ]
    report = f"""# ZERO_EXPENDITURE_POSITIVE_PROGRESS diagnostic: June-July 2026

## Scope and definitions

- Observation unit: project-month.
- Flag: cumulative expenditure equals exactly zero and physical progress is above zero, with project start not after report month (or start unavailable).
- Project age: whole calendar months from start month to report month.
- Source values were read only and not changed.

## Headline counts

- Flagged project-months: **{len(flagged_rows)}** ({flagged_by_month['2026-06']} June; {flagged_by_month['2026-07']} July).
- Unique flagged projects across either month: **{result['unique_flagged_projects_across_months']}**.
- Flagged in both months: **{result['flagged_project_cross_month_presence']['flagged_in_both_months']}**; June only: **{result['flagged_project_cross_month_presence']['flagged_in_june_only']}**; July only: **{result['flagged_project_cross_month_presence']['flagged_in_july_only']}**.
- Flagged-project age: median **{result['flagged_project_age_months']['median']} months**, mean **{result['flagged_project_age_months']['mean']} months**, range **{result['flagged_project_age_months']['minimum']}-{result['flagged_project_age_months']['maximum']} months**.

## Ministry

{_markdown_table(breakdowns['ministry'])}

## Sector

{_markdown_table(breakdowns['sector'])}

## Agency (top 20 by flagged project-months)

{_markdown_table(breakdowns['agency'], 20)}

## State (top 20 by flagged project-months)

{_markdown_table(breakdowns['state'], 20)}

## Physical progress bands

{_markdown_table(breakdowns['physical_progress_band'])}

## Project age bands

{_markdown_table(breakdowns['project_age_band'])}

## Cross-month expenditure transitions

Shared projects: **{transitions['projects_present_in_both_months']}**.

{_markdown_table(transition_rows)}

## Physical progress while expenditure remains zero

{_markdown_table(change_rows)}

Projects with physical progress increasing while expenditure stayed exactly zero in both months: **{transitions['zero_expenditure_both_months_with_increased_physical_progress']}**.

Agency counts for these increasing-progress cases: `{json.dumps(result['cross_month_transitions']['increased_cases_by_agency'], ensure_ascii=False)}`.

{_markdown_table(case_rows)}

The accompanying JSON contains every agency/state breakdown row and the complete detailed transition case records.
"""
    report_path = root / "reports" / "zero_expenditure_positive_progress_diagnostic_2026_06_07.md"
    report_path.write_text(report, encoding="utf-8")
    return json_path, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    json_path, report_path = run(args.root.resolve())
    print(json_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
