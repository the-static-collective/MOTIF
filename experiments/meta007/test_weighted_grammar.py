"""META-007 adversarial tests of EXACT inverse grammar optimization.

No test can promote a finite Collatz computation or restricted inverse
family into a general all-n theorem. All numerical growth coefficients have
power-integer certificates, NOT approximate floating-point proof status.
"""
from __future__ import annotations

import copy
from decimal import Decimal
from itertools import product
import json
import math
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from weighted_grammar import (
    HOLD, SCHEMA, Q, FLOOR_SCALE, ALPHABET_MAX, SEED,
    branch_weight, cost_refinement_receipt, generalized_branch, encode_word, decode_word,
    _pow_rational_bound,exact_growth_score,optimize_grammar,
    independent_classical_approximate_score,
    count_weighted_words,brute_force_count,lower_growth_certificate,
    enumerate_finite_source, investigate,verify_packet,reenter,digest,
)
from branching_inverse import decode as previous_binary_decoder
from infinite_inverse_rank import oracle_exact_rank
from collatz_frontier import reference_T


class WeightedProofGrammar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=investigate()

    def test_genuinely_open_conjecture_and_unmerged_math_scope(self):
        p=self.packet
        self.assertEqual(p["global_open_status"],
                         "COLLATZ_UNRESOLVED_NO_GENERAL_PROOF")
        self.assertFalse(p["automatic_admission"])
        self.assertFalse(p["installed"])
        self.assertTrue(p["not_a_Collatz_global_proof"])
        self.assertTrue(p["not_positive_density"])
        self.assertTrue(p["not_historically_novel_mathematics"])
        self.assertTrue(p["not_general_autonomous_axiom_invention"])
        self.assertEqual(p["external_authority"],"NONE")

    def test_self_critique_automatically_tightens_cost_using_source_divisor(self):
        details=self.packet["exact_self_critique_of_operator_costs"]
        self.assertEqual(details["status"],
                         "EXACT_SYMBOLIC_COST_REFINEMENT_SUCCEEDED")
        self.assertEqual(details,cost_refinement_receipt())
        self.assertEqual(len(details["all_source_branch_costs"]),12)
        for t,record in enumerate(details["all_source_branch_costs"]):
            self.assertEqual(record["symbol"],t)
            self.assertEqual(record["old_overconservative_weight"],7+6*t)
            self.assertEqual(record["exact_derived_minimal_integer_weight"],6+6*t)
            numerator=1<<(7+6*t)
            w=branch_weight(t)
            self.assertGreater(3*(1<<w),numerator)
            self.assertLessEqual(3*(1<<(w-1)),numerator)
        self.assertTrue(details["source_owned_not_statistical_inference"])

    def test_actual_search_not_handpicked_8_branch_answer(self):
        search=self.packet["grammar_optimizer"]
        self.assertEqual(search["source_candidate_alphabet_sizes"],[2,12])
        self.assertEqual(search["exponent_grid"],{
            "p_min":80,"p_max":160,"q":1000
        })
        self.assertEqual(len(search["all_alphabet_trials"]),11)
        self.assertEqual(
            [x["best_certified_p"] for x in search["all_alphabet_trials"]],
            [115,146,157,162,164,165,166,166,166,166,166])
        self.assertEqual(search["winning_alphabet_size"],8)
        self.assertEqual(search["winning_rational_growth_exponent"],166)
        self.assertTrue(search[
            "optimal_ONLY_within_predeclared_grammar_and_rational_grid"])
        self.assertEqual(search["optimization_tie_rule"],
                         "maximize proved p/q; then minimize K")

    def test_every_chosen_exponent_and_next_greater_is_exactly_certified(self):
        for item in self.packet["grammar_optimizer"]["all_alphabet_trials"]:
            K=item["K"]
            p=item["best_certified_p"]
            source=exact_growth_score(K,p)
            self.assertEqual(source,item["success"])
            self.assertEqual(source["verdict"],"CERTIFIED_SUPERCRITICAL")
            self.assertGreaterEqual(source["sum_lower_numerator"],FLOOR_SCALE)
            self.assertEqual(len(source["each_term_exact_lower_numerators"]),K)
            if p<160:
                failed=exact_growth_score(K,p+1)
                self.assertEqual(failed["verdict"],"CERTIFIED_SUBCRITICAL")
                self.assertLess(failed["sum_upper_numerator_exclusive"],FLOOR_SCALE)
                self.assertEqual(failed,item["first_excluded_exponent"])

    def test_integer_interval_proofs_are_real_not_float_extrapolation(self):
        for p,K in [(115,2),(146,3),(162,5),(166,8),(166,12),(167,12)]:
            score=exact_growth_score(K,p)
            for t,z in enumerate(score["each_term_exact_lower_numerators"]):
                w=branch_weight(t)
                self.assertEqual(z,_pow_rational_bound(p,w))
                self.assertLessEqual(z**Q * (1<<(p*w)),FLOOR_SCALE**Q)
                self.assertGreater((z+1)**Q * (1<<(p*w)),FLOOR_SCALE**Q)
            self.assertEqual(score["sum_upper_numerator_exclusive"],
                             score["sum_lower_numerator"]+K)
        self.assertEqual(exact_growth_score(8,166)["verdict"],
                         "CERTIFIED_SUPERCRITICAL")
        self.assertEqual(exact_growth_score(12,167)["verdict"],
                         "CERTIFIED_SUBCRITICAL")

    def test_strong_separate_classical_geometric_sum_agrees_all_alphabets(self):
        for item in self.packet["grammar_optimizer"]["all_alphabet_trials"]:
            K=item["K"]
            p=item["best_certified_p"]
            yes,source=independent_classical_approximate_score(K,p)
            no,source_next=independent_classical_approximate_score(K,p+1)
            self.assertTrue(yes)
            self.assertFalse(no)
            self.assertGreater(Decimal(source),Decimal(1))
            self.assertLess(Decimal(source_next),Decimal(1))
        self.assertTrue(self.packet["historical_published_global_predecessor_bound"][
            "stronger_than_our_restricted_family"])

    def test_generalized_branch_is_real_source_bigger_than_prior_binary(self):
        K=8
        self.assertEqual(encode_word([0],K)["odd_positive_integer"],53)
        self.assertEqual(encode_word([1],K)["odd_positive_integer"],3413)
        self.assertEqual(encode_word([2],K)["odd_positive_integer"],218453)
        new=encode_word([2],K)
        self.assertEqual(previous_binary_decoder(218453)["status"],
                         "HOLD_OUTSIDE_BINARY_BRANCH_GRAMMAR")
        self.assertEqual(decode_word(218453,K)["word"],[2])
        self.assertEqual(new["forward_rank"],oracle_exact_rank(218453))
        for t in range(K):
            x=generalized_branch(5,t,K)
            self.assertEqual(x["growth_cost_bits"],6+6*t)
            self.assertLess(x["child"],5*(1<<(6+6*t)))
            self.assertEqual(
                reference_T(x["child"]),x["source_forward_first_step"])
            self.assertEqual(x["accelerated_rank_increment"],2*x["e"]+1)

    def test_all_source_tree_words_distinct_and_exact_rank(self):
        observed=self.packet["independent_exact_integer_source_crosscheck"]
        K=observed["selected_grammar_K"]
        self.assertEqual(K,8)
        self.assertEqual(observed["source_checked_nodes"],585)
        self.assertEqual(observed["new_nodes_outside_original_META006_binary_grammar"],
                         570)
        self.assertEqual(
            [x["exact_new_nodes"] for x in observed[
                "source_verified_finite_growth_by_depth"]],
            [1,8,64,512])
        for first in observed["first_new_integer_instances"]:
            old=previous_binary_decoder(first["n"])
            self.assertNotEqual(old["status"],"CERTIFIED_BINARY_INVERSE_BRANCH")
            now=decode_word(first["n"],K)
            self.assertEqual(now["word"],first["word"])
            self.assertEqual(now["rank"],first["strict_rank"])
        self.assertTrue(observed[
            "independent_forward_source_rank_checked_for_every_node"])

    def test_weighted_word_count_recurrence_matches_independent_exhaustive_words(self):
        for K in (2,3,6,11):
            counts=count_weighted_words(K,32)
            for L in (0,1,6,7,12,13,19,25,31,32):
                self.assertEqual(counts[L],brute_force_count(K,L))
                self.assertGreaterEqual(counts[L],1)
                if L:
                    self.assertGreaterEqual(counts[L],counts[L-1])
        self.assertEqual(count_weighted_words(8,6)[6],2)
        self.assertEqual(count_weighted_words(8,12)[12],4)

    def test_proof_uses_exact_weighted_coding_not_only_uniform_worst_case(self):
        cert=self.packet["weighted_combinatorial_growth_certificate"]
        self.assertEqual(cert["selected_K"],8)
        self.assertEqual(cert["rational_alpha_p"],166)
        self.assertEqual(cert["rational_alpha_q"],1000)
        self.assertEqual(cert["maximum_symbol_weight_W"],48)
        self.assertTrue(cert["exact_Kraft_sum_strictly_greater_than_one"])
        self.assertFalse(cert["verified_strict_sum_lower_than_one_claim"])
        self.assertEqual(cert["exact_Kraft_sum_integer_certificate"],
                         exact_growth_score(8,166))
        self.assertTrue(cert["complete_symbolic_induction_human_review_required"])
        self.assertEqual(cert["formal_proof_assistant_verification"],"NOT_PERFORMED")
        self.assertFalse(cert["positive_natural_density_proved"])
        self.assertFalse(cert["global_Collatz_conjecture_proved"])
        for check in cert["checkpoints"]:
            L=check["weighted_budget_L"]
            count=check["distinct_executable_words_from_recurrence"]
            self.assertGreaterEqual(
                (count**1000)*(1<<(166*48)),
                1<<(166*L))

    def test_quantitative_gain_over_meta006_is_bounded_and_real(self):
        comparison=self.packet["comparison_against_META006"]
        self.assertEqual(comparison["prior_grammar"],2)
        self.assertEqual(comparison["new_grammar_K"],8)
        self.assertEqual(comparison["new_exact_lower_bound_exponent"],"166/1000")
        self.assertGreater(comparison[
            "improvement_factor_over_prior_guaranteed_lower_exponent"],1.89)
        self.assertLess(comparison[
            "improvement_factor_over_prior_guaranteed_lower_exponent"],1.90)
        self.assertTrue(comparison[
            "does_not_beat_historical_Krasikov_Lagarias"])
        self.assertTrue(self.packet[
            "historical_published_global_predecessor_bound"][
                "is_independent_historical_mathematics"])

    def test_all_strong_source_assumptions_reject_forged_grammar(self):
        for word in ([11],[True],[0,0,0,0],["2"]):
            with self.assertRaises(HOLD):
                encode_word(word,8)
        with self.assertRaises(HOLD):
            generalized_branch(5,8,8)
        with self.assertRaises(HOLD):
            generalized_branch(5,0,1)
        with self.assertRaises(HOLD):
            generalized_branch(7,0,8)
        with self.assertRaises(HOLD):
            encode_word([2],2)
        self.assertIn("HOLD_",decode_word(7,8)["status"])
        for invalid in (0,1,13,True):
            with self.assertRaises(HOLD):
                exact_growth_score(invalid,166)
        for p in (79,181,True):
            with self.assertRaises(HOLD):
                exact_growth_score(8,p)

    def test_integrity_rehash_cannot_promote_false_global_or_novel_claim(self):
        altered=copy.deepcopy(self.packet)
        altered["not_a_Collatz_global_proof"]=False
        altered["integrity_digest"]=digest({k:v for k,v in altered.items()
                                             if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(altered)
        altered=copy.deepcopy(self.packet)
        altered["grammar_optimizer"]["winning_rational_growth_exponent"]=160
        altered["integrity_digest"]=digest({k:v for k,v in altered.items()
                                             if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(altered)

    def test_exact_source_reentry_never_converts_research_to_theorem(self):
        saved=json.loads(json.dumps(self.packet))
        outcome=reenter(saved)
        self.assertEqual(outcome["new_investigative_source_questions"],0)
        self.assertTrue(outcome["all_mathematical_and_source_claims_recomputed"])
        self.assertFalse(outcome["global_collatz_conjecture_solved"])
        self.assertEqual(outcome["exact_proof_digest"],self.packet["integrity_digest"])


if __name__=="__main__":
    unittest.main()
