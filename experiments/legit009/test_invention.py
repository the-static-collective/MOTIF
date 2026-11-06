"""LEGIT-009: non-handwritten Boolean programs, CEGIS counterexamples,
independent exact truth verifier, minimality, real MOTIF-007 source bridge.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import itertools
from pathlib import Path
from random import Random
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"legit007"))

import synthesizer
from synthesizer import HOLD,cegis,load_verified,synthesize_samples,eval_pair,checksum
from independent_oracle import (IndependentVerifier,MaskVerifier,TASKS,
                                canonical_sop_xor,direct_builtin_disagreement)
from cartridge import conflicting_independent_origins,parity_fold
from simulator import trial,demonstration,N
from provenance import posterior
from importlib.util import spec_from_file_location,module_from_spec
_sp=spec_from_file_location("legit009_local_benchmark",HERE/"benchmark.py")
_benchmark=module_from_spec(_sp)
_sp.loader.exec_module(_benchmark)
run=_benchmark.run


class InventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programs={name:cegis(IndependentVerifier(name),name)
                      for name in TASKS}
        cls.xor=cls.programs["DISAGREEMENT"]["cartridge"]

    def test_learner_no_explicit_target_function_import(self):
        src=inspect.getsource(synthesizer)
        self.assertNotIn("from independent_oracle import",src)
        self.assertNotIn("import independent_oracle",src)
        self.assertNotIn('task_id=="DISAGREEMENT"',src)
        self.assertNotIn("def native_xor",src)

    def test_cegis_constructs_four_task_programs_from_nand_only(self):
        for name,result in self.programs.items():
            cartridge=result["cartridge"]
            self.assertEqual(cartridge["instruction_set"],
                             "NAND_DAG_WITH_INPUTS_A_B")
            self.assertEqual(cartridge["status"],
                             "PROVED_FINITE_DOMAIN_PROPOSAL_ONLY")
            self.assertGreater(cartridge["cegis_rounds"],1,name)
            self.assertGreater(cartridge["counterexample_count"],0,name)
            self.assertLessEqual(cartridge["gate_count"],5)
            self.assertEqual(len(cartridge["gates"]),cartridge["gate_count"])
            self.assertEqual(load_verified(cartridge,IndependentVerifier(name))
                             ["status"],"FINITE_TRUTH_TABLE_VERIFIED")

    def test_xor_not_hardcoded_and_four_nand_gates(self):
        self.assertEqual(self.xor["gate_count"],4)
        self.assertEqual(self.xor["truth_mask"],0b0110)
        self.assertNotEqual(self.xor["gates"],canonical_sop_xor())

    def test_all_four_targets_have_independent_minimality_witness(self):
        for name,result in self.programs.items():
            c=result["cartridge"]
            cert=IndependentVerifier(name).proof(c["gates"],c["output"])
            self.assertFalse(cert["shorter_NAND_DAG_found"])
            self.assertEqual(cert["minimum_NAND_gates_in_declared_grammar"],
                             c["gate_count"])
            self.assertEqual(cert["verified_full_input_domain_size"],4)

    def test_independent_oracle_checks_actual_16_boolean_functions(self):
        for truth_mask in range(16):
            oracle=MaskVerifier(truth_mask)
            synthesis=cegis(oracle,"Mask"+str(truth_mask))
            cartridge=synthesis["cartridge"]
            self.assertEqual(cartridge["truth_mask"],truth_mask)
            self.assertIsNone(oracle.check(cartridge["gates"],cartridge["output"]))
            certificate=oracle.proof(cartridge["gates"],cartridge["output"])
            self.assertEqual(certificate["minimum_NAND_gates_in_declared_grammar"],
                             cartridge["gate_count"])

    def test_new_program_matches_python_builtin_inequality(self):
        for a,b in itertools.product((False,True),repeat=2):
            self.assertIs(eval_pair(self.xor["gates"],a,b,self.xor["output"]),
                          direct_builtin_disagreement(a,b))

    def test_reject_garbled_unnormalized_nand_wiring(self):
        for bad in ([[0,2]],[[2,2]],[[1,0]],[["x",0]],[[-1,0]]):
            with self.assertRaises(HOLD):
                synthesizer.mask(bad)

    def test_reject_oversized_or_cyclic_circuit(self):
        with self.assertRaises(HOLD):
            synthesizer.mask([[0,1]]*6)
        with self.assertRaises(HOLD):
            synthesizer.mask([[2,2]])

    def test_counterexample_is_a_real_failure(self):
        for result in self.programs.values():
            for round in result["transcript"]:
                claim=round["observed_counterexample"]
                if claim is None:
                    continue
                proposal=round["candidate"]
                actual=eval_pair(proposal["gates"],claim["a"],claim["b"],
                                 proposal["output"])
                self.assertIs(actual,claim["proposed"])
                self.assertIsNot(actual,claim["expected"])

    def test_a_lying_verifier_must_hold(self):
        oracle=IndependentVerifier("DISAGREEMENT")
        class BadOracle:
            def label_initial(self,a,b):
                return oracle.truth(a,b)
            def check(self,gates,output):
                # Return fake counterexample identical to candidate output.
                return (False,False,eval_pair(gates,False,False,output))
        with self.assertRaises(HOLD):
            cegis(BadOracle(),"bad_task")

    def test_tamper_with_generated_gate_fails_checksum(self):
        bad=deepcopy(self.xor)
        bad["gates"][0]=[0,0]
        with self.assertRaises(HOLD):
            load_verified(bad,IndependentVerifier("DISAGREEMENT"))

    def test_rehashed_but_false_program_fails_independent_checker(self):
        bad=deepcopy(self.xor)
        bad["gates"]=[]
        bad["gate_count"]=0
        bad["output"]=0
        bad["truth_mask"]=synthesizer.mask([],0)
        raw={k:v for k,v in bad.items() if k!="sha256"}
        bad["sha256"]=checksum(raw)
        with self.assertRaises(HOLD):
            load_verified(bad,IndependentVerifier("DISAGREEMENT"))

    def test_reuse_another_task_cartridge_rejected(self):
        other=IndependentVerifier("AGREEMENT")
        with self.assertRaises(HOLD):
            load_verified(self.xor,other)

    def test_unsupported_hidden_world_command_rejected(self):
        bad=deepcopy(self.xor)
        bad["world_actuated"]=True
        with self.assertRaises(HOLD):
            load_verified(bad,IndependentVerifier("DISAGREEMENT"))

    def test_true_source_provenance_not_claimed(self):
        packet=demonstration()
        response=conflicting_independent_origins(packet,self.xor)
        self.assertFalse(response["source_identity_authenticated"])
        self.assertFalse(response["truth_about_world_inferred_from_conflict"])
        self.assertEqual(response["actions_issued"],0)
        self.assertTrue(response["legacy_inference_unmodified"])

    def test_historical_witness_case_has_correct_disagreements(self):
        packet=demonstration()
        response=conflicting_independent_origins(packet,self.xor)
        self.assertEqual(response["distinct_declared_origins"],3)
        self.assertEqual(response["pairs_compared"],3)
        self.assertEqual(response["opposing_source_pairs"],[
            ["campaign_root","review_a"],["campaign_root","review_b"]])

    def test_previous_bayesian_posterior_unchanged_by_generated_cartridge(self):
        packet=demonstration()
        old=posterior(packet)["posterior"]
        conflicting_independent_origins(packet,self.xor)
        new=posterior(packet)["posterior"]
        self.assertEqual(old,new)

    def test_actual_source_graph_crosswire_on_320_heldout_worlds(self):
        for i in range(N):
            packet=trial(i).public
            original=[r for r in packet["nodes"] if r["kind"]=="ROOT"]
            expected=sum(a["claim"]!=b["claim"]
                         for j,a in enumerate(original) for b in original[j+1:])
            observed=conflicting_independent_origins(packet,self.xor)
            self.assertEqual(len(observed["opposing_source_pairs"]),expected)
            self.assertEqual(observed["distinct_declared_origins"],len(original))

    def test_parity_fold_zero_length(self):
        r=parity_fold([],self.xor)
        self.assertFalse(r["odd_parity"])
        self.assertEqual(r["generated_NAND_operations"],0)

    def test_parity_fold_every_short_binary_sequence(self):
        for n in range(10):
            for bits in itertools.product((False,True),repeat=n):
                result=parity_fold(bits,self.xor)
                self.assertEqual(result["odd_parity"],bool(sum(bits)%2))
                self.assertEqual(result["generated_NAND_operations"],4*n)
                self.assertEqual(result["canonical_NAND_SOP_operations"],5*n)

    def test_parity_fold_one_thousand_random_long_inputs(self):
        rng=Random(1012026)
        for n in (10,25,50,100,333,1000):
            bits=[bool(rng.getrandbits(1)) for _ in range(n)]
            result=parity_fold(bits,self.xor)
            self.assertEqual(result["odd_parity"],bool(sum(bits)%2))

    def test_shortcuts_compared_on_same_nand_instruction_model(self):
        self.assertEqual(len(canonical_sop_xor()),5)
        self.assertEqual(self.xor["gate_count"],4)
        for a,b in itertools.product((False,True),repeat=2):
            expected=IndependentVerifier("DISAGREEMENT").truth(a,b)
            self.assertEqual(eval_pair(canonical_sop_xor(),a,b,6),expected)
            self.assertEqual(eval_pair(self.xor["gates"],a,b,self.xor["output"]),expected)

    def test_single_native_xor_is_allowed_to_be_stronger(self):
        # We explicitly do not claim to beat an optimized classical machine
        # with a direct XOR opcode.
        self.assertEqual(len(self.xor["gates"]),4)
        self.assertEqual(sum(a!=b for a,b in
                             itertools.product((False,True),repeat=2)),2)

    def test_synthesis_samples_reject_malformed_examples(self):
        with self.assertRaises(HOLD):
            synthesize_samples({})
        with self.assertRaises(HOLD):
            synthesize_samples({(False,False):"false"})

    def test_generated_artifact_is_untrusted_by_default(self):
        self.assertFalse(self.xor["real_world_authority"])
        verifier=load_verified(self.xor,IndependentVerifier("DISAGREEMENT"))
        self.assertFalse(verifier["source_identity_authenticated"])
        self.assertFalse(verifier["real_world_authority"])

    def test_benchmark_reproducible_and_classical_optimum_tied(self):
        a=run()
        self.assertEqual(a,run())
        self.assertFalse(a["independent_blinded_research_challenge"])
        self.assertFalse(a["proof_of_new_mathematics"])
        self.assertFalse(a["source_authentication_verified"])
        self.assertTrue(a["comparison_same_NAND_instruction_set"]
                        ["exact_classical_superoptimizer_tie"])
        self.assertEqual(a["finite_to_recursive_induction"]
                         ["exhaustive_sequences_through_length_8"],511)
        self.assertEqual(a["actually_executed_MOTIF007_crosswire"]
                         ["actual_MOTIF007_graphs_reexamined"],320)


if __name__=="__main__":
    unittest.main()
