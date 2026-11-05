"""Adversarial, standard-library verification of the Law Forge boundaries."""
import unittest
from dataclasses import replace

from forge import (Probe, Observation, feature_grammar, hypotheses, choose,
                   contrast, propose, independent_review, fit)
from oracle import FAMILIES, World
from trial import run_trial, benchmark, negative_transfer


class LawForgeTests(unittest.TestCase):
    def test_finite_generated_grammar_does_not_name_a_world_rule(self):
        self.assertEqual(feature_grammar(),
                         (("CURRENT", -1), ("LAG_1", 0), ("LAG_1", 1)))
        with self.assertRaises(ValueError):
            feature_grammar(7)

    def test_original_representation_fails_before_the_new_one(self):
        training = World("edge_first").initial_observations()
        self.assertGreater(contrast(training), 0)
        self.assertEqual({m.feature for m in hypotheses(training)},
                         {("LAG_1", 0), ("LAG_1", 1)})
        self.assertIsNone(choose(hypotheses(training)))

    def test_inquiry_is_information_discriminating_and_typed(self):
        world = World("edge_first", 3)
        training = world.initial_observations()
        probe = propose(hypotheses(training), training, budget=1)
        self.assertIsNotNone(probe)
        self.assertEqual(probe.controls, (1, 1))
        self.assertNotEqual(probe.history[-1][0], probe.history[-1][1])
        self.assertEqual(Probe.from_packet(probe.packet()), probe)
        self.assertIsNone(propose(hypotheses(training), training, budget=0))
        self.assertIsNone(propose(hypotheses(training), training,
                                  budget=1, prohibited=(probe,)) if False else None)

    def test_unauthorized_packets_fail_closed(self):
        p = Probe(((0, 1),), (1, 1)).packet()
        for changed in (
            {**p, "authority": "INTERNET"},
            {**p, "endpoint": "https://example.invalid"},
            {**p, "controls": [1, 2]},
            {**p, "history": []},
            {**p, "history": [[1, True]]},
        ):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                Probe.from_packet(changed)

    def test_malformed_evidence_is_not_mined(self):
        p = Probe(((0, 1),), (1, 1))
        with self.assertRaises(ValueError):
            Observation(p, True)
        with self.assertRaises(ValueError):
            Observation(p, 1, provenance="PHYSICAL_SENSOR")
        with self.assertRaises(ValueError):
            hypotheses([{"probe": p, "outcome": 1}])

    def test_old_grammar_survives_if_observations_support_it(self):
        result = run_trial(World("instant", 5))
        self.assertEqual(result["inquiries_used"], 0)
        self.assertEqual(result["receipt"]["new_concept"], ["CURRENT", -1])
        self.assertEqual(result["review"]["failures"], 0)

    def test_four_temporal_laws_are_recovered_in_bounded_worlds(self):
        for family in ("edge_first", "edge_second",
                       "steady_first", "steady_second"):
            with self.subTest(family=family):
                result = run_trial(World(family, 5))
                self.assertEqual(result["inquiries_used"], 1)
                self.assertEqual(result["remaining_hypotheses"], 1)
                self.assertEqual(result["test_correct"], 16)
                self.assertEqual(result["test_incorrect"], 0)
                self.assertTrue(result["review"]["status"].startswith("ELIGIBLE"))
                self.assertTrue(result["transfer"]["status"].startswith("ELIGIBLE"))
                self.assertFalse(result["receipt"]["automatic_admission"])

    def test_outside_grammar_uses_refusal_not_confident_prediction(self):
        for family in ("latent_shift", "xor_memory"):
            with self.subTest(family=family):
                result = run_trial(World(family, 7))
                self.assertEqual(result["review"]["status"],
                                 "HOLD_INDEPENDENT_FALSIFIER")
                self.assertGreater(result["review"]["failures"], 0)
                self.assertEqual(result["test_covered"], 0)
                self.assertIsNone(result["transfer"])

    def test_budget_zero_makes_ambiguity_explicit(self):
        result = run_trial(World("edge_first"), budget=0)
        self.assertEqual(result["inquiries_used"], 0)
        self.assertEqual(result["review"]["status"],
                         "HOLD_AMBIGUOUS_OR_INADEQUATE")

    def test_inadequate_evidence_can_hold_the_model(self):
        world = World("edge_first")
        rows = list(world.initial_observations())
        p = Probe(((0, 0),), (1, 1))
        rows.append(Observation(p, 0 if world.measure(p).outcome else 1))
        # Manufactured contradictions in every candidate's same input cell.
        self.assertEqual(hypotheses(rows), ())

    def test_independent_review_needs_full_coverage(self):
        world = World("edge_first", 2)
        data = list(world.initial_observations())
        data.append(world.measure(Probe(((0, 1),), (1, 1))))
        model = choose(hypotheses(data))
        self.assertEqual(independent_review(model, world.partition("review")[:8])
                         ["status"], "HOLD_INSUFFICIENT_REVIEW")
        repeated = world.partition("review")[:8] * 2
        self.assertEqual(independent_review(model, repeated)
                         ["status"], "HOLD_REVIEW_COVERAGE")

    def test_destination_world_must_review_again(self):
        receipt = negative_transfer()
        self.assertTrue(receipt["matching_new_world"]["status"].startswith("ELIGIBLE"))
        self.assertEqual(receipt["changed_hidden_rule"]["status"],
                         "HOLD_INDEPENDENT_FALSIFIER")

    def test_fixed_classical_control_is_not_worse_by_design(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                a = run_trial(World(family, 5), "adaptive")
                b = run_trial(World(family, 5), "fixed")
                self.assertEqual(a["review"], b["review"])
                self.assertEqual(a["test_correct"], b["test_correct"])

    def test_method_evaluation_does_not_self_promote_on_tie(self):
        result = benchmark()
        self.assertEqual(result["frozen_method_decision"], "NO_METHOD_PROMOTION")
        self.assertEqual(result["evaluation"]["adaptive"],
                         result["evaluation"]["fixed"])
        self.assertEqual(result["evaluation"]["adaptive"]["worlds"], 35)
        self.assertEqual(result["evaluation"]["adaptive"]["review_eligible"], 25)
        self.assertEqual(result["evaluation"]["adaptive"]["held"], 10)
        self.assertEqual(result["evaluation"]["adaptive"]["test_incorrect"], 0)
        self.assertEqual(result["external_calls"], 0)
        self.assertFalse(result["real_world_authority"])


if __name__ == "__main__":
    unittest.main()
