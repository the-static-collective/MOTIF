"""Additional conventional finite-learner baseline for MOTIF-Q-001."""
import unittest

from question import (
    HYPOTHESES, candidate_trials, decide_with_oracle,
    run_demo, select_information_gain, select_question, target_trial,
)


class BaselineTests(unittest.TestCase):
    def test_same_budget_same_information_and_cost(self):
        active = select_question(
            HYPOTHESES, candidate_trials(), target_trial(), 1)
        conventional = select_information_gain(
            HYPOTHESES, candidate_trials(), 1)
        self.assertEqual(active.id, conventional.id)
        self.assertEqual(active.cost, conventional.cost)

    def test_equally_performing_finite_baseline_disproves_superiority_here(self):
        stats = run_demo()["statistics"]
        self.assertEqual(stats["active"]["answered"],
                         stats["info_gain"]["answered"])
        self.assertEqual(stats["active"]["correct_answers"],
                         stats["info_gain"]["correct_answers"])
        self.assertEqual(stats["active"]["total_query_cost"],
                         stats["info_gain"]["total_query_cost"])
        self.assertEqual(stats["active"]["answered"], 4)
        self.assertEqual(stats["active"]["correct_answers"], 4)

    def test_no_oracle_leak_to_baseline(self):
        ids = {decide_with_oracle(h, policy="info_gain", budget=1)
               ["query_receipts"][0]["trial"] for h in HYPOTHESES}
        self.assertEqual(ids, {"a_part-surrogate"})

    def test_unaffordable_or_refused_probe_not_selected(self):
        self.assertIsNone(select_information_gain(
            HYPOTHESES, candidate_trials(), budget=0))


if __name__ == "__main__":
    unittest.main()
