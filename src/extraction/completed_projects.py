"""Extraction pipeline for Table 3: Completed Projects.

Extracts auditable, source-faithful completed project records from PAIMANA/OCMS
monthly Flash Report PDFs into data/processed/projects_completed.csv.

Supported Layouts:
1. table3-completed-legacy-six-column-v1 (April - June 2025)
2. table3-completed-seven-column-v1 (September 2025 - July 2026)

Reports where Table 3 Completed Projects is absent:
- July 2025 (Table 3 is North-Eastern Region Ongoing Projects)
- August 2025 (Table 3 is North-Eastern Region Ongoing Projects)
"""

from __future__ import annotations

import csv
import json
import logging
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pdfplumber

LOGGER = logging.getLogger("paimana.completed_projects")

EXTRACTION_METHOD = "pdfplumber-table3-v1"
TABLE_SELECTION_METHOD = "semantic-table3-header-v1"

LAYOUT_LEGACY_SIX_COLUMN = "table3-completed-legacy-six-column-v1"
LAYOUT_SEVEN_COLUMN = "table3-completed-seven-column-v1"

MONTH_NAMES = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12,
}

MISSING_TOKENS = {"", "-", "(-)", "na", "n/a", "n.a.", "nil", "none"}

# Signatures for header matching
# Legacy 6-column layout (Apr - Jun 2025)
TABLE3_LEGACY_SIX_COLUMN_SIGNATURE = (
    ("sector",),
    ("sl",),
    ("project name", "project code"),
    ("original", "cost"),
    ("commissioning", "original"),
    ("cumulative", "expenditure"),
)

# Standard 7-column layout (Sep 2025 - Jul 2026 except Jun 2026 variant)
TABLE3_SEVEN_COLUMN_SIGNATURE = (
    ("sl",),
    ("project name", "project code"),
    ("state",),
    ("approval",),
    ("doc",),
    ("cost",),
    ("cumulative", "expenditure"),
)

# 7-column layout variant in June 2026: Col 4 header omits "Actual Date of Completion"
TABLE3_SEVEN_COLUMN_JUN2026_SIGNATURE = (
    ("sl",),
    ("project name", "project code"),
    ("state",),
    ("approval",),
    ("doc", "revised"),
    ("cost",),
    ("cumulative", "expenditure"),
)

COMPLETED_FIELDS = [
    "project_code",
    "project_name",
    "agency",
    "ministry",
    "sector",
    "state",
    "approval_date",
    "start_date",
    "original_completion_date",
    "revised_completion_date",
    "actual_completion_date",
    "original_cost",
    "revised_cost",
    "cumulative_expenditure",
    "report_month",
    "approval_date_raw",
    "start_date_raw",
    "original_completion_date_raw",
    "revised_completion_date_raw",
    "actual_completion_date_raw",
    "original_cost_raw",
    "revised_cost_raw",
    "cumulative_expenditure_raw",
    "source_file",
    "source_page",
    "source_row_number",
    "source_serial_number",
    "extraction_method",
]


class SchemaChangeDetected(RuntimeError):
    """Raised when encountering an unsupported or unexpected schema/table structure."""


class TableCandidateSelectionError(RuntimeError):
    """Raised when candidate selection fails closed."""

    def __init__(self, message: str, audits: list[dict[str, Any]], tables: list[Any]) -> None:
        super().__init__(message)
        self.audits = audits
        self.tables = tables


def normalize_space(value: str | None) -> str:
    """Collapse consecutive whitespace while preserving non-empty text."""
    return re.sub(r"\s+", " ", value or "").strip()


def is_missing(value: str | None) -> bool:
    """Check whether a source value represents a missing token."""
    normalized = normalize_space(value).lower()
    compact = re.sub(r"\s+", "", normalized)
    return normalized in MISSING_TOKENS or compact in MISSING_TOKENS


def parse_month_string(value: str | None) -> str | None:
    """Convert MM/YYYY to YYYY-MM; retain no invented day component."""
    if not value or is_missing(value):
        return None
    val = normalize_space(value).strip("()")
    match = re.match(r"^(0[1-9]|1[0-2])/(19|20\d{2})$", val)
    if match:
        return f"{match.group(2)}-{match.group(1)}"
    return None


def parse_cost_number(value: str | None) -> float | None:
    """Parse a numeric cost/expenditure string in Rs crore without treating missing as zero."""
    if not value or is_missing(value):
        return None
    val = normalize_space(value).strip("()").replace(",", "")
    try:
        return float(val)
    except ValueError:
        return None


def detect_report_month(text: str, filename: str) -> str:
    """Extract report month (YYYY-MM) from text or fallback to filename."""
    match = re.search(r"\b(" + "|".join(MONTH_NAMES) + r")\s+(20\d{2})\b", text.upper())
    if not match:
        match = re.search(r"(" + "|".join(MONTH_NAMES) + r")[_ -]+(20\d{2})", filename.upper())
    if not match:
        raise SchemaChangeDetected(f"Could not determine report month for {filename}")
    return f"{match.group(2)}-{MONTH_NAMES[match.group(1)]:02d}"


def is_table3_page(text: str) -> bool:
    """Semantically detect if a page belongs to Table 3 Completed Projects.
    
    Explicitly rejects North-Eastern region ongoing projects and general ongoing tables.
    """
    normalized = normalize_space(text).lower()
    legacy_match = "project list: completed during" in normalized
    seven_col_match = "completed projects during month" in normalized
    if not (legacy_match or seven_col_match):
        return False
    if "ongoing projects" in normalized and ("table 3" in normalized or "table:-3" in normalized or "table-3" in normalized):
        return False
    return True


def _get_page_sector_headings(page: Any, table: Any) -> list[tuple[float, str]]:
    """Find all sector headings on the page with their top y-coordinate from Column 0 margin."""
    headings: list[tuple[float, str]] = []
    c0_hdr = table.rows[0].cells[0]
    if not c0_hdr:
        return []
    x0_min, x0_max = c0_hdr[0] - 10, c0_hdr[2] + 10
    y0_min = c0_hdr[3]
    y0_max = table.bbox[3]
    margin_words = [w for w in page.extract_words() if x0_min <= w["x0"] <= x0_max and y0_min <= w["top"] <= y0_max]
    lines: list[tuple[float, str]] = []
    curr_line: list[str] = []
    curr_top: float | None = None
    for w in sorted(margin_words, key=lambda x: (x["top"], x["x0"])):
        if curr_top is None or abs(w["top"] - curr_top) < 6:
            curr_line.append(w["text"])
            curr_top = w["top"]
        else:
            lines.append((curr_top, " ".join(curr_line)))
            curr_line = [w["text"]]
            curr_top = w["top"]
    if curr_line and curr_top is not None:
        lines.append((curr_top, " ".join(curr_line)))
    merged_lines: list[list[Any]] = []
    for top, text in lines:
        if not merged_lines:
            merged_lines.append([top, text])
        else:
            prev_top, prev_text = merged_lines[-1]
            if top - prev_top < 16:
                merged_lines[-1][1] = f"{prev_text} {text}"
            else:
                merged_lines.append([top, text])
    for top, text in merged_lines:
        clean = normalize_space(text)
        if clean and clean.lower() not in ("sector", "total"):
            headings.append((top, clean))
    return headings


def classify_table3_header(row: list[str | None]) -> tuple[str | None, list[str]]:
    """Positional matching of a table header row against supported signatures."""
    cells = [normalize_space(c).lower() for c in row]
    matches: list[str] = []
    failures: list[str] = []

    # Check legacy 6-column
    if len(row) == 6:
        missing: list[str] = []
        for col_idx, required_tokens in enumerate(TABLE3_LEGACY_SIX_COLUMN_SIGNATURE):
            actual = cells[col_idx]
            absent = [tok for tok in required_tokens if tok not in actual]
            if absent:
                missing.append(f"col {col_idx} missing {absent}")
        if not missing:
            matches.append(LAYOUT_LEGACY_SIX_COLUMN)
        else:
            failures.append(f"{LAYOUT_LEGACY_SIX_COLUMN}: {'; '.join(missing)}")

    # Check 7-column
    elif len(row) == 7:
        missing_std: list[str] = []
        for col_idx, required_tokens in enumerate(TABLE3_SEVEN_COLUMN_SIGNATURE):
            actual = cells[col_idx]
            absent = [tok for tok in required_tokens if tok not in actual]
            if absent:
                missing_std.append(f"col {col_idx} missing {absent}")
        if not missing_std:
            matches.append(LAYOUT_SEVEN_COLUMN)
        else:
            # Check June 2026 variant
            missing_variant: list[str] = []
            for col_idx, required_tokens in enumerate(TABLE3_SEVEN_COLUMN_JUN2026_SIGNATURE):
                actual = cells[col_idx]
                absent = [tok for tok in required_tokens if tok not in actual]
                if absent:
                    missing_variant.append(f"col {col_idx} missing {absent}")
            if not missing_variant:
                matches.append(LAYOUT_SEVEN_COLUMN)
            else:
                failures.append(f"{LAYOUT_SEVEN_COLUMN}: std: {'; '.join(missing_std)} | var: {'; '.join(missing_variant)}")
    else:
        failures.append(f"unsupported column count {len(row)}; expected 6 or 7")

    if len(matches) == 1:
        return matches[0], []
    reason = "no supported header signature" if not matches else "ambiguous supported header signatures"
    return None, [f"{reason}: {' | '.join(failures)}"]


def table_candidate_audit(
    table: Any,
    table_index: int,
    page_number: int,
    page_width: float,
    page_height: float,
) -> tuple[list[list[str | None]], dict[str, Any]]:
    """Assess one detected table candidate against Table 3 canonical signatures."""
    data = table.extract()
    row_count = len(data)
    column_count = max((len(r) for r in data), default=0)
    bbox = [round(float(v), 4) for v in table.bbox]
    within_page = (
        bbox[0] >= 0
        and bbox[1] >= 0
        and bbox[2] <= page_width
        and bbox[3] <= page_height
        and bbox[0] < bbox[2]
        and bbox[1] < bbox[3]
    )
    header = data[0] if data else []
    layout_version, header_reasons = classify_table3_header(header)
    reasons: list[str] = list(header_reasons)

    serial_column = 1 if layout_version == LAYOUT_LEGACY_SIX_COLUMN else 0
    project_rows = 0
    if layout_version is not None:
        project_rows = sum(
            bool(r) and len(r) == column_count and normalize_space(r[serial_column]).isdigit()
            for r in data[1:]
        )
        if project_rows == 0:
            reasons.append("no rows with numeric serial in serial column")

    audit = {
        "page_number": page_number,
        "table_index": table_index,
        "row_count": row_count,
        "column_count": column_count,
        "dimensions": f"{row_count}x{column_count}",
        "bbox": bbox,
        "bbox_within_page": within_page,
        "project_row_count": project_rows,
        "layout_version": layout_version,
        "matches_table3_signature": (layout_version is not None and not reasons),
        "reason": "matched canonical Table 3 signature" if not reasons else "; ".join(reasons),
    }
    return data, audit


def select_table3_candidate(
    tables: list[Any],
    page_number: int,
    page_width: float,
    page_height: float,
) -> tuple[list[list[str | None]], int, list[dict[str, Any]]]:
    """Select exactly one canonical Table 3 candidate or fail closed."""
    extracted: list[list[list[str | None]]] = []
    audits: list[dict[str, Any]] = []
    for idx, t in enumerate(tables):
        data, audit = table_candidate_audit(t, idx, page_number, page_width, page_height)
        extracted.append(data)
        audits.append(audit)

    matching = [a["table_index"] for a in audits if a["matches_table3_signature"]]
    if len(matching) != 1:
        raise TableCandidateSelectionError(
            f"Page {page_number}: expected exactly 1 canonical Table 3 candidate; found {len(matching)} among {len(tables)} tables",
            audits,
            extracted,
        )
    return extracted[matching[0]], matching[0], audits


def parse_legacy_composite_cell(text: str) -> tuple[str, str, str, str]:
    """Parse the composite cell from the legacy six-column layout.
    
    Structure:
    Project Name (multiline)
    (Agency Name)
    (Project Code: N######## or 9-digit)
    (State Name)
    """
    lines = [normalize_space(l) for l in text.splitlines() if normalize_space(l)]
    code_matches = [(idx, re.search(r"\((N\d{8}|\d{9})\)", l)) for idx, l in enumerate(lines)]
    code_found = [(idx, m.group(1)) for idx, m in code_matches if m]
    if not code_found:
        raise SchemaChangeDetected(f"Could not locate legacy project code in composite cell: {repr(text)}")
    code_idx, code = code_found[-1]

    # State is after code
    state_lines = lines[code_idx + 1 :]
    state = " ".join(l.strip("()") for l in state_lines)

    # Agency is the line(s) immediately before code
    agency_line = lines[code_idx - 1]
    agency = agency_line.strip("()") if (agency_line.startswith("(") and agency_line.endswith(")")) else agency_line

    # Project name is everything preceding agency
    name = " ".join(lines[: code_idx - 1])
    return name, agency, code, state


def parse_seven_column_composite_cell(text: str) -> tuple[str, str, str]:
    """Parse the composite cell from the seven-column layout.
    
    Structure:
    Project Name (multiline)
    (Agency)
    Project Code (6 digits)
    """
    lines = [normalize_space(l) for l in text.splitlines() if normalize_space(l)]
    if len(lines) < 2:
        raise SchemaChangeDetected(f"Too few lines in 7-column composite cell: {repr(text)}")
    code_match = re.search(r"\b(\d{6})\b", lines[-1])
    if not code_match:
        raise SchemaChangeDetected(f"Could not locate 6-digit project code in line: {repr(lines[-1])}")
    code = code_match.group(1)

    agency_line = lines[-2]
    agency = agency_line.strip("()") if (agency_line.startswith("(") and agency_line.endswith(")")) else agency_line

    name = " ".join(lines[:-2])
    return name, agency, code


def extract_completed_projects_from_pdf(pdf_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Extract all Table 3 Completed Projects from a single Flash Report PDF."""
    records: list[dict[str, Any]] = []
    audits_all: list[dict[str, Any]] = []
    removed_counts = {"repeated_header": 0, "total": 0, "ministry_heading": 0, "sector_heading": 0, "empty_row": 0}

    with pdfplumber.open(pdf_path) as pdf:
        page_texts = [(idx + 1, page.extract_text() or "") for idx, page in enumerate(pdf.pages)]
        table_pages = [pno for pno, txt in page_texts if is_table3_page(txt)]

        if not table_pages:
            # Table 3 completed projects absent (e.g. July 2025, August 2025)
            LOGGER.info("Table 3 Completed Projects absent in %s", pdf_path.name)
            manifest = {
                "source_file": pdf_path.name,
                "table3_present": False,
                "pages_processed": 0,
                "table_pages": [],
                "row_count": 0,
                "layout_version": None,
                "removed_counts": removed_counts,
                "table_audits": [],
            }
            return records, manifest

        month = detect_report_month(dict(page_texts)[table_pages[0]], pdf_path.name)
        LOGGER.info("Processing %s: detected month %s, Table 3 pages %s", pdf_path.name, month, table_pages)

        current_ministry: str | None = None
        current_sector: str | None = None
        detected_layout: str | None = None

        for pno in table_pages:
            page = pdf.pages[pno - 1]
            tables = page.find_tables()
            data, selected_idx, page_audits = select_table3_candidate(
                tables, pno, float(page.width), float(page.height)
            )
            audits_all.extend(page_audits)
            page_layout = page_audits[selected_idx]["layout_version"]
            if detected_layout is None:
                detected_layout = page_layout
            elif detected_layout != page_layout:
                raise SchemaChangeDetected(f"Layout changed across pages in {pdf_path.name}: {detected_layout} -> {page_layout}")

            header_row = data[0]
            table_obj = tables[selected_idx]
            page_headings = _get_page_sector_headings(page, table_obj) if page_layout == LAYOUT_LEGACY_SIX_COLUMN else []

            for r_idx, row in enumerate(data[1:], start=1):
                # Check for repeated header
                if any("sl" in str(c or "").lower() for c in row[:2]) and any("cost" in str(c or "").lower() for c in row[2:]):
                    removed_counts["repeated_header"] += 1
                    continue

                if page_layout == LAYOUT_LEGACY_SIX_COLUMN:
                    c0 = normalize_space(row[0])
                    c1 = normalize_space(row[1])
                    # Check sector band row
                    if c0 and not c1.isdigit() and not any(normalize_space(x) for x in row[2:]):
                        current_sector = c0
                        removed_counts["sector_heading"] += 1
                        continue
                    # Check blank row
                    if not any(normalize_space(x) for x in row):
                        removed_counts["empty_row"] += 1
                        continue
                    if not c1.isdigit():
                        if "total" in " ".join(normalize_space(x) for x in row).lower():
                            removed_counts["total"] += 1
                        else:
                            removed_counts["empty_row"] += 1
                        continue

                    # Canonical project row
                    row_obj = table_obj.rows[r_idx]
                    row_top = min(cell[1] for cell in row_obj.cells if cell is not None)
                    applicable = [h for h in page_headings if h[0] <= row_top + 2]
                    if applicable:
                        current_sector = applicable[-1][1]

                    sector = c0 or current_sector
                    if not sector:
                        raise SchemaChangeDetected(f"Missing sector in legacy row: {row}")
                    name, agency, code, state = parse_legacy_composite_cell(str(row[2] or ""))
                    
                    orig_cost_raw = normalize_space(row[3]) or None
                    orig_doc_raw = normalize_space(row[4]) or None
                    exp_raw = normalize_space(row[5]) or None

                    record = {
                        "project_code": code,
                        "project_name": name,
                        "agency": agency,
                        "ministry": None,
                        "sector": sector,
                        "state": state,
                        "approval_date": None,
                        "start_date": None,
                        "original_completion_date": parse_month_string(orig_doc_raw),
                        "revised_completion_date": None,
                        "actual_completion_date": None,
                        "original_cost": parse_cost_number(orig_cost_raw),
                        "revised_cost": None,
                        "cumulative_expenditure": parse_cost_number(exp_raw),
                        "report_month": month,
                        "approval_date_raw": None,
                        "start_date_raw": None,
                        "original_completion_date_raw": orig_doc_raw,
                        "revised_completion_date_raw": None,
                        "actual_completion_date_raw": None,
                        "original_cost_raw": orig_cost_raw,
                        "revised_cost_raw": None,
                        "cumulative_expenditure_raw": exp_raw,
                        "source_file": pdf_path.name,
                        "source_page": pno,
                        "source_row_number": r_idx,
                        "source_serial_number": int(c1),
                        "extraction_method": EXTRACTION_METHOD,
                    }
                    records.append(record)

                else:  # LAYOUT_SEVEN_COLUMN
                    c0 = normalize_space(row[0])
                    c1 = normalize_space(row[1])

                    # Check band rows
                    if not c0.isdigit():
                        if not any(normalize_space(x) for x in row):
                            removed_counts["empty_row"] += 1
                            continue
                        if "total" in c1.lower():
                            removed_counts["total"] += 1
                            continue
                        if c1.startswith("Ministry of") or c1.startswith("Department of"):
                            current_ministry = c1
                            current_sector = None
                            removed_counts["ministry_heading"] += 1
                            continue
                        if c1:
                            current_sector = c1
                            removed_counts["sector_heading"] += 1
                            continue
                        removed_counts["empty_row"] += 1
                        continue

                    # Canonical project row
                    name, agency, code = parse_seven_column_composite_cell(str(row[1] or ""))
                    state = normalize_space(row[2])

                    # Col 3: Approval / Start date
                    c3 = str(row[3] or "").strip()
                    c3_lines = [l.strip() for l in c3.splitlines() if l.strip()]
                    app_raw = c3_lines[0] if (len(c3_lines) > 1 or (len(c3_lines) == 1 and not c3_lines[0].startswith("("))) else None
                    start_raw = c3_lines[1] if len(c3_lines) > 1 else (c3_lines[0] if (len(c3_lines) == 1 and c3_lines[0].startswith("(")) else None)

                    # Col 4: Actual DoC / Target DoC / Revised DoC
                    c4 = str(row[4] or "").strip()
                    c4_lines = [l.strip() for l in c4.splitlines() if l.strip()]
                    if len(c4_lines) == 3:
                        act_raw = c4_lines[0]
                        orig_doc_raw = c4_lines[1]
                        rev_doc_raw = c4_lines[2]
                    elif len(c4_lines) == 2:
                        act_raw = None
                        orig_doc_raw = c4_lines[0]
                        rev_doc_raw = c4_lines[1]
                    else:
                        act_raw = c4_lines[0] if c4_lines else None
                        orig_doc_raw = rev_doc_raw = None

                    # Col 5: Original Cost / Revised Cost
                    c5 = str(row[5] or "").strip()
                    c5_lines = [l.strip() for l in c5.splitlines() if l.strip()]
                    orig_cost_raw = c5_lines[0] if len(c5_lines) > 0 else None
                    rev_cost_raw = c5_lines[1] if len(c5_lines) > 1 else None

                    # Col 6: Cumulative Expenditure
                    exp_raw = normalize_space(row[6]) or None

                    record = {
                        "project_code": code,
                        "project_name": name,
                        "agency": agency,
                        "ministry": current_ministry,
                        "sector": current_sector,
                        "state": state,
                        "approval_date": parse_month_string(app_raw),
                        "start_date": parse_month_string(start_raw),
                        "original_completion_date": parse_month_string(orig_doc_raw),
                        "revised_completion_date": parse_month_string(rev_doc_raw),
                        "actual_completion_date": parse_month_string(act_raw),
                        "original_cost": parse_cost_number(orig_cost_raw),
                        "revised_cost": parse_cost_number(rev_cost_raw),
                        "cumulative_expenditure": parse_cost_number(exp_raw),
                        "report_month": month,
                        "approval_date_raw": app_raw,
                        "start_date_raw": start_raw,
                        "original_completion_date_raw": orig_doc_raw,
                        "revised_completion_date_raw": rev_doc_raw,
                        "actual_completion_date_raw": act_raw,
                        "original_cost_raw": orig_cost_raw,
                        "revised_cost_raw": rev_cost_raw,
                        "cumulative_expenditure_raw": exp_raw,
                        "source_file": pdf_path.name,
                        "source_page": pno,
                        "source_row_number": r_idx,
                        "source_serial_number": int(c0),
                        "extraction_method": EXTRACTION_METHOD,
                    }
                    records.append(record)

        manifest = {
            "source_file": pdf_path.name,
            "report_month": month,
            "table3_present": True,
            "pages_processed": len(table_pages),
            "table_pages": table_pages,
            "row_count": len(records),
            "layout_version": detected_layout,
            "removed_counts": removed_counts,
            "table_audits": audits_all,
        }
        return records, manifest


def extract_all_completed_projects(
    raw_dir: Path,
    output_csv: Path,
    target_pdfs: list[Path] | None = None,
) -> list[dict[str, Any]]:
    """Extract Completed Projects across Flash Reports and write combined CSV.
    
    If output_csv exists, preserves existing accepted records and additively incorporates
    newly extracted records.
    """
    existing_records: list[dict[str, Any]] = []
    if output_csv.exists():
        with output_csv.open(encoding="utf-8-sig", newline="") as stream:
            existing_records = list(csv.DictReader(stream))

    existing_keys = {(r["project_code"], r["report_month"]) for r in existing_records}

    if target_pdfs is not None:
        pdf_paths = target_pdfs
    else:
        pdf_paths = [
            p for p in sorted(raw_dir.rglob("*.pdf"))
            if "synopsis" not in p.name.lower() and p.name not in (
                "July_Part-I.pdf",
                "May_Part-1.pdf",
                "April_Part-I_Synopsis.pdf",
                "April_Part-II_List_of_tables.pdf",
                "May_Part-2.pdf",
            )
        ]

    new_records: list[dict[str, Any]] = []
    manifests: list[dict[str, Any]] = []

    for pdf_path in pdf_paths:
        records, manifest = extract_completed_projects_from_pdf(pdf_path)
        for rec in records:
            key = (rec["project_code"], rec["report_month"])
            if key not in existing_keys:
                new_records.append(rec)
        manifests.append(manifest)

    # Format new records as strings matching CSV schema representation
    combined_records: list[dict[str, Any]] = list(existing_records)
    for nr in new_records:
        str_rec = {}
        for k in COMPLETED_FIELDS:
            v = nr.get(k)
            str_rec[k] = "" if v is None else str(v)
        combined_records.append(str_rec)

    # Sort deterministically by (report_month, int(source_serial_number))
    combined_records.sort(key=lambda r: (r["report_month"], int(r["source_serial_number"])))

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COMPLETED_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(combined_records)

    LOGGER.info("Wrote %s completed project records to %s (added %s new)", len(combined_records), output_csv, len(new_records))
    return combined_records
