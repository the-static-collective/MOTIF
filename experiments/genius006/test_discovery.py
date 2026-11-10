"""GENIUS-006 adversarial and strong-classical comparison tests."""
import json
import unittest

from discovery import (
    Capability, Planner, World, episode, independent_verify, sample_space, scenario,
)
from benchmark import (
    CANDIDATES, FAMILIES, FUTURE_SEEDS, VALIDATION_SEEDS,
    public_sample_indices, trial,
)


class TestGatedAffordance(unittest.TestCase):
    def test_model_is_public_but_target_is_not_used_when_choosing(self):
        p = Planner(scenario("CHAIN"))
        self.assertEqual(len(p.worlds), 256)
        a = p.choose(p.root, (), 3, "EXACT_BELLMAN")
        b = p.choose(p.root, (), 3, "EXACT_BELLMAN")
        self.assertEqual(a, b)
        self.assertIn(a["question"], p.available(p.root, ()))
        self.assertEqual(a["hypotheses_considered"], len(p.root))
        self.assertIn("survey_noise_x", p.available(p.root, ()))
        self.assertNotIn("inspect_c", p.available(p.root, ()))
        self.assertNotIn("verify_d", p.available(p.root, ()))

    def test_fact_to_question_to_capability_three_hops(self):
        p = Planner(scenario("CHAIN"))
        # This is a proof-of-interface for a chain, not a new algorithm.
        belief = p.root
        asked = []
        for qname, outcome in (("confirm_b", 1), ("inspect_c", 1),
                               ("verify_d", 1)):
            self.assertIn(qname, p.available(belief, tuple(sorted(asked))))
            branch = dict(p.partitions(belief, qname))
            belief = branch[outcome]
            asked.append(qname)
        names = {c.name for c in p.certified(belief)}
        self.assertIn("new_service", names)
        self.assertIn("access", names)
        self.assertGreater(p.value(belief), 0)
        self.assertEqual(len(belief), 32)  # A, noise X/Y are unresolved.

    def test_invalid_transfer_or_out_of_model_is_hold(self):
        p = Planner(scenario("CHAIN"))
        fake = World((2, 1, 1, 1, 1, 1))
        r = episode(p, fake, "EXACT_BELLMAN")
        self.assertEqual(r["status"], "HOLD_OUTSIDE_DECLARED_MODEL")
        self.assertFalse(r["trace"])
        self.assertEqual(r["verified_capability_value"], 0)
        with self.assertRaises(AssertionError):
            independent_verify(
                World((0, 0, 0, 0, 0, 0)),
                (Capability("false", (("a", 1),), 9),),
            )

    def test_entropic_arms_can_choose_high_entropy_noise(self):
        p = Planner(scenario("CHAIN"))
        # Noise fields have 4 equally likely outcomes; a single actionable
        # Boolean fact has 2. This is an intentional stress case.
        q = p.choose(p.root, (), 3, "ENTROPY")
        self.assertEqual(q["question"], "survey_noise_x")
        self.assertEqual(q["candidates"][0]["entropy_bits"], 2)
        self.assertEqual(p.value(p.root), 0)
        self.assertEqual(
            p.choose(p.root, (), 3, "DIVERSITY")["question"],
            "survey_noise_x",
        )

    def test_research_objective_not_just_information_entropy(self):
        p = Planner(scenario("CHAIN"))
        e = p.choose(p.root, (), 3, "ENTROPY")
        dp = p.choose(p.root, (), 3, "EXACT_BELLMAN")
        self.assertNotEqual(e["question"], dp["question"])
        self.assertGreater(
            dp["candidates"][0]["selection_score"], 0,
        )
        self.assertGreaterEqual(
            p.exact_value(p.root, (), 3),
            p.expected_at_depth(p.root, (), 2),
        )

    def test_no_gating_bypass_after_negative_answer(self):
        p = Planner(scenario("CHAIN"))
        belief = dict(p.partitions(p.root, "confirm_b"))[0]
        self.assertFalse(p.certifies(belief, (("b", 1),)))
        self.assertNotIn("inspect_c", p.available(belief, ("confirm_b",)))
        self.assertNotIn("verify_d", p.available(belief, ("confirm_b",)))
        self.assertNotIn("new_service", [c.name for c in p.certified(belief)])

    def test_no_unverified_certificates_in_full_small_population(self):
        p = Planner(scenario("NOISE_USEFUL"))
        for i in range(0, len(p.worlds), 17):
            for arm in ("ENTROPY", "AFFORDANCE_2", "EXACT_BELLMAN"):
                r = episode(p, p.worlds[i], arm)
                self.assertTrue(r["no_real_world_action"])
                self.assertLessEqual(r["question_count"], 3)
                self.assertEqual(
                    r["verified_capability_value"],
                    sum(c["value"] for c in r["certificates"]),
                )
                self.assertTrue(all(
                    c["separate_world_check"] == "PASS" for c in r["certificates"]))

    def test_finite_exact_bellman_matches_full_population_average(self):
        p = Planner(scenario("CHAIN"))
        optimum = p.exact_value(p.root, (), p.task.budget)
        all_rewards = [
            episode(p, world, "EXACT_BELLMAN")["verified_capability_value"]
            for world in p.worlds
        ]
        self.assertAlmostEqual(sum(all_rewards)/len(all_rewards), optimum)
        self.assertGreater(optimum, 0)

    def test_four_step_delayed_value_defeats_shallow_horizon(self):
        p = Planner(scenario("DEEP_CHAIN"))
        self.assertEqual(p.task.budget, 4)
        self.assertEqual(p.choose(p.root, (), 4, "AFFORDANCE_2")["question"], "a_noise_x")
        self.assertEqual(p.choose(p.root, (), 4, "EXACT_BELLMAN")["question"], "z_confirm_b")
        self.assertGreater(p.exact_value(p.root, (), 4), 0)
        fully_true = World((1, 1, 1, 1, 0, 0))
        deep = episode(p, fully_true, "EXACT_BELLMAN")
        shallow = episode(p, fully_true, "AFFORDANCE_2")
        self.assertEqual(deep["verified_capability_value"], 32)
        self.assertEqual(shallow["verified_capability_value"], 0)
        self.assertEqual(
            [row["question"] for row in deep["trace"]],
            ["z_confirm_b", "z_inspect_c", "z_verify_d", "z_final_a"],
        )

    def test_different_goal_can_make_entropic_question_relevant(self):
        p = Planner(scenario("NOISE_USEFUL"))
        caps = [c.name for c in p.task.capabilities]
        self.assertIn("calibration_x", caps)
        q = p.choose(p.root, (), 3, "EXACT_BELLMAN")
        self.assertIn(q["question"], p.available(p.root, ()))
        self.assertGreater(p.exact_value(p.root, (), 3), 0)


class TestIndependentFuture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = trial()

    def test_freeze_is_stable_and_selection_is_training_only(self):
        r=self.result
        self.assertEqual(r["status"], "RESEARCH_HOLD_ENGINEER_AUTHORED")
        self.assertEqual(len(r["frozen_sha256_before_test_sampling"]), 64)
        self.assertEqual(set(r["selection"]), set(FAMILIES))
        self.assertTrue(r["no_external_action"])
        for row in r["selection"].values():
            self.assertIn(row["selected_method"], CANDIDATES)
            self.assertEqual(set(row["training_only_scores"]), set(CANDIDATES))

    def test_test_samples_differ_from_validation_seed_samples(self):
        self.assertFalse(set(FUTURE_SEEDS) & set(VALIDATION_SEEDS))
        for family in FAMILIES:
            future = public_sample_indices(FUTURE_SEEDS[0], family, 32, 256)
            val = public_sample_indices(VALIDATION_SEEDS[0], family, 20, 256)
            self.assertNotEqual(future, val)
            self.assertEqual(len(set(future)), len(future))
        # Different RNG seeds are a modest separation, not blind authorship.

    def test_all_comparators_equal_grammar_and_independent_check(self):
        r=self.result
        for family, result in r["future"].items():
            arms=result["evaluation"]
            self.assertEqual(
                set(arms),
                {"ENTROPY", "DIVERSITY", "MYOPIC_GAIN", "AFFORDANCE_2",
                 "EXACT_BELLMAN", "TRAINING_SELECTED",
                 "POSTHOC_GUARDED_RESEARCH_RECOMMENDATION"},
            )
            for arm in arms.values():
                self.assertEqual(arm["evaluated"], 96)
                self.assertEqual(arm["false_certificates"], 0)
                self.assertTrue(arm["no_external_action"])
            self.assertGreaterEqual(result["exact_uniform_prior_expected_value"], 0)
            self.assertGreater(result["exact_dp_memo_states"], 0)

    def test_proof_carrying_synthetic_receipts_include_questions_and_checks(self):
        r = self.result
        self.assertEqual(len(r["synthetic_examples"]), len(FAMILIES))
        for example in r["synthetic_examples"]:
            self.assertEqual(
                example["verified_value"],
                sum(c["value"] for c in example["certificates"]),
            )
            for c in example["certificates"]:
                self.assertEqual(c["proof"], "TRUE_IN_ALL_REMAINING_PUBLIC_HYPOTHESES")
            for trace in example["trace"]:
                self.assertTrue(trace["source"].startswith("synthetic://"))
                self.assertLessEqual(trace["candidates_after"],
                                     trace["candidates_before"])
                self.assertTrue(trace["no_action_executed"])

    def test_negative_deep_chain_is_not_promoted_over_classical(self):
        deep = self.result["selection"]["DEEP_CHAIN"]
        self.assertFalse(deep["candidate_within_005_of_exact_validation"])
        self.assertEqual(deep["research_adoption_status"],
                         "HOLD_NO_PROMOTION_FALLBACK_CLASSICAL")
        self.assertEqual(deep["recommended_nonexecuting_method"],
                         "EXACT_BELLMAN")
        future = self.result["future"]["DEEP_CHAIN"]["evaluation"]
        self.assertEqual(future["TRAINING_SELECTED"]["mean_verified_value"], 0.0)
        self.assertGreater(future["EXACT_BELLMAN"]["mean_verified_value"], 0)
        self.assertEqual(
            future["POSTHOC_GUARDED_RESEARCH_RECOMMENDATION"]["mean_verified_value"],
            future["EXACT_BELLMAN"]["mean_verified_value"])
        self.assertTrue(
            future["POSTHOC_GUARDED_RESEARCH_RECOMMENDATION"]["posthoc_guard_not_fresh_blind_test"])

    def test_no_broad_novelty_claim(self):
        self.assertTrue(any("No novel mathematics" in c for c in self.result["nonclaims"]))
        self.assertIn("optimal only", self.result["classical_optimality_scope"])


if __name__ == "__main__":
    unittest.main()
