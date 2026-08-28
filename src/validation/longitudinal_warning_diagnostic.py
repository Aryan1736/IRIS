"""Read-only longitudinal warning diagnosis for the Jan-Jul 2026 baseline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

MONTHS = tuple(f"2026-{month:02d}" for month in range(1, 8))
RULES = (
    "AGENCY_CHANGED",
    "PROJECT_NAME_CHANGED",
    "STATE_CHANGED",
    "CUMULATIVE_EXPENDITURE_DECREASED",
    "PHYSICAL_PROGRESS_DECREASED",
    "REVISED_COST_DECREASED",
    "POSITIVE_EXPENDITURE_TO_ZERO",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def number(value: str) -> float | None:
    return None if value == "" else float(value)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ascii_text(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()


def alnum(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", ascii_text(value).lower())


def words(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", ascii_text(value).lower())


def strip_bracketed(value: str) -> str:
    return re.sub(r"\s*[\[(][^\])]*[\])]\s*", " ", value).strip()


def strip_roman_unit_suffix(value: str) -> str:
    return re.sub(r"\s*-\s*(?:I|II|III)\s*$", "", value, flags=re.IGNORECASE).strip()


def acronym(value: str) -> str:
    ignored = {"and", "of", "the", "limited", "ltd", "corporation", "company", "ministry", "department"}
    tokens = [token for token in words(strip_bracketed(value)) if token not in ignored]
    return "".join(token[0] for token in tokens if token)


def ministry_like(value: str) -> bool:
    basic = alnum(value)
    return basic.startswith("ministry") or basic.startswith("department")


def agency_category(previous: str, current: str) -> str:
    if alnum(previous) == alnum(current):
        return "WHITESPACE_PUNCTUATION_CASING_DIFFERENCES"

    left_no_bracket = alnum(strip_bracketed(previous))
    right_no_bracket = alnum(strip_bracketed(current))
    if left_no_bracket == right_no_bracket:
        return "ABBREVIATION_ACRONYM_DIFFERENCES"
    if alnum(strip_roman_unit_suffix(strip_bracketed(previous))) == alnum(strip_roman_unit_suffix(strip_bracketed(current))):
        return "ABBREVIATION_ACRONYM_DIFFERENCES"

    left, right = alnum(previous), alnum(current)
    left_tokens, right_tokens = set(words(previous)), set(words(current))
    explicit_acronyms = {
        token.lower()
        for token in re.findall(r"[\[(]([A-Za-z0-9/-]{2,})[\])]", previous + " " + current)
    }
    collapsed_acronyms = {acronym(previous), acronym(current)} - {""}
    short_values = {left, right}
    if any(token in short_values for token in explicit_acronyms | collapsed_acronyms):
        return "ABBREVIATION_ACRONYM_DIFFERENCES"
    if any(short.startswith(token) for short in short_values for token in collapsed_acronyms if len(token) >= 3):
        return "ABBREVIATION_ACRONYM_DIFFERENCES"
    if ("cil" in left_tokens | right_tokens) and (left_tokens & right_tokens):
        return "ABBREVIATION_ACRONYM_DIFFERENCES"
    if {left, right} & {"nhai", "wclcil", "seclcil", "eclcil", "nclcil", "cclcil", "iocl", "bpcl", "hpcl", "gail", "ongc"}:
        longer = current if len(current) > len(previous) else previous
        if any(token in alnum(longer) for token in ("nationalhighwaysauthority", "coalfields", "petroleum", "naturalgas", "oilcorporation")):
            return "ABBREVIATION_ACRONYM_DIFFERENCES"

    if ministry_like(previous) != ministry_like(current):
        return "LIKELY_EXTRACTION_OR_GROUP_HEADING_PROPAGATION_ISSUE"
    if previous in {"Ministry of Coal", "Ministry of Railways", "Ministry of Petroleum & Natural Gas", "MinistryofPetroleumNaturalGas"}:
        return "LIKELY_EXTRACTION_OR_GROUP_HEADING_PROPAGATION_ISSUE"

    ratio = SequenceMatcher(None, left, right).ratio()
    if ratio >= 0.82:
        return "APPARENT_SOURCE_SPELLING_CHANGES"
    return "GENUINE_DIFFERENT_AGENCY_NAMES"


def name_category(previous: str, current: str) -> str:
    return "SUPERFICIAL_ONLY" if alnum(previous) == alnum(current) else "SUBSTANTIVE_TEXT_CHANGE"


def raw_lookup(root: Path, month: str) -> dict[tuple[int, int], list[str]]:
    path = root / "data" / "extracted" / month / "raw_table6_rows.jsonl"
    result: dict[tuple[int, int], list[str]] = {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            result[(int(row["source_page"]), int(row["source_row_number"]))] = row["cells"]
    return result


def event_base(transition: str, left: dict[str, str], right: dict[str, str]) -> dict[str, Any]:
    return {
        "transition": transition,
        "previous_month": left["report_month"],
        "current_month": right["report_month"],
        "project_code": right["project_code"],
        "agency": right["agency"],
        "previous_agency": left["agency"],
        "current_agency": right["agency"],
        "ministry": right["ministry"],
        "previous_ministry": left["ministry"],
        "current_ministry": right["ministry"],
        "project_name": right["project_name"],
        "previous_project_name": left["project_name"],
        "current_project_name": right["project_name"],
        "previous_source_file": left["source_file"],
        "current_source_file": right["source_file"],
        "previous_source_page": int(left["source_page"]),
        "current_source_page": int(right["source_page"]),
        "previous_source_row_number": int(left["source_row_number"]),
        "current_source_row_number": int(right["source_row_number"]),
    }


def run(root: Path) -> Path:
    source_paths = [root / "data" / "cleaned" / f"projects_{month.replace('-', '_')}.csv" for month in MONTHS]
    monthly = {month: {row["project_code"]: row for row in read_csv(path)} for month, path in zip(MONTHS, source_paths)}
    raw = {month: raw_lookup(root, month) for month in MONTHS}
    counts: dict[str, Counter[str]] = {}
    agency_changes: list[dict[str, Any]] = []
    name_changes: list[dict[str, Any]] = []
    expenditure_decreases: list[dict[str, Any]] = []
    physical_decreases: list[dict[str, Any]] = []
    revised_cost_decreases: list[dict[str, Any]] = []
    state_changes: list[dict[str, Any]] = []

    for earlier, later in zip(MONTHS, MONTHS[1:]):
        transition = f"{earlier}->{later}"
        transition_counts: Counter[str] = Counter()
        for code in sorted(set(monthly[earlier]) & set(monthly[later])):
            left, right = monthly[earlier][code], monthly[later][code]
            base = event_base(transition, left, right)
            left_raw = raw[earlier].get((base["previous_source_page"], base["previous_source_row_number"]), [])
            right_raw = raw[later].get((base["current_source_page"], base["current_source_row_number"]), [])
            raw_fields = {"previous_raw_cells": left_raw, "current_raw_cells": right_raw}
            if left["agency"] != right["agency"]:
                transition_counts["AGENCY_CHANGED"] += 1
                agency_changes.append({**base, "category": agency_category(left["agency"], right["agency"]), **raw_fields})
            if left["project_name"] != right["project_name"]:
                transition_counts["PROJECT_NAME_CHANGED"] += 1
                name_changes.append({
                    **base,
                    "change_type": name_category(left["project_name"], right["project_name"]),
                    "similarity_ratio": round(SequenceMatcher(None, alnum(left["project_name"]), alnum(right["project_name"])).ratio(), 6),
                    **raw_fields,
                })
            if left["state"] != right["state"]:
                transition_counts["STATE_CHANGED"] += 1
                state_changes.append({**base, "previous_state": left["state"], "current_state": right["state"], **raw_fields})

            previous_exp, current_exp = number(left["cumulative_expenditure"]), number(right["cumulative_expenditure"])
            if previous_exp is not None and current_exp is not None and current_exp < previous_exp:
                transition_counts["CUMULATIVE_EXPENDITURE_DECREASED"] += 1
                decrease = previous_exp - current_exp
                positive_to_zero = previous_exp > 0 and current_exp == 0
                if positive_to_zero:
                    transition_counts["POSITIVE_EXPENDITURE_TO_ZERO"] += 1
                expenditure_decreases.append({
                    **base,
                    "previous_value": previous_exp,
                    "current_value": current_exp,
                    "absolute_decrease": round(decrease, 6),
                    "percentage_decrease": round(decrease / previous_exp * 100, 6) if previous_exp > 0 else None,
                    "positive_to_zero": positive_to_zero,
                    **raw_fields,
                })

            previous_progress, current_progress = number(left["physical_progress"]), number(right["physical_progress"])
            if previous_progress is not None and current_progress is not None and current_progress < previous_progress:
                transition_counts["PHYSICAL_PROGRESS_DECREASED"] += 1
                decrease = previous_progress - current_progress
                if decrease < 1:
                    band = "<1"
                elif decrease <= 5:
                    band = "1-5"
                elif decrease <= 10:
                    band = "5-10"
                else:
                    band = ">10"
                physical_decreases.append({
                    **base,
                    "previous_value": previous_progress,
                    "current_value": current_progress,
                    "decrease_percentage_points": round(decrease, 6),
                    "decrease_band": band,
                    **raw_fields,
                })

            previous_cost, current_cost = number(left["revised_cost"]), number(right["revised_cost"])
            if previous_cost is not None and current_cost is not None and current_cost < previous_cost:
                transition_counts["REVISED_COST_DECREASED"] += 1
                revised_cost_decreases.append({
                    **base,
                    "previous_value": previous_cost,
                    "current_value": current_cost,
                    "absolute_decrease": round(previous_cost - current_cost, 6),
                    **raw_fields,
                })
        counts[transition] = transition_counts

    agency_pair_counts = Counter((row["previous_agency"], row["current_agency"]) for row in agency_changes)
    top_pairs = [
        {"previous_agency": previous, "current_agency": current, "count": count}
        for (previous, current), count in sorted(agency_pair_counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:20]
    ]
    agency_category_counts = Counter(row["category"] for row in agency_changes)
    agency_category_by_transition: dict[str, dict[str, int]] = {}
    for transition in counts:
        local = Counter(row["category"] for row in agency_changes if row["transition"] == transition)
        agency_category_by_transition[transition] = dict(sorted(local.items()))
    name_counts = Counter(row["change_type"] for row in name_changes)
    name_by_transition: dict[str, dict[str, int]] = {}
    for transition in counts:
        local = Counter(row["change_type"] for row in name_changes if row["transition"] == transition)
        name_by_transition[transition] = dict(sorted(local.items()))
    band_order = ("<1", "1-5", "5-10", ">10")
    physical_distribution = {band: sum(row["decrease_band"] == band for row in physical_decreases) for band in band_order}
    physical_by_transition = {
        transition: {band: sum(row["transition"] == transition and row["decrease_band"] == band for row in physical_decreases) for band in band_order}
        for transition in counts
    }

    result = {
        "scope": "Accepted Jan-Jul 2026 baseline; read-only diagnosis",
        "definitions": {
            "positive_to_zero_is_subset_of_cumulative_expenditure_decreased": True,
            "physical_decrease_bands": "<1; 1-5 inclusive; >5-10 inclusive; >10 percentage points",
            "superficial_text_equivalence": "Unicode NFKD to ASCII, lowercase, remove non-alphanumeric characters; source strings remain unchanged",
            "source_values_modified": False,
        },
        "source_sha256": {str(path.relative_to(root)): sha256(path) for path in [*source_paths, root / "data" / "processed" / "projects_monthly.csv"]},
        "rule_counts_by_transition": {transition: {rule: counter.get(rule, 0) for rule in RULES} for transition, counter in counts.items()},
        "agency_change": {
            "total": len(agency_changes),
            "category_counts": dict(sorted(agency_category_counts.items())),
            "category_counts_by_transition": agency_category_by_transition,
            "top_20_pairs": top_pairs,
            "cases": agency_changes,
        },
        "project_name_change": {
            "total": len(name_changes),
            "classification_counts": dict(sorted(name_counts.items())),
            "classification_counts_by_transition": name_by_transition,
            "cases": name_changes,
        },
        "cumulative_expenditure_decrease": {
            "total": len(expenditure_decreases),
            "positive_to_zero_count": sum(row["positive_to_zero"] for row in expenditure_decreases),
            "cases": expenditure_decreases,
            "positive_to_zero_cases": [row for row in expenditure_decreases if row["positive_to_zero"]],
        },
        "physical_progress_decrease": {
            "total": len(physical_decreases),
            "distribution": physical_distribution,
            "distribution_by_transition": physical_by_transition,
            "cases": physical_decreases,
        },
        "revised_cost_decrease": {"total": len(revised_cost_decreases), "cases": revised_cost_decreases},
        "state_change": {"total": len(state_changes), "cases": state_changes},
    }
    output = root / "data" / "validation" / "diagnostics" / "longitudinal_warning_diagnostic_2026_01_07.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(run(args.root.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
