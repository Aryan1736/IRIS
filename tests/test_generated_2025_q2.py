import csv
import json
import unittest
from pathlib import Path


class Generated2025Q2AcceptanceTests(unittest.TestCase):
    EXPECTED = {
        "2025-04": {"rows": 1670, "pages": (43, 268), "warnings": 253},
        "2025-05": {"rows": 1637, "pages": (43, 207), "warnings": 242},
        "2025-06": {"rows": 1595, "pages": (41, 229), "warnings": 228},
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
            self.assertEqual(manifest["clean_rows"], expected["rows"])
            self.assertEqual((manifest["table6_start_page"], manifest["table6_end_page"]), expected["pages"])
            self.assertEqual(manifest["layout_versions"], ["legacy-all-ongoing-nine-column-v1"])
            self.assertEqual(manifest["missing_project_codes"], 0)
            self.assertEqual(manifest["duplicate_project_codes"], 0)
            self.assertEqual(manifest["serial_gaps"], [])
            self.assertEqual(manifest["serial_duplicates"], [])
            self.assertEqual(manifest["rejected_rows"], 0)
            self.assertEqual(manifest["warning_count"], expected["warnings"])
            self.assertTrue(all(item["success_rate"] == 1.0 for item in manifest["numeric_parse"].values()))
            self.assertEqual(manifest["date_parse"]["success_rate"], 1.0)

    def test_source_boundaries_missing_values_and_nested_agency(self):
        expected_last = {"2025-04": "1670", "2025-05": "1637", "2025-06": "1595"}
        for month in self.EXPECTED:
            rows = self._rows(month)
            self.assertEqual(rows[0]["project_code"], "N04000073")
            self.assertEqual(rows[-1]["project_code"], "N30000042")
            self.assertEqual(rows[-1]["source_serial_number"], expected_last[month])
            self.assertTrue(all(not row["start_date"] and not row["start_date_raw"] for row in rows))
            self.assertTrue(all(not row["ministry"] for row in rows))
            self.assertGreaterEqual(
                sum(left["source_page"] != right["source_page"] for left, right in zip(rows, rows[1:])), 2
            )
            nested = next(row for row in rows if row["project_code"] == "N16000513")
            self.assertEqual(nested["agency"], "HPCLRRL(JV)")
            no_revision = next(row for row in rows if row["project_code"] == "N22000584")
            self.assertEqual(no_revision["revised_cost_raw"], "")
            self.assertEqual(no_revision["revised_cost"], "")


if __name__ == "__main__":
    unittest.main()
