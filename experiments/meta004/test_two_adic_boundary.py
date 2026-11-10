"""META-004: nonlocal proof ranks, 2-adic ghost/positive integer separation."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from two_adic_boundary import (
    HOLD,T,signed_T,rational_parity,rational_T,
    program_for_parity_word,periodic_point,enumerate_periodic_grammar,
    positive_shadow,ghost_branches,build_finite_nonlocal_basin,
    investigate,verify_packet,reenter,digest,
)


class TwoAdicAndNonlocalRank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=investigate()

    def test_open_collatz_stays_open(self):
        p=self.packet
        self.assertEqual(p["global_collatz_status"],
                         "OPEN_NO_GLOBALLY_VALID_TERMINATION_PROOF")
        self.assertFalse(p["automatic_admission"])
        self.assertFalse(p["installed"])
        self.assertTrue(p["no_historically_novel_mathematics_claimed"])
        self.assertTrue(p["human_supplied_grammar_and_source_budget"])
        self.assertEqual(p["external_authority"],"NONE")

    def test_periodic_two_adic_grammar_exhausts_all_510_programs(self):
        out=self.packet["exact_periodic_two_adic_program_enumeration"]
        self.assertEqual(out["max_word_length"],8)
        self.assertEqual(out["all_parity_words_examined"],510)
        self.assertEqual(out["classifications"],{
            "NEGATIVE_INTEGER_GHOST":14,
            "NONINTEGER_RATIONAL_TWO_ADIC_GHOST":480,
            "POSITIVE_INTEGER":8,
            "ZERO_NOT_POSITIVE":8,
        })
        self.assertTrue(out["every_periodic_word_has_one_exact_two_adic_point"])
        self.assertTrue(out[
            "positive_ordinary_integer_rational_cycles_never_beyond_trivial_1_2"])

    def test_all_ones_two_adic_limit_is_negative_one_not_positive(self):
        cases=self.packet["ghost_positive_boundary"]["special_cases"]
        ghost=cases["all_odd_negative_minus_one"]["periodic_program"]
        self.assertEqual(ghost["periodic_x"],{"num":-1,"den":1})
        self.assertEqual(ghost["classification"],"NEGATIVE_INTEGER_GHOST")
        self.assertEqual(ghost["input_word"],[1])
        for sample in cases["all_odd_negative_minus_one"]["finite_positive_shadows"]:
            self.assertEqual(sample["positive_shadow_n"],2**sample["depth"]-1)
            self.assertTrue(sample["parity_match_for_all_declared_prefix_steps"])
            self.assertTrue(sample["finite_shadow_reached_one"])
            self.assertTrue(sample["no_general_positive_integer_convergence_proof"])
        boundary=self.packet["ghost_positive_boundary"]
        self.assertTrue(boundary["all_ones_intersection_with_positive_integers_is_empty"])
        self.assertTrue(boundary["each_finite_all_ones_cylinder_contains_infinite_positive_integers"])
        self.assertTrue(boundary["infinite_undecided_path_does_not_prove_actual_positive_divergence"])

    def test_minus_five_and_minus_seventeen_are_exact_negative_cycles(self):
        specials=self.packet["ghost_positive_boundary"]["special_cases"]
        examples=[
            ("negative_three_cycle_minus_five",-5,3),
            ("negative_eleven_cycle_minus_seventeen",-17,11),
        ]
        for key,num,period in examples:
            p=specials[key]["periodic_program"]
            self.assertEqual(p["periodic_x"],{"num":num,"den":1})
            self.assertEqual(p["classification"],"NEGATIVE_INTEGER_GHOST")
            self.assertEqual(len(p["exact_cycle_states"]),period)
            self.assertTrue(p["rational_cycle_verified_exactly"])
            for level in specials[key]["finite_positive_shadows"]:
                self.assertTrue(level["parity_match_for_all_declared_prefix_steps"])
                self.assertTrue(level["finite_shadow_reached_one"])

    def test_noninteger_rational_two_adic_point_not_a_positive_natural(self):
        special=self.packet["ghost_positive_boundary"]["special_cases"][
            "noninteger_rational_four_fifths"]
        p=special["periodic_program"]
        self.assertEqual(p["periodic_x"],{"num":4,"den":5})
        self.assertEqual(p["classification"],"NONINTEGER_RATIONAL_TWO_ADIC_GHOST")
        self.assertEqual(p["input_word"],[0,0,1])
        self.assertEqual(rational_parity(Fraction(4,5)),0)
        self.assertEqual(rational_T(Fraction(4,5)),Fraction(2,5))
        self.assertEqual(rational_T(Fraction(2,5)),Fraction(1,5))
        self.assertEqual(rational_T(Fraction(1,5)),Fraction(4,5))
        for sample in special["finite_positive_shadows"]:
            self.assertTrue(sample["finite_shadow_reached_one"])
            self.assertFalse(sample["n_is_exactly_equal_to_the_two_adic_point"])

    def test_positive_trivial_cycle_not_wrongly_classified_ghost(self):
        special=self.packet["ghost_positive_boundary"]["special_cases"][
            "legitimate_positive_one_two"]
        p=special["periodic_program"]
        self.assertEqual(p["periodic_x"],{"num":1,"den":1})
        self.assertEqual(p["classification"],"POSITIVE_INTEGER")
        self.assertEqual(signed_T(1),2)
        self.assertEqual(signed_T(2),1)
        self.assertTrue(all(x["finite_shadow_reached_one"]
                            for x in special["finite_positive_shadows"]))

    def test_original_META003_held_frontier_contains_negative_ghost_cylinders(self):
        links=self.packet["ghost_positive_boundary"][
            "crosscheck_against_original_META003_residue_HOLDs"]
        self.assertEqual(len(links),9)
        self.assertEqual({x["two_adic_negative_integer"] for x in links},
                         {-1,-5,-17})
        for record in links:
            k=record["k"]
            self.assertEqual(record["residue"],
                             record["two_adic_negative_integer"]%(1<<k))
            self.assertEqual(record["inherited_META003_first_descent_status"],
                             "HOLD_WITHIN_K")
            self.assertTrue(record["no_positive_counterexample_proven"])

    def test_every_finite_k_ghost_has_real_positive_approximants(self):
        ghost=periodic_point((1,1,0))
        for k in (8,12,16,20,24):
            test=positive_shadow(ghost,k)
            self.assertEqual(test["positive_shadow_n"],2**k-5)
            self.assertEqual(test["modulus"],2**k)
            self.assertTrue(test["finite_shadow_reached_one"])
        with self.assertRaises(HOLD):
            positive_shadow(ghost,10)
        with self.assertRaises(HOLD):
            program_for_parity_word((1,0,2))
        with self.assertRaises(HOLD):
            rational_parity(Fraction(1,2))

    def test_exact_nonlocal_rank_on_closed_finite_source_basin(self):
        out=self.packet["genuine_nonlocal_closed_finite_ranking"]
        self.assertEqual(out["training_start_range"],[2,128])
        self.assertEqual(out["heldout_start_range"],[129,512])
        self.assertEqual(out["finite_basin_nodes"],800)
        self.assertEqual(out["total_unique_source_transition_queries"],799)
        self.assertEqual(out["max_integer_encountered_in_finite_basin"],19682)
        self.assertTrue(out["all_transitions_closed_in_exact_finite_basin"])
        self.assertTrue(out["terminal_absorbing_by_program_semantics"])
        self.assertTrue(out["strong_classical_memoization_exact_tie"])
        self.assertTrue(out["this_does_not_supply_a_total_rank_on_all_positive_integers"])
        for e in out["source_ranking_witnesses"]:
            self.assertEqual(e["next"],T(e["n"]))
            self.assertEqual(e["rank"],e["next_rank"]+1)

    def test_nonlocal_reusable_proof_answers_without_redundant_source_work(self):
        out=self.packet["genuine_nonlocal_closed_finite_ranking"]
        self.assertEqual(out["naive_unmemoized_all_starts_transition_queries"],18043)
        self.assertEqual(out["source_queries_avoided_vs_unmemoized_baseline"],17244)
        self.assertEqual(out["train_new_transition_queries"]+
                         out["heldout_new_transition_queries"],799)
        self.assertEqual(len(out["all_source_starts_and_proof_reuse"]),511)
        for trial in out["all_source_starts_and_proof_reuse"]:
            self.assertEqual(trial["status"],"FINITE_SOURCE_CLOSED_BASIN_PROVED")
            self.assertGreaterEqual(trial["rank"],1)
            self.assertGreaterEqual(trial["reused_known_suffix"],1)
        self.assertFalse(out["this_does_not_prove_collatz"] is False)

    def test_rehashed_fabricated_positive_two_adic_ghost_refused(self):
        fake=copy.deepcopy(self.packet)
        fake["ghost_positive_boundary"]["all_ones_intersection_with_positive_integers_is_empty"]=False
        fake["integrity_digest"]=digest({
            k:v for k,v in fake.items() if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(fake)

    def test_rehashed_forged_unbounded_rank_refused(self):
        fake=copy.deepcopy(self.packet)
        fake["genuine_nonlocal_closed_finite_ranking"][
            "this_does_not_supply_a_total_rank_on_all_positive_integers"]=False
        fake["integrity_digest"]=digest({
            k:v for k,v in fake.items() if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(fake)

    def test_reenter_is_complete_evidence_recheck_not_checksum_only(self):
        reply=reenter(json.loads(json.dumps(self.packet)))
        self.assertEqual(reply["new_investigative_source_questions"],0)
        self.assertFalse(reply["collatz_global_proof"])
        self.assertTrue(reply["complete_transition_and_symbolic_source_replay"])
        self.assertEqual(reply["source_digest"],self.packet["integrity_digest"])

    def test_invalid_program_and_budget_refused(self):
        for bad in [(1,1,2),(True,0),tuple(),tuple([1]*12)]:
            with self.assertRaises(HOLD):
                periodic_point(bad)
        with self.assertRaises(HOLD):
            enumerate_periodic_grammar(9)
        with self.assertRaises(HOLD):
            build_finite_nonlocal_basin(100,512)
        with self.assertRaises(HOLD):
            build_finite_nonlocal_basin(128,1000)


if __name__=="__main__":
    unittest.main()
