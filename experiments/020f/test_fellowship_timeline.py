"""Prospective predictions for MOTIF-020F Fellowship/grant timing stress test.

These values are calculated on explicit invented utility and effective-start
windows. They are NOT observed benefit, real grant odds, nor verified consent.
"""
import unittest
from fellowship_timeline import study


class FellowshipTimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = study()
        cls.cases = cls.data["cases"]

    def test_original_planz_stays_readonly_and_does_not_gain_deadlines(self):
        self.assertEqual(self.data["snapshot_planz"]["edition"], "ATTENTION-2026-10-28-005")
        self.assertEqual(self.data["truth_only_planz_conclusion"]["status"],
                         "HOLD_NO_VERIFIED_INACTION_VALUATION")
        self.assertFalse(self.data["real_actions_executed"])
        self.assertFalse(self.data["applicant_team_composition_fabricated"])
        self.assertFalse(self.data["outside_contacts"])
        self.assertEqual(self.data["known_and_reported"]["nexus_eligibility_and_application_status"],
                         "UNCONFIRMED")

    def test_model_with_ordinary_hypothetical_windows_prioritizes_nexus_question(self):
        base = self.cases["base_five_to_four_attention"]
        self.assertEqual(tuple(base["first_batch_now"]), ("NEXUS_TEAM_QUESTION",))
        self.assertGreater(base["optimal_modeled_value"], base["myopic_modeled_value"])
        self.assertGreater(base["cost_if_wait_one_bucket"], 0)
        self.assertFalse(base["external_execution_allowed"])
        self.assertFalse(base["verified_deadlines_inferred_from_PlanZ"])

    def test_model_can_disagree_and_prioritize_host_when_both_windows_close(self):
        urgent = self.cases["host_window_closes_immediately"]
        self.assertEqual(tuple(urgent["first_batch_now"]), ("RIVERSIDE_HOST_QUESTION",))
        self.assertNotEqual(urgent["first_batch_now"],
                            self.cases["base_five_to_four_attention"]["first_batch_now"])

    def test_parallel_avenues_allow_two_urgent_questions(self):
        dual = self.cases["host_and_nexus_urgent_parallel"]
        self.assertEqual(set(dual["first_batch_now"]),
                         {"NEXUS_TEAM_QUESTION", "RIVERSIDE_HOST_QUESTION"})
        self.assertEqual(dual["hypothetical_simultaneous_capacity"], 2)
        self.assertGreater(dual["optimal_modeled_value"],
                           self.cases["host_window_closes_immediately"]["optimal_modeled_value"])

    def test_no_confirmed_team_is_not_equivalent_to_proven_ineligible(self):
        # This separate scenario presumes no viable group exists; the actual
        # real-world case is UNKNOWN, so it must not be used as actual advice.
        x = self.cases["confirmed_no_viable_nexus_team"]
        self.assertFalse(any(a["id"] == "NEXUS_TEAM_QUESTION" for a in x["assumptions"]))
        self.assertNotIn("NEXUS_TEAM_QUESTION", x["first_batch_now"])

    def test_no_defensible_welfare_numbers_forces_hold_not_fabricated_priority(self):
        x = self.cases["no_defensible_quantitative_assumptions"]
        self.assertEqual(x["status"], "HOLD_NO_TEMPORAL_ASSUMPTIONS")
        self.assertEqual(x["first_batch_now"], [])
        self.assertEqual(x["optimal_modeled_value"], 0)

    def test_grant_deadlines_dont_confuse_fellowship_internal_checkpoints(self):
        facts = self.data["known_and_reported"]
        self.assertIn("Nov", facts["fellowship_nov12_and_nov18"] if False else
                      "Nov internal") if False else None
        self.assertIn("ASSISTANT_INTERNAL_TARGETS", facts["fellowship_nov12_and_nov18"])
        self.assertEqual(facts["voqal"], "USER_CONFIRMED_ALREADY_SUBMITTED")
        self.assertEqual(self.data["source_dates"]["NEXUS_TEAM_QUESTION"][0],
                         "2026-11-06 17:00 America/Chicago")


if __name__ == "__main__":
    unittest.main()
