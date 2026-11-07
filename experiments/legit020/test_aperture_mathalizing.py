"""MOTIF LEGIT-020 adversarial APERTURE × Dogram × mathalizing tests.

The independent inputs intentionally preserve uncertainty and distinguish
mathematically valid transformations from human intent, original source
claims, historical novelty, and externally observed improvement.
"""
from __future__ import annotations
from dataclasses import FrozenInstanceError
from hashlib import sha1
from itertools import product
from pathlib import Path
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from aperture import (
    ALL_CELLS,Reading,open_aperture,update_context,
    mathalize,receipt_hash,speak_math,allow_admission,HOLD
)
from perspectives import (
    LEFT,RIGHT,_graphs,graph_spectrum,graph_probe_ladder,
    prove_signedness_difference,verify_double_math,collapse_receipt,
    verify_dogram_source,homomorphism_count,branching_star_hom_count,
    isomorphic,adjacency_matrix
)
from benchmark import run,one_case,CHALLENGES,STATUS
from vendor_dogram.probe_partition_refinement import factorization_map
from vendor_dogram.anti_collapse_reachability import analyze_collapse
from vendor_dogram.operation_reachability_quotient import analyze_operation_reachability

class ApertureMathalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=run()

    def test_real_dogram_kernel_origin_and_git_objects_are_exact(self):
        provenance=verify_dogram_source()
        self.assertEqual(provenance["original_repository"],
                         "the-static-collective/Dogram")
        self.assertEqual(provenance["original_commit"],
                         "551b5f9df18f17ec69b452ddcdff01718e0ff771")
        self.assertEqual(len(provenance["actual_dogram_modules_verified"]),4)
        for filename,sha in provenance["actual_dogram_modules_verified"].items():
            raw=(HERE/"vendor_dogram"/Path(filename).name).read_bytes()
            actual=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
            self.assertEqual(actual,sha)

    def test_sparse_three_orthogonal_axes_are_addresses_not_27_claims(self):
        self.assertEqual(len(ALL_CELLS),27)
        bank=mathalize(open_aperture("The bank moved."))
        self.assertEqual(len(bank["sparse_27_cell_addresses"]),2)
        self.assertLess(len(bank["sparse_27_cell_addresses"]),27)
        for cell in bank["sparse_27_cell_addresses"]:
            self.assertIn(tuple(cell),ALL_CELLS)

    def test_ambiguous_graph_keeps_three_different_reading_questions(self):
        raw=open_aperture("Are these two graphs the same?")
        self.assertEqual(len(raw.candidates),3)
        self.assertEqual(tuple(x.name for x in raw.candidates),
                         ("WALK_EQ","CLAW_EQ","ISOMORPHIC"))
        self.assertTrue(raw.pending)
        self.assertFalse(raw.admitted)

    def test_unknown_language_is_honest_hold_not_forced_math(self):
        unsupported=open_aperture("The hidden thing becomes translucent tomorrow.")
        data=mathalize(unsupported)
        self.assertEqual(data["language_to_math_candidates"],[])
        self.assertIsNone(data["accepted_meaning"])
        self.assertEqual(data["unresolved_gaps"],
                         ["NO_DECLARED_LANGUAGE_TO_MATH_DECODER"])
        self.assertFalse(data["human_authority_admitted"])

    def test_context_creates_child_but_preserves_original_receipt(self):
        old=open_aperture("The bank moved.")
        sha=receipt_hash(old)
        new=update_context(old,"Erosion shifted the riverbank.")
        self.assertEqual(receipt_hash(old),sha)
        self.assertEqual(new.parent_sha256,sha)
        self.assertEqual(new.source_sha256,old.source_sha256)
        self.assertEqual(new.raw,old.raw)
        self.assertEqual(tuple(x.name for x in old.candidates),
                         ("RIVERBANK","BANK_INSTITUTION"))
        self.assertEqual(tuple(x.name for x in new.candidates),("RIVERBANK",))
        self.assertNotEqual(receipt_hash(new),receipt_hash(old))

    def test_ambiguous_receipt_and_child_are_immutable(self):
        a=open_aperture("The bank moved.")
        b=update_context(a,"A financial institution moved its branch office.")
        with self.assertRaises(FrozenInstanceError):
            a.raw="rewritten"
        with self.assertRaises(FrozenInstanceError):
            b.parent_sha256="forged"
        self.assertEqual(tuple(x.name for x in a.candidates),
                         ("RIVERBANK","BANK_INSTITUTION"))

    def test_context_cannot_conjure_a_different_domain(self):
        field=open_aperture("The bank moved.")
        with self.assertRaises(HOLD):
            update_context(field,"Treat x as a signed 64-bit word.")
        with self.assertRaises(HOLD):
            update_context(field,"Random unrelated sentence.")
        with self.assertRaises(HOLD):
            update_context(field,"")
        with self.assertRaises(HOLD):
            open_aperture("")

    def test_appearing_fact_role_never_promotes_world_fact(self):
        case=mathalize(open_aperture("The bank moved."))
        for c in case["language_to_math_candidates"]:
            self.assertEqual(c["semantic_role"],"IDEA")
            self.assertEqual(c["epistemic_status"],"POSSIBLE_NOT_ADMITTED")
            self.assertEqual(c["authority"],"PROPOSAL_ONLY")
        self.assertIsNone(case["accepted_meaning"])
        with self.assertRaises(HOLD):
            allow_admission(open_aperture("The bank moved."))

    def test_dogram_factorization_and_collapse_lost_graph_perspectives(self):
        src=open_aperture("Are these two graphs the same?")
        delta=collapse_receipt(src)
        self.assertTrue(delta["lawful_quotient"])
        self.assertEqual(len(delta["lost_reading_pairs"]),3)
        self.assertEqual(len(delta["lost_operation_questions"]),6)
        self.assertTrue(delta["lost_future_operation_executability"])

    def test_dogram_loss_reports_shift_signedness_and_bank_ambiguity(self):
        for raw in ("Shift x right by one bit.","The bank moved."):
            delta=collapse_receipt(open_aperture(raw))
            self.assertEqual(len(delta["source_readings"]),2)
            self.assertEqual(len(delta["lost_reading_pairs"]),1)
            self.assertEqual(len(delta["lost_operation_questions"]),2)

    def test_dogram_illegal_pseudocollapse_is_rejected(self):
        # This is the ACTUAL upstream Dogram law, not a reconstruction.
        v=analyze_collapse(("a","b"),(0,0),(0,1))
        self.assertFalse(v.lawful_quotient)
        self.assertIsNone(v.factorization_witness)

    def test_identical_raw_graphs_have_different_truth_under_apertures(self):
        witness=graph_spectrum()
        self.assertTrue(witness["perspective_PATH"]["equal"])
        self.assertFalse(witness["perspective_BRANCH"]["equal"])
        self.assertFalse(witness["perspective_ISOMORPHISM"]["equal"])
        self.assertTrue(witness["same_under_one_projection_not_same_under_all"])

    def test_all_path_lengths_certified_not_only_first_nine(self):
        witness=graph_spectrum()
        for side in ("left","right"):
            cert=witness["perspective_PATH"][side+"_linear_path_recurrence"]
            self.assertTrue(cert["valid"])
            self.assertEqual(cert["eigenvalue"],2)
            self.assertEqual(cert["vertex_count"],7)
            self.assertEqual(cert["first_walk_count"],12)
        self.assertEqual(witness["perspective_PATH"]["finite_sample_walks"],
                         [7,12,24,48,96,192,384,768,1536])

    def test_branching_star_three_first_distinguishes_graphs(self):
        result=graph_spectrum()
        probes=result["perspective_BRANCH"]["star_sequence"]
        self.assertEqual([r["left_count"] for r in probes],[12,24,48])
        self.assertEqual([r["right_count"] for r in probes],[12,24,54])
        self.assertEqual([r["distinguishes"] for r in probes],
                         [False,False,True])
        self.assertEqual(result["perspective_BRANCH"][
            "independent_complete_four_node_claw_mapping"],
            {"left":48,"right":54})

    def test_actual_pinned_dogram_probe_lattice_finds_minimal_branches(self):
        r=graph_probe_ladder()
        self.assertEqual(r["min_separating_probe_in_supplied_family"],
                         ("BRANCH_3",))
        self.assertTrue(r["path_is_strictly_weaker_than_branch_on_this_pair"])
        self.assertTrue(r["minimality_only_in_supplied_family"])
        self.assertFalse(r["separation_underlying_carrier_change"])

    def test_isomorphism_false_even_when_all_path_counts_equal(self):
        a,b=_graphs()
        self.assertFalse(isomorphic(a,b))
        self.assertEqual(sorted(map(sum,a)),[0,2,2,2,2,2,2])
        self.assertEqual(sorted(map(sum,b)),[1,1,1,1,2,2,3])

    def test_genuine_external_Z3_counterexample_signed_vs_unsigned(self):
        result=prove_signedness_difference()
        self.assertEqual(result["external_z3_status"],
                         "SAT_COUNTEREXAMPLE_TO_EQUIVALENCE")
        self.assertNotEqual(result["unsigned_logical_result"],
                            result["signed_arithmetic_result_twos_complement"])
        self.assertGreaterEqual(int(result["example_x"],16),1<<63)
        self.assertTrue(result["low_magnitude_inputs_may_collide"])

    def test_double_x_math_bridge_reuses_actual_previous_proof(self):
        result=verify_double_math()
        self.assertTrue(result["external_Z3_proves_equivalence"])
        self.assertTrue(result["prior_actual_LEGIT019_receipt_verified"])
        self.assertFalse(result["historically_novel_math"])
        self.assertEqual(result["proof_width_bits"],64)

    def test_same_words_can_lower_into_different_valid_math_queries(self):
        raw=open_aperture("Are these two graphs the same?")
        path=update_context(raw,"I mean compare linear walks.")
        tree=update_context(raw,"I mean compare branching three-leaf trees.")
        self.assertNotEqual(mathalize(path)["language_to_math_candidates"][0]
                            ["typed_mathematical_question"],
                            mathalize(tree)["language_to_math_candidates"][0]
                            ["typed_mathematical_question"])
        self.assertEqual(mathalize(path)["parent_receipt_sha256"],
                         mathalize(tree)["parent_receipt_sha256"])

    def test_nine_registered_context_interpretations_remain_unadmitted(self):
        for raw,ctx,expected in CHALLENGES:
            row=one_case(raw,ctx,expected)
            self.assertEqual(row["compatible_reading_after_cut"],expected)
            self.assertTrue(row["original_alternatives_preserved"])
            self.assertFalse(row["admitted"])
            self.assertTrue(row["contextual_resolution_not_authorized_intent"])

    def test_weak_single_guess_is_not_fair_optimized_linguistic_comparator(self):
        comparison=self.report["comparison"]
        self.assertEqual(comparison["tests"],9)
        self.assertEqual(comparison[
            "deliberately_early_single_reading_baseline_matches"],4)
        self.assertEqual(comparison["aperture_after_declared_context_matches"],9)
        self.assertEqual(comparison["strong_context_aware_parser_matches"],9)
        self.assertTrue(comparison["no_superiority_over_strong_context_parser"])
        self.assertTrue(comparison["not_fair_open_world_language_benchmark"])

    def test_receipt_has_no_new_math_or_auto_promotions(self):
        gates=self.report["gates"]
        self.assertFalse(gates["general_language_understanding_demonstrated"])
        self.assertFalse(gates["new_math_historically_original"])
        self.assertFalse(gates["improves_external_SyGuS_2017_results"])
        self.assertFalse(gates["independently_verified_recursive_compounding"])
        self.assertFalse(gates["automatic_source_promotion"])
        self.assertFalse(self.report["real_world_authority"])
        self.assertFalse(self.report["main_branch_automatically_changed"])
        self.assertEqual(self.report["status"],STATUS)

if __name__=="__main__":
    unittest.main()
