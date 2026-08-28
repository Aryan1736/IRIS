import csv
import json
import unittest
from pathlib import Path


class Generated2024Q4AcceptanceTests(unittest.TestCase):
    EXPECTED = {
        "2024-10": {
            "rows": 1747,
            "pages": (51, 273),
            "warnings": 343,
            "layout": "legacy-all-ongoing-nine-column-v1",
            "last": "N30000049",
        },
        "2024-11": {
            "rows": 1742,
            "pages": (46, 277),
            "warnings": 342,
            "layout": "legacy-all-ongoing-nine-column-progress-only-v1",
            "last": "N30000049",
        },
        "2024-12": {
            "rows": 1724,
            "pages": (44, 214),
            "warnings": 327,
            "layout": "legacy-all-ongoing-nine-column-v1",
            "last": "N30000049",
        },
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

    def test_manually_checked_boundaries_and_source_values(self):
        boundaries = {
            "2024-10": (("51", "7"), ("52", "8"), ("162", "894"), ("163", "895")),
            "2024-11": (("46", "7"), ("47", "8"), ("162", "890"), ("163", "891")),
            "2024-12": (("44", "11"), ("45", "12"), ("129", "884"), ("130", "885")),
        }
        for month, expected in self.EXPECTED.items():
            rows = self._rows(month)
            self.assertEqual(rows[0]["source_serial_number"], "1")
            self.assertEqual(rows[0]["project_code"], "N04000073")
            self.assertEqual(rows[-1]["source_serial_number"], str(expected["rows"]))
            self.assertEqual(rows[-1]["project_code"], expected["last"])
            observed = {(row["source_page"], row["source_serial_number"]) for row in rows}
            self.assertTrue(set(boundaries[month]) <= observed)

            first = rows[0]
            self.assertEqual(first["original_cost_raw"], "417.23")
            self.assertEqual(first["revised_cost_raw"], "707.73")
            self.assertEqual(first["revised_completion_date_raw"], "May-23")

            missing_revision = next(row for row in rows if row["project_code"] == "N22000584")
            self.assertEqual(missing_revision["revised_cost_raw"], "")
            self.assertEqual(missing_revision["revised_completion_date_raw"], "")

            high_speed = next(row for row in rows if row["project_code"] == "N22000463")
            self.assertEqual(high_speed["original_cost_raw"], "108,000.00")
            self.assertEqual(high_speed["original_cost"], "108000.0")

    def test_raw_intermediate_and_clean_provenance_files_exist(self):
        for month in self.EXPECTED:
            token = month.replace("-", "_")
            extracted = self.root / "data" / "extracted" / month
            self.assertTrue((extracted / "raw_table6_pages.jsonl").exists())
            self.assertTrue((extracted / "raw_table6_rows.jsonl").exists())
            rows = self._rows(month)
            self.assertTrue(all(row["source_file"] and row["source_page"] for row in rows))

    def test_twenty_two_month_combined_summary_and_new_transitions(self):
        summary = json.loads(
            (self.root / "data" / "validation" / "longitudinal_summary_2024_10_2026_07.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(summary["rows"], 33794)
        self.assertEqual(summary["unique_projects"], 4104)
        self.assertEqual(summary["duplicate_project_month_keys"], 0)
        self.assertEqual(summary["projects_with_at_least_3_observations"], 3914)
        self.assertEqual(summary["projects_with_at_least_6_observations"], 3574)
        self.assertEqual(summary["projects_with_at_least_12_observations"], 629)
        self.assertEqual(summary["projects_with_at_least_18_observations"], 0)
        transitions = {
            f"{item['earlier_month']}->{item['later_month']}": item
            for item in summary["adjacent_month_transitions"]
        }
        self.assertEqual(transitions["2024-10->2024-11"]["projects_in_both"], 1727)
        self.assertEqual(transitions["2024-11->2024-12"]["projects_in_both"], 1709)
        self.assertEqual(transitions["2024-12->2025-01"]["projects_in_both"], 1702)


if __name__ == "__main__":
    unittest.main()
