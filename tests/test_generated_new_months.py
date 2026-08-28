import csv
import json
import unittest
from pathlib import Path


class GeneratedNewMonthAcceptanceTests(unittest.TestCase):
    EXPECTED = {
        "2026-01": {"rows": 1702, "pages": (62, 133), "rejected": 3, "warnings": 573},
        "2026-02": {"rows": 1948, "pages": (65, 167), "rejected": 2, "warnings": 717},
        "2026-03": {"rows": 1941, "pages": (55, 156), "rejected": 1, "warnings": 711},
    }

    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]

    def test_structural_and_parse_acceptance(self):
        for month, expected in self.EXPECTED.items():
            token = month.replace("-", "_")
            manifest = json.loads(
                (self.root / "data" / "validation" / f"manifest_{token}.json").read_text(encoding="utf-8")
            )
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

    def test_boundaries_first_last_multiline_and_pairs(self):
        for month, expected in self.EXPECTED.items():
            token = month.replace("-", "_")
            with (self.root / "data" / "cleaned" / f"projects_{token}.csv").open(
                encoding="utf-8-sig", newline=""
            ) as stream:
                rows = list(csv.DictReader(stream))
            serials = [int(row["source_serial_number"]) for row in rows]
            self.assertEqual(serials, list(range(1, expected["rows"] + 1)))
            self.assertEqual((rows[0]["project_code"], rows[-1]["project_code"]), ("612786", "613787"))
            boundaries = [(left, right) for left, right in zip(rows, rows[1:]) if left["source_page"] != right["source_page"]]
            self.assertGreaterEqual(len(boundaries), 2)
            raw_rows = [
                json.loads(line)
                for line in (self.root / "data" / "extracted" / month / "raw_table6_rows.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            self.assertTrue(any(len(row["cells"][1].splitlines()) >= 5 for row in raw_rows if row["cells"][0].isdigit()))
            self.assertTrue(all(row["original_cost_raw"] and row["revised_cost_raw"] for row in rows))


if __name__ == "__main__":
    unittest.main()
