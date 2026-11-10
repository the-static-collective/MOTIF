"""Adversarial and reproducibility tests for a finite one-fact possibility field."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest
from math import comb

import field


class TestField001(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = field.AtlasOracle()
        cls.field = field.expand(observer=cls.oracle.observe, depth=3)
        cls.initial_queries = cls.oracle.queries

    def test_seed_is_actual_external_atlas_graph(self):
        witness = self.field["facts"][field.SEED_MASK]["evidence"]
        self.assertEqual(witness["atlas_id"], 31)
        self.assertTrue(witness["properties"]["tree"])
        self.assertEqual(witness["properties"]["m"], 4)
        self.assertTrue(field.verify_receipt(witness, field.AtlasOracle()))

    def test_one_fact_expands_to_all_three_step_labeled_states(self):
        self.assertEqual(len(self.field["facts"]), sum(comb(10, k) for k in range(4)))
        self.assertEqual(len(self.field["relations"]), 560)
        self.assertEqual(self.initial_queries, 176)
        self.assertEqual({k: sum(x["generation"] == k for x in self.field["facts"].values())
                          for k in range(4)}, {0: 1, 1: 10, 2: 45, 3: 120})
        self.assertTrue(all(x["status"] == "both_endpoints_observed"
                            for x in self.field["relations"]))
        self.assertEqual(len(set(f["evidence"]["atlas_id"]
                                 for f in self.field["facts"].values())), 27)

    def test_ideas_do_not_become_facts_without_observation(self):
        seen = 0
        def refuse(mask):
            nonlocal seen
            seen += 1
            if seen == 2:
                raise RuntimeError("No authoritative response")
            return self.oracle.observe(mask)
        with self.assertRaisesRegex(RuntimeError, "No authoritative response"):
            field.expand(depth=1, observer=refuse)
        with self.assertRaises(ValueError):
            field.expand(depth=1, observer=None)

    def test_lineage_is_connected_and_labeled(self):
        path = field.ancestry(self.field)
        self.assertEqual(len(path), 3)
        state = field.SEED_MASK
        for row in path:
            self.assertEqual(row["from_state"], state)
            bit = field.EDGES.index(tuple(row["edge"]))
            self.assertEqual(row["to_state"], state ^ (1 << bit))
            self.assertEqual(row["atlas_id"],
                self.field["facts"][row["to_state"]]["evidence"]["atlas_id"])
            state = row["to_state"]

    def test_tampering_and_rehashed_forgery_are_rejected(self):
        witness = self.field["facts"][field.SEED_MASK]["evidence"]
        adversarial = copy.deepcopy(witness)
        adversarial["atlas_id"] = 999
        self.assertFalse(field.verify_receipt(adversarial, field.AtlasOracle()))
        adversarial["receipt_sha256"] = hashlib.sha256(json.dumps(
            {k: v for k, v in adversarial.items() if k != "receipt_sha256"},
            sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertFalse(field.verify_receipt(adversarial, field.AtlasOracle()))

    def test_early_overgeneralization_fails_and_later_specialization_survives(self):
        all_rows = field.transition_rows(self.field)
        first = [x for x, r in zip(all_rows, self.field["relations"])
                 if r["parent_generation"] == 0]
        test = field.independent_atlas_rows(6)
        self.assertEqual(len(test), 2340)
        early = field.evaluate(field.mine_hypotheses(first, 3), test)
        late = field.evaluate(field.mine_hypotheses(all_rows, 3), test)
        self.assertEqual((len(early), sum(r["status"] == "REFUTED" for r in early)),
                         (32, 16))
        self.assertEqual((len(late), sum(r["status"] == "REFUTED" for r in late)),
                         (16, 0))
        failure = next(r for r in early if r["status"] == "REFUTED")
        self.assertIn("source_atlas_id", failure["counterexample"])
        self.assertIn("edit_edge", failure["counterexample"])
        self.assertNotEqual(failure["counterexample"]["observed"], failure["predicted"])

    def test_results_are_exactly_reproducible(self):
        generated = field.run()
        archived = json.loads((Path(__file__).parent / "experiment-results.json").read_text())
        self.assertEqual(json.loads(json.dumps(generated)), archived)
        self.assertEqual(generated["strong_classical_baseline"]["reachable_labeled_states"], 176)
        self.assertTrue(generated["strong_classical_baseline"]["equal_to_field"])


if __name__ == "__main__":
    unittest.main()
