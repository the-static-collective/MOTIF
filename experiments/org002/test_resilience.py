import copy
import json
import unittest
from pathlib import Path

from resilience import analyze

CASE = json.loads((Path(__file__).parent / "fictional-case.json").read_text(encoding="utf-8"))


class InstitutionalResilienceTests(unittest.TestCase):
    def test_outcome_not_activity_and_conditional_routes(self):
        r = analyze(copy.deepcopy(CASE))
        self.assertEqual(r["baseline_forecast_days"], 9)
        scenarios = {s["shock_id"]: s for s in r["shock_scenarios"]}
        funding = scenarios["funding_window_pause"]
        self.assertEqual(funding["disrupted_forecast_days"], 30)
        routes = {x["id"]: x for x in funding["alternative_routes"]}
        self.assertEqual(routes["independently_donated_meal"]["route_forecast_days"], 5)
        self.assertEqual(routes["independently_donated_meal"]["conditional_days_difference"], 25)
        self.assertEqual(routes["independently_donated_meal"]["disposition"], "HOLD_FOR_SCOPE_AUTHORITY_AND_EVIDENCE")
        self.assertEqual(routes["dependent_grant_renamed_local"]["comparison"], "INDEPENDENCE_UNVERIFIED")
        self.assertIsNone(routes["dependent_grant_renamed_local"]["conditional_days_difference"])
        self.assertEqual(routes["give_information_not_food"]["comparison"], "NOT_COMPARABLE_DIFFERENT_BENEFIT")

    def test_bottleneck_moves_when_capacity_is_disrupted(self):
        scenarios = {s["shock_id"]: s for s in analyze(copy.deepcopy(CASE))["shock_scenarios"]}
        self.assertEqual(scenarios["voluntary_capacity_gap"]["disrupted_forecast_days"], 13)
        self.assertEqual(scenarios["declared_condition_on_approval"]["disrupted_forecast_days"], 19)

    def test_never_label_intent_without_source(self):
        b = copy.deepcopy(CASE)
        b["events"][0]["intent_evidence"] = "documented_public_position"
        with self.assertRaisesRegex(ValueError, "source"):
            analyze(b)
        b["events"][0]["sources"] = ["synthetic:invented"]
        self.assertTrue(analyze(b)["shock_scenarios"][0]["not_a_motive_verdict"])

    def test_rejects_hypothesized_malice_class(self):
        b = copy.deepcopy(CASE)
        b["events"][0]["intent_evidence"] = "deliberate_harm"
        with self.assertRaisesRegex(ValueError, "motive-evidence"):
            analyze(b)

    def test_no_legal_gate_bypass_even_in_alt_route(self):
        b = copy.deepcopy(CASE)
        b["alternatives"][0]["workflow"]["steps"][3]["non_negotiable_gate"] = False
        with self.assertRaisesRegex(ValueError, "safety gates"):
            analyze(b)

    def test_no_rewriting_completed_past(self):
        b = copy.deepcopy(CASE)
        b["events"][0]["effects"] = [{"step_id":"space", "extra_days":21}]
        with self.assertRaisesRegex(ValueError, "completed"):
            analyze(b)

    def test_no_unknown_steps_and_duplicate_effects(self):
        b = copy.deepcopy(CASE)
        b["events"][0]["effects"] = [{"step_id":"federal_agency", "extra_days":2}]
        with self.assertRaisesRegex(ValueError, "unknown affected"):
            analyze(b)
        b = copy.deepcopy(CASE)
        b["events"][0]["effects"] *= 2
        with self.assertRaisesRegex(ValueError, "duplicate"):
            analyze(b)

    def test_no_negative_time_or_unbounded_time(self):
        b = copy.deepcopy(CASE)
        b["events"][0]["effects"][0]["extra_days"] = -1
        with self.assertRaises(ValueError):
            analyze(b)
        b = copy.deepcopy(CASE)
        b["events"][0]["effects"][0]["extra_days"] = float("inf")
        with self.assertRaises(ValueError):
            analyze(b)

    def test_all_models_stay_local_and_hypothetical(self):
        r = analyze(copy.deepcopy(CASE))
        self.assertTrue(r["return_receipt"]["no_outside_action"])
        self.assertTrue(r["return_receipt"]["all_alternatives_hold"])
        self.assertTrue(r["return_receipt"]["not_measured_real_outcomes"])
        self.assertEqual(r["return_receipt"]["source_authentication"], "NOT_PERFORMED")


if __name__ == "__main__":
    unittest.main()
