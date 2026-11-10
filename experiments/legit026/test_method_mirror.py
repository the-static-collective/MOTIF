"""LEGIT-026 method-of-question-invention tests, including forged evidence."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
for name in ("legit021", "legit022", "legit023", "legit025"):
    sys.path.insert(0, str(HERE.parent / name))
sys.path.insert(0, str(HERE))
import meta
from research import find_blindspots, generate_extensions, grammar, HOLD, _spectrum
from worlds import (TRAIN_SEEDS, EVAL_SEEDS, synthetic_world,
                    training_worlds, evaluation_worlds)


class MethodMirrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orders, cls.receipt = meta.learn()

    def test_mutator_programs_are_bounded_and_distinguishable(self):
        proposals = meta.candidate_programs()
        self.assertEqual(len(proposals),24)
        self.assertEqual(len(set(tuple(r["program"]) for r in proposals)),24)
        self.assertTrue(any(tuple(x["program"]) == meta.PARENT for x in proposals))
        self.assertTrue(any(x["edits_from_parent"] >= 2 for x in proposals))
        self.assertTrue(all(len(x["operators"]) == 3 for x in proposals))
        with self.assertRaises(HOLD):
            meta.compile_program(("EXEC", "SHELL", "INJECT"), {})

    def test_train_and_future_seed_lists_are_disjoint_and_predeclared(self):
        self.assertEqual(TRAIN_SEEDS,(26001,26002))
        self.assertEqual(EVAL_SEEDS,(26003,26004))
        self.assertFalse(set(TRAIN_SEEDS) & set(EVAL_SEEDS))
        training, origin=training_worlds()
        self.assertEqual(len(training),4)
        self.assertEqual(set(training),{
            "atlas_old_training", "prior_025_random_8",
            "research_train_seed_26001","research_train_seed_26002"})
        for label in ("research_train_seed_26001",
                      "research_train_seed_26002"):
            self.assertTrue(origin[label][
                "five_node_answer_unseen_during_selection"])
            self.assertEqual(origin[label]["draws"],1000)

    def test_source_grammar_same_for_every_candidate(self):
        train,_=meta.training_matrix()
        eligible={x["atlas_source_id"] for x in generate_extensions()}
        for recipe in meta.candidate_programs():
            order=meta.compile_program(recipe["program"],train)
            self.assertEqual(len(order),21)
            self.assertEqual(set(order),eligible)

    def test_cv_and_mutation_selection_do_not_open_future_worlds(self):
        matrix,_=meta.training_matrix()
        with patch("meta.evaluation_worlds",
                   side_effect=AssertionError("future leaked to training")):
            packet=meta.cross_validate(matrix)
            self.assertTrue(packet["no_future_evaluation_data_consulted"])
            order=meta.compile_program(packet["adopted_program"],matrix)
            self.assertEqual(len(order),21)
        candidate=packet["best_training_crossvalidation_candidate"]
        parent=packet["parent_crossvalidation"]
        if packet["proposed_rewrite_promoted_from_training_only"]:
            self.assertLess(candidate["policy_selection_objective"],
                            parent["policy_selection_objective"])
            self.assertNotEqual(tuple(packet["adopted_program"]),meta.PARENT)
        else:
            self.assertEqual(tuple(packet["adopted_program"]),meta.PARENT)
            self.assertIsNotNone(packet["rejection_reason_if_unimproved"])

    def test_frozen_orders_and_actual_prior_cartridge_are_recoverable(self):
        frozen=json.dumps(self.orders,sort_keys=True,
                          separators=(",",":")).encode()
        self.assertEqual(sha256(frozen).hexdigest(),self.receipt[
            "frozen_sha256_before_eval_world_loading"])
        self.assertTrue(self.receipt[
            "future_world_generator_not_called_in_training"])
        self.assertEqual(self.orders["PRIOR_025_FROZEN"][0],30)
        self.assertEqual(len(set(self.orders["METHOD_MIRROR_ADOPTED"])),21)
        self.assertEqual(set(self.orders["EXACT_TRAINING_DP_CLASSICAL"]),
                         set(self.orders["METHOD_MIRROR_ADOPTED"]))

    def test_exact_training_dp_matches_brute_exhaustive_ordering(self):
        from itertools import permutations
        sources=[{"atlas_source_id":i} for i in (30,31,32)]
        cases = [
            {"answers":{30:(0,1),31:(0,0),32:(0,1)}},
            {"answers":{30:(0,0),31:(0,1),32:(0,1)}},
            {"answers":{30:(0,0),31:(0,0),32:(0,1)}},
        ]
        with patch("meta.source_catalog",return_value=tuple(sources)):
            solution=meta.exact_training_dp({"toy":cases})
        def objective(order):
            return sum(next(j+1 for j,source in enumerate(order)
                            if row["answers"][source][0] !=
                               row["answers"][source][1]) for row in cases)
        truth=min(objective(p) for p in permutations((30,31,32)))
        self.assertEqual(solution["exact_training_questions"],truth)
        self.assertEqual(objective(solution["order"]),truth)
        self.assertEqual(solution["optimality_scope"],
                         "known_finite_training_pairs_only")

    def test_future_worlds_have_real_new_graphs_and_old_aperture_failures(self):
        import networkx as nx
        _, future= None, None
        cases, origin=synthetic_world(26003)
        self.assertGreaterEqual(len(cases),4)
        self.assertTrue(origin[
            "five_node_answer_unseen_during_selection"])
        for ids,(a,b) in cases:
            self.assertEqual(a[0],8)
            self.assertEqual(b[0],8)
            self.assertEqual(_spectrum(a,grammar()),_spectrum(b,grammar()))
            from research import _graph
            self.assertFalse(nx.is_isomorphic(_graph(a),_graph(b)))

    def test_malformed_oracle_output_cannot_promote_false_witness(self):
        _,heldout,_=find_blindspots()
        tiny={"first":heldout[:1]}
        with patch("meta.hom_count",return_value={"value":0}):
            with self.assertRaises(HOLD):
                meta.evaluate_worlds(tiny,{"candidate":self.orders[
                    "METHOD_MIRROR_ADOPTED"]})

    def test_full_future_replay_is_checked_per_negative_and_positive_probe(self):
        report=meta.run()
        self.assertEqual(report["status"],meta.STATUS)
        self.assertEqual(report["source_count"],21)
        self.assertTrue(report["same_source_grammar_for_all_competing_methods"])
        self.assertTrue(report[
            "generated_policy_rewrites_are_engineer_specified_grammar"])
        self.assertIn("cross-domain general mathematical strategy improvement",
                      report["claims_not_demonstrated"])
        self.assertEqual(set(report["evaluation"]),{
            "known_atlas_regression", "future_seed_26003",
            "future_seed_26004"})
        for world, arms in report["evaluation"].items():
            counts={x["cases"] for x in arms.values()}
            self.assertEqual(len(counts),1)
            self.assertGreaterEqual(next(iter(counts)),4)
            for label, arm in arms.items():
                self.assertEqual(arm["resolved"],arm["cases"],
                                 (world,label))
                self.assertEqual(sum(x["questions"] for x in
                                     arm["full_receipts"]),
                                 arm["questions"])
                self.assertTrue(all(x["independently_checked"]
                                   for row in arm["full_receipts"]
                                   for x in row["all_attempted_questions"]))
                self.assertTrue(all(row["all_attempted_questions"][-1][
                                    "separates"] for row in arm["full_receipts"]))


if __name__ == "__main__":
    unittest.main()
