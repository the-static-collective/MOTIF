"""Regression: a reported permission changes the active question, not the owner index."""
import unittest

from fellowship_operator_update import USER_OBSERVATION, analyze


class FellowshipOperatorUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = analyze()
        cls.scenarios = cls.report["scenario_model_not_verified_impact"]

    def test_space_permission_is_recorded_as_user_report_not_third_party_proof(self):
        self.assertEqual(USER_OBSERVATION["venue_use_permission"], "REPORTED_GRANTED")
        self.assertEqual(USER_OBSERVATION["two_core_organizers"], "USER_AND_PAULA")
        self.assertIn("FOOD_SERVICE_APPROVAL", USER_OBSERVATION["not_inferred"])
        self.assertIn("VOLUNTEER_COMMITMENTS_FINAL", USER_OBSERVATION["not_inferred"])

    def test_obsolete_host_question_is_not_reasked(self):
        self.assertEqual(self.report["resolved_old_question"], "RIVERSIDE_HOST_QUESTION")
        for case in self.scenarios.values():
            self.assertNotIn(
                "RIVERSIDE_HOST_QUESTION",
                [x["id"] for x in case["invented_assumptions"]],
            )

    def test_new_work_is_operational_not_reconfirmation_of_venue(self):
        names = {x["id"] for x in self.report["operational_questions_now"]}
        self.assertEqual(names, {
            "FELLOWSHIP_SIMPLE_RUN_OF_SHOW",
            "FELLOWSHIP_INVITE_AND_HELPER_MAP",
            "FELLOWSHIP_GO_NO_GO_CHECK",
        })
        for x in self.report["operational_questions_now"]:
            self.assertIn("internal_last_window_is_hypothesis_not_real_deadline", x)

    def test_nexus_remains_separate_unknown_not_an_imagined_application(self):
        self.assertEqual(self.report["continuing_grant_question"], "NEXUS_TEAM_QUESTION")
        self.assertFalse(self.report["applications_submitted"])
        self.assertFalse(self.report["people_contacted"])
        self.assertFalse(self.report["event_guaranteed"])

    def test_planz_status_is_not_promoted(self):
        source = self.report["source_planz"]
        self.assertTrue(source["read_only"])
        self.assertEqual(source["authority"], "INDEX_ONLY")
        self.assertEqual(source["original_index_conclusion"],
                         "HOLD_NO_VERIFIED_INACTION_VALUATION")
        self.assertTrue(source["planZ_field_outcomes_not_rewritten"])

    def test_rerun_compares_serial_and_parallel_without_dispatch(self):
        for name in (
            "reported_venue_granted_limited_capacity",
            "reported_venue_granted_two_organizers_can_parallelize"
        ):
            result = self.scenarios[name]
            self.assertTrue(result["no_actual_authority"])
            self.assertGreater(result["hypothetical_total_value"], 0)

    def test_no_real_values_still_means_hold(self):
        no_data = self.scenarios["no_defensible_time_or_value_assumptions"]
        self.assertEqual(no_data["hypothetical_total_value"], 0)
        self.assertEqual(no_data["first_review_step"], ())
        self.assertEqual(no_data["proposed_sequence"], [])

    def test_if_team_is_proven_nonviable_nexus_inquiry_goes_away(self):
        no_team = self.scenarios["no_viable_nexus_team_verified"]
        self.assertNotIn(
            "NEXUS_TEAM_QUESTION",
            [x["id"] for x in no_team["invented_assumptions"]]
        )


if __name__ == "__main__":
    unittest.main()
