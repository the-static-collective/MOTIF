"""LEGIT-009: CEGIS program invention, exhaustive proof, and real code crosswire.

No pretrained program solutions in learner. Independent verifier challenges
proposed DAGs; the candidate grows a counterexample set until the FULL
two-input domain is proved. Synthesized programs become read-only cartridges
and are executed against existing MOTIF-007 provenance graph outputs.

Benchmark includes a strong independent exhaustive NAND superoptimizer.
It is expected to tie the synthesized program's optimal gate count.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import itertools
import json
from pathlib import Path
from random import Random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit007"))
from simulator import trial,N,demonstration
from provenance import validate
from independent_oracle import (IndependentVerifier, TASKS,
                                canonical_sop_xor, direct_builtin_disagreement)
from synthesizer import cegis,eval_pair,load_verified
from cartridge import conflicting_independent_origins,parity_fold

def _exercise_fold(learned):
    rng=Random(2026110609)
    comparison=[]
    for size in range(0,21):
        for i in range(28):
            bits=[bool(rng.getrandbits(1)) for _ in range(size)]
            output=parity_fold(bits,learned)
            expected=(sum(bits)%2)==1
            if output["odd_parity"]!=expected:
                raise AssertionError("Unseen parity fold incorrect")
            comparison.append((size,output["generated_NAND_operations"],
                               output["canonical_NAND_SOP_operations"]))
    # All binary sequences through n=8: this is a finite exhaustive test
    # beyond the local 2-bit instruction proof.
    finite=0
    for size in range(9):
        for bits in itertools.product((False,True),repeat=size):
            result=parity_fold(bits,learned)
            if result["odd_parity"] != (sum(bits)%2==1):
                raise AssertionError("Exhaustive finite fold mismatch")
            finite+=1
    return {"heldout_random_lists":len(comparison),
            "exhaustive_sequences_through_length_8":finite,
            "total_generated_NAND_operations":sum(x[1] for x in comparison),
            "total_canonical_NAND_SOP_operations":sum(x[2] for x in comparison),
            "native_XOR_reference_is_cheaper_when_available":True,
            "mathematical_all_lengths_argument":"Base empty parity false; for every Boolean prior state and next bit, the independent verifier proves generated XOR=prior XOR bit. Ordinary induction then proves finite folds.",
            "new_logic_discovered":False}

def _exercise_origin_conflict(learned):
    checked=0
    conflicting=0
    for i in range(N):
        packet=trial(i).public
        graph=validate(packet)
        names=sorted(graph["origin_signature"])
        result=conflicting_independent_origins(packet,learned)
        expected_pairs=[[a,b] for j,a in enumerate(names) for b in names[j+1:]
                        if (graph["origin_signature"][a][0] !=
                            graph["origin_signature"][b][0])]
        if result["opposing_source_pairs"]!=expected_pairs:
            raise AssertionError("Generated source inconsistency diagnostic failed")
        if result["pairs_compared"]!=len(names)*(len(names)-1)//2:
            raise AssertionError("Count of inspected roots differs")
        if result["source_identity_authenticated"]:
            raise AssertionError("Generated circuit fabricated source trust")
        checked+=1
        conflicting+=int(bool(expected_pairs))
    return {
        "actual_MOTIF007_graphs_reexamined":checked,
        "source_graphs_with_opposing_roots":conflicting,
        "direct_boolean_inequality_reference_matches":True,
        "previous_posterior_modified":False,
        "independence_assertions_authenticated":False}

def run():
    successes=[]
    learned={}
    for task in TASKS:
        verifier=IndependentVerifier(task)
        result=cegis(verifier,task)
        cartridge=result["cartridge"]
        certificate=load_verified(cartridge,verifier)
        minimum=verifier.proof(cartridge["gates"],cartridge["output"])
        if certificate["gate_count"]!=minimum["minimum_NAND_gates_in_declared_grammar"]:
            raise AssertionError("Independent superoptimizer found a shorter program")
        successes.append({
            "task":task,
            "gates":cartridge["gates"],
            "output":cartridge["output"],
            "truth_mask":cartridge["truth_mask"],
            "gate_count":cartridge["gate_count"],
            "counterexample_rounds":result["transcript"],
            "counterexamples_rejected":cartridge["counterexample_count"],
            "independent_minimality_certificate":minimum,
            "cartridge_sha256":cartridge["sha256"],
            "real_world_authority":False})
        learned[task]=cartridge
    xor=learned["DISAGREEMENT"]
    baseline=canonical_sop_xor()
    checker=IndependentVerifier("DISAGREEMENT")
    if checker.check(baseline,len(baseline)+1) is not None:
        raise AssertionError("Canonical reference has wrong mathematical meaning")
    if xor["gate_count"]>=len(baseline):
        raise AssertionError("Synthesized program did not shorten canonical circuit")
    example=conflicting_independent_origins(demonstration(),xor)
    return {
        "experiment":"MOTIF-LEGIT-009",
        "method":"CEGIS_OVER_TYPED_NAND_DAG_WITH_INDEPENDENT_FINITE_VERIFIER",
        "task_authorship":"ASSISTANT_CHOSEN_BOOLEAN_SPECIFICATIONS",
        "teacher_provided_explicit_solution_circuits":False,
        "independent_blinded_research_challenge":False,
        "candidate_instruction_grammar":"two wire inputs, NAND, bounded DAG, maximum 5 gates",
        "available_target_functions":list(TASKS),
        "synthesis_results":successes,
        "comparison_same_NAND_instruction_set":{
            "canonical_sum_of_products_XOR_gates":len(baseline),
            "synthesized_NAND_XOR_gates":xor["gate_count"],
            "independent_exact_NAND_optimum_gates":
                checker.proof(xor["gates"],xor["output"])["minimum_NAND_gates_in_declared_grammar"],
            "exact_classical_superoptimizer_tie":True,
            "native_XOR_would_be_one_primitive_if_allowed":True},
        "finite_to_recursive_induction":_exercise_fold(xor),
        "actually_executed_MOTIF007_crosswire":_exercise_origin_conflict(xor),
        "demonstration":{
            "upstream_origins_declared":example["distinct_declared_origins"],
            "opposing_source_pairs":example["opposing_source_pairs"],
            "inference_unmodified":example["legacy_inference_unmodified"]},
        "scope":"SYNTHETIC_RESEARCH_ONLY",
        "generated_programs_evaluated_as_typed_data_not_eval":True,
        "source_authentication_verified":False,
        "proof_of_new_mathematics":False,
        "all_operations_sandboxed":True,
        "status":"RESEARCH_HOLD",
    }

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
