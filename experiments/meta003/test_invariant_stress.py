"""META-003: refute deceptive ranks; exact stateful 2-adic partial proofs."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from invariant_stress import (
    HOLD,T,rank,fit_rank,same_residue_increasing_step,
    counterexample_guided_ranking,affine_prefixes,
    first_class_descent,independent_first_class_descent,
    choose_adversarial_odd_continuation,refine_frontier,
    investigate,verify_packet,reenter,digest
)


class StatefulRankingResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=investigate()

    def test_collatz_remains_open_without_diluting_research_question(self):
        p=self.report
        self.assertEqual(p["status"],"OPEN_UNRESOLVED_MATHEMATICAL_RESEARCH_HOLD")
        self.assertFalse(p["automatic_admission"])
        self.assertFalse(p["installed"])
        self.assertEqual(p["external_authority"],"NONE")
        self.assertTrue(p["known_mathematics_not_historically_new"])
        self.assertTrue(p["strong_classical_adaptive_baseline_ties"])
        self.assertFalse(p["source_owner_independent_human_authenticated"])

    def test_cegis_actually_fits_initial_nonlinear_quadratic_model(self):
        c=fit_rank(16,2,14)
        self.assertEqual(c["status"],"FITTED_FINITE_SAMPLE_ONLY")
        self.assertEqual(len(c["offsets"]),16)
        for n in range(2,15):
            self.assertLess(rank(T(n),2,c["offsets"]),rank(n,2,c["offsets"]))
        self.assertGreaterEqual(rank(T(15),2,c["offsets"]),rank(15,2,c["offsets"]))
        self.assertTrue(c["not_a_global_rank_proof"])

    def test_cegis_is_progressive_and_preserves_failed_hypotheses(self):
        for p in (1,2,3):
            trial=counterexample_guided_ranking(16,p,14)
            self.assertEqual(trial["status"],
                "REFUTED_BOUNDED_NONLINEAR_RESIDUE_RANK_GRAMMAR")
            steps=trial["attempts"]
            self.assertEqual([x["status"] for x in steps],
                ["CANDIDATE_REFUTED_ON_HELDOUT",
                 "CANDIDATE_REFUTED_ON_HELDOUT",
                 "TRAINING_GRAMMAR_INFEASIBLE"])
            self.assertEqual([x["first_heldout_counterexample_n"]
                              for x in steps[:2]],[15,17])
            self.assertEqual(steps[2]["training_max"],17)
            self.assertEqual(trial["formal_family_counterexample"][
                "base_residue"],15)

    def test_finite_residue_self_loop_blocks_any_increasing_size_rank(self):
        for m in (2,4,8,16,32,64,128):
            proof=same_residue_increasing_step(m)
            self.assertEqual(proof["base_residue"],m-1)
            for t in (1,2,3,11):
                n=2*m*t-1
                after=T(n)
                self.assertEqual(after,3*m*t-1)
                self.assertEqual(n%m,after%m)
                self.assertGreater(after,n)
                for p in (1,2,3):
                    offsets=[(j*j-17*j) for j in range(m)]
                    # The proof is for all finite m. Avoid rank() sandbox
                    # restrictions when m is 2/4/64/128.
                    self.assertGreater(
                        after**p+offsets[after%m],
                        n**p+offsets[n%m])
            self.assertTrue(proof["does_not_refute_collatz"])
            self.assertTrue(proof[
                "does_not_exclude_variable_horizon_or_nonmonotone_functions"])
        # Strictly increasing log also violates monotonicity by same-state
        # cancellation, but we do not rely on approximate floating numbers.
        self.assertIn("STRICTLY INCREASING",
                      self.report["self_loop_general_counterexamples"][0][
                          "mathematical_no_go"])

    def test_base_12_bit_holds_are_real_exact_classical_holds(self):
        level=self.report["stateful_two_adic_question_frontier"]
        self.assertEqual(level["base_k"],12)
        self.assertEqual(level["previously_certified_base_classes"],3870)
        self.assertEqual(level["previously_held_base_classes"],226)
        self.assertEqual(level["initial_modular_parent_classes"],4096)
        self.assertTrue(level["classical_exact_reference_agrees_for_all_new_queries"])
        self.assertIn(4095,[
            x["base_residue"] for x in level["parent_refinements"]])

    def test_selective_refinement_certifies_new_infinite_families(self):
        level=self.report["stateful_two_adic_question_frontier"]
        self.assertEqual(level["deep_k"],16)
        self.assertEqual(level["exact_new_subclasses_examined"],3616)
        self.assertEqual(level["already_proven_descendants_reused_not_requeried"],
                         61920)
        self.assertEqual(level["newly_certified_infinite_descendant_classes"],1502)
        self.assertEqual(level["remaining_uncertified_descendant_classes"],2114)
        self.assertEqual(level["total_certified_deep_residue_classes"],63422)
        self.assertEqual(level["total_deep_residue_classes"],65536)
        self.assertTrue(level["saved_prior_certificates_are_reused"])
        self.assertTrue(level["this_is_infinite_family_coverage_not_individual_orbit_proof"])

    def test_all_new_infinite_class_certificates_replay_independent_algorithm(self):
        level=self.report["stateful_two_adic_question_frontier"]
        for entry in level["complete_new_child_certificates"]:
            self.assertEqual(entry["status"],"INFINITE_CHILD_CLASS_CERTIFIED")
            r=entry["child_residue"]
            j=entry["first_proved_strict_descent_time"]
            self.assertEqual(first_class_descent(16,r),j)
            self.assertEqual(independent_first_class_descent(16,r),j)
            proof=entry["proof_affine"]
            a,b,d=(proof[x] for x in ("a","b","d"))
            self.assertLess(a,d)
            for q in (0,1,3):
                n=proof["smallest_descendant_integer_gt_one"]+(1<<16)*q
                value=n
                for _ in range(j):
                    value=T(value)
                self.assertEqual(d*value,a*n+b)
                self.assertLess(value,n)

    def test_unresolved_infinite_classes_are_not_falsely_promoted(self):
        level=self.report["stateful_two_adic_question_frontier"]
        for entry in level["complete_remaining_holds"]:
            self.assertEqual(entry["status"],"HOLD_INFINITE_CHILD_CLASS_UNRESOLVED")
            self.assertIsNone(entry["first_proved_strict_descent_time"])
            self.assertIsNone(first_class_descent(16,entry["child_residue"]))
        self.assertFalse(level["no_completeness_of_infinite_collatz_conjecture"] is False)

    def test_no_finite_parity_tree_covers_any_held_parent(self):
        level=self.report["stateful_two_adic_question_frontier"]
        self.assertEqual(len(level["parent_refinements"]),226)
        for parent in level["parent_refinements"]:
            self.assertFalse(parent["full_parent_class_certified"])
            adversary=parent["adversarial_no_full_parent_cert"]
            self.assertTrue(adversary[
                "all_integers_in_descendant_have_no_strict_descent_by_that_depth"])
            self.assertEqual(
                adversary["base_residue"],parent["base_residue"])
            self.assertEqual(len(adversary["odd_tail_bit_choices"]),4)
            self.assertIsNone(first_class_descent(16,adversary["selected_residue"]))
            for j,choice in enumerate(adversary["odd_tail_bit_choices"],12):
                self.assertEqual(choice["from_precision"],j)
                self.assertTrue(choice["jth_iterate_odd"])

    def test_deeper_adversarial_tail_is_constructible_on_multiple_parent_holds(self):
        parents=[x["base_residue"] for x in
                 self.report["stateful_two_adic_question_frontier"]["parent_refinements"]]
        for r in parents[:10]+parents[-10:]:
            for extra in (1,3,5):
                witness=choose_adversarial_odd_continuation(12,r,12+extra)
                self.assertEqual(witness["new_k"],12+extra)
                self.assertTrue(witness[
                    "selected_descendant_has_no_strict_descent_up_to_depth"])
                p=affine_prefixes(12+extra,witness["selected_residue"])
                self.assertTrue(all(
                    x["numerator_a"]>=x["denominator"] for x in p))

    def test_more_precision_refines_finite_subclasses_but_not_all_parents(self):
        a=refine_frontier(deep_k=13)
        b=refine_frontier(deep_k=15)
        self.assertEqual((a["newly_certified_infinite_descendant_classes"],
                          a["remaining_uncertified_descendant_classes"]),(85,367))
        self.assertEqual((b["newly_certified_infinite_descendant_classes"],
                          b["remaining_uncertified_descendant_classes"]),(513,1295))
        self.assertTrue(all(not p["full_parent_class_certified"] for p in
                            a["parent_refinements"]+b["parent_refinements"]))

    def test_resealed_fake_rank_solution_and_fake_no_holds_rejected(self):
        a=copy.deepcopy(self.report)
        a["new_nonlinear_finite_state_potential_proposals"][0][
            "status"]="PROVED_GLOBAL_RANK"
        a["integrity_digest"]=digest({k:v for k,v in a.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(a)
        b=copy.deepcopy(self.report)
        b["stateful_two_adic_question_frontier"][
            "remaining_uncertified_descendant_classes"]=0
        b["integrity_digest"]=digest({k:v for k,v in b.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(b)

    def test_proof_packet_reentry_recomputes_no_new_questions(self):
        cloned=json.loads(json.dumps(self.report))
        outcome=reenter(cloned)
        self.assertEqual(outcome["new_investigative_source_questions"],0)
        self.assertTrue(outcome["all_source_observations_recomputed"])
        self.assertFalse(outcome["global_collatz_conjecture_solved"])

    def test_invalid_grammar_and_adversary_specs_refused(self):
        with self.assertRaises(HOLD):
            fit_rank(7,2,14)
        with self.assertRaises(HOLD):
            fit_rank(16,4,14)
        with self.assertRaises(HOLD):
            rank(2,2,[0,0])
        with self.assertRaises(HOLD):
            same_residue_increasing_step(3)
        with self.assertRaises(HOLD):
            refine_frontier(base_k=11,deep_k=16)
        with self.assertRaises(HOLD):
            refine_frontier(deep_k=17)
        with self.assertRaises(HOLD):
            choose_adversarial_odd_continuation(12,2,16)
        with self.assertRaises(HOLD):
            choose_adversarial_odd_continuation(12,4096,16)


if __name__=="__main__":
    unittest.main()
