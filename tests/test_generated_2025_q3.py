import csv
import json
import unittest
from pathlib import Path


class Generated2025Q3AcceptanceTests(unittest.TestCase):
    EXPECTED = {
        "2025-07": {"rows": 791, "pages": (37, 66), "warnings": 99, "layout": "table6-eight-column-approval-only-v1"},
        "2025-08": {"rows": 800, "pages": (37, 66), "warnings": 112, "layout": "table6-eight-column-v1"},
        "2025-09": {"rows": 794, "pages": (42, 71), "warnings": 125, "layout": "table6-eight-column-v1"},
    }

    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]

    def _rows(self, month):
        token = month.replace("-", "_")
        with (self.root / "data" / "cleaned" / f"projects_{token}.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            return list(csv.DictReader(stream))

    def test_structural_parse_and_layout_acceptance(self):
        for month, expected in self.EXPECTED.items():
            token = month.replace("-", "_")
            manifest = json.loads(
                (self.root / "data" / "validation" / f"manifest_{token}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["report_month"], month)
            self.assertEqual(manifest["clean_rows"], expected["rows"])
            self.assertEqual((manifest["table6_start_page"], manifest["table6_end_page"]), expected["pages"])
            self.assertEqual(manifest["layout_versions"], [expected["layout"]])
            self.assertEqual(manifest["missing_project_codes"], 0)
            self.assertEqual(manifest["duplicate_project_codes"], 0)
            self.assertEqual(manifest["serial_gaps"], [])
            self.assertEqual(manifest["serial_duplicates"], [])
            self.assertEqual(manifest["rejected_rows"], 0)
            self.assertEqual(manifest["warning_count"], expected["warnings"])
            self.assertTrue(all(item["success_rate"] == 1.0 for item in manifest["numeric_parse"].values()))
            self.assertEqual(manifest["date_parse"]["success_rate"], 1.0)

    def test_manual_samples_and_provenance(self):
        for month, expected in self.EXPECTED.items():
            rows = self._rows(month)
            self.assertEqual([int(row["source_serial_number"]) for row in rows], list(range(1, expected["rows"] + 1)))
            self.assertEqual((rows[0]["project_code"], rows[-1]["project_code"]), ("612786", "613787"))
            self.assertTrue(all(row["source_file"] and row["source_page"] and row["source_pages"] for row in rows))
            self.assertGreaterEqual(sum(left["source_page"] != right["source_page"] for left, right in zip(rows, rows[1:])), 2)
            bharatnet = next(row for row in rows if row["project_code"] == "706775")
            self.assertEqual((bharatnet["original_cost_raw"], bharatnet["revised_cost_raw"]), ("61109", "188000"))
            western = next(row for row in rows if row["project_code"] == "705237")
            self.assertEqual(western["cumulative_expenditure_raw"], "124623")
        july = self._rows("2025-07")
        self.assertTrue(all(row["start_date_raw"] == "" and row["start_date"] == "" for row in july))
        self.assertEqual(july[0]["approval_date_raw"], "01/2024")


if __name__ == "__main__":
    unittest.main()
