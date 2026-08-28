import json
import unittest
from pathlib import Path


class ZeroExpenditureDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        path = root / "data" / "validation" / "diagnostics" / "zero_expenditure_positive_progress_2026_06_07.json"
        cls.data = json.loads(path.read_text(encoding="utf-8"))

    def test_headline_and_cross_month_counts(self):
        self.assertEqual(self.data["flagged_project_months"], 339)
        self.assertEqual(self.data["flagged_by_month"], {"2026-06": 226, "2026-07": 113})
        self.assertEqual(
            self.data["flagged_project_cross_month_presence"],
            {"flagged_in_both_months": 107, "flagged_in_june_only": 119, "flagged_in_july_only": 6},
        )
        transitions = self.data["cross_month_transitions"]
        self.assertEqual(
            transitions["expenditure_transitions"],
            {"positive_to_positive": 1488, "positive_to_zero": 2, "zero_to_positive": 118, "zero_to_zero": 124},
        )
        self.assertEqual(transitions["zero_expenditure_both_months_with_increased_physical_progress"], 45)

    def test_every_reported_increase_case_has_exact_zero_expenditure(self):
        cases = self.data["cross_month_transitions"]["increased_physical_progress_cases"]
        self.assertEqual(len(cases), 45)
        for case in cases:
            self.assertEqual(case["june_expenditure"], 0.0)
            self.assertEqual(case["july_expenditure"], 0.0)
            self.assertGreater(case["july_physical_progress"], case["june_physical_progress"])

    def test_analysis_declares_source_values_unchanged(self):
        self.assertFalse(self.data["definitions"]["source_values_modified"])


if __name__ == "__main__":
    unittest.main()
