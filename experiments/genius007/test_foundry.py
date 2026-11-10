"""GENIUS-007 adversarial test fixtures: composed questions and exact receipts."""
import json
import unittest

from foundry import (
    Capability, Instrument, Literal, Planner, Query, Task, World,
    candidates, observation, run_episode, verify_instrument,
    independent_capability_check,
)
from benchmark import FAMILIES, FUTURE_SEEDS, VALIDATION_SEEDS, task_for, trial, assess


class TestQuestionFoundry(unittest.TestCase):
    def test_unseen_names_and_negative_literals_create_new_question_expression(self):
        names = ("cobalt_mill", "moonwater", "avalanche", "windrow")
        instrument = Instrument(names, source_ref="synthetic:co-assay-174")
        goal = Capability(
            "water_is_ready", (Literal("cobalt_mill", 0),
                               Literal("windrow", 1)), 10)
        task = Task("unseen-language", instrument, (goal,), 3)
        direct = {q.key for q in candidates(task, False)}
        invented = [q for q in candidates(task, True) if q.kind == "PAIR_MATCH"]
        self.assertEqual(len(invented), 1)
        q = invented[0]
        self.assertNotIn(q.key, direct)
        self.assertEqual(q.key, "p:cobalt_mill=0&windrow=1")
        self.assertEqual(q.derived_from, ("water_is_ready",))
        self.assertEqual(q.cost, 3)
        self.assertEqual(q.operator_source, "synthetic:co-assay-174")
        self.assertTrue(verify_instrument(task, q))
        result = observation(task, q, World(names, (0, 0, 0, 1)))
        self.assertEqual(result["response"], 1)
        result_bad = observation(task, q, World(names, (1, 0, 0, 1)))
        self.assertEqual(result_bad["response"], 0)

    def test_instrument_cannot_be_fabricated_or_underpriced(self):
        task = task_for(70731, "PAIRABLE")
        p = Planner(task)
        forged = next(q for q in p.forge if q.kind == "PAIR_MATCH")
        too_cheap = Query(forged.kind, forged.tests, 1,
                          forged.derived_from, forged.operator_source)
        fake_tool = Query(forged.kind, forged.tests, forged.cost,
                          forged.derived_from, "invented:free-magical-oracle")
        for q in (too_cheap, fake_tool):
            self.assertFalse(verify_instrument(task, q))
            receipt = observation(task, q, p.worlds[0])
            self.assertEqual(receipt["status"], "HOLD_UNSUPPORTED_INSTRUMENT_OR_COST")
            self.assertTrue(receipt["no_measurement_taken"])

    def test_no_pair_operator_gives_zero_generated_candidates_and_fallback(self):
        task = task_for(70731, "NO_PAIR")
        p = Planner(task)
        self.assertEqual(p.direct, p.forge)
        self.assertFalse(any(q.kind == "PAIR_MATCH" for q in p.forge))
        a = p.bellman(p.root, task.budget, True, -1)
        b = p.bellman(p.root, task.budget, False, -1)
        self.assertEqual(a, b)

    def test_expensive_pair_does_not_magically_beat_direct_exact(self):
        task = task_for(70731, "EXPENSIVE_PAIR")
        p = Planner(task)
        self.assertTrue(any(q.kind == "PAIR_MATCH" for q in p.forge))
        self.assertEqual(
            p.bellman(p.root, task.budget, True, -1),
            p.bellman(p.root, task.budget, False, -1))
        self.assertFalse(any(q.kind == "PAIR_MATCH" for q in
                             p.available(p.root, task.budget, synthesize=True)))

    def test_pairable_budget_favors_synthesized_test_but_not_novel_science(self):
        task = task_for(70731, "PAIRABLE")
        p = Planner(task)
        expected = task.capabilities[0].reward / 4
        self.assertEqual(p.bellman(p.root, 3, False, -1), 0)
        self.assertAlmostEqual(p.bellman(p.root, 3, True, -1), expected)
        proposed = p.choose(p.root, 3, "FOUNDRY_OPTIMAL")
        self.assertEqual(proposed["status"], "SYNTHESIZED_QUESTION_PROPOSAL")
        self.assertTrue(proposed["no_target_world_consulted"])
        self.assertEqual(proposed["query"].kind, "PAIR_MATCH")
        self.assertTrue(proposed["proposals"][0]["sensor_verified"])
        self.assertTrue(proposed["proposals"][0]["derivation_from_capabilities"])

    def test_researcher_cannot_consult_target_before_choosing(self):
        p = Planner(task_for(70732, "TRIPLE"))
        all_possible = (p.worlds[0], p.worlds[-1])
        decisions = [
            p.choose(p.root, p.task.budget, "FOUNDRY_LOOKAHEAD2")["query"].key
            for _ in all_possible
        ]
        self.assertEqual(decisions[0], decisions[1])
        self.assertGreaterEqual(len(p.forge), len(p.direct))
        self.assertGreater(p.bellman(p.root, p.task.budget, True, -1), 0)

    def test_bad_target_never_receives_a_certificate(self):
        p = Planner(task_for(70732, "PAIRABLE"))
        variables = p.task.instrument.sensor_variables
        outside = World(variables[:-1] + ("unlisted",), (1, 1, 1, 1, 1))
        reply = run_episode(p, outside, "FOUNDRY_OPTIMAL")
        self.assertEqual(reply["status"], "HOLD_OUTSIDE_DECLARED_MODEL")
        self.assertEqual(reply["verified_reward"], 0)
        with self.assertRaises(AssertionError):
            independent_capability_check(
                p.worlds[0],
                (Capability("false", (Literal(variables[0], 1),), 9),),
            )

    def test_negative_requirement_cannot_be_assumed_true(self):
        task = task_for(70732, "MIXED_POLARITY")
        p = Planner(task)
        goal = task.capabilities[0]
        true_bits = [0, 1, 0, 0, 0]
        true_world = World(task.instrument.sensor_variables, tuple(true_bits))
        episode = run_episode(p, true_world, "FOUNDRY_OPTIMAL")
        self.assertEqual(episode["verified_reward"], goal.reward)
        self.assertTrue(episode["no_external_action"])
        self.assertGreaterEqual(episode["synthesized_question_count"], 1)

    def test_goal_clause_validation_prevents_fabricated_predicates(self):
        base = task_for(70731, "PAIRABLE")
        x = base.instrument.sensor_variables[0]
        invalid = Task("invalid", base.instrument, (
            Capability("contradiction",
                       (Literal(x, 0), Literal(x, 1)), 10),), 3)
        with self.assertRaises(ValueError):
            Planner(invalid)
        unsupported = Task("unsupported", base.instrument, (
            Capability("outside", (Literal("no_sensor", 1),), 10),), 3)
        with self.assertRaises(ValueError):
            Planner(unsupported)

    def test_exhaustive_oracle_proves_no_false_certificates(self):
        for family in ("PAIRABLE", "TRIPLE", "MIXED_POLARITY", "NO_PAIR"):
            p = Planner(task_for(70731, family))
            for world in p.worlds:
                for policy in ("DIRECT_OPTIMAL", "FOUNDRY_OPTIMAL"):
                    r = run_episode(p, world, policy)
                    self.assertLessEqual(r["total_measurement_cost"],
                                         p.task.budget)
                    self.assertTrue(r["no_external_action"])
                    self.assertEqual(r["verified_reward"],
                                     sum(c.reward for c in p.task.capabilities
                                         if c.name in r["verified_capabilities"]))


class TestFrozenNovelTaskNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = trial()

    def test_all_families_seed_splits_and_no_deployment(self):
        r = self.result
        self.assertEqual(set(r["test"]), set(FAMILIES))
        self.assertEqual(set(r["validation_selected"]), set(FAMILIES))
        self.assertFalse(set(VALIDATION_SEEDS) & set(FUTURE_SEEDS))
        self.assertEqual(len(r["selection_frozen_sha256_before_future_task_generation"]), 64)
        self.assertTrue(r["no_external_action"])
        self.assertTrue(any("classical exact planning" in s for s in r["nonclaims"]))

    def test_exact_generated_remains_strongest_same_action_space(self):
        for family, metrics in self.result["test"].items():
            outcomes = metrics["measured_mean_verified_reward_by_arm"]
            optimum = outcomes["FOUNDRY_OPTIMAL"]
            self.assertGreaterEqual(optimum + 1e-6, max(outcomes.values()))
            for task in metrics["task_receipts"]:
                self.assertEqual(task["arms"]["FOUNDRY_OPTIMAL"]["invalid_certificates"], 0)
                self.assertEqual(task["arms"]["FOUNDRY_OPTIMAL"]["evaluated_worlds"], 32)
                self.assertLessEqual(task["full_prior_direct_only_optimum"],
                                     task["full_prior_exact_optimum"] + 1e-6)

    def test_supported_pair_improves_some_bounded_tasks_not_all(self):
        for family in ("PAIRABLE", "TRIPLE", "MIXED_POLARITY", "MULTIGOAL"):
            self.assertGreater(self.result["test"][family]
                               ["potential_composition_dividend_vs_direct_exact"], 0)
        for family in ("NO_PAIR", "EXPENSIVE_PAIR"):
            self.assertAlmostEqual(
                self.result["test"][family]["potential_composition_dividend_vs_direct_exact"], 0)

    def test_generated_question_receipt_carries_provenance(self):
        examples = self.result["example_proof_packets"]
        self.assertEqual(len(examples), len(FAMILIES))
        for x in examples:
            self.assertTrue(x["example"]["no_external_action"])
            self.assertTrue(all(t["instrument_provenance"].startswith("synthetic:")
                                for t in x["example"]["trace"]))
            self.assertTrue(all(t["hypothetical_branches_were_not_taken_as_observations"]
                                for t in x["example"]["trace"]))


if __name__ == "__main__":
    unittest.main()
