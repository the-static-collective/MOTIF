"""Hostile and comparative tests for MOTIF-Q-001's finite synthetic study."""
import copy
import unittest

from question import (
    HYPOTHESES, Observation, Trial, candidate_trials, compatible,
    decide_with_oracle, dogram_probe_family, forecast, predict,
    run_demo, select_question, target_trial
)


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.probes = candidate_trials()
        self.target = target_trial()

    def test_prior_is_ambiguous(self):
        prior = (
            Observation(Trial("both", True, True, 0), True),
            Observation(Trial("neither", False, False, 0), False),
        )
        self.assertEqual(compatible(prior), HYPOTHESES)
        self.assertEqual(forecast(HYPOTHESES, self.target), "ABSTAIN")

    def test_selects_informative_affordable_permitted_question(self):
        chosen = select_question(HYPOTHESES, self.probes, self.target, 1)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.id, "a_part-surrogate")
        self.assertTrue(chosen.admitted)
        self.assertLessEqual(chosen.cost, 1)

    def test_no_hidden_oracle_in_question_selection(self):
        # Every possible hidden mechanism produces the SAME first question.
        rows = [decide_with_oracle(hidden, budget=1) for hidden in HYPOTHESES]
        self.assertEqual({row["query_receipts"][0]["trial"]
                          for row in rows}, {"a_part-surrogate"})
        for row in rows:
            self.assertEqual(set(row["initial_hypotheses"]), set(HYPOTHESES))
            self.assertTrue(row["correct_if_answered"])
            self.assertEqual(row["remaining_budget"], 0)

    def test_declared_cost_and_refusal_override_information(self):
        blocked = (Trial("forbidden", True, False, 0, admitted=False),
                   Trial("expensive", True, False, 9))
        self.assertIsNone(select_question(HYPOTHESES, blocked, self.target, 2))
        result = decide_with_oracle("part", probes=blocked, budget=2)
        self.assertEqual(result["query_receipts"], [])
        self.assertEqual(result["target_prediction"], "ABSTAIN")

    def test_nuisance_does_not_manufacture_learning(self):
        row = decide_with_oracle("part", policy="fixed_nuisance", budget=1)
        self.assertEqual(row["target_prediction"], "ABSTAIN")
        self.assertEqual(row["remaining_hypotheses"], list(HYPOTHESES))
        self.assertEqual(row["query_receipts"][0]["hypotheses_before"],
                         row["query_receipts"][0]["hypotheses_after"])

    def test_unresolvable_ambiguity_abstains(self):
        only_badge = (Trial("badge", False, True, 1),)
        row = decide_with_oracle("both", probes=only_badge, budget=1)
        self.assertEqual(row["target_prediction"], "ABSTAIN")
        self.assertEqual(row["query_receipts"], [])

    def test_contradictory_witnesses_are_model_miss(self):
        contradictory = (
            Observation(Trial("same", True, False, 1), True),
            Observation(Trial("same", True, False, 1), False),
        )
        self.assertEqual(compatible(contradictory), ())
        self.assertEqual(forecast((), self.target), "ABSTAIN_MODEL_MISS")

    def test_non_synthetic_claim_cannot_be_laundered(self):
        with self.assertRaises(ValueError):
            compatible((Observation(Trial("x", True, False, 0), True,
                                    provenance="REAL_WORLD"),))

    def test_no_effect_of_fixture_order_on_question(self):
        self.assertEqual(
            select_question(HYPOTHESES, self.probes, self.target, 1),
            select_question(tuple(reversed(HYPOTHESES)),
                            tuple(reversed(self.probes)), self.target, 1),
        )

    def test_dogram_vectors_represent_declared_probe_partition(self):
        payload = dogram_probe_family()
        self.assertEqual(payload["schema"], "motif.dogram-probe-family/v0")
        self.assertNotIn("e_refused-part", payload["probes"])
        self.assertEqual(payload["excluded_trials"], ["e_refused-part"])
        self.assertEqual(payload["target_labels"], [1, 0, 0, 1])
        self.assertEqual(payload["probes"]["a_part-surrogate"], [1, 0, 0, 1])
        self.assertNotIn("hidden_mechanism", payload)

    def test_no_mutation_of_declared_probes_or_observed_history(self):
        before = copy.deepcopy(self.probes)
        decide_with_oracle("either", probes=self.probes, budget=1)
        self.assertEqual(self.probes, before)

    def test_comparator_is_reported_without_accuracy_inflation(self):
        stats = run_demo()["statistics"]
        self.assertEqual(stats["active"]["answered"], 4)
        self.assertEqual(stats["active"]["correct_answers"], 4)
        self.assertEqual(stats["fixed_nuisance"]["answered"], 0)
        self.assertEqual(stats["fixed_nuisance"]["correct_answers"], 0)

    def test_oracle_not_permitted_as_real_world_causal_claim(self):
        self.assertTrue(all(predict(h, Trial("both", True, True, 0))
                            for h in HYPOTHESES))
        self.assertTrue(run_demo()["cases"][0]["no_real_action"])


if __name__ == "__main__":
    unittest.main()
