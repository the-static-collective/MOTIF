"""META-001 — adversarial open-problem tests: correct local math, global HOLD."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from collatz_frontier import (
    HOLD, CLAIM, PRIMITIVES, T, C, reference_T, certificate,
    independent_classical_certificate, verify_certificate,
    FiniteSourceOwner, investigate_open_problem, verify_packet, reenter,digest
)


class OpenCollatzTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=investigate_open_problem(max_k=8, finite_n=4096)

    def test_genuinely_open_global_question_and_citations_retained(self):
        p=self.packet
        self.assertIn("every positive integer",p["question"])
        self.assertEqual(p["research_status"],
                         "OPEN_PROBLEM_GLOBAL_ANSWER_NOT_ESTABLISHED")
        self.assertTrue(all(x["not_a_global_proof"] for x in p["sources"]))
        self.assertFalse(p["automatic_admission"])
        self.assertFalse(p["no_new_mathematical_theorem_claimed"] is False)
        self.assertEqual(p["external_authority"],"NONE")

    def test_correct_original_collatz_and_independent_fast_form(self):
        for n in range(1,2000):
            self.assertEqual(T(n),reference_T(n))
            self.assertEqual(C(n),3*n+1 if n&1 else n//2)
        for bad in (0,-1,2.5,True):
            with self.assertRaises(HOLD):
                T(bad)

    def test_false_global_monotonicity_is_falsified_not_promoted(self):
        n=self.packet["counterexample_to_naive_question"]
        self.assertEqual(n["counterexample"],{"n":3,"T_n":5})
        self.assertEqual(n["result"],"REFUTED_BY_EXACT_COUNTEREXAMPLE")
        self.assertTrue(n["conjecture_original_question_not_refuted"])

    def test_new_question_type_is_universal_residue_certification(self):
        self.assertIn("QUANTIFY_ALL_IN_RESIDUE_CLASS",PRIMITIVES)
        self.assertEqual(self.packet["meta_generated_question_type"],
            "MODULAR_CONDITIONED_SYMBOLIC_K_STEP_STRICT_DESCENT_CERTIFICATE")
        self.assertEqual(len(self.packet["all_depths_and_proof_cards"]),8)
        for k,row in enumerate(self.packet["all_depths_and_proof_cards"],1):
            self.assertEqual(row["modulus"],2**k)
            self.assertEqual(len(row["proof_cards"]),2**k)
            self.assertTrue(row["all_residue_classes_exhausted"])
            self.assertEqual(
                row["non_descent_at_this_fixed_depth_class_count"]+
                row["guaranteed_eventual_descent_class_count"],2**k)

    def test_all_infinitely_many_one_mod_four_cases_rigorously_descend_locally(self):
        c=certificate(2,1)
        self.assertEqual(c["symbolic_affine"],{
            "a":3,"b":1,"denominator":4})
        self.assertTrue(c["uniform_for_every_n_gt_one_in_class"])
        self.assertEqual(c["first_certified_n_gt_one"],5)
        self.assertTrue(verify_certificate(c))
        lemma=self.packet["globally_valid_but_restricted_lemma"]
        self.assertEqual(lemma["proof_card"],c)
        self.assertTrue(lemma["this_is_known_elementary_mathematics_not_novel"])
        self.assertTrue(lemma["this_does_not_prove_collatz"])

    def test_odd_three_mod_four_does_not_descend_in_first_two_T_steps(self):
        c=certificate(2,3)
        self.assertEqual(c["symbolic_affine"],{
            "a":9,"b":5,"denominator":4})
        self.assertEqual(c["classification"],
            "NO_STRICT_DESCENT_AT_THIS_FIXED_DEPTH_FOR_CLASS")
        self.assertIsNone(c["first_certified_n_gt_one"])
        self.assertTrue(verify_certificate(c))
        self.assertEqual(T(T(3)),8)

    def test_small_exception_to_eventual_residue_descent_not_suppressed(self):
        c=certificate(2,2)
        self.assertEqual(c["symbolic_affine"],{"a":3,"b":2,"denominator":4})
        self.assertEqual(c["first_certified_n_gt_one"],6)
        self.assertFalse(c["uniform_for_every_n_gt_one_in_class"])
        self.assertEqual(T(T(2)),2)
        self.assertEqual(T(T(6)),5)
        self.assertTrue(verify_certificate(c))

    def test_two_independent_algebra_algorithms_agree_all_256_classes(self):
        for k in range(1,9):
            for r in range(1<<k):
                c=certificate(k,r)
                self.assertEqual(c["symbolic_affine"],
                                 independent_classical_certificate(k,r))
                self.assertTrue(verify_certificate(c))

    def test_finite_observations_are_not_infinite_proof(self):
        finite=self.packet["finite_local_sweep"]
        self.assertEqual(finite["first"],1)
        self.assertEqual(finite["last"],4096)
        self.assertEqual(finite["saw_reach_one"],4096)
        self.assertEqual(finite["saw_hold"],0)
        self.assertTrue(self.packet["known_public_prior_computation_exceeds_this_sweep"])
        self.assertTrue(self.packet["why_open_problem_still_unanswered"])
        self.assertTrue(self.packet["next_question_automatically_marked_unresolved"])

    def test_source_owner_receipt_replay_and_changed_revision_refusal(self):
        owner=FiniteSourceOwner()
        receipt=owner.ask(27)
        self.assertEqual(receipt["status"],"REACHED_ONE")
        self.assertTrue(owner.recheck(receipt))
        forged=copy.deepcopy(receipt)
        forged["trace"][1]=7
        forged["integrity_digest"]=digest({k:v for k,v in forged.items()
                                           if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            owner.recheck(forged)
        with self.assertRaises(HOLD):
            FiniteSourceOwner(revision=2).recheck(receipt)
        for recorded in self.packet["finite_source_receipts"]:
            FiniteSourceOwner().recheck(recorded)

    def test_rehashed_false_universal_lemma_is_refused(self):
        altered=copy.deepcopy(self.packet)
        c=altered["globally_valid_but_restricted_lemma"]["proof_card"]
        c["uniform_for_every_n_gt_one_in_class"]=False
        altered["all_depths_and_proof_cards"][1]["proof_cards"][1][
            "uniform_for_every_n_gt_one_in_class"]=False
        altered["integrity_digest"]=digest({k:v for k,v in altered.items()
                                             if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(altered)

    def test_reentry_recomputes_proofs_and_asks_zero_new_questions(self):
        carried=json.loads(json.dumps(self.packet))
        receipt=reenter(carried)
        self.assertEqual(receipt["new_investigative_questions"],0)
        self.assertFalse(receipt["global_answer_available"])
        self.assertEqual(receipt["answer_packet_digest"],
                         self.packet["integrity_digest"])

    def test_refuse_invalid_unbounded_problem_specifications(self):
        for args in ({"max_k":0},{"max_k":13},{"finite_n":0},
                     {"finite_n":20001}):
            with self.assertRaises(HOLD):
                investigate_open_problem(**args)
        with self.assertRaises(HOLD):
            certificate(2,4)
        with self.assertRaises(HOLD):
            certificate(True,1)


if __name__=="__main__":
    unittest.main()
