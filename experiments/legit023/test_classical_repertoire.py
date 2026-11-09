"""Adversarial checks for LEGIT-023 classical methods and task-contract separation."""
from __future__ import annotations
from pathlib import Path
from types import SimpleNamespace
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "legit022"))
from atlas import cohort
from graph_inventor import grammar, reference_count
from methods import (
    EXECUTABLE, FUTURE_ADAPTERS, tree_hom_count, constrained_hom_count,
    hom_count, joint_wl_separation, vf2pp_decision, optimal_training_order,
)
from shoulders import run, frozen_policies, STATUS


class ClassicalPortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, cls.test, cls.origin = cohort()

    def test_all_connected_grammars_agree_with_independent_enumerator(self):
        sources = grammar()
        for task in (self.train + self.test)[:9]:
            for source in sources:
                for target in task.graphs:
                    expected = reference_count(source, target)
                    result = hom_count(source, target)
                    self.assertEqual(result["value"], expected)
                    self.assertEqual(constrained_hom_count(source, target),
                                     expected)
                    if tree_hom_count(source, target) is not None:
                        self.assertEqual(tree_hom_count(source, target),
                                         expected)

    def test_hom_not_monomorphism_or_injection(self):
        # A two-leaf star has four homomorphisms to one edge: both
        # leaves can map to the same target endpoint.
        star = (3, ((0, 1), (0, 2)))
        edge = (2, ((0, 1),))
        self.assertEqual(hom_count(star, edge)["value"], 2)
        self.assertEqual(reference_count(star, edge), 2)

    def test_forest_factorization_and_empty_target(self):
        pair_of_edges = (4, ((0, 1), (2, 3)))
        one_edge = (2, ((0, 1),))
        self.assertEqual(tree_hom_count(pair_of_edges, one_edge), 4)
        self.assertEqual(hom_count((1, ()), (0, ()))["value"], 0)
        self.assertEqual(hom_count((0, ()), (0, ()))["value"], 1)

    def test_cycle_goes_to_constraint_solver(self):
        tri = (3, ((0, 1), (1, 2), (2, 0)))
        edge = (2, ((0, 1),))
        self.assertIsNone(tree_hom_count(tri, edge))
        self.assertEqual(hom_count(tri, edge)["method"],
                         "constraint_backtracking_hom")
        self.assertEqual(hom_count(tri, edge)["value"], 0)

    def test_wl_unknown_not_falsely_called_isomorphic(self):
        c6 = (6, tuple((i, (i + 1) % 6) for i in range(6)))
        two_triangles = (6, ((0, 1), (1, 2), (2, 0),
                             (3, 4), (4, 5), (5, 3)))
        self.assertEqual(joint_wl_separation(c6, two_triangles)["conclusion"],
                         "INCONCLUSIVE")
        self.assertFalse(vf2pp_decision(c6, two_triangles)["isomorphic"])

    def test_wl_can_certify_nonisomorphism(self):
        star = (4, ((0, 1), (0, 2), (0, 3)))
        path = (4, ((0, 1), (1, 2), (2, 3)))
        self.assertEqual(joint_wl_separation(star, path)["conclusion"],
                         "CERTIFIED_NONISOMORPHIC_BY_INVARIANT")
        self.assertFalse(vf2pp_decision(star, path)["isomorphic"])
        self.assertTrue(vf2pp_decision(path, path)["isomorphic"])
        self.assertEqual(joint_wl_separation(path, path)["conclusion"],
                         "INCONCLUSIVE")

    def test_planner_solves_exact_training_objective(self):
        # Construct a tiny known instance: A covers tasks 0/1, B covers
        # tasks 1/2, C covers only task 0. An optimal unit order costs 4.
        patterns = ("A", "B", "C")
        cover = {"A": {0, 1}, "B": {1, 2}, "C": {0}}
        tasks = [SimpleNamespace(graphs=(f"x{i}", f"y{i}"))
                 for i in range(3)]
        def oracle(probe, target):
            if target.startswith("x"):
                return 0
            return int(int(target[1:]) in cover[probe])
        result = optimal_training_order(tasks, patterns, oracle, model="unit")
        self.assertEqual(result["training_objective"], 4)
        self.assertEqual(result["order"], ("A", "B", "C"))
        self.assertFalse(result["heldout_influenced_selection"])

    def test_method_registry_refuses_unconnected_solvers(self):
        live = {x["id"] for x in EXECUTABLE}
        self.assertIn("networkx_VF2pp", live)
        for item in FUTURE_ADAPTERS:
            self.assertNotIn(item["id"], live)
            self.assertEqual(item["status"], "NOT_INTEGRATED")

    def test_order_is_frozen_from_training_before_test(self):
        policies, freeze = frozen_policies(self.train)
        self.assertTrue(freeze["policies_only_read_training_cases"])
        self.assertEqual(set(policies["LEGIT021_PRIOR_APERTURES"]),
                         set(policies["CLASSICAL_DP_OPTIMAL_TRAINING_QUESTIONS"]))
        payload = json.dumps(freeze["full_source_orders"], sort_keys=True,
                             separators=(",", ":")).encode()
        from hashlib import sha256
        self.assertEqual(sha256(payload).hexdigest(),
                         freeze["sha256_frozen_before_heldout"])

    def test_external_run_preserves_two_separate_acceptance_contracts(self):
        packet = run()
        self.assertEqual(packet["status"], STATUS)
        self.assertEqual(packet["heldout_cases"], 28)
        self.assertTrue(packet["task_A_direct_graph_nonisomorphism"]
                        ["not_interchangeable_with_task_B"])
        self.assertTrue(packet["task_B_find_separating_hom_source"]
                        ["not_interchangeable_with_task_A"])
        self.assertEqual(packet["task_A_direct_graph_nonisomorphism"]
                         ["VF2pp_nonisomorphic"], 28)
        arms = packet["task_B_find_separating_hom_source"]["cases_by_policy"]
        self.assertEqual(len(arms), 5)
        for row in arms.values():
            self.assertEqual(row["heldout_cases"], 28)
            self.assertEqual(row["solved_hom_witness_cases"], 28)
            self.assertGreater(row["total_source_questions"], 0)
            self.assertTrue(all(item["receipt"][-1]["independently_checked"]
                                for item in row["per_case_evidence"]))
        self.assertIn("recursive autonomous self-improvement",
                      packet["not_demonstrated"])


if __name__ == "__main__":
    unittest.main()
