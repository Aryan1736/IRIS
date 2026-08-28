import csv
import json
import unittest
from collections import Counter
from pathlib import Path


class JuneJulyIdentifierCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        validation = root / "data" / "validation"
        cls.summary = json.loads(
            (validation / "id_crosswalk_summary_june_july_2025.json").read_text(
                encoding="utf-8"
            )
        )
        with (validation / "id_crosswalk_june_july_2025.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.rows = list(csv.DictReader(stream))
        with (validation / "id_crosswalk_ambiguous_june_july_2025.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.ambiguous = list(csv.DictReader(stream))

    def test_source_identifier_inspection(self):
        self.assertEqual(self.summary["explicit_source_crosswalk_matches"], 0)
        raw = self.summary["raw_identifier_inspection"]
        self.assertEqual(
            (raw["2025-06"]["rows_with_old_style_id"], raw["2025-06"]["rows_with_six_digit_id"]),
            (1595, 0),
        )
        self.assertEqual(
            (raw["2025-07"]["rows_with_old_style_id"], raw["2025-07"]["rows_with_six_digit_id"]),
            (0, 791),
        )
        self.assertEqual(raw["2025-06"]["rows_with_both_id_styles"], 0)
        self.assertEqual(raw["2025-07"]["rows_with_both_id_styles"], 0)

    def test_every_june_project_has_one_conservative_outcome(self):
        high = {r["legacy_project_code"] for r in self.rows if r["match_confidence"] == "HIGH_CONFIDENCE"}
        ambiguous = {r["legacy_project_code"] for r in self.rows if r["match_confidence"] == "AMBIGUOUS"}
        unmatched = {r["legacy_project_code"] for r in self.rows if r["match_confidence"] == "UNMATCHED"}
        self.assertEqual((len(high), len(ambiguous), len(unmatched)), (137, 346, 1112))
        self.assertFalse(high & ambiguous)
        self.assertFalse(high & unmatched)
        self.assertFalse(ambiguous & unmatched)
        self.assertEqual(len(high | ambiguous | unmatched), 1595)

    def test_high_confidence_links_are_bijective_and_material_conflict_free(self):
        high = [r for r in self.rows if r["match_confidence"] == "HIGH_CONFIDENCE"]
        self.assertEqual(len(high), 137)
        self.assertEqual(len({r["legacy_project_code"] for r in high}), 137)
        self.assertEqual(len({r["new_project_code"] for r in high}), 137)
        for row in high:
            conflicts = set(filter(None, row["conflicting_fields"].split("|")))
            self.assertFalse(conflicts & {"state", "approval_date", "original_cost"})
            evidence = set(filter(None, row["evidence_fields"].split("|")))
            self.assertTrue("agency" in evidence or "state" in evidence)
            self.assertGreaterEqual(len(evidence - {"project_name_exact", "project_name_near"}), 3)

    def test_ambiguity_and_split_merge_counts(self):
        self.assertEqual(len(self.ambiguous), 408)
        self.assertTrue(all(r["match_confidence"] == "AMBIGUOUS" for r in self.ambiguous))
        self.assertEqual(self.summary["possible_splits_one_legacy_multiple_new"], 41)
        self.assertEqual(self.summary["possible_mergers_multiple_legacy_one_new"], 44)
        self.assertEqual(self.summary["unmatched_july_projects"], 307)

    def test_manually_reviewed_cases_remain_classified_as_expected(self):
        index = {(r["legacy_project_code"], r["new_project_code"]): r for r in self.rows}
        for pair in [
            ("N16000484", "709754"),
            ("N16000535", "709761"),
            ("N16000485", "709766"),
            ("N16000386", "701324"),
        ]:
            self.assertEqual(index[pair]["match_confidence"], "HIGH_CONFIDENCE")
        self.assertEqual(index[("N30000036", "616616")]["match_confidence"], "AMBIGUOUS")

    def test_output_status_counts_are_stable(self):
        self.assertEqual(
            Counter(r["match_confidence"] for r in self.rows),
            Counter({"UNMATCHED": 1112, "AMBIGUOUS": 408, "HIGH_CONFIDENCE": 137}),
        )


if __name__ == "__main__":
    unittest.main()
