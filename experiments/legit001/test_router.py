"""Falsifiers for the finite MOTIF-LEGIT-001 reason router (synthetic only)."""
from __future__ import annotations

from copy import deepcopy
import math
import unittest

from benchmark import report, one_trial
from classical_reference import reference
from router import Hold, route, validate_task, posterior_after, digest
from stranger_gate import public_problem, cases


class ReasonRoutingTests(unittest.TestCase):
    def test_xor_needs_two_step_future_question(self):
        task = public_problem("xor", 0)
        self.assertEqual(route(task)["action"], "ASK_SYNTHETIC")
        self.assertEqual(route(task, lookahead=1)["action"], "ABSTAIN")
        self.assertEqual(route(task)["question"], "measure_a")
        # This is classical value-of-information, not novel model invention.
        self.assertEqual(reference(task)[:2], ("ASK_SYNTHETIC", "measure_a"))

    def test_classical_exact_reference_ties_across_registered_inputs(self):
        for family, task in cases():
            if family == "grammar_gap":
                continue
            for lookahead in (0, 1, 2):
                actual = route(task, lookahead=lookahead)
                optimal = reference(task, depth=lookahead)
                self.assertEqual((actual["action"], actual["question"]),
                                 optimal[:2], msg=task["id"])
                self.assertAlmostEqual(actual["expected_remaining_loss"],
                                       optimal[2], places=8)

    def test_post_observation_replans_and_does_not_fabricate_answer(self):
        task = public_problem("xor", 1)
        first = route(task)
        self.assertEqual(first["action"], "ASK_SYNTHETIC")
        self.assertIsNone(first["prediction"])
        one = [{"question": first["question"], "yes": True}]
        nxt = route(task, one)
        self.assertEqual(nxt["action"], "ASK_SYNTHETIC")
        self.assertNotEqual(nxt["question"], first["question"])
        two = one + [{"question": nxt["question"], "yes": False}]
        last = route(task, two)
        self.assertEqual(last["action"], "PREDICT_TRUE")
        self.assertAlmostEqual(last["confidence_true"], 0.82, places=5)

    def test_no_query_when_uninformative(self):
        self.assertEqual(route(public_problem("uninformative", 0))["action"],
                         "ABSTAIN")

    def test_no_query_when_price_exceeds_value(self):
        self.assertEqual(route(public_problem("costly", 0))["action"], "ABSTAIN")

    def test_no_query_when_future_inquiry_budget_disallows_synergy(self):
        self.assertEqual(route(public_problem("limited", 0))["action"], "ABSTAIN")

    def test_grammar_gap_is_held_not_a_fake_capability(self):
        task = public_problem("grammar_gap", 0)
        response = route(task)
        self.assertEqual(response["action"], "PROPOSE_GRAMMAR_REVIEW_HELD")
        self.assertEqual(response["status"], "HOLD")
        self.assertIsNone(response["prediction"])
        self.assertFalse(response["real_world_authority"])

    def test_predict_when_prior_certain_and_still_no_authority(self):
        task = public_problem("xor", 3)
        task["worlds"][0]["prior"] = 0.0
        task["worlds"][1]["prior"] = 1.0
        task["worlds"][2]["prior"] = 0.0
        task["worlds"][3]["prior"] = 0.0
        response = route(task)
        self.assertEqual(response["action"], "PREDICT_TRUE")
        self.assertIs(response["prediction"], True)
        self.assertFalse(response["real_world_authority"])

    def test_schema_refuses_unknown_real_scope(self):
        task = public_problem("xor", 0)
        task["scope"] = "REAL_WORLD_WRITE"
        with self.assertRaises(Hold):
            route(task)

    def test_schema_refuses_unknown_field_as_hidden_answer(self):
        task = public_problem("xor", 0)
        task["hidden_truth"] = "w3"
        with self.assertRaises(Hold):
            route(task)

    def test_nan_and_negative_cost_not_allowed(self):
        task = public_problem("xor", 0)
        task["queries"][0]["cost"] = float("nan")
        with self.assertRaises(Hold):
            route(task)
        task["queries"][0]["cost"] = -1.0
        with self.assertRaises(Hold):
            route(task)

    def test_non_normalized_priors_refused(self):
        task = public_problem("xor", 0)
        task["worlds"][0]["prior"] = 0.30
        with self.assertRaises(Hold):
            route(task)

    def test_duplicate_world_and_query_names_refused(self):
        task = public_problem("xor", 0)
        task["worlds"][0]["id"] = "w1"
        with self.assertRaises(Hold):
            route(task)
        task = public_problem("xor", 0)
        task["queries"][0]["id"] = "measure_b"
        with self.assertRaises(Hold):
            route(task)

    def test_repeated_observation_refused_even_if_consistent(self):
        task = public_problem("xor", 0)
        history = [{"question": "measure_a", "yes": True}] * 2
        with self.assertRaises(Hold):
            route(task, history)

    def test_unknown_or_tampered_observation_refused(self):
        task = public_problem("xor", 0)
        for record in ({"question": "invented", "yes": True},
                       {"question": "measure_a", "yes": 1},
                       {"question": "measure_a", "yes": True, "real": True}):
            with self.assertRaises(Hold):
                route(task, [record])

    def test_cannot_ask_past_budget(self):
        task = public_problem("xor", 0)
        task["max_total_cost"] = 0.03
        with self.assertRaises(Hold):
            route(task, [{"question": "measure_a", "yes": True},
                         {"question": "measure_b", "yes": False}])

    def test_impossible_observation_does_not_create_certain_belief(self):
        task = public_problem("xor", 0)
        task["queries"][0]["p_yes"] = {w["id"]: 0.0 for w in task["worlds"]}
        with self.assertRaises(Hold):
            route(task, [{"question": "measure_a", "yes": True}])

    def test_content_hash_is_not_authentication(self):
        task = public_problem("xor", 0)
        self.assertEqual(route(task)["status"], "PROPOSAL_ONLY")
        old = route(task)["content_digest"]
        task["abstain_loss"] = 0.29
        self.assertNotEqual(old, route(task)["content_digest"])
        self.assertFalse(route(task)["real_world_authority"])

    def test_reproducible_scoring_and_baseline_tie(self):
        result = report()
        self.assertEqual(result, report())
        self.assertFalse(result["independent_unseen_test"])
        self.assertFalse(result["classical_superiority_claim"])
        self.assertEqual(result["total_registered"], 184)
        self.assertEqual(result["two_step_affordance_vs_myopia_on_xor"], 40)
        self.assertEqual(result["overall"]["routing_2_step"],
                         result["overall"]["classical_exact_2_step"])
        self.assertEqual(result["overall"]["routing_2_step"]["held_grammar_gaps"], 8)
        self.assertTrue(result["overall"]["routing_2_step"]["mean_realized_loss"]
                        < result["overall"]["routing_myopic"]["mean_realized_loss"])

    def test_no_hidden_truth_exposed_in_public_task(self):
        task = public_problem("xor", 4)
        self.assertNotIn("truth", str(task).lower())
        self.assertNotIn("selected_world", str(task).lower())
        self.assertEqual(task["scope"], "SYNTHETIC_ONLY")


if __name__ == "__main__":
    unittest.main()
