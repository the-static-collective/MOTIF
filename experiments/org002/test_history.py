import copy
import json
import unittest
from pathlib import Path

from history import summarize

DATA = json.loads((Path(__file__).parent / "historical-funding-gaps.json").read_text(encoding="utf-8"))


class HouseHistoryTests(unittest.TestCase):
    def test_entire_house_table_distinguishes_gap_from_shutdown(self):
        result = summarize(copy.deepcopy(DATA))
        self.assertEqual(result["funding_gap_rows"], 23)
        self.assertEqual(result["procedures_followed_yes"], 13)
        self.assertEqual(result["procedures_followed_no"], 10)
        self.assertEqual(result["intent_assessments"], 0)
        self.assertEqual(result["full_rows"], 5)
        self.assertEqual(result["partial_rows"], 18)

    def test_chronology_does_not_establish_intentions(self):
        d = copy.deepcopy(DATA)
        d["cases"][0]["intent"] = "MALICIOUS"
        with self.assertRaisesRegex(ValueError, "intent"):
            summarize(d)

    def test_conflicting_2026_duration_sources_not_hidden(self):
        r = summarize(copy.deepcopy(DATA))
        disagreements = {x["id"]: x for x in r["known_unresolved_count_disagreements"]}
        self.assertEqual(disagreements["2026a"]["house_days"], 43)
        self.assertEqual(disagreements["2026a"]["crs_days"], 42)
        self.assertEqual(disagreements["2026c"]["house_days"], 76)
        self.assertEqual(disagreements["2026c"]["crs_days"], 75)

    def test_ambiguity_cannot_be_erased_by_silent_harmonization(self):
        d = copy.deepcopy(DATA)
        d["cases"][-1]["house_reported_days"] = 75
        with self.assertRaisesRegex(ValueError, "disagreement"):
            summarize(d)


if __name__ == "__main__":
    unittest.main()
