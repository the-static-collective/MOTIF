"""Hostile controls and independent synthetic checks for MOTIF QC-002."""
import unittest
from dataclasses import replace
from structural import (
    PROVENANCE, STATUS, CUE_BRACE, CUE_SPLIT, CUE_DECOY,
    Graph, Episode, World, edge, extract, specimen, fixture, induce, review,
    preview, cycle4, search, exact_classical_control, compile_macro,
    replay_macro, named_graph_memorization, score, experiment_report,
    equivalent_fresh,
)


class StructuralQuantumCodeTests(unittest.TestCase):
    def setUp(self):
        self.train, self.valid, self.test = fixture()
        self.candidates = induce(self.train)
        self.rules = review(self.candidates, self.train, self.valid)
        self.seed = World(Graph.of({"p", "q"}, {("p", "q")}))

    def test_predeclared_dataset_and_rules(self):
        self.assertEqual((len(self.train), len(self.valid), len(self.test)),
                         (9, 6, 18))
        self.assertEqual(len(self.candidates), 3)
        self.assertEqual({r.signal for r in self.rules},
                         {CUE_SPLIT, CUE_BRACE})
        self.assertNotIn(CUE_DECOY, {r.signal for r in self.rules})

    def test_graph_facts_not_action_labels_are_learned(self):
        split = next(r for r in self.rules if r.signal == CUE_SPLIT)
        brace = next(r for r in self.rules if r.signal == CUE_BRACE)
        self.assertTrue(split.candidate.edit.remove_link)
        self.assertFalse(brace.candidate.edit.remove_link)
        self.assertEqual(split.candidate.edit.add_edges,
                         (("A", "N"), ("B", "N")))
        self.assertEqual(brace.candidate.edit.add_edges,
                         (("A", "N"), ("B", "N")))

    def test_holdout_larger_graphs_not_memorized(self):
        self.assertEqual(score(self.rules, self.test),
                         {"covered": 12, "correct": 12, "wrong": 0, "held": 6})
        self.assertEqual(named_graph_memorization(self.train, self.test),
                         {"covered": 0, "held": 18})

    def test_all_original_unrelated_edges_preserved(self):
        for row in self.test:
            result = preview(World(row.before), row.signal, row.anchors,
                             self.rules)
            if row.signal == CUE_DECOY:
                self.assertIsNone(result)
            else:
                self.assertTrue(equivalent_fresh(row.before, row.after, result.graph))
                self.assertEqual(row.before.edges & row.after.edges,
                                 row.before.edges & result.graph.edges)

    def test_label_rename_invariance_not_keyword_lookup(self):
        original = self.test[0]
        before = Graph.of({f"renamed::{v}" for v in original.before.vertices},
                          [(f"renamed::{x}", f"renamed::{y}")
                           for x, y in original.before.edges])
        anchors = tuple(f"renamed::{x}" for x in original.anchors)
        actual = preview(World(before), original.signal, anchors, self.rules)
        self.assertIsNotNone(actual)
        self.assertEqual(len(actual.graph.vertices), len(before.vertices)+1)
        self.assertEqual(len(actual.graph.edges)-len(before.edges), 2)

    def test_fresh_vertex_not_present_in_original(self):
        original = self.test[0]
        result = preview(World(original.before), original.signal,
                         original.anchors, self.rules)
        self.assertEqual(len(result.graph.vertices-original.before.vertices), 1)

    def test_no_predeclared_cycle_in_training_or_test(self):
        self.assertFalse(any(cycle4(ep.after) for ep in self.train))
        self.assertFalse(any(cycle4(ep.after) for ep in self.valid))
        self.assertFalse(any(cycle4(ep.after) for ep in self.test))

    def test_new_four_cycle_is_generated_by_a_two_step_plan(self):
        outcome = search(self.seed, self.rules, max_depth=2)
        self.assertEqual(outcome.depth, 2)
        self.assertTrue(cycle4(outcome.outcome.graph))
        self.assertEqual(len(outcome.outcome.graph.vertices), 4)
        self.assertEqual(len(outcome.outcome.history), 2)
        self.assertEqual(exact_classical_control(self.seed.graph, self.rules), 2)

    def test_one_step_goal_unreachable(self):
        self.assertIsNone(search(self.seed, self.rules, max_depth=1).outcome)
        self.assertIsNone(exact_classical_control(self.seed.graph, self.rules, 1))

    def test_without_learned_rules_no_discovery(self):
        self.assertIsNone(search(self.seed, (), max_depth=2).outcome)

    def test_reentry_produces_pinned_new_macro(self):
        goal = search(self.seed, self.rules)
        macro = compile_macro(self.seed, goal.outcome, self.rules)
        self.assertEqual(len(macro.steps), 2)
        self.assertEqual(macro.status, STATUS)
        self.assertEqual(replay_macro(self.seed, macro, self.rules), goal.outcome)
        self.assertEqual(goal.outcome.projection(), macro.expected_projection)
        self.assertNotEqual(self.seed.witness(), goal.outcome.witness())

    def test_revoked_dependency_holds_macro(self):
        goal = search(self.seed, self.rules)
        macro = compile_macro(self.seed, goal.outcome, self.rules)
        restricted = tuple(r for r in self.rules if r.signal != macro.steps[0].signal)
        self.assertIsNone(replay_macro(self.seed, macro, restricted))

    def test_tampered_macro_witness_holds(self):
        goal = search(self.seed, self.rules)
        macro = compile_macro(self.seed, goal.outcome, self.rules)
        self.assertIsNone(replay_macro(self.seed,
                                       replace(macro, expected_witness="fake"),
                                       self.rules))
        self.assertIsNone(replay_macro(self.seed,
                                       replace(macro, status="INSTALLED"),
                                       self.rules))

    def test_changed_decoder_signal_holds_macro(self):
        goal = search(self.seed, self.rules)
        macro = compile_macro(self.seed, goal.outcome, self.rules)
        bad = replace(macro,
                      steps=(replace(macro.steps[0], signal=CUE_DECOY),)+macro.steps[1:])
        self.assertIsNone(replay_macro(self.seed, bad, self.rules))

    def test_fake_edited_goal_not_compilable(self):
        goal = search(self.seed, self.rules)
        fake_graph = Graph.of(goal.outcome.graph.vertices, ())
        with self.assertRaises(ValueError):
            compile_macro(self.seed, replace(goal.outcome, graph=fake_graph),
                          self.rules)

    def test_invalid_provenance_rejected(self):
        bad = replace(self.train[0], provenance="REAL_GLYPH")
        with self.assertRaises(ValueError):
            induce((bad,)+self.train[1:])

    def test_duplicate_receipts_rejected(self):
        with self.assertRaises(ValueError):
            induce(self.train+(self.train[0],))

    def test_validation_ids_cannot_be_reused(self):
        forged = replace(self.valid[0], evidence_id=self.train[0].evidence_id)
        with self.assertRaises(ValueError):
            review(self.candidates, self.train, (forged,)+self.valid[1:])

    def test_fabricated_rule_envelope_rejected(self):
        forged = replace(self.candidates[0], training_digest="invented")
        with self.assertRaises(ValueError):
            review((forged,), self.train, self.valid)

    def test_insufficient_validation_holds(self):
        missing = tuple(r for r in self.valid if r.signal != CUE_SPLIT)
        rules = review(self.candidates, self.train, missing)
        self.assertNotIn(CUE_SPLIT, {r.signal for r in rules})

    def test_disagreement_in_training_holds_cue(self):
        rows = list(self.train)
        i = next(i for i, r in enumerate(rows) if r.signal == CUE_SPLIT)
        a, b = rows[i].anchors
        old = rows[i]
        # Effect is shifted from subdivision to a brace.
        n = next(iter(old.after.vertices-old.before.vertices))
        altered = Graph.of(old.before.vertices | {n},
                           old.before.edges | {edge(a, n), edge(b, n)})
        rows[i] = replace(old, after=altered)
        proposed = induce(tuple(rows))
        self.assertNotIn(CUE_SPLIT, {c.signal for c in proposed})

    def test_illegal_nonlocal_edit_holds_cue(self):
        before, anchors = specimen("bad", 3)
        a,b = anchors
        unrelated = next(e for e in before.edges if e != edge(a,b))
        new = "new"
        after = Graph.of(before.vertices|{new},
                         (before.edges-{unrelated})|{edge(a,new)})
        row = Episode("TRAIN/bad", "TRAIN", "sig-bad", anchors,before,after)
        with self.assertRaises(ValueError):
            extract(row)

    def test_two_new_vertices_outside_declared_grammar(self):
        before, (a,b) = specimen("two", 2)
        after = Graph.of(before.vertices|{"new0","new1"},
                         before.edges|{edge(a,"new0"),edge(b,"new1")})
        row = Episode("TRAIN/2", "TRAIN", "any", (a,b), before, after)
        with self.assertRaises(ValueError):
            extract(row)

    def test_unknown_signal_and_missing_anchors_hold(self):
        self.assertIsNone(preview(self.seed, "unknown", ("p","q"),self.rules))
        self.assertIsNone(preview(self.seed, CUE_SPLIT, ("p","ghost"),self.rules))

    def test_no_externally_executable_authority(self):
        self.assertEqual(experiment_report()["external_actions"], 0)
        self.assertEqual(experiment_report()["status"],
                         "SYNTHETIC_LOCAL_RESEARCH_ONLY")

    def test_exact_classical_comparator_ties(self):
        report = experiment_report()
        self.assertEqual(report["planned_depth"],report["exact_classical_minimum_depth"])
        self.assertEqual(report["heldout_graph_prediction"]["covered"],12)
        self.assertTrue(report["macro"]["replayed"])


if __name__ == "__main__":
    unittest.main()
