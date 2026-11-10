"""META-005: exact infinite symbolic rank and non-completeness falsifiers."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from infinite_inverse_rank import (
    HOLD, T, reference_T, v3, odd_inverse, even_inverse,
    parameter, _compressed_member, successor, power_two_state,
    verify_power_two_edge, oracle_exact_rank, recognize,
    verify_lte_induction_examples, inverse_tree_fair_baseline,
    investigate, verify_packet, reenter, digest
)


class InfiniteFamilyRankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=investigate()

    def test_true_infinite_symbolic_family_but_not_collatz_solution(self):
        p=self.packet
        self.assertEqual(p["global_collatz_problem_status"],
                         "OPEN_COLLATZ_NOT_PROVEN")
        self.assertFalse(p["all_positive_integers_claimed_certified"])
        self.assertFalse(p["automatic_admission"])
        self.assertFalse(p["real_independent_agents_or_unrestricted_math_invention"])
        self.assertTrue(p["equal_information_classical_inverse_tree_not_beaten"])
        self.assertTrue(p["general_induction_certificate"][
            "human_review_of_general_induction_required"])
        self.assertEqual(p["general_induction_certificate"][
            "formal_proof_assistant_check"],"NOT_PERFORMED")

    def test_odd_inverse_is_derived_from_actual_accelerated_T(self):
        for y,x in ((8,5),(5,3),(32,21),(512,341)):
            self.assertEqual(odd_inverse(y),x)
            self.assertEqual(T(x),y)
            self.assertEqual(reference_T(x),y)
        self.assertIsNone(odd_inverse(2))  # would be terminal 1, forbidden
        self.assertIsNone(odd_inverse(4))
        self.assertIsNone(odd_inverse(3))
        for y in range(1,400):
            self.assertEqual(T(even_inverse(y)),y)
            if odd_inverse(y) is not None:
                self.assertGreater(odd_inverse(y),1)
                self.assertEqual(odd_inverse(y)%2,1)

    def test_general_v3_lte_valuation_matches_independent_bigint_arithmetic(self):
        for m in range(1,300,2):
            self.assertEqual(v3((1<<m)+1),1+v3(m))
        trial=self.packet["bounded_LTE_and_direct_orbit_crosschecks"]
        self.assertEqual(len(trial),41)
        self.assertEqual(trial[0]["j"],1)
        self.assertTrue(all(x["v3_2_power_m_plus_1"]>=x["j"] for x in trial))
        self.assertTrue(all(
            x["rank_without_tracing_full_orbit"]==x["direct_reference_rank"]
            for x in trial))

    def test_arbitrarily_long_generated_odd_prefixes_have_symbolic_proof(self):
        examples=self.packet["arbitrarily_long_odd_prefix_programs"]
        self.assertEqual(len(examples),8)
        for row in examples:
            j=row["j"]
            self.assertEqual(row["representative"]["j"],j)
            self.assertTrue(row["first_j_accelerated_steps_odd"])
            self.assertEqual(row["rank_symbolic"],"m+j (and +h for any even lift 2**h)")
            m=3**(j-1) * (3 if j==1 else 1)
            if j<=6:
                n=parameter(j,1 if j==1 else 0,j,0)["positive_integer"]
                x=n
                for _ in range(j):
                    self.assertEqual(x%2,1)
                    x=reference_T(x)
                self.assertEqual(x,1<<m)
                self.assertEqual(oracle_exact_rank(n,max_steps=12000),m+j)

    def test_every_generated_member_has_strict_decreasing_rank_and_closure(self):
        for j in range(1,6):
            for t in range(0,4):
                for i in range(j+1):
                    if j==1 and t==0 and i==1:
                        continue
                    for h in (0,1,2,4):
                        member=parameter(j,t,i,h)
                        edge=successor(member)
                        self.assertTrue(edge["strictly_decreases"])
                        self.assertEqual(edge["source"]["positive_integer"],
                                         member["positive_integer"])
                        self.assertEqual(edge["rank_after"]+1,edge["rank_before"])
                        self.assertGreater(edge["target"]["positive_integer"],0)
                        self.assertEqual(oracle_exact_rank(
                            member["positive_integer"],max_steps=12000),
                            member["rank"])

    def test_power_of_two_subfamily_is_closed_at_arbitrarily_large_exponents(self):
        for exponent in (1,2,3,5,8,100,1024):
            proof=verify_power_two_edge(exponent)
            self.assertEqual(proof["from"]["rank"],exponent)
            self.assertEqual(proof["to"]["rank"],exponent-1)
            self.assertEqual(proof["from"]["positive_integer"],
                             1<<exponent)
        self.assertEqual(power_two_state(0)["positive_integer"],1)
        self.assertEqual(power_two_state(0)["rank"],0)

    def test_numerical_examples_known_but_not_circularly_derived_from_trace(self):
        values=[
            (2,1,"CERTIFIED_POWERS_OF_TWO"),
            (3,5,"CERTIFIED_NONTRIVIAL_ODD_INVERSE_FAMILY"),
            (5,4,"CERTIFIED_NONTRIVIAL_ODD_INVERSE_FAMILY"),
            (21,6,"CERTIFIED_NONTRIVIAL_ODD_INVERSE_FAMILY"),
            (227,11,"CERTIFIED_NONTRIVIAL_ODD_INVERSE_FAMILY"),
        ]
        for n,r,kind in values:
            x=recognize(n)
            self.assertEqual((x["rank"],x["status"]),(r,kind))
            self.assertEqual(oracle_exact_rank(n),r)
        self.assertEqual(recognize(1)["status"],"CERTIFIED_TERMINAL_1")

    def test_known_convergent_seven_is_outside_symbolic_family_not_divergent(self):
        hold=recognize(7)
        self.assertEqual(hold["status"],
                         "HOLD_OUTSIDE_EXPLICIT_PARAMETRIC_FAMILY")
        self.assertIsNone(hold["rank"])
        self.assertGreater(oracle_exact_rank(7),0)
        self.assertEqual(self.packet[
            "counterexample_to_false_family_completeness"][
                "reference_accelerated_steps_to_one"],oracle_exact_rank(7))
        self.assertTrue(self.packet[
            "counterexample_to_false_family_completeness"][
                "nonmembership_does_not_imply_divergence"])

    def test_classical_inverse_tree_baseline_is_precise_not_superiority(self):
        c=self.packet["classical_inverse_tree_baseline"]
        self.assertEqual(c["max_depth"],13)
        self.assertEqual(c["layers"][0]["new_nodes"],[1])
        self.assertEqual(c["layers"][1]["new_nodes"],[2])
        self.assertEqual(c["layers"][2]["new_nodes"],[4])
        self.assertEqual(c["layers"][3]["new_nodes"],[8])
        self.assertTrue(c["direct_calculated_depths_match_all_inverse_edges"])
        self.assertTrue(c["not_a_proof_of_every_n_positive"])
        self.assertGreater(c["source_nodes"],14)

    def test_parametric_rank_not_unique_textual_derivation_but_state_consistent(self):
        # The same 5 has redundant parameter sources j=1,m=3 and j=2,m=3.
        a=parameter(1,1,1,0)
        b=parameter(2,0,1,0)
        self.assertEqual(a["positive_integer"],5)
        self.assertEqual(a["positive_integer"],b["positive_integer"])
        self.assertEqual(a["rank"],b["rank"])
        self.assertEqual(recognize(5)["rank"],a["rank"])
        # Categorical family proof does not claim unique derivation strings.
        self.assertEqual(successor(a)["target"]["positive_integer"],8)
        self.assertEqual(successor(b)["target"]["positive_integer"],8)

    def test_bad_or_false_authority_packet_rejected_even_after_rehash(self):
        x=copy.deepcopy(self.packet)
        x["all_positive_integers_claimed_certified"]=True
        x["integrity_digest"]=digest({k:v for k,v in x.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(x)
        y=copy.deepcopy(self.packet)
        y["general_induction_certificate"][
            "formal_proof_assistant_check"]="LEAN_VERIFIED"
        y["integrity_digest"]=digest({k:v for k,v in y.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(y)

    def test_source_preserving_proof_reentry_as_json_no_new_discovery_queries(self):
        saved=json.loads(json.dumps(self.packet))
        z=reenter(saved)
        self.assertFalse(z["collatz_conjecture_globally_solved"])
        self.assertFalse(z["theorem_prover_formalization"])
        self.assertEqual(z["new_external_investigative_questions"],0)
        self.assertTrue(z["finite_exact_source_examples_and_general_induction_replayed"])

    def test_fails_closed_on_invalid_inverse_family_parameters(self):
        for params in [
            (1,0,1,0), (0,0,0,0), (9,0,9,0),
            (2,0,3,0), (2,0,1,-1), (3,0,2,11),
            (3,True,2,0),
        ]:
            with self.assertRaises(HOLD):
                parameter(*params)
        for bad in (0,-1,True,1.5):
            with self.assertRaises(HOLD):
                recognize(bad)
        with self.assertRaises(HOLD):
            recognize(7,max_odd_prefix=0)
        with self.assertRaises(HOLD):
            successor({"positive_integer":3,"rank":5})
        with self.assertRaises(HOLD):
            _compressed_member(1,0,1,0)


if __name__=="__main__":
    unittest.main()
