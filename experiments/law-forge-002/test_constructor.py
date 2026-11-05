"""Adversarial boundaries for the finite representation-constructor trial."""
import unittest

from constructor import (
    ConstructorModel, atoms, deserialize, distinct, evaluate, feature_programs,
    query, review, serialize, synthesize
)
from unseen_world import FAMILIES, World
from trial import benchmark, negative_transfer, select, trial

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "law-forge-001"))
from forge import Probe, Observation


class LawForgeConstructorTests(unittest.TestCase):
    def test_grammar_is_finite_and_has_composites_absent_from_old_grammar(self):
        programs = feature_programs()
        self.assertEqual(len(programs), 5)
        self.assertEqual(atoms(), (("LAG", 0), ("LAG", 1)))
        self.assertIn(("XOR", ("LAG", 0), ("LAG", 1)), programs)
        self.assertIn(("OR", ("LAG", 0), ("LAG", 1)), programs)

    def test_original_concepts_fail_and_composed_candidates_survive(self):
        result = synthesize(World("xor_memory").initial_observations())
        self.assertTrue(result["failed_original"])
        self.assertEqual(result["state"], "PROPOSE_CONSTRUCTORS")
        self.assertEqual([m.program[0] for m in result["proposals"]],
                         ["OR", "XOR"])
        self.assertIsNone(distinct(result["proposals"]))

    def test_adaptive_discriminating_query_is_not_world_rule_hint(self):
        rows = World("xor_memory").initial_observations()
        chosen = query(synthesize(rows)["proposals"], rows, budget=1)
        self.assertEqual(chosen, Probe(((1, 1),), (1, 1)))
        self.assertEqual(Probe.from_packet(chosen.packet()), chosen)

    def test_constraints_are_applied_before_selection(self):
        natural = World("xor_memory").initial_observations()
        options = synthesize(natural)["proposals"]
        self.assertIsNone(query(options, natural, budget=0))
        self.assertIsNone(query(options, natural, budget=1,
                                prohibited=(Probe(((1, 1),), (1, 1)),)))
        with self.assertRaises(ValueError):
            query(options, natural, budget=-1)

    def test_one_probe_discovers_xor_constructor(self):
        model, probes, state = select(World("xor_memory", 2))
        self.assertEqual(state, "CONSTRUCTOR_IDENTIFIED")
        self.assertEqual(len(probes), 1)
        self.assertIsInstance(model, ConstructorModel)
        self.assertEqual(model.program[0], "XOR")

    def test_one_probe_discovers_or_constructor(self):
        model, probes, state = select(World("or_memory", 2))
        self.assertEqual(state, "CONSTRUCTOR_IDENTIFIED")
        self.assertEqual(len(probes), 1)
        self.assertEqual(model.program[0], "OR")

    def test_original_solution_not_replaced_when_sufficient(self):
        result = trial(World("instant", 2))
        self.assertEqual(result["state"], "INCUMBENT_SUFFICIENT")
        self.assertTrue(result["incumbent_kept"])
        self.assertIsNone(result["new_constructor"])
        self.assertEqual(len(result["probes"]), 0)
        self.assertEqual(result["test_correct"], 16)

    def test_a_finite_budget_can_leave_ambiguity(self):
        result = trial(World("xor_memory", 2), budget=0)
        self.assertEqual(result["state"], "HOLD_UNIDENTIFIABLE")
        self.assertEqual(result["test_covered"], 0)
        self.assertIsNone(result["new_constructor"])

    def test_old_only_model_holds_new_language_cases(self):
        result = trial(World("xor_memory", 2), method="old_only")
        self.assertEqual(result["state"], "HOLD_OLD_GRAMMAR_FAILED")
        self.assertEqual(result["test_covered"], 0)

    def test_synthetic_hidden_two_tick_defeats_one_tick_constructor(self):
        result = trial(World("two_tick_hidden", 2))
        self.assertEqual(result["review"]["status"],
                         "HOLD_INDEPENDENT_FALSIFICATION")
        self.assertGreater(result["review"]["contradictions"], 0)
        self.assertEqual(result["test_covered"], 0)

    def test_simulated_distribution_shift_fails_review(self):
        result = trial(World("distribution_shift", 2))
        self.assertEqual(result["review"]["status"],
                         "HOLD_INDEPENDENT_FALSIFICATION")
        self.assertGreater(result["review"]["contradictions"], 0)

    def test_require_full_review_coverage(self):
        model, _, _ = select(World("xor_memory"))
        rows = World("xor_memory").partition("review")
        self.assertEqual(review(model, rows[:8])["status"],
                         "HOLD_INSUFFICIENT_REVIEW")
        self.assertEqual(review(model, rows[:8] * 2)["status"],
                         "HOLD_COVERAGE")

    def test_data_only_constructor_round_trip_and_tamper_rejection(self):
        model, _, _ = select(World("xor_memory"))
        packet = model.packet()
        self.assertEqual(ConstructorModel.from_packet(packet), model)
        evil = [
            {**packet, "authority": "RUN_PROGRAM"},
            {**packet, "status": "APPROVED"},
            {**packet, "real_world_authority": True},
            {**packet, "callback_url": "https://invalid.example"},
            {**packet, "table": [[0, 0, 0, 1]]},
            {**packet, "program": {"op": "PYTHON", "code": "exec()"}},
            {**packet, "program": {"op": "XOR", "args": [
                {"op": "LAG", "index": 0}, {"op": "LAG", "index": True}
            ]}},
        ]
        for row in evil:
            with self.subTest(row=row), self.assertRaises(ValueError):
                ConstructorModel.from_packet(row)

    def test_no_arbitrary_program_or_deep_expressions(self):
        bad = {"op": "OR", "args": [
            {"op": "XOR", "args": [
                {"op": "LAG", "index": 0}, {"op": "LAG", "index": 1}
            ]},
            {"op": "LAG", "index": 0}
        ]}
        with self.assertRaises(ValueError):
            deserialize(bad)
        with self.assertRaises(ValueError):
            serialize(("SYSTEM", "exec"))

    def test_no_forged_physical_or_non_boolean_observations(self):
        p = Probe(((0, 1),), (1, 1))
        with self.assertRaises(ValueError):
            Observation(p, 1, provenance="REAL_WITNESS")
        with self.assertRaises(ValueError):
            Observation(p, True)
        with self.assertRaises(ValueError):
            synthesize([{"probe": p, "outcome": 1}])

    def test_negative_transfer_always_requires_new_review(self):
        x = negative_transfer()
        self.assertTrue(x["equivalent_world"]["status"].startswith("ELIGIBLE"))
        self.assertEqual(x["changed_rule"]["status"],
                         "HOLD_INDEPENDENT_FALSIFICATION")

    def test_fixed_classical_query_is_matched_and_not_outperformed(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                a = trial(World(family, 3), "adaptive")
                f = trial(World(family, 3), "fixed")
                self.assertEqual(a["review"], f["review"])
                self.assertEqual(a["test_correct"], f["test_correct"])
                self.assertEqual(len(a["probes"]), len(f["probes"]))

    def test_comparison_and_no_automatic_method_promotion(self):
        result = benchmark()
        self.assertEqual(result["frozen_method_decision"], "NO_METHOD_PROMOTION")
        final = result["evaluation"]
        self.assertEqual(final["adaptive"], final["fixed"])
        self.assertEqual(final["adaptive"]["worlds"], 25)
        self.assertEqual(final["adaptive"]["review_eligible"], 15)
        self.assertEqual(final["adaptive"]["held"], 10)
        self.assertEqual(final["adaptive"]["new_constructors"], 20)
        self.assertEqual(final["adaptive"]["test_incorrect"], 0)
        self.assertEqual(final["old_only"]["review_eligible"], 5)
        self.assertEqual(result["external_operations"], 0)
        self.assertFalse(result["real_world_authority"])


if __name__ == "__main__":
    unittest.main()
