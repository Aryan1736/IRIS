"""Regression and unit tests for Table 3: Completed Projects extraction."""

import csv
from pathlib import Path
import unittest

from src.extraction.completed_projects import (
    COMPLETED_FIELDS,
    LAYOUT_LEGACY_SIX_COLUMN,
    LAYOUT_SEVEN_COLUMN,
    SchemaChangeDetected,
    TableCandidateSelectionError,
    classify_table3_header,
    detect_report_month,
    extract_completed_projects_from_pdf,
    is_table3_page,
    parse_cost_number,
    parse_legacy_composite_cell,
    parse_month_string,
    parse_seven_column_composite_cell,
)
from src.validation.completed_projects import (
    EXPECTED_MONTHLY_ROW_COUNTS,
    validate_completed_csv,
    validate_completed_records,
)


class CompletedProjectsTests(unittest.TestCase):
    """Test suite for Table 3 extraction, parsing, and validation."""

    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.raw_dir = cls.root / "data" / "raw"
        cls.output_csv = cls.root / "data" / "processed" / "projects_completed.csv"

    def test_semantic_page_detection(self):
        """Verify semantic identification of Table 3 Completed Projects pages and rejection of others."""
        # Legacy completed page
        legacy_txt = "MOSPI_ (April 2025) _FR_ Central Sector Projects cost Rs. 150Cr and above Table:-3. Project List: Completed during April 2025"
        self.assertTrue(is_table3_page(legacy_txt))

        # 7-column completed page
        seven_txt = "Completed Projects During Month SEPTEMBER 2025 Actual Date of Completion"
        self.assertTrue(is_table3_page(seven_txt))

        # North-Eastern ongoing table (July/August 2025 Table 3) must be rejected
        ne_txt = "Table 3: Ongoing Projects North Eastern Region"
        self.assertFalse(is_table3_page(ne_txt))

        ne_txt2 = "Ongoing Projects of North-East Region"
        self.assertFalse(is_table3_page(ne_txt2))

        # General ongoing project table must be rejected
        ongoing_txt = "All Ongoing Projects as of September 2025"
        self.assertFalse(is_table3_page(ongoing_txt))

    def test_header_classification(self):
        """Test positional header matching against verified signatures and rejection of invalid headers."""
        legacy_hdr = [
            "Sector",
            "Sl. No.",
            "Project Name\n(Agency Name)\n(Project Code)\n(State Name)",
            "Original\nCost\nin Rs. Crore",
            "Date of Commissioning\nOriginal\n(MM/YYYY)",
            "Cumulative\nExpenditure\nin Rs. Crore",
        ]
        layout, failures = classify_table3_header(legacy_hdr)
        self.assertEqual(layout, LAYOUT_LEGACY_SIX_COLUMN)
        self.assertEqual(failures, [])

        seven_hdr = [
            "Sl.No",
            "Project Name (Agency) (Project Code)",
            "State",
            "Date of Approval\n(Start Date)\nMM/YYYY",
            "Actual Date of Completion\n(Orignal/Target DoC)\n(Revised DoC)\nMM/YYYY",
            "Orignal Cost\nRevised Cost\nin Rs. Crore",
            "Cumulative\nExpenditure\nin Rs. Crore",
        ]
        layout, failures = classify_table3_header(seven_hdr)
        self.assertEqual(layout, LAYOUT_SEVEN_COLUMN)
        self.assertEqual(failures, [])

        jun2026_hdr = [
            "Sl.No",
            "Project Name (Agency) (Project Code)",
            "State",
            "Date of Approval\n(Start Date)\nMM/YYYY",
            "(Orignal/Target DoC)\n(Revised DoC)\nMM/YYYY",
            "Orignal Cost\nRevised Cost\nin Rs. Crore",
            "Cumulative\nExpenditure\nin Rs. Crore",
        ]
        layout, failures = classify_table3_header(jun2026_hdr)
        self.assertEqual(layout, LAYOUT_SEVEN_COLUMN)
        self.assertEqual(failures, [])

        # Unsupported 5-column header
        bad_hdr = ["Sl.No", "Project", "Cost", "Exp", "Progress"]
        layout, failures = classify_table3_header(bad_hdr)
        self.assertIsNone(layout)
        self.assertTrue(any("unsupported column count" in f for f in failures))

    def test_legacy_composite_cell_parsing(self):
        """Test parsing of legacy 4-element composite cells."""
        cell = (
            "UPGRADATION OF PASSENGER TERMINAL BUILDING\n"
            "AND AIRSIDE FACILITIES AT TIRUCHIRAPALLI\n"
            "INTERNATIONAL AI\n"
            "(AAI)\n"
            "(N04000075)\n"
            "(TAMIL NADU)"
        )
        name, agency, code, state = parse_legacy_composite_cell(cell)
        self.assertEqual(code, "N04000075")
        self.assertEqual(agency, "AAI")
        self.assertEqual(state, "TAMIL NADU")
        self.assertEqual(
            name,
            "UPGRADATION OF PASSENGER TERMINAL BUILDING AND AIRSIDE FACILITIES AT TIRUCHIRAPALLI INTERNATIONAL AI",
        )

        # 9-digit numeric legacy code
        cell9 = "PROJECT FOO BAR\n(NHAI)\n(123456789)\n(KARNATAKA)"
        name9, agency9, code9, state9 = parse_legacy_composite_cell(cell9)
        self.assertEqual(code9, "123456789")
        self.assertEqual(agency9, "NHAI")
        self.assertEqual(state9, "KARNATAKA")

        # Missing code must fail closed
        with self.assertRaises(SchemaChangeDetected):
            parse_legacy_composite_cell("PROJECT WITHOUT CODE\n(NHAI)\n(KERALA)")

    def test_seven_column_composite_cell_parsing(self):
        """Test parsing of seven-column 3-element composite cells."""
        cell = (
            "IoE Projects [Civil Works], IIT Kharagpur\n"
            "(Indian Institute of Technology, Kharagpur)\n"
            "609041"
        )
        name, agency, code = parse_seven_column_composite_cell(cell)
        self.assertEqual(code, "609041")
        self.assertEqual(agency, "Indian Institute of Technology, Kharagpur")
        self.assertEqual(name, "IoE Projects [Civil Works], IIT Kharagpur")

        # Agency with brackets inside parens
        cell_bracket = (
            "Goa Airport Terminal Building Extension Project\n"
            "(Airport Authority of India [AAI])\n"
            "701105"
        )
        name_b, agency_b, code_b = parse_seven_column_composite_cell(cell_bracket)
        self.assertEqual(code_b, "701105")
        self.assertEqual(agency_b, "Airport Authority of India [AAI]")
        self.assertEqual(name_b, "Goa Airport Terminal Building Extension Project")

        # Missing 6-digit code must fail closed
        with self.assertRaises(SchemaChangeDetected):
            parse_seven_column_composite_cell("PROJECT WITHOUT CODE\n(AAI)")

    def test_date_and_cost_parsing(self):
        """Test date and cost parsing helpers."""
        self.assertEqual(parse_month_string("08/2025"), "2025-08")
        self.assertEqual(parse_month_string("(03/2023)"), "2023-03")
        self.assertIsNone(parse_month_string("N.A."))
        self.assertIsNone(parse_month_string("(-)"))
        self.assertIsNone(parse_month_string(""))

        self.assertEqual(parse_cost_number("287.2"), 287.2)
        self.assertEqual(parse_cost_number("1,084.94"), 1084.94)
        self.assertEqual(parse_cost_number("(2465.68)"), 2465.68)
        self.assertIsNone(parse_cost_number("(-)"))
        self.assertIsNone(parse_cost_number("-"))

    def test_absence_handling_july_and_august_2025(self):
        """Verify July and August 2025 cleanly report absence of Table 3 Completed Projects."""
        for m, pdf_name in [("2025-07", "FlashReport_July_2025.pdf"), ("2025-08", "FlashReport_August_2025.pdf")]:
            pdf_path = self.raw_dir / "2025" / pdf_name
            if pdf_path.exists():
                records, manifest = extract_completed_projects_from_pdf(pdf_path)
                self.assertEqual(len(records), 0)
                self.assertFalse(manifest["table3_present"])
                self.assertEqual(manifest["row_count"], 0)

    def test_output_dataset_integrity(self):
        """Verify generated projects_completed.csv passes all structural and quality checks."""
        self.assertTrue(self.output_csv.exists(), f"Missing {self.output_csv}")
        summary = validate_completed_csv(self.output_csv)

        # Total records must match 617 exactly (375 baseline + 242 historical)
        self.assertEqual(summary["total_records"], 617)
        self.assertEqual(summary["unique_projects"], 617)
        self.assertEqual(summary["missing_project_codes"], 0)
        self.assertEqual(summary["duplicate_keys"], 0)
        self.assertTrue(summary["serial_continuity_all_months"])
        self.assertEqual(summary["warnings_count"], 0)

        # Monthly row counts must match expected counts exactly
        for month, expected_count in EXPECTED_MONTHLY_ROW_COUNTS.items():
            if expected_count > 0:
                self.assertEqual(summary["rows_by_month"].get(month), expected_count, f"Mismatch in {month}")

        # Check schema header matches COMPLETED_FIELDS
        with self.output_csv.open(encoding="utf-8-sig", newline="") as stream:
            header = next(csv.reader(stream))
        self.assertEqual(header, COMPLETED_FIELDS)

    def test_historical_legacy_extraction(self):
        """Test extraction of historical legacy reports with sector margin headings and NER project names."""
        july_pdf = self.raw_dir / "2024" / "July_Part-II.pdf"
        if july_pdf.exists():
            records, manifest = extract_completed_projects_from_pdf(july_pdf)
            self.assertEqual(len(records), 21)
            self.assertEqual(manifest["layout_version"], LAYOUT_LEGACY_SIX_COLUMN)
            self.assertEqual(records[0]["sector"], "POWER")
            self.assertEqual(records[13]["sector"], "ROAD TRANSPORT AND HIGHWAYS")
            self.assertEqual(records[20]["sector"], "STEEL")

        dec_pdf = self.raw_dir / "2024" / "December.pdf"
        if dec_pdf.exists():
            records, manifest = extract_completed_projects_from_pdf(dec_pdf)
            self.assertEqual(len(records), 22)
            self.assertEqual(manifest["layout_version"], LAYOUT_LEGACY_SIX_COLUMN)
            self.assertEqual(records[6]["project_code"], "N18000316")
            self.assertIn("NORTH EASTERN REGION", records[6]["project_name"])


if __name__ == "__main__":
    unittest.main()
