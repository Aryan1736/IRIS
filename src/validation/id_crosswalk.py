"""Investigate, without applying, the June-to-July 2025 identifier redesign."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

OLD_ID_RE = re.compile(r"(?<![A-Z0-9])(?:N\d{8}|\d{9})(?!\d)")
NEW_ID_RE = re.compile(r"(?<!\d)\d{6}(?!\d)")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").casefold()
    return " ".join(re.findall(r"[a-z0-9]+", value))


def _compact(value: str) -> str:
    return _norm(value).replace(" ", "")


def _number(value: str) -> float | None:
    return None if value == "" else round(float(value), 2)


def _agency_key(value: str) -> str:
    value = value or ""
    simple = re.fullmatch(r"\s*([A-Za-z][A-Za-z0-9/&.-]{1,15})\s*", value)
    if simple:
        return _compact(simple.group(1))
    bracketed = re.findall(r"[\[(]([A-Za-z][A-Za-z0-9/&.-]{1,15})[\])]", value)
    if bracketed:
        return _compact(bracketed[-1])
    words = re.findall(r"[A-Za-z0-9]+", value)
    return "".join(word[0] for word in words).casefold() if words else ""


def _prepare(row: dict[str, str]) -> dict[str, Any]:
    name_compact = _compact(row["project_name"])
    return {
        "row": row,
        "name_compact": name_compact,
        "name_tokens": set(_norm(row["project_name"]).split()),
        "state": _compact(row["state"]),
        "sector": _compact(row["sector"]),
        "agency": _agency_key(row["agency"]),
        "approval_date": row["approval_date"],
        "original_cost": _number(row["original_cost"]),
        "revised_cost": _number(row["revised_cost"]),
        "original_completion_date": row["original_completion_date"],
        "revised_completion_date": row["revised_completion_date"],
    }


def _name_similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
    a, b = left["name_compact"], right["name_compact"]
    if not a or not b:
        return 0.0
    sequence = SequenceMatcher(None, a, b).ratio()
    ta, tb = left["name_tokens"], right["name_tokens"]
    jaccard = len(ta & tb) / len(ta | tb) if ta and tb else 0.0
    return max(sequence, jaccard)


def _compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    agreements: list[str] = []
    conflicts: list[str] = []
    missing: list[str] = []
    for field in (
        "approval_date",
        "original_cost",
        "revised_cost",
        "original_completion_date",
        "revised_completion_date",
        "state",
        "sector",
        "agency",
    ):
        a, b = left[field], right[field]
        if a in (None, "") or b in (None, ""):
            missing.append(field)
        elif a == b:
            agreements.append(field)
        else:
            conflicts.append(field)
    similarity = _name_similarity(left, right)
    exact_name = left["name_compact"] == right["name_compact"]
    material_conflicts = [field for field in conflicts if field in {"approval_date", "original_cost", "state"}]
    return {
        "agreements": agreements,
        "conflicts": conflicts,
        "missing": missing,
        "similarity": similarity,
        "exact_name": exact_name,
        "material_conflicts": material_conflicts,
    }


def _inspect_raw_ids(path: Path, serial_column: int) -> dict[str, int]:
    old = new = both = legacy_field = pmgid_field = 0
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if len(row["cells"]) <= serial_column or not row["cells"][serial_column].isdigit():
                continue
            text = " ".join(row["cells"])
            old_hit, new_hit = bool(OLD_ID_RE.search(text)), bool(NEW_ID_RE.search(text))
            old += old_hit
            new += new_hit
            both += old_hit and new_hit
            legacy_field += "legacy ocms" in text.casefold()
            pmgid_field += "pmgid" in text.casefold()
    return {
        "rows_with_old_style_id": old,
        "rows_with_six_digit_id": new,
        "rows_with_both_id_styles": both,
        "rows_printing_legacy_ocms_label": legacy_field,
        "rows_printing_pmgid_label": pmgid_field,
    }


DETAIL_FIELDS = (
    "project_name",
    "agency",
    "ministry",
    "sector",
    "state",
    "approval_date",
    "original_cost",
    "revised_cost",
    "original_completion_date",
    "revised_completion_date",
    "source_file",
    "source_page",
    "source_serial_number",
)


def _output_row(
    left: dict[str, str],
    right: dict[str, str] | None,
    confidence: str,
    method: str,
    edge: dict[str, Any] | None,
    legacy_candidates: int,
    new_candidates: int,
) -> dict[str, Any]:
    exact_name = bool(edge and edge["exact_name"])
    evidence = (["project_name_exact"] if exact_name else (["project_name_near"] if edge else []))
    evidence += edge["agreements"] if edge else []
    conflicts = edge["conflicts"] if edge else []
    flags = []
    if legacy_candidates > 1:
        flags.append("ONE_LEGACY_TO_MULTIPLE_NEW_CANDIDATES")
    if new_candidates > 1:
        flags.append("MULTIPLE_LEGACY_TO_ONE_NEW_CANDIDATE")
    if edge and edge["similarity"] < 0.68:
        flags.append("SUBSTANTIAL_PROJECT_NAME_CHANGE")
    if "agency" in conflicts:
        flags.append("AGENCY_CHANGED")
    if set(conflicts) & {"original_cost", "revised_cost", "original_completion_date", "revised_completion_date"}:
        flags.append("COST_OR_COMPLETION_CHANGED")
    output: dict[str, Any] = {
        "legacy_project_code": left["project_code"],
        "new_project_code": right["project_code"] if right else "",
        "match_confidence": confidence,
        "match_method": method,
        "evidence_fields": "|".join(evidence),
        "conflicting_fields": "|".join(conflicts),
        "missing_comparison_fields": "|".join(edge["missing"] if edge else []),
        "ambiguity_flags": "|".join(flags),
        "name_similarity_for_candidate_retrieval": round(edge["similarity"], 6) if edge else "",
        "legacy_candidate_count": legacy_candidates,
        "new_candidate_count": new_candidates,
    }
    for field in DETAIL_FIELDS:
        output[f"legacy_{field}"] = left[field]
        output[f"new_{field}"] = right[field] if right else ""
    return output


def investigate(root: Path) -> dict[str, Any]:
    june_rows = _read_csv(root / "data" / "cleaned" / "projects_2025_06.csv")
    july_rows = _read_csv(root / "data" / "cleaned" / "projects_2025_07.csv")
    june = [_prepare(row) for row in june_rows]
    july = [_prepare(row) for row in july_rows]

    edges: list[dict[str, Any]] = []
    by_legacy: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_new: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for li, left in enumerate(june):
        for ri, right in enumerate(july):
            comparison = _compare(left, right)
            agreements = comparison["agreements"]
            similarity = comparison["similarity"]
            credible = (
                comparison["exact_name"]
                or (similarity >= 0.68 and len(agreements) >= 2)
                or (similarity >= 0.50 and len(agreements) >= 4)
            )
            if not credible:
                continue
            high_eligible = (
                not comparison["material_conflicts"]
                and ("agency" in agreements or "state" in agreements)
                and (
                    (comparison["exact_name"] and len(agreements) >= 3)
                    or (similarity >= 0.80 and len(agreements) >= 4)
                    or (similarity >= 0.65 and len(agreements) >= 5)
                )
            )
            edge = {"li": li, "ri": ri, "high_eligible": high_eligible, **comparison}
            edges.append(edge)
            by_legacy[li].append(edge)
            by_new[ri].append(edge)

    high: list[dict[str, Any]] = []
    for edge in edges:
        eligible_left = [item for item in by_legacy[edge["li"]] if item["high_eligible"]]
        eligible_right = [item for item in by_new[edge["ri"]] if item["high_eligible"]]
        if edge["high_eligible"] and len(eligible_left) == 1 and len(eligible_right) == 1:
            high.append(edge)
    high_legacy = {edge["li"] for edge in high}
    high_new = {edge["ri"] for edge in high}
    unresolved = [edge for edge in edges if edge["li"] not in high_legacy and edge["ri"] not in high_new]
    unresolved_legacy = {edge["li"] for edge in unresolved}
    unresolved_new = {edge["ri"] for edge in unresolved}
    unresolved_by_legacy: dict[int, list[dict[str, Any]]] = defaultdict(list)
    unresolved_by_new: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for edge in unresolved:
        unresolved_by_legacy[edge["li"]].append(edge)
        unresolved_by_new[edge["ri"]].append(edge)

    output_rows = []
    ambiguous_rows = []
    for edge in high:
        method = "EXACT_NAME_MULTI_ATTRIBUTE" if edge["exact_name"] else "NEAR_NAME_MULTI_ATTRIBUTE"
        output_rows.append(
            _output_row(june_rows[edge["li"]], july_rows[edge["ri"]], "HIGH_CONFIDENCE", method, edge, 1, 1)
        )
    for edge in unresolved:
        row = _output_row(
            june_rows[edge["li"]],
            july_rows[edge["ri"]],
            "AMBIGUOUS",
            "CANDIDATE_ONLY_MULTI_ATTRIBUTE",
            edge,
            len(unresolved_by_legacy[edge["li"]]),
            len(unresolved_by_new[edge["ri"]]),
        )
        output_rows.append(row)
        ambiguous_rows.append(row)
    for li, left in enumerate(june_rows):
        if li in high_legacy or li in unresolved_legacy:
            continue
        output_rows.append(
            _output_row(left, None, "UNMATCHED", "NO_CREDIBLE_MULTI_ATTRIBUTE_CANDIDATE", None, 0, 0)
        )

    fields = [
        "legacy_project_code",
        "new_project_code",
        "match_confidence",
        "match_method",
        "evidence_fields",
        "conflicting_fields",
        "missing_comparison_fields",
        "ambiguity_flags",
        "name_similarity_for_candidate_retrieval",
        "legacy_candidate_count",
        "new_candidate_count",
        *[f"{side}_{field}" for field in DETAIL_FIELDS for side in ("legacy", "new")],
    ]
    confidence_order = {"HIGH_CONFIDENCE": 0, "AMBIGUOUS": 1, "UNMATCHED": 2}
    output_rows.sort(key=lambda row: (confidence_order[row["match_confidence"]], row["legacy_project_code"], row["new_project_code"]))
    ambiguous_rows.sort(key=lambda row: (row["legacy_project_code"], row["new_project_code"]))
    validation = root / "data" / "validation"
    _write_csv(validation / "id_crosswalk_june_july_2025.csv", output_rows, fields)
    _write_csv(validation / "id_crosswalk_ambiguous_june_july_2025.csv", ambiguous_rows, fields)

    raw_inspection = {
        "2025-06": _inspect_raw_ids(root / "data" / "extracted" / "2025-06" / "raw_table6_rows.jsonl", 2),
        "2025-07": _inspect_raw_ids(root / "data" / "extracted" / "2025-07" / "raw_table6_rows.jsonl", 0),
    }
    raw_inspection["clean_identifier_fields"] = {
        month: {
            field: sum(bool(row[field]) for row in rows)
            for field in ("project_code", "legacy_ocms_code", "pmgid")
        }
        for month, rows in (("2025-06", june_rows), ("2025-07", july_rows))
    }
    summary = {
        "june_unique_projects": len(june_rows),
        "july_unique_projects": len(july_rows),
        "explicit_source_crosswalk_matches": 0,
        "high_confidence_matches": len(high),
        "ambiguous_candidate_edges": len(unresolved),
        "ambiguous_legacy_projects": len(unresolved_legacy),
        "ambiguous_july_projects": len(unresolved_new),
        "unmatched_june_projects": len(june_rows) - len(high_legacy) - len(unresolved_legacy),
        "unmatched_july_projects": len(july_rows) - len(high_new) - len(unresolved_new),
        "july_projects_without_high_confidence_mapping": len(july_rows) - len(high_new),
        "possible_splits_one_legacy_multiple_new": sum(len(items) > 1 for items in unresolved_by_legacy.values()),
        "possible_mergers_multiple_legacy_one_new": sum(len(items) > 1 for items in unresolved_by_new.values()),
        "raw_identifier_inspection": raw_inspection,
        "rules": {
            "candidate_retrieval": [
                "exact normalized project name",
                "name similarity >= 0.68 plus at least 2 independent agreeing attributes",
                "name similarity >= 0.50 plus at least 4 independent agreeing attributes",
            ],
            "high_confidence": [
                "no conflict in approval_date, original_cost, or state",
                "agency or state agrees",
                "exact normalized name plus at least 3 agreeing attributes; or name similarity >= 0.80 plus at least 4; or >= 0.65 plus at least 5",
                "only one high-eligible candidate in both directions",
            ],
            "important_note": "Name similarity retrieves candidates only and never creates a mapping by itself.",
        },
        "output_files": {
            "all": str((validation / "id_crosswalk_june_july_2025.csv").resolve()),
            "ambiguous": str((validation / "id_crosswalk_ambiguous_june_july_2025.csv").resolve()),
        },
    }
    (validation / "id_crosswalk_summary_june_july_2025.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(investigate(args.root.resolve()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
