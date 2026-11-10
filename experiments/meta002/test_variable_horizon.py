"""META-002 — falsifiers and fair classical equivalence for partial Collatz ranks."""
from __future__ import annotations
from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from variable_horizon import (
    HOLD, T, minimum_member_over_one, classical_first_descent,
    compare_finite_horizon, _first_card, _check_lifted_card,
    weighted_potential_value, refute_everywhere_one_step_linear_potential,
    verify_weighted_obstruction, investigate, verify_packet, reenter, digest,
)


class VariableTimeRankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=investigate(k=9)

    def test_original_problem_remains_open(self):
        self.assertEqual(self.packet["global_status"],"OPEN_HOLD_NO_UNIVERSAL_PROOF")
        self.assertTrue(self.packet["equivalence_known_classical_not_new"])
        self.assertFalse(self.packet["methodology_discovered_historically_novel"])
        self.assertTrue(self.packet["same_information_classical_solver_tied"])
        self.assertFalse(self.packet["automatic_admission"])
        self.assertEqual(self.packet["external_authority"],"NONE")

    def test_variable_time_beats_restricted_final_step_not_fair_solver(self):
        card=self.packet["main_level"]
        self.assertEqual(card["modulus"],512)
        self.assertEqual(card["fixed_horizon_strict_descent_classes"],382)
        self.assertEqual(card["adaptive_variable_time_certified_infinite_classes"],474)
        self.assertEqual(card["classical_independent_adaptive_certified_classes"],474)
        self.assertEqual(card["additional_class_distinctions_over_fixed"],92)
        self.assertEqual(card["honest_uncertified_classes"],38)
        self.assertEqual(len(card["complete_research_cards"]),512)
        self.assertEqual(len(card["unresolved_residues"]),38)
        self.assertIn(511,card["unresolved_residues"])
        self.assertTrue(card["same_information_strong_classical_tie"])

    def test_level_by_level_all_residues_recounted_without_dropped_cases(self):
        reports=self.packet["summary_by_maximum_depth"]
        self.assertEqual(len(reports),9)
        for k,report in enumerate(reports,1):
            self.assertEqual(report["modulus"],2**k)
            self.assertEqual(report["adaptive_variable_time_certified_infinite_classes"]+
                             report["honest_uncertified_classes"],2**k)
            self.assertEqual(report["adaptive_variable_time_certified_infinite_classes"],
                             report["classical_independent_adaptive_certified_classes"])
            self.assertTrue(report["all_odd_residue_is_uncertified"])
            self.assertGreaterEqual(report["adaptive_variable_time_certified_infinite_classes"],
                                    report["fixed_horizon_strict_descent_classes"])
        self.assertEqual(reports[5]["honest_uncertified_classes"],8)

    def test_lifted_infinite_class_affine_lemmas_are_verified(self):
        for row in self.packet["main_level"]["complete_research_cards"]:
            k=9
            self.assertTrue(_check_lifted_card(k,row["residue"],row))
            independent=classical_first_descent(k,row["residue"])
            self.assertEqual(independent,row["first_certified_horizon"])
            if independent is not None:
                n0=row["least_positive_n_gt_one"]
                n=n0
                for _ in range(independent):
                    n=T(n)
                self.assertLess(n,n0)
                self.assertTrue(row["certificate"]["global_collatz_conjecture_proven"] is False)
            else:
                self.assertEqual(row["status"],
                    "HOLD_NO_VARIABLE_HORIZON_CERTIFICATE_WITHIN_K")

    def test_edge_examples_n_equal_one_and_two_not_confused(self):
        self.assertEqual(minimum_member_over_one(9,0),512)
        self.assertEqual(minimum_member_over_one(9,1),513)
        self.assertEqual(minimum_member_over_one(9,2),2)
        with self.assertRaises(HOLD):
            minimum_member_over_one(9,512)
        with self.assertRaises(HOLD):
            minimum_member_over_one(0,0)
        self.assertEqual(classical_first_descent(9,2),1)

    def test_two_more_levels_transfer_without_changing_search_grammar(self):
        twelve=compare_finite_horizon(12,detailed=False)
        self.assertEqual(twelve["fixed_horizon_strict_descent_classes"],3301)
        self.assertEqual(twelve["adaptive_variable_time_certified_infinite_classes"],3870)
        self.assertEqual(twelve["honest_uncertified_classes"],226)
        self.assertEqual(twelve["classical_independent_adaptive_certified_classes"],3870)
        self.assertEqual(twelve["additional_class_distinctions_over_fixed"],569)
        self.assertTrue(twelve["all_odd_residue_is_uncertified"])

    def test_finite_state_positive_weights_obstructed_constructively(self):
        for record in self.packet["general_rank_no_go_evidence"]:
            self.assertTrue(verify_weighted_obstruction(record))
            self.assertGreater(record["actual_potential_end"],
                               record["actual_potential_start"])
            self.assertGreater(record["rigorous_lower_bound_at_end"],
                               record["rigorous_upper_bound_at_start"])
            self.assertGreaterEqual(
                record["first_non_decreasing_step"]["potential_after"],
                record["first_non_decreasing_step"]["potential_before"])
            self.assertFalse(record["refutes_global_collatz_conjecture"])
            self.assertTrue(record["does_not_exclude_variable_time_or_non_linear_potentials"])
            self.assertEqual(len(record["full_source_trajectory"]),
                             record["all_odd_diagonal_k"])

    def test_outside_sample_weighted_potentials_also_cannot_work(self):
        for w,b in [
            ([1,64],[0,-1000]),
            ([64,1,32,11],[1000,0,-1000,3]),
            ([1,1,1,1,1,1,1,1],[9,-3,4,2,-7,8,0,1]),
            ([2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53],
             list(range(-8,8))),
        ]:
            record=refute_everywhere_one_step_linear_potential(w,b)
            self.assertTrue(verify_weighted_obstruction(record))
            self.assertGreater(record["actual_potential_end"],record["actual_potential_start"])
        with self.assertRaises(HOLD):
            weighted_potential_value(5,[1,0],[0,0])
        with self.assertRaises(HOLD):
            weighted_potential_value(5,[1],[0])

    def test_proven_general_all_odd_obstruction_remains_compatible_with_variable_time(self):
        obstruction=self.packet["inherited_negative_fixed_k_strategy"]
        self.assertTrue(obstruction["not_a_counterexample_to_collatz"])
        self.assertEqual(obstruction["tested_finite_depths"],9)
        self.assertTrue(all(x["exact_k_step_value"]>x["witness_n"]
                            for x in obstruction["proof_instances"]))
        self.assertIn("well-founded",self.packet["next_discriminating_question"])

    def test_uncertified_infinite_classes_finite_samples_do_not_become_certificates(self):
        examples=self.packet["finite_observations_on_uncovered_classes"]
        self.assertEqual(len(examples),5)
        self.assertEqual([x["class_residue"] for x in examples],
                         self.packet["main_level"]["unresolved_residues"][:5])
        for item in examples:
            self.assertFalse(item["proves_entire_infinite_class"])
            self.assertEqual(item["status"],
                             "FINITE_REPRESENTATIVE_NOT_UNIVERSAL_EVIDENCE")
            self.assertGreater(item["observed_first_descent_step_for_this_one_integer"],0)
            self.assertEqual(item["source_observation"]["global_conjecture_proved"],False)

    def test_rehashing_failed_rank_witness_does_not_create_proof(self):
        tampered=deepcopy(self.packet)
        tampered["general_rank_no_go_evidence"][0]["actual_potential_end"]=-1
        tampered["integrity_digest"]=digest({
            k:v for k,v in tampered.items() if k!="integrity_digest"
        })
        with self.assertRaises(HOLD):
            verify_packet(tampered)

    def test_rehashing_horizon_coverage_cannot_erase_hold(self):
        tampered=deepcopy(self.packet)
        tampered["main_level"]["honest_uncertified_classes"]=0
        tampered["main_level"]["unresolved_residues"]=[]
        tampered["integrity_digest"]=digest({
            k:v for k,v in tampered.items() if k!="integrity_digest"
        })
        with self.assertRaises(HOLD):
            verify_packet(tampered)

    def test_reenter_rechecks_all_sources_without_new_inquiry(self):
        stored=json.loads(json.dumps(self.packet))
        replay=reenter(stored)
        self.assertEqual(replay["new_discovery_questions"],0)
        self.assertFalse(replay["collatz_globally_solved"])
        self.assertTrue(replay["proofs_and_finite_source_observations_fully_replayed"])
        self.assertEqual(replay["research_packet_integrity_digest"],
                         self.packet["integrity_digest"])

    def test_invalid_global_proof_budgets_rejected(self):
        for x in (0,2,13,True):
            with self.assertRaises(HOLD):
                investigate(k=x)
        with self.assertRaises(HOLD):
            compare_finite_horizon(13)
        with self.assertRaises(HOLD):
            classical_first_descent(9,512)


if __name__=="__main__":
    unittest.main()
