import csv
import json
import unittest
from pathlib import Path


class Generated2025Q1AcceptanceTests(unittest.TestCase):
    EXPECTED = {
        "2025-01": {"rows": 1719, "pages": (42, 239), "warnings": 228, "last": "N30000049"},
        "2025-02": {"rows": 1682, "pages": (42, 246), "warnings": 210, "last": "N30000042"},
        "2025-03": {"rows": 1677, "pages": (40, 239), "warnings": 222, "last": "N30000042"},
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
            self.assertEqual(manifest["layout_versions"], ["legacy-all-ongoing-nine-column-v1"])
            self.assertEqual(manifest["missing_project_codes"], 0)
            self.assertEqual(manifest["duplicate_project_codes"], 0)
            self.assertEqual(manifest["serial_gaps"], [])
            self.assertEqual(manifest["serial_duplicates"], [])
            self.assertEqual(manifest["rejected_rows"], 0)
            self.assertEqual(manifest["warning_count"], expected["warnings"])
            self.assertTrue(all(item["success_rate"] == 1.0 for item in manifest["numeric_parse"].values()))
            self.assertEqual(manifest["date_parse"]["success_rate"], 1.0)

    def test_manually_checked_boundaries_and_source_values(self):
        expected_boundaries = {
            "2025-01": (("52", "93"), ("53", "94")),
            "2025-02": (("52", "89"), ("53", "90")),
            "2025-03": (("50", "90"), ("51", "91")),
        }
        for month, expected in self.EXPECTED.items():
            rows = self._rows(month)
            self.assertEqual(rows[0]["source_serial_number"], "1")
            self.assertEqual(rows[0]["project_code"], "N04000073")
            self.assertEqual(rows[-1]["source_serial_number"], str(expected["rows"]))
            self.assertEqual(rows[-1]["project_code"], expected["last"])
            self.assertTrue(all(not row["start_date"] and not row["start_date_raw"] for row in rows))
            self.assertTrue(all(not row["ministry"] for row in rows))
            self.assertGreaterEqual(
                sum(left["source_page"] != right["source_page"] for left, right in zip(rows, rows[1:])), 2
            )
            left, right = expected_boundaries[month]
            self.assertTrue(any((row["source_page"], row["source_serial_number"]) == left for row in rows))
            self.assertTrue(any((row["source_page"], row["source_serial_number"]) == right for row in rows))

            high_speed = next(row for row in rows if row["project_code"] == "N22000463")
            self.assertEqual(high_speed["original_cost_raw"], "108,000.00")
            self.assertEqual(high_speed["original_cost"], "108000.0")

            no_revision = next(row for row in rows if row["project_code"] == "N22000584")
            self.assertEqual(no_revision["revised_cost_raw"], "")
            self.assertEqual(no_revision["revised_cost"], "")

    def test_character_spaced_date_text_is_parsed_without_changing_raw_value(self):
        january = self._rows("2025-01")
        march = self._rows("2025-03")
        january_first = january[0]
        march_first = march[0]
        self.assertEqual(january_first["revised_completion_date_raw"], "May-23")
        self.assertEqual(january_first["revised_completion_date"], "2023-05")
        self.assertEqual(march_first["revised_completion_date_raw"], "Jun-23")
        self.assertEqual(march_first["revised_completion_date"], "2023-06")

    def test_nineteen_month_combined_summary_and_new_transitions(self):
        summary = json.loads(
            (
                self.root
                / "data"
                / "validation"
                / "longitudinal_summary_2025_01_2026_07.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(summary["rows"], 28581)
        self.assertEqual(summary["unique_projects"], 4029)
        self.assertEqual(summary["duplicate_project_month_keys"], 0)
        self.assertEqual(summary["projects_with_at_least_3_observations"], 3830)
        self.assertEqual(summary["projects_with_at_least_6_observations"], 3444)
        self.assertEqual(summary["projects_with_at_least_12_observations"], 629)
        self.assertEqual(summary["projects_with_at_least_19_observations"], 0)
        transitions = {
            f"{item['earlier_month']}->{item['later_month']}": item
            for item in summary["adjacent_month_transitions"]
        }
        self.assertEqual(transitions["2025-01->2025-02"]["projects_in_both"], 1673)
        self.assertEqual(transitions["2025-02->2025-03"]["projects_in_both"], 1665)
        self.assertEqual(transitions["2025-03->2025-04"]["projects_in_both"], 1643)


if __name__ == "__main__":
    unittest.main()
