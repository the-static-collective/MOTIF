"""QC-008 integration regression for the actual QC-007 zero-path toy."""
import unittest

from qc007_bridge import upgrade_legacy_hold
from recover import YES, NO, UNKNOWN, recover, synthetic_case


class LegacyBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.witness=upgrade_legacy_hold()

    def test_exact_previous_hold_survives_as_original_fact(self):
        self.assertEqual(self.witness.prior_status,
                         "HOLD_NO_SAFE_COMPLETE_PATH")
        self.assertEqual(self.witness.prior_viable_paths,0)
        self.assertEqual(len(self.witness.prior_world_receipt),64)

    def test_new_agent_does_not_stop_with_old_failed_goal(self):
        self.assertEqual(self.witness.new_status,
                         "NO_FOOD_ROUTE_YET__NEXT_CAPABILITY")
        self.assertGreaterEqual(len(self.witness.proposed_next_actions),3)
        self.assertIn("brief_grounding",self.witness.proposed_next_actions)

    def test_legacy_case_does_not_claim_ability_to_walk(self):
        self.assertIn("insufficient evidence",self.witness.note)
        self.assertIn("check_walking_safety",self.witness.proposed_next_actions)

    def test_regaining_options_is_not_asserting_a_meal(self):
        self.assertEqual(self.witness.restored_actual_meals,0)
        self.assertEqual(self.witness.actual_external_actions,0)

    def test_source_id_stays_stable_when_regenerating_case(self):
        replay=upgrade_legacy_hold()
        self.assertEqual(replay,self.witness)


if __name__=="__main__":
    unittest.main()
