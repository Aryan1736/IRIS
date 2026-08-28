import unittest
from pathlib import Path

import pdfplumber

from src.extraction.pipeline import (
    TableCandidateSelectionError,
    _locate_table6_candidate,
    _select_table6_candidate,
)


class FakeTable:
    def __init__(self, rows, bbox=(10, 10, 500, 700)):
        self._rows = rows
        self.bbox = bbox

    def extract(self):
        return self._rows


CANONICAL_HEADER = [
    "Sl.No",
    "Project Name (Agency) (Project Code)",
    "State",
    "Date of Approval (Start Date) MM/YYYY",
    "Original/Target DoC (Revised DoC) MM/YYYY",
    "Original Cost Revised Cost in Rs. Crore",
    "Cumulative Expenditure in Rs. Crore",
    "Physical Progress (%)",
]
CANONICAL_ROW = ["1", "Example (Agency) (612786)", "State", "01/2020", "01/2025", "1", "1", "1"]


class TableSelectionRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]

    def _assert_pdf_page_selects_one(self, relative_path: str, page_number: int, expected_detected: int):
        with pdfplumber.open(self.root / relative_path) as pdf:
            page = pdf.pages[page_number - 1]
            selected, _, _, audits, _ = _locate_table6_candidate(page, page_number)
        self.assertEqual(sum(audit["detection_pass"] == "full_page" for audit in audits), expected_detected)
        self.assertEqual(sum(audit["matches_table6_signature"] for audit in audits), 1)
        self.assertEqual(len(selected[0]), 8)
        self.assertIn("Project Name", selected[0][1])
        self.assertTrue(any(row[0] and row[0].isdigit() for row in selected[1:]))
        return audits

    def test_january_first_table6_page_ignores_enclosing_table(self):
        audits = self._assert_pdf_page_selects_one("data/raw/FlashReport_January_2026.pdf", 62, 2)
        ignored = [audit for audit in audits if not audit["matches_table6_signature"]]
        self.assertEqual(len(ignored), 1)
        self.assertEqual(ignored[0]["column_count"], 2)
        self.assertFalse(ignored[0]["bbox_within_page"])
        self.assertIn("expected 8 columns", ignored[0]["reason"])

    def test_february_first_table6_page_ignores_enclosing_table(self):
        self._assert_pdf_page_selects_one("data/raw/FlashReport_February_2026.pdf", 65, 2)

    def test_march_first_table6_page_ignores_enclosing_table(self):
        self._assert_pdf_page_selects_one("data/raw/FlashReport_March_2026.pdf", 55, 2)

    def test_april_normal_table6_page_selects_canonical_table(self):
        audits = self._assert_pdf_page_selects_one("data/raw/FlashReport_April2026.pdf", 55, 1)
        self.assertTrue(audits[0]["bbox_within_page"])

    def test_july_2025_approval_only_layout_selects_semantically(self):
        audits = self._assert_pdf_page_selects_one("data/raw/2025/FlashReport_July_2025.pdf", 37, 2)
        matching = [audit for audit in audits if audit["matches_table6_signature"]]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["layout_version"], "table6-eight-column-approval-only-v1")

    def test_legacy_april_to_june_pages_select_nine_column_layout(self):
        cases = (
            ("data/raw/2025/FR_April_2025.pdf", 43),
            ("data/raw/2025/FR_May2025.pdf", 43),
            ("data/raw/2025/FR_JUNE_2025.pdf", 41),
        )
        for path, page_number in cases:
            with self.subTest(path=path):
                with pdfplumber.open(self.root / path) as pdf:
                    selected, _, _, audits, _ = _locate_table6_candidate(pdf.pages[page_number - 1], page_number)
                matching = [audit for audit in audits if audit["matches_table6_signature"]]
                self.assertEqual(len(matching), 1)
                self.assertEqual(matching[0]["layout_version"], "legacy-all-ongoing-nine-column-v1")
                self.assertEqual(len(selected[0]), 9)
                self.assertTrue(any(row[2] and row[2].isdigit() for row in selected[1:]))

    def test_page_frame_exclusion_recovers_merged_grid_pages(self):
        cases = (
            ("data/raw/FlashReport_January_2026.pdf", 76),
            ("data/raw/FlashReport_February_2026.pdf", 79),
            ("data/raw/FlashReport_March_2026.pdf", 70),
        )
        for path, page_number in cases:
            with self.subTest(path=path, page_number=page_number):
                audits = self._assert_pdf_page_selects_one(path, page_number, 1)
                matching = [audit for audit in audits if audit["matches_table6_signature"]]
                self.assertEqual(matching[0]["detection_pass"], "page_frame_excluded")
                self.assertTrue(any(audit["column_count"] == 10 for audit in audits if not audit["matches_table6_signature"]))

    def test_zero_matching_candidates_fails_closed(self):
        table = FakeTable([["not", "a project table"], ["", ""]])
        with self.assertRaisesRegex(TableCandidateSelectionError, "found 0"):
            _select_table6_candidate([table], 1, 600, 800)

    def test_multiple_matching_candidates_fails_closed(self):
        left = FakeTable([CANONICAL_HEADER, CANONICAL_ROW])
        right = FakeTable([CANONICAL_HEADER, CANONICAL_ROW], bbox=(20, 20, 510, 710))
        with self.assertRaisesRegex(TableCandidateSelectionError, "found 2"):
            _select_table6_candidate([left, right], 1, 600, 800)

    def test_eight_columns_without_semantic_signature_is_rejected(self):
        wrong = FakeTable([["x"] * 8, ["1"] + ["value"] * 7])
        with self.assertRaisesRegex(TableCandidateSelectionError, "found 0"):
            _select_table6_candidate([wrong], 1, 600, 800)


if __name__ == "__main__":
    unittest.main()
