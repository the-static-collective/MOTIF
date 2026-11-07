"""Regression and hostile controls for QC-001. Standard library, offline."""
import unittest
from dataclasses import replace
from quantum_code import (
    Observation, World, Candidate, KNOWN_PRIMITIVES, context_blind_score,
    fixture, local_review, preview, propose, route, run_experiment, score,
)


class QuantumCodeTrial(unittest.TestCase):
    def setUp(self):
        self.train, self.valid, self.test = fixture()
        self.proposals = propose(self.train)
        self.reviewed = local_review(self.proposals, self.train, self.valid)

    def test_predeclared_counts(self):
        result = run_experiment()
        self.assertEqual((result["train_count"], result["validation_count"],
                          result["test_count"]), (22, 22, 22))
        self.assertEqual((result["proposed"], result["locally_reviewed"]), (11, 10))
        self.assertEqual(result["held_candidate_keys"],
                         [["A", "CUP", "shortcut"]])

    def test_independent_held_out_examples(self):
        self.assertEqual(score(self.reviewed, self.test),
                         {"covered": 20, "correct": 20, "errors": 0})

    def test_equal_data_classical_control(self):
        result = run_experiment()
        self.assertEqual(result["same_data_classical_table"],
                         result["typed_lookup"])
        self.assertEqual(result["frozen_primitive"]["covered"], 8)
        self.assertIsNone(result["frozen_route_final"]["A"])
        self.assertIsNone(result["frozen_route_final"]["B"])

    def test_decoder_ablation_reveals_collision(self):
        blind = context_blind_score(self.train, self.test)
        self.assertEqual(blind["covered"], 22)
        self.assertEqual(blind["correct"], 18)
        self.assertEqual(blind["errors"], 4)
        a = preview(World("FORK", "A"), "curve", self.reviewed)
        b = preview(World("FORK", "B"), "curve", self.reviewed)
        self.assertEqual((a.carrier, b.carrier), ("CUP", "LOOP"))

    def test_feedback_changes_next_reachable_actions(self):
        self.assertEqual(route(World("POINT", "A"),
                               ("extend", "branch", "curve", "close"),
                               self.reviewed).carrier, "LOOP")
        self.assertEqual(route(World("POINT", "B"),
                               ("extend", "branch", "curve", "release"),
                               self.reviewed).carrier, "CUP")
        fixed = tuple(r for r in self.reviewed if r.key in KNOWN_PRIMITIVES)
        self.assertIsNone(route(World("POINT", "A"),
                                ("extend", "branch", "curve", "close"), fixed))

    def test_same_projection_not_same_history(self):
        beginning = World("LOOP", "A")
        after = route(beginning, ("open", "close"), self.reviewed)
        self.assertEqual(after.observable(), beginning.observable())
        self.assertNotEqual(after.witness(), beginning.witness())
        self.assertEqual(len(after.steps), 2)

    def test_unknown_decoder_holds(self):
        self.assertIsNone(preview(World("FORK", "C"), "curve", self.reviewed))

    def test_unvalidated_rule_holds(self):
        self.assertIsNone(preview(World("CUP", "A"), "shortcut", self.reviewed))
        self.assertTrue(any(c.key == ("A", "CUP", "shortcut")
                            for c in self.proposals))

    def test_conflicting_train_results_not_promoted(self):
        rows = list(self.train)
        i = next(i for i, r in enumerate(rows)
                 if r.key == ("A", "FORK", "curve"))
        rows[i] = replace(rows[i], result="LOOP")
        candidates = propose(tuple(rows))
        self.assertNotIn(("A", "FORK", "curve"),
                         {c.key for c in candidates})

    def test_duplicate_training_receipt_rejected(self):
        with self.assertRaises(ValueError):
            propose(self.train + (self.train[0],))

    def test_cross_split_receipt_rejected(self):
        forged = (replace(self.valid[0], evidence_id=self.train[0].evidence_id),)
        with self.assertRaises(ValueError):
            local_review(self.proposals, self.train, forged)

    def test_fake_provenance_rejected(self):
        forged = replace(self.train[0], provenance="REAL_WORLD")
        with self.assertRaises(ValueError):
            propose((forged,) + self.train[1:])

    def test_cross_split_training_rejected(self):
        with self.assertRaises(ValueError):
            propose(self.valid)

    def test_validation_falsifies_candidate(self):
        contradicted = list(self.valid)
        i = next(i for i, r in enumerate(contradicted)
                 if r.key == ("B", "FORK", "curve"))
        contradicted[i] = replace(contradicted[i], result="CUP")
        reviewed = local_review(self.proposals, self.train, tuple(contradicted))
        self.assertNotIn(("B", "FORK", "curve"), {r.key for r in reviewed})

    def test_observed_noop_does_not_preview(self):
        sample = Observation("TRAIN/noop1", "TRAIN", "A", "LOOP", "stay", "LOOP")
        # The learner can identify a lookup, but preview refuses no-op inflation.
        other = replace(sample, evidence_id="TRAIN/noop2")
        v1 = replace(sample, evidence_id="VALIDATE/noop1", split="VALIDATE")
        v2 = replace(sample, evidence_id="VALIDATE/noop2", split="VALIDATE")
        rules = local_review(propose((sample, other)), (sample, other), (v1, v2))
        self.assertIsNone(preview(World("LOOP", "A"), "stay", rules))


if __name__ == "__main__":
    unittest.main()
