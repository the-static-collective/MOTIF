"""MOTIF-010: falsifiable synthetic intervention + tree cartridge tests."""
import inspect
import json
import unittest
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "009"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import oracle
import scientist
import benchmark
from cartridge import CartridgeBay, HOLD, export_cartridge, validate_cartridge


class ScientistTests(unittest.TestCase):

    def setUp(self):
        self.world = oracle.world("source_a", 11)
        self.natural = oracle.natural_observations(self.world)
        self.initial = scientist.candidate_cartridges(self.natural,
                                                       self.world.controls)

    def test_six_hidden_rules_are_programmatically_distinct(self):
        self.assertEqual(len(oracle.FAMILIES), 6)
        patterns = set()
        for name in oracle.FAMILIES:
            w = oracle.world(name, 11)
            patterns.add(tuple(scientist.validated_result(
                oracle.intervene(w, a, b, 10 + 2*int(a) + int(b)))
                               for a,b in scientist.OPTIONS))
        self.assertEqual(len(patterns), 6)

    def test_natural_correlations_cannot_separate_four_explanations(self):
        for name in oracle.FAMILIES:
            w = oracle.world(name, 11)
            initial = oracle.natural_observations(w)
            self.assertEqual(len(scientist.candidate_cartridges(initial,
                                                                 w.controls)), 4)
            for obs in initial:
                x, y = scientist.controls_present(obs, w.controls)
                self.assertEqual(x, y)

    def test_learner_cannot_import_oracle_or_hidden_rules(self):
        source = inspect.getsource(scientist)
        self.assertNotIn("import oracle", source)
        self.assertNotIn("from oracle import", source)
        self.assertNotIn("_hidden_rule(", source)
        self.assertNotIn("test_world(", source)

    def test_initial_cartridges_are_real_roundtrippable_trees(self):
        self.assertEqual(len(self.initial), 4)
        for tree in self.initial:
            roundtrip = validate_cartridge(export_cartridge(tree))
            self.assertEqual(roundtrip, tree)
            self.assertEqual(tree.status, "PROPOSAL_ONLY")
            self.assertEqual(tree.evidence_count, 2)
            self.assertEqual(len(tree.leaves), 4)
            self.assertNotIn("w11_", export_cartridge(tree))

    def test_intervention_is_on_demand_and_changes_input_graph(self):
        a = oracle.intervene(self.world, False, True, 2000)
        b = oracle.intervene(self.world, True, False, 2001)
        self.assertNotEqual(a.before, b.before)
        self.assertNotEqual(a.roles, b.roles)
        self.assertEqual({a.provenance, b.provenance},
                         {"SYNTHETIC_INTERVENTION"})

    def test_scientist_chooses_off_diagonal_informative_question(self):
        q = scientist.propose_intervention(self.initial)
        self.assertEqual((q.first, q.second), (False, True))
        self.assertEqual(q.information_gain_bits, 1.0)
        self.assertEqual(len(q.predicted_votes), 4)
        self.assertEqual(q.predicted_votes.count(True), 2)
        self.assertFalse(q.real_world_authority)
        self.assertEqual(q.action, "DO_SYNTHETIC_PORT_SETTINGS")

    def test_second_intervention_identifies_one_tree_in_every_world(self):
        for name in oracle.FAMILIES:
            w = oracle.world(name, 11)
            evidence = list(oracle.natural_observations(w))
            done = set()
            for index in range(2):
                possibilities = scientist.candidate_cartridges(evidence, w.controls)
                q = scientist.propose_intervention(possibilities, done)
                self.assertIsNotNone(q)
                self.assertEqual(q.information_gain_bits, 1.0)
                setting = (q.first, q.second)
                self.assertNotIn(setting, done)
                done.add(setting)
                evidence.append(oracle.intervene(w, *setting, 3000 + index))
            final = scientist.candidate_cartridges(evidence, w.controls)
            self.assertEqual(len(final), 1)
            for x,y in scientist.OPTIONS:
                output = oracle.intervene(w, x, y, 4000+2*int(x)+int(y))
                self.assertEqual(scientist.consensus(final, x, y),
                                 scientist.validated_result(output))

    def test_intervention_reduces_version_space_four_two_one(self):
        evidence = list(self.natural)
        counts = [len(scientist.candidate_cartridges(evidence, self.world.controls))]
        for step in range(2):
            current = scientist.candidate_cartridges(evidence, self.world.controls)
            q = scientist.propose_intervention(current)
            evidence.append(oracle.intervene(self.world, q.first, q.second,
                                              5000 + step))
            counts.append(len(scientist.candidate_cartridges(
                evidence, self.world.controls)))
        self.assertEqual(counts, [4, 2, 1])
        self.assertIsNone(scientist.propose_intervention(
            scientist.candidate_cartridges(evidence, self.world.controls)))

    def test_only_consensus_is_reported_before_inquiry(self):
        c = self.initial
        self.assertEqual(sum(scientist.consensus(c, x,y) is not None
                             for x,y in scientist.OPTIONS), 2)
        self.assertIsNone(scientist.consensus(c, False, True))
        self.assertIsNone(scientist.consensus(c, True, False))

    def test_two_passive_observations_preserve_ambiguity(self):
        evidence = list(self.natural)
        evidence += [oracle.natural_case(self.world, False, 5000),
                     oracle.natural_case(self.world, True, 5001)]
        remaining = scientist.candidate_cartridges(evidence, self.world.controls)
        self.assertEqual(len(remaining), 4)

    def test_adversarial_partial_graph_change_not_learned_as_outcome(self):
        case = self.natural[0]
        forged = replace(case, observed_after=case.before |
                         {("unrelated_change", case.roles[0])})
        with self.assertRaisesRegex(ValueError, "Partial or unrelated"):
            scientist.validated_result(forged)

    def test_non_synthetic_provenance_is_not_accepted(self):
        case = replace(self.natural[0], provenance="REAL_VERIFIED")
        with self.assertRaisesRegex(ValueError, "Unverified"):
            scientist.validated_result(case)

    def test_inconsistent_duplicate_evidence_refuses_to_predict(self):
        case = self.natural[0]
        _, target = case.roles
        false_claim = replace(case, observed_after=frozenset(
            (case.before - {("pending", target)}) | {("achieved", target)}))
        with self.assertRaises(scientist.NoConsistentExplanation):
            scientist.candidate_cartridges((case, false_claim),
                                          self.world.controls)

    def test_exported_id_is_content_fingerprint_not_signature(self):
        tree = self.initial[0]
        payload = json.loads(export_cartridge(tree))
        self.assertEqual(payload["status"], "PROPOSAL_ONLY")
        self.assertEqual(payload["schema"], "motif.decision-tree-cartridge.v0")
        self.assertNotIn("real_identity", payload)
        self.assertEqual(tree.id, payload["id"])
        self.assertTrue(all("w11_" not in json.dumps(row) for row in
                            (payload["first"], payload["second"])))

    def test_reviewed_closed_world_tree_accepts_absent_port_relations(self):
        review = benchmark.cartridge_review_example()
        self.assertTrue(review["semantic_roundtrip"])
        self.assertTrue(review["local_hold_first"])
        self.assertTrue(review["prediction_allowed_with_absent_false_ports"])
        self.assertTrue(review["revoke_blocks_predict"])
        self.assertFalse(review["real_world_authority"])

    def test_foreign_relation_graph_is_still_held(self):
        spec = oracle.world("exclusive", 11)
        evidence = list(oracle.natural_observations(spec))
        evidence += [oracle.intervene(spec,False,True,1993),
                     oracle.intervene(spec,True,False,1994)]
        car = scientist.candidate_cartridges(evidence, spec.controls)[0]
        bay = CartridgeBay()
        ticket = bay.offer(export_cartridge(car))
        local = [oracle.intervene(spec, a,b,20000+i*4+2*int(a)+int(b))
                 for i in range(2) for a,b in scientist.OPTIONS]
        bay.review(ticket, "ADMIT_PREDICT_ONLY", "TEST_STEWARD",local)
        before = local[0].before | {("unreviewed_new_predicate",local[0].roles[0])}
        with self.assertRaisesRegex(HOLD, "unreviewed"):
            bay.predict_admitted(ticket, before, local[0].roles)

    def test_budget_and_equal_observation_cost(self):
        spec = oracle.world("either", 11)
        results = [benchmark.evaluate_method(spec, name)
                   for name in benchmark.METHODS]
        self.assertEqual({x["oracle_calls_after_initial"] for x in results}, {2})
        self.assertEqual({x["initial_natural_observations"] for x in results}, {2})
        self.assertTrue(all(len(x["events"]) == 2 for x in results))
        self.assertTrue(all(x["wrong_covered_predictions"] == 0 for x in results))

    def test_fixed_diagnostic_control_is_strong_and_not_new_invention(self):
        for name in oracle.FAMILIES:
            record = benchmark.evaluate_method(oracle.world(name,11),
                                               "fixed_diagnostic")
            self.assertTrue(record["unique_model_identified"])
            self.assertEqual(record["heldout_coverage"], 1)

    def test_random_baseline_seed_order_is_repeatable(self):
        a = benchmark.control_order("source_a", 11)
        b = benchmark.control_order("source_a", 11)
        self.assertEqual(a,b)
        self.assertEqual(len(set(a)), 2)
        self.assertTrue(all(pair in scientist.OPTIONS for pair in a))

    def test_world_vocabulary_is_opaque_and_separate(self):
        first = oracle.world("source_a",11).controls
        second = oracle.world("source_b",11).controls
        third = oracle.world("source_a",23).controls
        self.assertFalse(set(vars(first).values()) & set(vars(second).values()))
        self.assertFalse(set(vars(first).values()) & set(vars(third).values()))

    def test_full_report_and_checked_in_receipt_match(self):
        r = benchmark.benchmark()
        self.assertEqual(r["summary"]["worlds"],
                         len(oracle.FAMILIES)*len(oracle.SEEDS))
        self.assertEqual(set(r["summary"]["families"]), set(oracle.FAMILIES))
        self.assertTrue(r["summary"]["classical_diagnostic_baseline_included"])
        self.assertEqual(r["summary"]["real_world_actions"], 0)
        self.assertFalse(r["review"]["checksum_authenticates_origin"])
        file = Path(__file__).parent / "experiment-results.json"
        self.assertEqual(r, json.loads(file.read_text()))


if __name__ == "__main__":
    unittest.main()
