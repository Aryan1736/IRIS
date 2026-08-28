import csv
import unittest
from pathlib import Path


class ManualFixtureRegressionTests(unittest.TestCase):
    def test_manually_verified_rows_match_generated_monthly_csvs(self):
        root = Path(__file__).resolve().parents[1]
        fixture_path = root / "tests" / "fixtures" / "manual_verified_records.csv"
        with fixture_path.open(encoding="utf-8-sig", newline="") as stream:
            fixtures = list(csv.DictReader(stream))

        monthly = {}
        for month in {row["report_month"] for row in fixtures}:
            path = root / "data" / "cleaned" / f"projects_{month.replace('-', '_')}.csv"
            self.assertTrue(path.exists(), f"Run the extraction pipeline first: missing {path}")
            with path.open(encoding="utf-8-sig", newline="") as stream:
                monthly[month] = {row["project_code"]: row for row in csv.DictReader(stream)}

        ignored = {"verification_case"}
        for expected in fixtures:
            actual = monthly[expected["report_month"]][expected["project_code"]]
            for field, value in expected.items():
                if field not in ignored:
                    self.assertEqual(actual[field], value, f"{expected['report_month']} {expected['project_code']} {field}")


if __name__ == "__main__":
    unittest.main()

