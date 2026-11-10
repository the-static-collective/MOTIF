"""META-006: mathematical adversaries for recursive inverse-family expansion."""
from __future__ import annotations
import copy
import itertools
import json
import math
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from branching_inverse import (
    HOLD,T,reference_T,SEED,SEED_RANK,SCHEMA,
    e_base,child,encode,decode,rank_member,transition_proof,
    enumerate_family,symbolic_growth_lower_bound,
    classical_inverse_tree_control,old_family_status,
    investigate,verify_packet,reenter,digest
)
from infinite_inverse_rank import oracle_exact_rank,sparse_family_upper_bound


class BranchingInfiniteRank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=investigate()

    def test_original_open_conjecture_and_authority_remain_unchanged(self):
        p=self.packet
        self.assertEqual(p["global_status"],"COLLATZ_CONJECTURE_STILL_OPEN")
        self.assertFalse(p["automatic_admission"])
        self.assertFalse(p["installed"])
        self.assertFalse(p["no_historically_novel_mathematics_claimed"] is False)
        self.assertTrue(p["strong_classical_baseline_ties"])
        self.assertFalse(p["general_mathematical_growth_certificate"][
            "neither_natural_density_nor_full_collatz_conjecture_proven"] is False)
        self.assertFalse(p["source_owned_nonmember_refusal"][
            "must_not_promote_nonmembership_to_nonconvergence"] is False)

    def test_mod9_condition_is_derived_exactly_for_all_three_states(self):
        for y,e in [(11,1),(5,2),(17,3),(53,3),(2261,1)]:
            self.assertEqual(e_base(y),e)
            for bit in (0,1):
                op=child(y,bit)
                self.assertEqual(op["modular_exponent_e"],e+3*bit)
                self.assertEqual(op["child"]%3,2)
                self.assertEqual(op["child"]%2,1)
                self.assertGreater(op["child"],y)
                self.assertEqual(T(op["child"]),
                                 (1<<(2*op["modular_exponent_e"]))*y)
                self.assertEqual(reference_T(op["child"]),T(op["child"]))
        for y in (1,2,3,7,9,10,12,14,16):
            with self.assertRaises(HOLD):
                e_base(y)

    def test_tree_generates_concrete_families_not_in_old_language(self):
        self.assertEqual(encode([])["odd_node"],5)
        self.assertEqual(encode([0])["odd_node"],53)
        self.assertEqual(encode([1])["odd_node"],3413)
        self.assertEqual(encode([0,0])["odd_node"],2261)
        self.assertEqual(encode([0,0,0])["odd_node"],6029)
        self.assertFalse(old_family_status(53))
        self.assertFalse(old_family_status(2261))
        self.assertFalse(old_family_status(3413))
        self.assertTrue(old_family_status(5))
        self.assertTrue(old_family_status(3))

    def test_symbolic_rank_is_known_before_independent_trajectory(self):
        for depth in range(0,6):
            for word in itertools.product((0,1),repeat=depth):
                proof=encode(word)
                n=proof["odd_node"]
                self.assertTrue(proof["explicit_positive_natural_integer"])
                self.assertEqual(decode(n)["word"],list(word))
                self.assertEqual(decode(n)["rank"],proof["strict_rank"])
                self.assertEqual(rank_member(n)["rank"],proof["strict_rank"])
                self.assertEqual(oracle_exact_rank(n,max_steps=3000),
                                 proof["strict_rank"])
                for h in (0,1,2,3):
                    candidate=n<<h
                    r=rank_member(candidate)
                    self.assertEqual(r["rank"],proof["strict_rank"]+h)
                    self.assertEqual(oracle_exact_rank(candidate,max_steps=3000),
                                     r["rank"])
                    if candidate>1:
                        edge=transition_proof(candidate)
                        self.assertEqual(edge["rank_decreases_exactly_one"],True)
                        self.assertEqual(edge["to"]["rank"],r["rank"]-1)

    def test_odd_prefix_can_contain_even_blocks_nonlocal_source_rank(self):
        p=encode([0,0])
        self.assertEqual(p["odd_node"],2261)
        self.assertEqual([z["following_even_halvings"] for z in
                         p["inverse_macro_edges"]],[4,6])
        self.assertEqual(p["strict_rank"],4+5+7)
        n=p["odd_node"]
        states=[n]
        while n!=1:
            n=T(n)
            states.append(n)
        self.assertEqual(len(states)-1,p["strict_rank"])
        self.assertIn(53,states)
        self.assertIn(5,states)
        self.assertEqual(states[-1],1)

    def test_real_coverage_is_exact_and_new_not_old(self):
        prior={64:18,512:38,4096:64,16384:85}
        extra={64:1,512:4,4096:9,16384:18}
        result={x["cap"]:x for x in
                self.packet["exact_increased_coverage_against_prior_research"]}
        self.assertEqual(set(result),set(prior))
        for cap,old_count in prior.items():
            row=result[cap]
            self.assertEqual(row["prior_META005_exact_members"],old_count)
            self.assertEqual(row["new_inverse_branch_nonmembers_of_prior"],
                             extra[cap])
            self.assertEqual(row["provable_union_exact_members"],
                             old_count+extra[cap])
            self.assertTrue(row["all_new_members_have_exact_nonlocal_rank"])
        self.assertEqual(self.packet["source_owned_nonmember_refusal"]["n"],7)
        self.assertIn("HOLD_",self.packet["source_owned_nonmember_refusal"]["status"])

    def test_proven_polynomial_lower_bound_not_just_fit_to_small_counts(self):
        levels=self.packet["checked_growth_levels"]
        self.assertEqual([x["depth"] for x in levels],
                         [0,1,2,3,5,8,10])
        for entry in levels:
            d=entry["depth"]
            self.assertEqual(entry["unique_positive_odd_members"],2**d)
            self.assertEqual(entry["different_binary_paths"],2**d)
            self.assertEqual(entry["uniform_rational_upper_bound_numerator"],
                             5*8192**d)
            self.assertEqual(entry["uniform_rational_upper_bound_denominator"],
                             3**d)
            self.assertTrue(entry["polynomial_lower_bound_asymptotically_proved"])
            self.assertFalse(entry["natural_density_proven_positive"])
            self.assertAlmostEqual(entry["alpha_reference_decimal"],0.08760374,places=8)
        self.assertEqual(self.packet["general_mathematical_growth_certificate"][
            "prior_family_asymptotic_upper"],"O((log X)**2*loglog X) from META-005")

    def test_equal_information_classical_inverse_tree_ties(self):
        baseline=self.packet["classical_equal_information_baseline"]
        self.assertEqual(baseline["max_depth"],10)
        self.assertEqual(baseline["distinct_classical_nodes"],2047)
        self.assertTrue(baseline["same_information_classical_exact_tie"])
        for depth in (0,1,2,4,6):
            c=classical_inverse_tree_control(depth)
            self.assertEqual(c["distinct_classical_nodes"],2**(depth+1)-1)

    def test_nonmember_or_wrong_parity_state_refused_not_declared_divergent(self):
        for n in (1,3,7,9,11,15,17,27):
            if n==1:
                self.assertEqual(rank_member(n)["rank"],0)
                continue
            if n==3:
                self.assertIsNone(rank_member(n)["rank"])
                self.assertGreater(oracle_exact_rank(n),0)
                continue
            proof=rank_member(n)
            self.assertIsNone(proof["rank"])
            self.assertIn("HOLD_",proof["status"])
            with self.assertRaises(HOLD):
                transition_proof(n)
        with self.assertRaises(HOLD):
            encode([2])
        with self.assertRaises(HOLD):
            encode([True])
        with self.assertRaises(HOLD):
            child(5,2)
        with self.assertRaises(HOLD):
            enumerate_family(10**9)

    def test_rehashed_fake_global_answer_or_coverage_rejected(self):
        a=copy.deepcopy(self.packet)
        a["global_status"]="COLLATZ_PROVED"
        a["integrity_digest"]=digest({k:v for k,v in a.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(a)
        b=copy.deepcopy(self.packet)
        b["general_mathematical_growth_certificate"][
            "neither_natural_density_nor_full_collatz_conjecture_proven"]=False
        b["integrity_digest"]=digest({k:v for k,v in b.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(b)

    def test_reentry_rebuilds_evidence_without_new_investigative_queries(self):
        p=json.loads(json.dumps(self.packet))
        result=reenter(p)
        self.assertEqual(result["new_external_investigative_questions"],0)
        self.assertFalse(result["original_global_collatz_conjecture_solved"])
        self.assertTrue(result["full_mathematical_source_replay"])


if __name__=="__main__":
    unittest.main()
