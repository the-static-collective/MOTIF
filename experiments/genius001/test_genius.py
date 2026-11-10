import unittest

from genius import (clock_offset_receipt, partition_numbers,
                    mine_modular_congruences, exact_min_cut, transfer_min_cut,
                    next_question)


class TestDiscoveryOperations(unittest.TestCase):
    def test_clock_assumption_and_naive_control(self):
        # A t=10 send, B receives at true A-time 14 but reads 17; return A=18.
        r = clock_offset_receipt(10, 17, 18, symmetric_path=True)
        self.assertEqual(r["conditional_offset"], 3)
        self.assertEqual(r["naive_offset"], 7)  # ignores travel
        self.assertEqual(r["status"], "CONDITIONAL")
        self.assertEqual(clock_offset_receipt(10, 17, 18)["status"], "HOLD")
        self.assertEqual(clock_offset_receipt(10, 17, 18, symmetric_path=False)["status"], "HOLD")
        with self.assertRaises(ValueError):
            clock_offset_receipt(10, 17, 9, symmetric_path=True)

    def test_ramanujan_known_congruences_only_finite(self):
        p = partition_numbers(220)
        self.assertEqual(p[:10], [1, 1, 2, 3, 5, 7, 11, 15, 22, 30])
        r = mine_modular_congruences(p, (5, 7, 11), train_end=110)
        by_pair = {(x["modulus"], x["residue"]): x for x in r}
        for pair in [(5, 4), (7, 5), (11, 6)]:
            self.assertIn(pair, by_pair)
            self.assertEqual(by_pair[pair]["status"], "FINITE_TEST_PASS_NOT_PROOF")
            self.assertFalse(by_pair[pair]["test_counterexamples"])
        self.assertNotIn((5, 1), by_pair)
        self.assertTrue(all(x["status"] != "PROVEN_THEOREM" for x in r))
        with self.assertRaises(ValueError):
            mine_modular_congruences(p, (1,), train_end=110)

    def test_analogy_exact_cut_and_invalid_mapping(self):
        # A bottleneck made of two edges rather than one lowest-capacity edge.
        nodes = ("spring", "fork", "left", "right", "pond")
        edges = (("spring", "fork", 8), ("fork", "left", 3),
                 ("fork", "right", 2), ("left", "pond", 9),
                 ("right", "pond", 7))
        original = exact_min_cut(nodes, edges, "spring", "pond")
        self.assertEqual(original["capacity"], 5)
        self.assertEqual(original["cuts_checked"], 8)
        self.assertNotEqual(original["capacity"], min(w for _, _, w in edges))
        mapping = {"spring": "supply", "fork": "sorting", "left": "north",
                   "right": "south", "pond": "neighbors"}
        target_nodes = tuple(mapping.values())
        target_edges = tuple((mapping[u], mapping[v], w) for u, v, w in edges)
        transfer = transfer_min_cut(nodes, edges, "spring", "pond", mapping, target_nodes, target_edges)
        self.assertEqual(transfer["status"], "EXACT_FINITE")
        self.assertEqual(transfer["target_cut"]["capacity"], 5)
        altered = target_edges[:-1] + (("south", "neighbors", 10),)
        self.assertEqual(transfer_min_cut(nodes, edges, "spring", "pond", mapping,
                                          target_nodes, altered)["status"], "HOLD")
        self.assertEqual(transfer_min_cut(nodes, edges, "spring", "pond", {},
                                          target_nodes, target_edges)["status"], "HOLD")

    def test_router_does_not_claim_learned_intelligence(self):
        self.assertEqual(next_question("integer_sequence")["operator"], "CONJECTURE_THEN_FALSIFY")
        self.assertEqual(next_question("unknown")["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
