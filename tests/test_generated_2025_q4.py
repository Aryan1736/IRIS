import csv
import json
import unittest
from pathlib import Path


class Generated2025Q4AcceptanceTests(unittest.TestCase):
    EXPECTED = {
        "2025-10": {"rows": 820, "pages": (42, 72), "rejected": 3, "warnings": 130},
        "2025-11": {"rows": 823, "pages": (42, 72), "rejected": 1, "warnings": 104},
        "2025-12": {"rows": 1392, "pages": (50, 107), "rejected": 2, "warnings": 406},
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

    def test_structural_and_parse_acceptance(self):
        for month, expected in self.EXPECTED.items():
            token = month.replace("-", "_")
            manifest = json.loads(
                (self.root / "data" / "validation" / f"manifest_{token}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["report_month"], month)
            self.assertEqual(manifest["clean_rows"], expected["rows"])
            self.assertEqual((manifest["table6_start_page"], manifest["table6_end_page"]), expected["pages"])
            self.assertEqual(manifest["missing_project_codes"], 0)
            self.assertEqual(manifest["duplicate_project_codes"], 0)
            self.assertEqual(manifest["serial_gaps"], [])
            self.assertEqual(manifest["serial_duplicates"], [])
            self.assertEqual(manifest["rejected_rows"], expected["rejected"])
            self.assertEqual(manifest["warning_count"], expected["warnings"])
            self.assertTrue(all(item["success_rate"] == 1.0 for item in manifest["numeric_parse"].values()))
            self.assertEqual(manifest["date_parse"]["success_rate"], 1.0)

    def test_boundaries_provenance_multiline_and_paired_values(self):
        for month, expected in self.EXPECTED.items():
            rows = self._rows(month)
            serials = [int(row["source_serial_number"]) for row in rows]
            self.assertEqual(serials, list(range(1, expected["rows"] + 1)))
            self.assertEqual((rows[0]["project_code"], rows[-1]["project_code"]), ("612786", "613787"))
            boundaries = [
                (left, right) for left, right in zip(rows, rows[1:])
                if left["source_page"] != right["source_page"]
            ]
            self.assertGreaterEqual(len(boundaries), 2)
            self.assertTrue(all(row["source_file"] and row["source_page"] and row["source_pages"] for row in rows))
            raw_rows = [
                json.loads(line)
                for line in (self.root / "data" / "extracted" / month / "raw_table6_rows.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            self.assertTrue(any(len(row["cells"][1].splitlines()) >= 5 for row in raw_rows if row["cells"][0].isdigit()))
            revised_cost = next(row for row in rows if row["project_code"] == "706775")
            self.assertEqual((revised_cost["original_cost_raw"], revised_cost["revised_cost_raw"]), ("61109", "188000"))
            missing_revised_date = next(row for row in rows if row["project_code"] == "612183")
            self.assertEqual(missing_revised_date["revised_completion_date_raw"], "")
            self.assertTrue(any("612183" in row["cells"][1] and "(-)" in row["cells"][4] for row in raw_rows))


if __name__ == "__main__":
    unittest.main()
