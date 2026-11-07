"""Checks for QC-003: no supplied anchors or cues; no false promotion."""
from dataclasses import replace
import unittest

from aperture import (
    GENERATED, LOCAL, PROVENANCE, STATUS, Graph, Episode, World, edge,
    infer_delta, local_feature, feature, candidate_feature, labelled,
    closure, independent_bridge, oracle_after, sample_graph, fixture,
    discover, review, preview, enumerate_futures, equivalent_new,
    evaluate_on_test, whole_graph_control, compile_macro, replay_macro,
    run, apply_template,
)


class ApertureTests(unittest.TestCase):
    def setUp(self):
        self.train, self.valid, self.test = fixture()
        self.candidate = discover(self.train)
        self.rules = review(self.candidate, self.train, self.valid)

    def test_data_freeze(self):
        self.assertEqual((len(self.train), len(self.valid), len(self.test)),
                         (6, 4, 8))
        self.assertIsNotNone(self.rules)
        self.assertEqual(len(self.candidate.effects), 2)
        self.assertEqual(self.rules.status, STATUS)

    def test_no_operation_cue_or_supplied_anchor_in_episode(self):
        for row in self.train:
            self.assertFalse(hasattr(row, "action"))
            self.assertFalse(hasattr(row, "anchors"))
            self.assertFalse(hasattr(row, "signal"))

    def test_inferred_anchors_and_multi_fresh_node_effects(self):
        for row in self.train:
            anchors, effect = infer_delta(row)
            self.assertEqual(len(anchors), 2)
            self.assertEqual(effect.new_roles, 2)
            self.assertEqual(effect.old_roles, 2)
            self.assertEqual(len(effect.add_edges), 3)
            self.assertIn(edge(*anchors), row.before.edges)

    def test_primal_edit_schemas_alpha_invariant(self):
        for i in range(0, len(self.train), 2):
            one, two = self.train[i:i+2]
            self.assertEqual(one.before, two.before)
            _, t1 = infer_delta(one)
            _, t2 = infer_delta(two)
            self.assertNotEqual(t1, t2)
        distinct = {infer_delta(row)[1] for row in self.train}
        self.assertEqual(distinct, set(self.candidate.effects))

    def test_all_local_descriptors_fail_to_discriminate(self):
        for i in range(0, len(self.train), 2):
            one, two = self.train[i:i+2]
            a1, _ = infer_delta(one)
            a2, _ = infer_delta(two)
            for name in LOCAL:
                self.assertEqual(local_feature(one.before, a1, name),
                                 local_feature(two.before, a2, name),
                                 msg=(i, name))
        self.assertTrue(self.candidate.locality_failed)
        for name in LOCAL:
            self.assertIsNone(candidate_feature(labelled(self.train), name))

    def test_feature_program_is_constructed_on_failure(self):
        self.assertEqual(self.candidate.feature_program, GENERATED)
        self.assertEqual(self.candidate.truth_table,
                         (("False", next(t.seal() for t in self.candidate.effects
                                          if t.remove_edges == ())),
                          ("True", next(t.seal() for t in self.candidate.effects
                                         if t.remove_edges))))

    def test_closure_reachability_divides_effects(self):
        for row in self.train:
            anchors, effect = infer_delta(row)
            alternate = feature(row.before, anchors, GENERATED)
            self.assertEqual(alternate, bool(effect.remove_edges))

    def test_independently_implemented_union_find_agrees(self):
        for row in self.test:
            anchors, _ = infer_delta(row)
            self.assertEqual(feature(row.before, anchors, GENERATED),
                             not independent_bridge(row.before, anchors))

    def test_heldout_longer_and_perturbed_graphs(self):
        summary = evaluate_on_test(self.rules, self.test)
        self.assertEqual(summary, {"total": 8, "covered": 8, "correct": 8,
                                   "wrong": 0, "held": 0})

    def test_all_edges_are_predicted_not_just_selected_targets(self):
        for i in range(0, len(self.test), 2):
            graph = self.test[i].before
            result = whole_graph_control(self.rules, graph)
            self.assertEqual(result["predicted_edges"], len(graph.edges))
            self.assertEqual(result["oracle_edges"], len(graph.edges))
            self.assertEqual(result["correct"], len(graph.edges))
            self.assertEqual((result["false_predictions"], result["missed"]),
                             (0, 0))

    def test_absence_of_anchor_cue_yields_multiple_futures(self):
        candidates = enumerate_futures(World(self.test[0].before), self.rules)
        self.assertEqual(len(candidates), len(self.test[0].before.edges))
        self.assertGreater(len(candidates), 20)

    def test_labels_are_not_conditions(self):
        graph, (cycle, bridge) = sample_graph("totally-renamed-world", 30, 30)
        self.assertTrue(feature(graph, cycle, GENERATED))
        self.assertFalse(feature(graph, bridge, GENERATED))
        self.assertIsNotNone(preview(World(graph), cycle, self.rules))
        self.assertIsNotNone(preview(World(graph), bridge, self.rules))

    def test_global_graph_size_is_not_sole_explanation(self):
        for i in range(0, len(self.test), 2):
            cycle_row, bridge_row = self.test[i:i+2]
            self.assertEqual(cycle_row.before, bridge_row.before)
            self.assertEqual(len(cycle_row.before.vertices),
                             len(bridge_row.before.vertices))

    def test_local_dsl_ablation_is_a_genuine_hold(self):
        self.assertFalse(any(candidate_feature(labelled(self.train), x)
                             for x in LOCAL))

    def test_decoder_reentry_changes_its_own_relational_class(self):
        graph, (_, bridge) = sample_graph("evolve", 20, 20)
        start = World(graph)
        first = preview(start, bridge, self.rules)
        second = preview(first, bridge, self.rules)
        self.assertTrue(independent_bridge(graph, bridge))
        self.assertFalse(independent_bridge(first.graph, bridge))
        self.assertFalse(independent_bridge(second.graph, bridge))
        self.assertNotEqual(first.history[-1].effect, second.history[-1].effect)
        self.assertEqual(len(second.history), 2)

    def test_recursive_output_compiles_pinned_macro(self):
        graph, (_, bridge) = sample_graph("macro", 20, 20)
        start = World(graph)
        first = preview(start, bridge, self.rules)
        final = preview(first, bridge, self.rules)
        macro = compile_macro(start, final, self.rules)
        self.assertEqual(replay_macro(start, macro, self.rules), final)
        self.assertEqual(len(macro.steps), 2)

    def test_revoked_validation_pin_holds_macro(self):
        graph, (_, bridge) = sample_graph("revoke", 20, 20)
        start = World(graph)
        final = preview(preview(start, bridge, self.rules), bridge, self.rules)
        macro = compile_macro(start, final, self.rules)
        fake = replace(self.rules, valid_digest="changed")
        self.assertIsNone(replay_macro(start, macro, fake))

    def test_forged_macro_goal_and_status_hold(self):
        graph, (_, bridge) = sample_graph("forge", 20, 20)
        start = World(graph)
        final = preview(preview(start, bridge, self.rules), bridge, self.rules)
        macro = compile_macro(start, final, self.rules)
        self.assertIsNone(replay_macro(start, replace(macro, expected_final="fake"),
                                       self.rules))
        self.assertIsNone(replay_macro(start, replace(macro, status="INSTALLED"),
                                       self.rules))

    def test_nonreconstructible_candidate_refused(self):
        fake = replace(self.candidate, train_digest="fabricated")
        with self.assertRaises(ValueError):
            review(fake, self.train, self.valid)

    def test_changed_feature_without_training_proof_refused(self):
        fake = replace(self.candidate, feature_program=LOCAL[0])
        with self.assertRaises(ValueError):
            review(fake, self.train, self.valid)

    def test_conflicting_validation_refuses_the_grammar(self):
        records = list(self.valid)
        # Retain the same base graph and inferred anchors, but use the other
        # geometric effect as the observational result.
        records[0] = replace(records[0], after=records[1].after)
        self.assertIsNone(review(self.candidate, self.train, tuple(records)))

    def test_duplicate_receipt_rejected(self):
        with self.assertRaises(ValueError):
            discover(self.train+(self.train[0],))

    def test_wrong_split_and_provenance_rejected(self):
        with self.assertRaises(ValueError):
            discover(self.valid)
        fake = replace(self.train[0], provenance="PUBLIC_EVIDENCE")
        with self.assertRaises(ValueError):
            discover((fake,)+self.train[1:])

    def test_reused_training_receipt_validation_refused(self):
        changed = replace(self.valid[0], evidence_id=self.train[0].evidence_id)
        with self.assertRaises(ValueError):
            review(self.candidate, self.train, (changed,)+self.valid[1:])

    def test_nonlocal_old_edge_edit_refused(self):
        graph, (cyclic, bridge) = sample_graph("nonlocal", 16, 16)
        after = oracle_after(graph, cyclic, "nonlocal")
        # Cut another unrelated existing edge without a receipt.
        corrupted = Graph.of(after.vertices, after.edges-{bridge})
        row = Episode("TRAIN/bad", "TRAIN", graph, corrupted)
        with self.assertRaises(ValueError):
            infer_delta(row)

    def test_too_many_fresh_vertices_refused(self):
        graph, (cyclic, _) = sample_graph("excess", 16, 16)
        after = oracle_after(graph, cyclic, "excess")
        altered = Graph.of(after.vertices|{"extra1", "extra2"},
                           after.edges|{edge("extra1", "extra2")})
        row = Episode("TRAIN/excess", "TRAIN", graph, altered)
        with self.assertRaises(ValueError):
            infer_delta(row)

    def test_unknown_edge_or_unauthorized_status_holds(self):
        before = World(self.test[0].before)
        self.assertIsNone(preview(before, ("ghost", "phantom"), self.rules))
        with self.assertRaises(ValueError):
            preview(before, next(iter(before.graph.edges)),
                    replace(self.rules, status="INSTALL"))

    def test_unvalidated_grammar_is_not_executable(self):
        self.assertIsNone(preview(World(self.test[0].before),
                                  next(iter(self.test[0].before.edges)), None))

    def test_report_preserves_classical_equality(self):
        report = run()
        self.assertEqual(report["selected_program"], GENERATED)
        self.assertEqual(report["heldout_prediction"]["correct"], 8)
        self.assertTrue(report["classical_union_find_oracle_all_edges_tied"])
        self.assertTrue(report["two_phase_source_pinned_replay"])
        self.assertEqual(report["outside_actions"], 0)


if __name__ == "__main__":
    unittest.main()
