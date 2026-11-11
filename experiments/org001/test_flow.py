import copy
import json
import unittest
from pathlib import Path
from flow import analyze

FIXTURE = json.loads((Path(__file__).parent / "example.json").read_text(encoding="utf-8"))


class OrganizationFlowTests(unittest.TestCase):
    def test_critical_path_and_leverage(self):
        r = analyze(copy.deepcopy(FIXTURE))
        self.assertEqual(r["model"]["baseline"]["forecast_days"], 9)
        p = {x["id"]: x for x in r["conditional_proposals"]}
        self.assertEqual(p["ask_budget_for_specific_yes_no"]["modeled_days_saved"], 4)
        self.assertEqual(p["recruit_extra_volunteers"]["modeled_days_saved"], 0)
        self.assertEqual(p["coupled_budget_food_and_volunteers"]["modeled_days_saved"], 5)
        self.assertEqual(p["expedite_safeguarding_without_bypass"]["modeled_days_saved"], 0)
        self.assertEqual(p["ask_budget_for_specific_yes_no"]["status"], "HOLD_FOR_HUMAN_AUTHORITY")
        self.assertTrue(r["receipts"]["no_external_actions"])

    def test_crossings_are_held_and_private(self):
        r = analyze(copy.deepcopy(FIXTURE))
        self.assertTrue(all(x["state"] == "HOLD" and x["scope"] == "LOCAL_REVIEW_ONLY" for x in r["local_handoff_drafts"]))

    def test_no_gate_bypass(self):
        b = copy.deepcopy(FIXTURE)
        b["interventions"][0]["changes"] = [{"step_id": "safeguarding", "new_remaining_days": 0}]
        with self.assertRaisesRegex(ValueError, "non-negotiable gate"):
            analyze(b)

    def test_cycle_rejected(self):
        b = copy.deepcopy(FIXTURE)
        b["steps"][0]["depends_on"] = ["meal_served"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            analyze(b)

    def test_missing_evidence_and_aging_do_not_become_fact(self):
        b = copy.deepcopy(FIXTURE)
        b["steps"][0]["evidence_refs"] = []
        b["steps"][1]["last_verified"] = "2026-10-01"
        issues = analyze(b)["verification_gaps"]
        self.assertTrue(any("no evidence" in s for s in issues))
        self.assertTrue(any("recheck" in s for s in issues))

    def test_unknown_dependency_rejected(self):
        b = copy.deepcopy(FIXTURE)
        b["steps"][1]["depends_on"] = ["imaginary"]
        with self.assertRaisesRegex(ValueError, "unknown dependency"):
            analyze(b)

    def test_false_nonfinite_and_done_rewrite_rejected(self):
        b = copy.deepcopy(FIXTURE)
        b["steps"][1]["remaining_days"] = float("nan")
        with self.assertRaises(ValueError):
            analyze(b)
        b = copy.deepcopy(FIXTURE)
        b["interventions"][0]["changes"] = [{"step_id": "space", "new_remaining_days": 1}]
        with self.assertRaises(ValueError):
            analyze(b)


if __name__ == "__main__":
    unittest.main()
