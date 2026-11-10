"""LEGIT-025 adversarial protocol and independent per-question witness tests."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
for name in ("legit021", "legit022", "legit023"):
    sys.path.insert(0, str(HERE.parent / name))
sys.path.insert(0, str(HERE))

from graph_inventor import grammar, reference_count
from methods import hom_count
from research import (
    find_blindspots, generate_extensions, make_plan,
    transfer_tasks, run, _evaluate, _spectrum, _graph, HOLD, STATUS,
)


class ApertureEscapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.training, cls.heldout, cls.origin = find_blindspots()
        cls.policies, cls.plan = make_plan(cls.training)
        cls.report = run()

    def test_true_external_graphs_and_old_grammar_blind_spots(self):
        self.assertEqual(self.origin["seven_vertex_graphs_inspected"],1044)
        self.assertEqual(self.origin["collisions_found_after_seeing_old_probe_answers"],10)
        self.assertEqual(len(self.training),4)
        self.assertEqual(len(self.heldout),6)
        self.assertTrue(self.origin[
            "new_five_vertex_answers_not_seen_in_challenge_selection"])
        self.assertEqual(self.origin["external_graph_data_sha256"],
            "73fc416df0164923607751cb759f4ae81deb5f6550bf25be59c86de3b747e41d")
        known={tuple(ids) for ids, _ in self.training+self.heldout}
        self.assertEqual(len(known),10)
        for ids, (a,b) in self.training+self.heldout:
            self.assertEqual(_spectrum(a, grammar()), _spectrum(b, grammar()))
            self.assertNotEqual(a,b)

    def test_historical_five_vertex_grammar_not_falsely_new(self):
        import networkx as nx
        current=generate_extensions()
        classical=tuple(x for x in grammar(5) if x[0]==5)
        self.assertEqual(len(current),21)
        self.assertEqual(len(classical),21)
        for x in current:
            self.assertTrue(any(nx.is_isomorphic(_graph(x["source"]),_graph(p))
                                for p in classical))
        self.assertTrue(self.report["generation"][
            "same_as_LEGIT021_existing_classical_5_grammar"])
        self.assertFalse(self.report["generation"][
            "not_autonomous_algorithm_invention"] is False)

    def test_composed_parent_is_real_not_fabricated_novelty(self):
        for item in generate_extensions():
            n, edges=item["source"]
            self.assertEqual(n,5)
            self.assertIn(item["parent"],grammar())
            self.assertEqual(item["parent"][0],4)
            self.assertEqual(tuple(sorted(item["parent"][1] + tuple(
                (i,4) for i in item["new_vertex_neighbors"]))),edges)
            self.assertEqual(item["operator_arity"],
                             len(item["new_vertex_neighbors"]))

    def test_next_question_is_really_generated_after_known_inadequacy(self):
        self.assertIn("four-vertex",
            self.plan["next_relevant_question"])
        self.assertEqual(self.plan["candidate_count"],21)
        self.assertGreater(self.plan["leaf_candidate_count"],1)
        cartridge=self.plan["selected_training_cartridge"]
        self.assertEqual(cartridge["operator_arity"],1)
        self.assertEqual(cartridge["generated_source"]["vertices"],5)
        self.assertEqual(cartridge["source_parent"]["vertices"],4)
        self.assertTrue(cartridge["verified_training_coverage"])
        self.assertTrue(cartridge[
            "classical_five_vertex_grammar_already_existed_in_LEGIT021"])

    def test_classical_baseline_has_identical_grammar_and_training_information(self):
        orders=self.plan["frozen_source_orders"]
        expected=set(s["atlas_source_id"] for s in generate_extensions())
        for name, source_ids in orders.items():
            self.assertEqual(len(source_ids),21,name)
            self.assertEqual(set(source_ids),expected,name)
        self.assertEqual(orders["COMPOSED_LEAF_FIRST_TRAINED"][0],
                         self.plan["selected_training_cartridge"]["atlas_source_id"])
        self.assertTrue(self.plan["no_heldout_five_probe_answers_used"])
        frozen=json.dumps(orders,sort_keys=True,separators=(",",":")).encode()
        self.assertEqual(sha256(frozen).hexdigest(),
                         self.plan["policies_frozen_sha256"])

    def test_future_tasks_are_strictly_heldout_derived_not_same_train_pairs(self):
        future=transfer_tasks(self.heldout)
        self.assertEqual(set(future),{"atlas_original_7",
                                     "atlas_complements_7",
                                     "atlas_join_universal_8",
                                     "seeded_random_8"})
        train_ids={ids for ids,_ in self.training}
        for label,cases in future.items():
            self.assertEqual(len(cases),8 if label=="seeded_random_8" else 6)
            if label!="seeded_random_8":
                self.assertFalse(train_ids & {ids for ids,_ in cases})
            self.assertTrue(all(g[0] == (8 if label.endswith("_8") else 7)
                                for _,pair in cases for g in pair))
            self.assertTrue(all(_spectrum(pair[0],grammar()) ==
                                _spectrum(pair[1],grammar())
                                for _,pair in cases))

    def test_adversarial_wrong_source_count_refused_by_independent_enumerator(self):
        case=self.heldout[:1]
        source=generate_extensions()[1]["source"]
        with patch("research.hom_count",return_value={"value":0}):
            with self.assertRaises(HOLD):
                _evaluate(case,[source],"MALICIOUS_FALSE_COUNT")

    def test_every_attempt_including_negative_probe_verified(self):
        archive=self.report["transferred_research"]
        self.assertEqual(set(archive),{
            "atlas_original_7","atlas_complements_7",
            "atlas_join_universal_8","seeded_random_8"})
        for family,arms in archive.items():
            old=arms["NO_ADAPTATION_OLD_FOUR"]
            expected=8 if family=="seeded_random_8" else 6
            self.assertEqual(old["resolved"],0)
            self.assertEqual(old["cases"],expected)
            self.assertEqual(old["total_questions"],10*expected)
            for method in ("CANONICAL_FIVE_CLASSICAL",
                           "STRONG_CLASSICAL_TRAINED_GREEDY",
                           "COMPOSED_LEAF_FIRST_TRAINED"):
                arm=arms[method]
                self.assertEqual(arm["resolved"],expected,(family,method))
                self.assertEqual(arm["cases"],expected)
                for task in arm["all_question_receipts"]:
                    self.assertTrue(task["resolved_by_hom_witness"])
                    self.assertEqual(len(task["all_attempted_question_receipts"]),
                                     task["questions"])
                    self.assertTrue(all(x["independent_enumerator_agrees"] for x
                                        in task["all_attempted_question_receipts"]))
                    self.assertTrue(task["all_attempted_question_receipts"][-1]["separates"])

    def test_separately_seeded_future_population_is_not_atlas_derivative(self):
        from new_population import independent_synthetic_eight
        cases, origin=independent_synthetic_eight()
        self.assertEqual(origin["draws"],1000)
        self.assertEqual(origin["vertex_count"],8)
        self.assertEqual(origin["random_seed"],25025)
        self.assertEqual(len(cases),8)
        self.assertTrue(origin["not_derived_from_seven_vertex_Atlas_pairs"])
        self.assertTrue(origin["no_five_vertex_responses_used_for_challenge_selection"])
        self.assertTrue(origin["not_independently_authored_or_externally_blinded"])
        self.assertEqual(self.report["separate_eight_vertex_population"],origin)

    def test_source_cartridge_reused_without_retraining_after_transfer(self):
        chosen=self.plan["selected_training_cartridge"]
        all_arms=self.report["transferred_research"]
        for family in all_arms:
            arm=all_arms[family]["COMPOSED_LEAF_FIRST_TRAINED"]
            first_witnesses=[case["all_attempted_question_receipts"][0]["source"]
                             for case in arm["all_question_receipts"]]
            # Same frozen first query, though evidence values change.
            self.assertTrue(all(x==chosen["generated_source"]
                                for x in first_witnesses))
        self.assertEqual(self.report["training_frozen_plan"][
            "policies_frozen_sha256"],chosen["source_frozen_sha256"])

    def test_does_not_promote_method_reuse_as_independent_math(self):
        self.assertEqual(self.report["status"],STATUS)
        self.assertIn("Task selection intentionally conditioned on old-probe failure",
                      self.report["limitations"])
        self.assertIn("Heldout complement and universal-join cases are dependent transformations",
                      self.report["limitations"])
        self.assertIn("Only one constructed probe-selection episode; not autonomous compounding",
                      self.report["limitations"])


if __name__ == "__main__":
    unittest.main()
