"""LEGIT-021 hostile falsifiers for a bounded mathematics-aperture inventor.

The strongest controls are REAL independent enumeration of every source
homomorphism and an exact classical decision-tree DP, not a weak preselected
path-only parser. A "new viewpoint" remains a graph question in a finite
grammar, not a new mathematical law or an interpretation of human intent.
"""
from __future__ import annotations

from itertools import combinations,permutations
from pathlib import Path
from statistics import mean
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from graph_inventor import (
    grammar,characterize,connected,normalized,cycles,
    dogram_calibration,count,reference_count,all_path_collision,
    independent_minimal_separator,invent_separator,selected_action_tree,
    execute_tree,classical_optimal_tree,uniform_entropy_split,HOLD
)
from math_apertures import (
    invent_bitvector_counterprobe,indistinguishable_math,
    perspective_lattice_for_worlds,verify_dogram_source
)
# LEGIT-020 adds its own directory to sys.path; use an exact file import
# rather than silently importing the older "benchmark" module.
import importlib.util
_spec=importlib.util.spec_from_file_location(
    "LEGIT021_BENCHMARK_UNDER_TEST",HERE/"benchmark.py")
_actual=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_actual)
CALIBRATION,VALIDATION,STATUS=_actual.CALIBRATION,_actual.VALIDATION,_actual.STATUS
run,reuse_search,experiment_on_pair=(
    _actual.run,_actual.reuse_search,_actual.experiment_on_pair
)

class InventorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=run()

    def test_source_graphs_are_actually_generated_from_all_combinations(self):
        sources=grammar()
        self.assertEqual(len(sources),10)
        self.assertEqual(len(set(sources)),len(sources))
        self.assertEqual([sum(n==x[0] for x in sources) for n in (1,2,3,4)],
                         [1,1,2,6])
        self.assertTrue(all(connected(n,edges) for n,edges in sources))
        self.assertEqual(sources,tuple(sorted(sources,
                         key=lambda p:(p[0],len(p[1]),p[1]))))

    def test_source_graph_canonicalization_is_relabeling_invariant(self):
        for n,edges in grammar():
            for perm in list(permutations(range(n)))[:8]:
                transformed=tuple((perm[a],perm[b]) for a,b in edges)
                self.assertEqual(normalized(n,edges),
                                 normalized(n,transformed))

    def test_enumerator_contains_triangle_and_star_and_square_without_templates(self):
        samples=[characterize(p) for p in grammar()]
        self.assertEqual(sum(p["triangle"] for p in samples),1)
        self.assertEqual(sum(p["three_leaf_star"] for p in samples),1)
        self.assertEqual(sum(p["four_cycle"] for p in samples),1)
        self.assertTrue(all(p["generated_from_connected_graph_enumeration"]
                            and not p["previously_authored_probe_template"]
                            for p in samples))

    def test_original_Dogram_source_is_really_pinned_through_020(self):
        fixed=verify_dogram_source()
        self.assertEqual(fixed["original_repository"],
                         "the-static-collective/Dogram")
        self.assertEqual(len(fixed["actual_dogram_modules_verified"]),4)
        self.assertFalse(fixed["vendor_copy_is_canonical_project_ownership"])

    def test_all_path_equivalence_proof_on_both_original_pairs(self):
        for name,pair in CALIBRATION:
            proved=all_path_collision(pair)
            self.assertTrue(proved["same_all_finite_paths"])
            self.assertTrue(all(x["valid"] for x in proved["certificates"]))
            self.assertEqual(len(set(proved["first_nine_walk_counts"])),9)

    def test_first_unlabeled_probe_for_regular_6_worlds_is_triangle(self):
        pair=(cycles(6),cycles(3,3))
        proof=invent_separator(pair)
        self.assertTrue(proof["first_separating_probe"]["triangle"])
        self.assertEqual(proof["first_separating_counts"],[0,12])
        self.assertEqual(proof["search_probes_inspected"],4)
        self.assertTrue(proof["independent_classical_exhaustive_minimum_agrees"])

    def test_Dogram_path_collision_requires_branching_not_new_world(self):
        pair=dogram_calibration()
        proof=invent_separator(pair)
        self.assertTrue(proof["first_separating_probe"]["three_leaf_star"])
        self.assertEqual(proof["first_separating_counts"],[48,54])
        self.assertTrue(all(not p["separates"]
                            for p in proof["actual_failed_probe_receipts"]))

    def test_triangle_transfer_on_new_7_and_8_vertex_instances(self):
        tri=next(p for p in grammar() if characterize(p)["triangle"])
        for name,pair in VALIDATION[:2]:
            proof=invent_separator(pair)
            self.assertTrue(proof["first_separating_probe"]["triangle"])
            reuse=reuse_search(pair,(tri,))
            self.assertEqual(reuse["probes_evaluated_including_prior_failures"],1)
            self.assertTrue(reuse["selected_matches_grammar_global_minimum"])
            self.assertLess(reuse["probes_evaluated_including_prior_failures"],
                            proof["search_probes_inspected"])

    def test_four_cycle_missing_aperture_in_new_worlds_is_actually_invented(self):
        pair=VALIDATION[2][1]
        proof=invent_separator(pair)
        self.assertTrue(proof["first_separating_probe"]["four_cycle"])
        self.assertEqual(proof["first_separating_counts"],[48,64])
        self.assertTrue(proof["independent_classical_exhaustive_minimum_agrees"])

    def test_actual_prior_views_do_not_hide_a_later_missing_view(self):
        tri=next(p for p in grammar() if characterize(p)["triangle"])
        star=next(p for p in grammar() if characterize(p)["three_leaf_star"])
        reuse=reuse_search(VALIDATION[2][1],(tri,star))
        self.assertTrue(reuse["selected"]["four_cycle"])
        self.assertTrue(reuse["selected_matches_grammar_global_minimum"])
        self.assertEqual([x["origin"] for x in reuse["actual_trace"][:2]],
                         ["PRIOR_GENERATION","PRIOR_GENERATION"])
        self.assertFalse(reuse["actual_trace"][0]["separates"])
        self.assertFalse(reuse["actual_trace"][1]["separates"])

    def test_all_found_probes_have_independent_assignment_count(self):
        for _,pair in CALIBRATION+VALIDATION:
            probe,values,_=independent_minimal_separator(pair)
            self.assertIsNotNone(probe)
            self.assertEqual(values,tuple(count(probe,t) for t in pair))
            self.assertEqual(values,tuple(reference_count(probe,t)
                                          for t in pair))

    def test_identical_worlds_do_not_generate_a_false_difference(self):
        same=(cycles(6),cycles(6))
        self.assertTrue(all_path_collision(same)["same_all_finite_paths"])
        no=invent_separator(same)
        self.assertIsNone(no["first_separating_probe"])
        self.assertEqual(no["search_probes_inspected"],len(grammar()))
        self.assertEqual(no["actual_failed_probe_receipts"].__len__(),
                         len(grammar()))

    def test_Dogram_three_world_probe_lattice_is_not_single_perspective(self):
        worlds=(cycles(8),cycles(3,5),cycles(4,4))
        r=perspective_lattice_for_worlds(worlds)
        self.assertTrue(r["linear_path_counts_equal_for_all_lengths"])
        self.assertEqual(r["worlds"],
                         ("C8","C3_PLUS_C5","C4_PLUS_C4"))
        self.assertEqual(len(set(r["triangle_counts"])),2)
        self.assertEqual(len(set(r["four_cycle_counts"])),2)
        self.assertEqual(len(r["original_Dogram_partitions"]),3)
        self.assertTrue(r["source_probe_is_part_of_mathematical_question"])

    def test_greedy_active_questions_resolve_all_worlds_with_correct_receipts(self):
        worlds=(cycles(8),cycles(3,5),cycles(4,4))
        tree=selected_action_tree(worlds)["tree"]
        answers=[execute_tree(tree,t) for t in worlds]
        self.assertEqual([x["resolved_world_index"] for x in answers],[0,1,2])
        self.assertEqual([len(x["trace"]) for x in answers],[2,1,2])
        self.assertTrue(characterize(grammar()[tree["question_index"]])["triangle"])

    def test_exact_classical_DP_is_at_least_as_good_as_proposed_greedy_tree(self):
        worlds=(cycles(8),cycles(3,5),cycles(4,4))
        plan=selected_action_tree(worlds)["tree"]
        total=sum(len(execute_tree(plan,t)["trace"]) for t in worlds)
        optimum=classical_optimal_tree(worlds)
        self.assertLessEqual(optimum["minimum_sum_questions"],total)
        self.assertEqual(total,5)
        self.assertEqual(optimum["minimum_sum_questions"],5)
        self.assertEqual(optimum["minimum_mean_questions"],5/3)
        self.assertTrue(optimum["exact_classical_finite_dynamic_programming"])

    def test_active_viewpoints_are_better_than_fixed_two_test_program_on_three_worlds(self):
        worlds=(cycles(8),cycles(3,5),cycles(4,4))
        total=sum(len(execute_tree(selected_action_tree(worlds)["tree"],t)["trace"])
                  for t in worlds)
        fixed=2*len(worlds)
        self.assertEqual(total,5)
        self.assertEqual(fixed,6)
        # The strong exact classical planner ties the active result.
        self.assertEqual(classical_optimal_tree(worlds)["minimum_sum_questions"],5)

    def test_an_unseparated_pair_stays_unresolved_without_lying(self):
        worlds=(cycles(6),cycles(6))
        plan=selected_action_tree(worlds)["tree"]
        self.assertTrue(plan["HOLD"])
        self.assertEqual(plan["unresolved_states"],[0,1])

    def test_active_split_criterion_does_not_reward_nondiscriminating_observation(self):
        self.assertEqual(uniform_entropy_split((4,4,4),(0,1,2)),0)
        self.assertEqual(uniform_entropy_split((3,4,3),(0,1,2)),4)
        self.assertEqual(uniform_entropy_split((3,4,5),(0,1,2)),6)

    def test_Z3_invents_globally_minimum_unsigned_signedness_witness(self):
        proof=invent_bitvector_counterprobe()
        self.assertEqual(proof["witness_unsigned_x"],
                         "0x8000000000000000")
        self.assertEqual(proof["logical_output"],"0x4000000000000000")
        self.assertEqual(proof["arithmetic_output_twos_complement"],
                         "0xc000000000000000")
        self.assertEqual(proof["independent_Z3_no_smaller_unsigned_witness"],
                         "UNSAT")
        self.assertTrue(proof["minimal_within_all_unsigned_64bit_inputs"])
        self.assertTrue(proof["model_does_not_claim_to_know_user_intent"])

    def test_math_equivalence_is_proven_no_numeric_counterprobe_exists(self):
        result=indistinguishable_math()
        self.assertFalse(result["different_observation_possible"])
        self.assertEqual(result["separation_query_Z3_result"],"UNSAT")
        self.assertTrue(result["known_identity_reused_from_LEGIT019"])
        self.assertTrue(result["does_not_erase_source_reading_difference"])

    def test_earlier_aperture_perspectives_remain_visible_and_unadmitted(self):
        packet=self.packet["raw_language_aperture"]
        self.assertEqual([r["id"] for r in packet[
            "language_to_math_candidates"]],
            ["WALK_EQ","CLAW_EQ","ISOMORPHIC"])
        self.assertFalse(packet["human_authority_admitted"])
        self.assertIsNone(packet["accepted_meaning"])
        self.assertEqual(len(packet["sparse_27_cell_addresses"]),2)

    def test_actual_generation_transfer_is_just_cached_known_questions(self):
        r=self.packet
        self.assertEqual(len(r["two_calibration_invention_trials"]),2)
        self.assertEqual(len(r["validation_trials"]),3)
        self.assertTrue(r["bounded_generated_source_grammar"][
            "minimum_is_only_within_declared_grammar"])
        self.assertTrue(r["measured_planner_comparison"][
            "calibration_learned_apertures_are_really_reused"])
        self.assertFalse(r["measured_planner_comparison"][
            "independently_demonstrated_recursive_compounding"])
        self.assertFalse(r["limits"]["automatic_source_merge_or_deploy"])

    def test_declared_result_never_claims_new_math_or_authority(self):
        p=self.packet
        self.assertEqual(p["status"],STATUS)
        self.assertFalse(p["measured_planner_comparison"][
            "new_historical_math_proven"])
        self.assertFalse(p["limits"]["human_intent_not_inferred_from_probe"] is False)
        self.assertFalse(p["limits"]["not_general_mathematical_operation_invention"] is False)
        self.assertFalse(p["limits"]["public_SyGuS_benchmark_not_rerun"] is False)

if __name__=="__main__":
    unittest.main()
