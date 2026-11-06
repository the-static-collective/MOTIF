"""LEGIT-010 falsifiers: a reasoning engine using its own generated methods
to construct its next methods, under independent finite verification.

No unreviewed Python is generated or evaluated; portable programs are typed
NAND and composition data. All results remain synthetic research HOLD.
"""
from __future__ import annotations

from copy import deepcopy
from itertools import product
from pathlib import Path
import inspect
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.append(str(HERE.parent/"legit009"))

import bootstrap
from bootstrap import (
    HOLD,BinarySpecification,library,catalog,
    invent_successor_search,_compressed_candidates,_validate_search,
    synthesize_successor,reverify_successor,build_four_input,
    reverify_four_input,compose_circuit
)
from independent_oracle import (
    TernaryVerifier,QuaternaryVerifier,TRI_TASKS,UNREACHABLE,
    independent_minimal_composition,flat_nand_search,interpret
)
from benchmark import execute
from synthesizer import load_verified


class SelfBootstrappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.methods=library()
        cls.meta_receipt=invent_successor_search()
        cls.meta=cls.meta_receipt["algorithm"]
        cls.parity=synthesize_successor(
            TernaryVerifier("ODD_PARITY3"),cls.meta,"ODD_PARITY3")
        cls.quad=build_four_input(cls.parity["program"],cls.meta)

    def test_actual_legit009_generator_is_imported_not_reimplemented(self):
        source=inspect.getsource(bootstrap)
        self.assertIn("from synthesizer import cegis as PREVIOUS_CEGIS",source)
        self.assertIn("PREVIOUS_CEGIS(oracle,",source)
        self.assertEqual(len(self.methods),16)

    def test_all_sixteen_prior_generated_methods_independently_reverified(self):
        for mask,cartridge in self.methods.items():
            self.assertEqual(cartridge["truth_mask"],mask)
            self.assertEqual(
                load_verified(cartridge,BinarySpecification(mask))["status"],
                "FINITE_TRUTH_TABLE_VERIFIED")
            self.assertFalse(cartridge["real_world_authority"])

    def test_generated_binary_programs_not_handwritten_circuits(self):
        self.assertEqual(
            self.methods[6]["gate_count"],4)
        self.assertEqual(self.methods[6]["truth_mask"],0b0110)
        self.assertNotEqual(
            self.methods[6]["gates"],[[0,0],[1,1],[0,3],[1,2],[4,5]])

    def test_next_search_algorithm_is_written_by_actual_metacegis(self):
        self.assertEqual(self.meta["schema"],
                         "motif.self-composed-search-program.v1")
        self.assertEqual(self.meta["status"],
                         "FINITE_EQUIVALENCE_CLASSES_PROVED")
        self.assertEqual(self.meta["candidate_compositions"],3072)
        self.assertEqual(self.meta["distinct_truth_functions"],152)
        self.assertEqual(len(_compressed_candidates(self.meta)),152)
        self.assertGreater(self.meta["meta_counterexamples"],0)

    def test_meta_verifier_exposes_real_inequivalent_counterexamples(self):
        source=self.meta_receipt["counterexample_transcript"]
        self.assertEqual(len(source),self.meta["meta_counterexamples"]+1)
        for record in source:
            cex=record["semantic_collision"]
            if cex is None:
                continue
            x,y=cex["witness_masks"]
            row=cex["row"]
            self.assertNotEqual((x>>row)&1,(y>>row)&1)
            self.assertNotIn(row,record["proposed_distinguishing_indices"])
        self.assertIsNone(source[-1]["semantic_collision"])

    def test_no_two_distinct_truths_share_final_learned_signature(self):
        indices=_validate_search(self.meta)
        seen={}
        for r in catalog():
            key=tuple((r["truth_mask"]>>i)&1 for i in indices)
            if key in seen:
                self.assertEqual(r["truth_mask"],seen[key])
            seen[key]=r["truth_mask"]
        self.assertEqual(len(seen),152)

    def test_meta_source_tag_is_not_crypto_identity(self):
        self.assertFalse(self.meta["real_world_authority"])
        self.assertFalse(self.meta["python_self_rewriting_permitted"])
        self.assertTrue(self.meta["generated_program_requires_reverification"])

    def test_tampered_meta_algorithm_is_rejected(self):
        bad=deepcopy(self.meta)
        bad["program"]["distinguishing_rows"]=[0]
        with self.assertRaises(HOLD):
            _compressed_candidates(bad)

    def test_rehashed_but_incomplete_meta_algorithm_is_rejected(self):
        bad=deepcopy(self.meta)
        bad["program"]["distinguishing_rows"]=[0]
        raw={k:v for k,v in bad.items() if k!="sha256"}
        bad["sha256"]=bootstrap._hash(raw)
        with self.assertRaises(HOLD):
            _compressed_candidates(bad)

    def test_unknown_meta_program_cannot_enable_arbitrary_execution(self):
        bad=deepcopy(self.meta)
        bad["python_self_rewriting_permitted"]=True
        raw={k:v for k,v in bad.items() if k!="sha256"}
        bad["sha256"]=bootstrap._hash(raw)
        with self.assertRaises(HOLD):
            _compressed_candidates(bad)

    def test_self_composed_ternary_parity_independently_verified(self):
        art=self.parity["program"]
        self.assertIsNotNone(art)
        proof=reverify_successor(art,TernaryVerifier("ODD_PARITY3"),self.meta)
        self.assertEqual(proof["status"],
                         "VERIFIED_TYPED_THREE_INPUT_ALGORITHM")
        self.assertEqual(art["compiled_NAND"]["truth_mask"],0b10010110)
        self.assertEqual(art["compiled_NAND"]["gate_count"],8)
        self.assertEqual(art["parent_search_program_sha256"],self.meta["sha256"])

    def test_every_binary_truth_input_is_not_conflated_with_three_bit(self):
        program=self.parity["program"]["compiled_NAND"]
        for inputs in product((False,True),repeat=3):
            got=interpret(program["gates"],program["output"],inputs)
            want=(inputs[0]^inputs[1]^inputs[2])
            self.assertIs(got,want)

    def test_all_six_supported_unseen_ternary_tasks_are_generated(self):
        for task in TRI_TASKS:
            result=synthesize_successor(TernaryVerifier(task),self.meta,task)
            self.assertIsNotNone(result["program"],task)
            certificate=reverify_successor(result["program"],
                                            TernaryVerifier(task),self.meta)
            self.assertEqual(certificate["status"],
                             "VERIFIED_TYPED_THREE_INPUT_ALGORITHM")

    def test_generated_programs_match_independent_exact_classical_composer(self):
        for task in TRI_TASKS:
            result=synthesize_successor(TernaryVerifier(task),self.meta,task)
            reference=independent_minimal_composition(self.methods,task)
            self.assertEqual(
                result["program"]["compiled_NAND"]["gate_count"],
                reference["least_total_NAND_gates"],task)
            self.assertEqual(reference["candidate_compositions_checked"],3072)

    def test_majority_three_outside_two_operator_grammar_holds(self):
        result=synthesize_successor(
            TernaryVerifier(UNREACHABLE),self.meta,UNREACHABLE)
        reference=independent_minimal_composition(self.methods,UNREACHABLE)
        self.assertIsNone(result["program"])
        self.assertEqual(result["status"],
                         "HOLD_UNREACHABLE_IN_TWO_PRIMITIVE_COMPOSITION")
        self.assertIsNone(reference["least_total_NAND_gates"])

    def test_malformed_composition_not_executable(self):
        bad={"first":6,"second":6,"shape":"FREE_PYTHON",
             "order":[0,1,2],"cost":8,"truth_mask":150}
        with self.assertRaises(HOLD):
            compose_circuit(bad)

    def test_duplicated_variable_or_fourth_wire_refused(self):
        for order in ([0,1,1],[0,1,3]):
            bad={"first":6,"second":6,"shape":"LEFT",
                 "order":order,"cost":8,"truth_mask":150}
            with self.assertRaises(HOLD):
                compose_circuit(bad)

    def test_prior_generated_cartridge_tamper_rejected_during_composition(self):
        bad_methods=deepcopy(self.methods)
        bad_methods[6]["gates"][0]=[1,1]
        target=next(row for row in catalog() if row["first"]==6 and
                    row["second"]==6 and row["shape"]=="LEFT")
        with self.assertRaises(Exception):
            compose_circuit(target,bad_methods)

    def test_generated_wrong_program_is_refuted_by_three_bit_oracle(self):
        other=TernaryVerifier("ANY3")
        with self.assertRaises(HOLD):
            reverify_successor(self.parity["program"],other,self.meta)

    def test_three_input_program_tamper_rejected_even_if_rehashed(self):
        bad=deepcopy(self.parity["program"])
        bad["compiled_NAND"]["gates"]=[]
        raw={k:v for k,v in bad.items() if k!="sha256"}
        bad["sha256"]=bootstrap._hash(raw)
        with self.assertRaises(HOLD):
            reverify_successor(bad,TernaryVerifier("ODD_PARITY3"),self.meta)

    def test_three_input_program_does_not_need_4bit_code_hardcoded(self):
        code=inspect.getsource(bootstrap)
        self.assertNotIn("def parity3",code)
        self.assertNotIn("def xor3",code)
        self.assertNotIn("def direct_xor4",code)

    def test_third_generation_executable_four_input_algorithm_verified(self):
        receipt=reverify_four_input(
            self.quad,QuaternaryVerifier(),self.parity["program"])
        self.assertEqual(receipt["status"],
                         "VERIFIED_TYPED_FOUR_INPUT_ALGORITHM")
        self.assertEqual(self.quad["gate_count"],12)
        self.assertEqual(self.quad["parent_three_input_sha256"],
                         self.parity["program"]["sha256"])
        self.assertTrue(self.quad["full_four_input_domain_exhausted"])

    def test_full_four_bit_truth_table_refutes_all_errors(self):
        checker=QuaternaryVerifier()
        self.assertIsNone(checker.check(self.quad["gates"],
                                        self.quad["output"]))
        for x in product((False,True),repeat=4):
            self.assertEqual(interpret(self.quad["gates"],
                                       self.quad["output"],x),
                             (x[0]^x[1]^x[2]^x[3]))

    def test_four_bit_parent_tamper_does_not_verify(self):
        forged=deepcopy(self.quad)
        forged["parent_three_input_sha256"]="0"*64
        raw={k:v for k,v in forged.items() if k!="sha256"}
        forged["sha256"]=bootstrap._hash(raw)
        with self.assertRaises(HOLD):
            reverify_four_input(
                forged,QuaternaryVerifier(),self.parity["program"])

    def test_four_bit_wrong_spec_refuted_without_editing_original(self):
        class WrongVerifier:
            def check(self,gates,out):
                return (False,False,False,False,True)
        with self.assertRaises(HOLD):
            reverify_four_input(self.quad,WrongVerifier(),
                                self.parity["program"])

    def test_fixed_flat_nand_budget_is_not_strong_composition_baseline(self):
        independent=flat_nand_search("ODD_PARITY3",limit=5)
        self.assertFalse(independent["within_budget"])
        self.assertEqual(independent["limit"],5)
        strong=independent_minimal_composition(self.methods,"ODD_PARITY3")
        self.assertEqual(strong["least_total_NAND_gates"],8)

    def test_committed_algorithms_were_actually_self_generated_and_replay(self):
        stored=json.loads((HERE/"generated"/"self_written_algorithms.json").read_text(
            encoding="utf-8"))
        report,recomputed=execute()
        self.assertEqual(stored,recomputed)
        self.assertEqual(stored["status"],"DRAFT_ONLY_HUMAN_REVIEW_REQUIRED")
        self.assertFalse(stored["autonomous_sandbox_escape"])
        self.assertFalse(stored["source_authentication_performed"])

    def test_saved_self_generated_methods_can_be_reverified_fresh(self):
        stored=json.loads((HERE/"generated"/"self_written_algorithms.json").read_text(
            encoding="utf-8"))
        meta=stored["generation_1_generated_search_cartridge"]
        self.assertEqual(len(_compressed_candidates(meta)),152)
        methods=stored["generation_2_derived_three_input_algorithms"]
        for task,program in methods.items():
            proof=reverify_successor(program,TernaryVerifier(task),meta)
            self.assertEqual(proof["status"],
                             "VERIFIED_TYPED_THREE_INPUT_ALGORITHM",task)
        final=stored["generation_3_reused_three_input_algorithm"]
        self.assertEqual(reverify_four_input(
            final,QuaternaryVerifier(),methods["ODD_PARITY3"])["status"],
            "VERIFIED_TYPED_FOUR_INPUT_ALGORITHM")

    def test_full_replay_generates_standalone_artifacts_not_code_edits(self):
        report,bundle=execute()
        self.assertEqual(report["experiment"],"MOTIF-LEGIT-010")
        self.assertEqual(report["old_synthesizer_generated_binary_primitive_count"],16)
        self.assertEqual(report["meta_search_representatives"],152)
        self.assertEqual(report["total_two_call_composition_templates"],3072)
        self.assertTrue(report["comparison"]["independent_exact_classical_composer_matched"])
        self.assertFalse(report["comparison"]["surpassed_optimized_classical_algorithm"])
        self.assertEqual(report["total_external_calls"],0)
        self.assertEqual(report["production_changes"],0)
        self.assertEqual(bundle["generation_3_reused_three_input_algorithm"],
                         self.quad)
        self.assertTrue(bundle["no_python_source_was_rewritten"])
        self.assertEqual(report,execute()[0])

    def test_real_prior_witness_bridge_read_only(self):
        report,_=execute()
        bridge=report["actual_existing_LEGIT007_witness_graph_use"]
        self.assertEqual(bridge["synthetic_graphs_total"],320)
        self.assertGreater(bridge["graphs_with_at_least_three_declared_origins"],0)
        self.assertFalse(bridge["source_assessment_changed"])
        self.assertFalse(bridge["origin_authentication_verified"])


if __name__=="__main__":
    unittest.main()
