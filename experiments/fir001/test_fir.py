"""Twelve executable field-book pressure tests, adapted from Lemon Press.

These are small behavioral probes, not an independent proof of FIR completeness.
"""
import unittest
from fir import Claim, Crossing, FIRRefusal, FIRWorld, Relation, Warrant, compose, relation_between_transitions


def proof(label):
    return Warrant("proof", label)


class TwelveWorlds(unittest.TestCase):
    def test_01_same_mark_different_carrier(self):
        w = FIRWorld("real")
        p = Claim("exists x: x*x = -1")
        w.propose(p)
        neg = Claim("no real solution to x*x = -1")
        w.propose(neg)
        w.admit(neg, proof("real squares are nonnegative"))
        w.change_carrier("complex")
        self.assertNotIn(neg, w.facts)
        w.admit(p, proof("x=i construction"))
        self.assertIn(p, w.facts)
        self.assertTrue(any(r["operation"] == "reopen" for r in w.receipts))

    def test_02_addressable_is_neither_fact_nor_idea(self):
        w = FIRWorld("3x3 matrices")
        w.address("A")
        self.assertNotIn("A", w.facts)
        self.assertNotIn("A", w.ideas)
        w.propose(Claim("A invertible"))
        self.assertEqual(len(w.ideas), 1)

    def test_03_true_endpoints_do_not_admit_edge(self):
        w = FIRWorld("natural numbers")
        for n in (2, 3):
            c = Claim(f"{n} prime")
            w.propose(c)
            w.admit(c, proof(f"trial division through sqrt({n})"))
        edge = Relation("explains", ("2 prime", "3 prime"))
        w.propose_relation(edge)
        self.assertNotIn(edge, w.relations)
        self.assertIn(edge, w.ideas)

    def test_04_exact_finite_promotion_is_bounded(self):
        w = FIRWorld("integers 1..20")
        bounded = Claim("n^2+n even", "n=1..20")
        universal = Claim("n^2+n even", "all integers")
        w.propose(bounded)
        w.propose(universal)
        warrant = Warrant("finite_computation", "enumerated 20 exact cases", "n=1..20")
        w.admit(bounded, warrant)
        with self.assertRaises(FIRRefusal):
            w.admit(universal, warrant)
        self.assertIn(universal, w.ideas)
        self.assertNotIn(universal, w.facts)

    def test_05_invertibility_does_not_cross_carrier(self):
        w = FIRWorld("Q^2")
        claim = Claim("diag(2,2) is invertible")
        w.propose(claim)
        w.admit(claim, proof("inverse diag(1/2,1/2) over rationals"))
        w.change_carrier("Z^2")
        self.assertNotIn(claim, w.facts)
        self.assertIn(claim, w.ideas)
        self.assertEqual(w.receipts[-1]["reopened"], 1)

    def test_06_goldbach_search_does_not_prove_unrestricted(self):
        w = FIRWorld("even integers")
        finite = Claim("every even n is sum of two primes", "4<=n<=100, even")
        infinite = Claim("every even n>2 is sum of two primes", "all even n>2")
        w.propose(finite)
        w.propose(infinite)
        witness = Warrant("finite_computation", "verified pairs", "4<=n<=100, even")
        w.admit(finite, witness)
        with self.assertRaises(FIRRefusal):
            w.admit(infinite, witness)
        self.assertIn(infinite, w.ideas)
        self.assertTrue(any(r["operation"] == "refused_admission" for r in w.receipts))

    def test_07_equal_endpoints_different_path_receipts(self):
        w = FIRWorld("ordered triples")
        start = (1, 2, 3)
        w.record_path("alpha", start, ["swap 1-2", "swap 1-2"], start)
        w.record_path("beta", start, ["identity"], start)
        a, b = w.receipts[-2:]
        self.assertEqual(a["end"], b["end"])
        self.assertNotEqual(a["steps"], b["steps"])

    def test_08_same_decoder_output_different_matrix(self):
        w = FIRWorld("matrices", decoder="trace")
        a = ((1, 0), (0, 1))
        b = ((2, 0), (0, 0))
        trace = lambda m: m[0][0] + m[1][1]
        self.assertEqual(w.observe(a, trace), w.observe(b, trace))
        self.assertNotEqual(a, b)
        self.assertEqual(len(w.facts), 0)  # observation did not assert equality

    def test_09_same_plus_one_different_graph_mechanism(self):
        isolated = Crossing("isolated vertex", "graph3", "graph4",
                            "add isolated vertex", (3, 4), "components +1")
        subdiv = Crossing("subdivide edge", "graph3", "graph4",
                          "replace bc with bd and dc", (3, 4), "components unchanged")
        result = relation_between_transitions(isolated, subdiv, "same_index")
        self.assertEqual(result["role"], "F")
        self.assertFalse(result["mechanism_equal"])
        higher = relation_between_transitions(isolated, subdiv, "same_mechanism")
        self.assertEqual(higher["role"], "I")
        self.assertFalse(higher["numeral_removal_survived"])

    def test_10_relation_reification_cannot_admit_next_edge(self):
        w = FIRWorld("graph")
        edge = Relation("adjacent", ("a", "b"))
        w.propose_relation(edge)
        w.admit(edge, proof("graph edge list"))
        e = w.reify(edge, "e_ab")
        self.assertIn(e, w.addressable)
        self.assertNotIn(e, w.facts)
        higher = Relation("supports", (e, "path_p"))
        w.propose_relation(higher)
        self.assertNotIn(higher, w.relations)

    def test_11_identical_glyphs_do_not_compose_types(self):
        a = Crossing("residue", "integer", "Z/5Z:2", "take residue")
        b = Crossing("successor", "Z:2", "Z:3", "add one")
        with self.assertRaises(FIRRefusal):
            compose(a, b)
        bridge = Crossing("representative-selection", "Z/5Z:2", "Z:2", "choose 2")
        valid = compose(compose(a, bridge), b)
        self.assertEqual(valid.target, "Z:3")

    def test_12_fir_self_ablation_and_no_promotion_guarantee(self):
        w = FIRWorld("meta-world")
        w.address("untyped-carrier")
        self.assertNotIn("untyped-carrier", w.facts)
        self.assertNotIn("untyped-carrier", w.ideas)
        open_idea = Claim("unproved universal conjecture", "all integers")
        w.propose(open_idea)
        with self.assertRaises(FIRRefusal):
            w.admit(open_idea, Warrant("finite_computation", "only 10 cases", "n<=10"))
        self.assertIn(open_idea, w.ideas)
        self.assertNotIn(open_idea, w.facts)


if __name__ == "__main__":
    unittest.main()
