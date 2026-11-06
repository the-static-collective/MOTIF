"""LEGIT-010: real self-composition run, not a simulated claim of autonomy.

Replay the original LEGIT-009 CEGIS generator to obtain executable
primitives. A second, counterexample-driven generated search policy
reduces equivalent next-generation programs. The *new* search policy is
used to write and verify 3-input programs, one of which is recursively
reused in a third-generation 4-input program.

The independent exact classical composition search must match all
accepted minimum costs, including out-of-grammar refusal for majority.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path
from collections import defaultdict
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.append(str(HERE.parent/"legit007"))

from bootstrap import (
    library,catalog,invent_successor_search,_compressed_candidates,
    synthesize_successor,reverify_successor,build_four_input,
    reverify_four_input
)
from independent_oracle import (
    TRI_TASKS,UNREACHABLE,TernaryVerifier,QuaternaryVerifier,
    independent_minimal_composition,flat_nand_search,interpret
)
from simulator import trial,N
from provenance import validate,posterior


def execute():
    primitives=library()
    meta=invent_successor_search()
    meta_program=meta["algorithm"]
    if meta_program["distinct_truth_functions"] != len(_compressed_candidates(meta_program)):
        raise AssertionError("Generated search program is not equivalent-class complete")
    results=[]
    generated={}
    for task in TRI_TASKS:
        checker=TernaryVerifier(task)
        outcome=synthesize_successor(checker,meta_program,task)
        if outcome["program"] is None:
            raise AssertionError("Two-primitive grammar unexpectedly held " + task)
        candidate=outcome["program"]
        verified=reverify_successor(candidate,checker,meta_program)
        strong=independent_minimal_composition(primitives,task)
        if strong["least_total_NAND_gates"]!=verified["gate_count"]:
            raise AssertionError("A strong exact classical composer beats generated method")
        generated[task]=candidate
        results.append({
            "task":task,
            "generated_gate_count":verified["gate_count"],
            "independently_enumerated_minimum_NAND_gate_count":
                strong["least_total_NAND_gates"],
            "correct_on_all_8_inputs":True,
            "actual_three_bit_counterexamples":len(outcome["counterexamples"]),
            "original_LEGIT009_cartridge_ids":[
                candidate["program_tree"]["first"],
                candidate["program_tree"]["second"]],
            "cartridge_sha256":candidate["sha256"],
            "strong_classical_composer_tied":True,
        })

    # A meaningful negative example: there are more three-bit Boolean
    # functions than this two-binary-call grammar can express.
    cannot=synthesize_successor(
        TernaryVerifier(UNREACHABLE),meta_program,UNREACHABLE)
    independently=independent_minimal_composition(primitives,UNREACHABLE)
    if cannot["program"] is not None or independently["least_total_NAND_gates"] is not None:
        raise AssertionError("A supposedly unreachable function was found")
    expected_failure={
        "task":UNREACHABLE,"status":cannot["status"],
        "counterexamples_before_hold":len(cannot["counterexamples"]),
        "independent_composition_found":False,
        "representability_limit_is_about_two_calls_not_logic_itself":True,
    }

    # The *next* layer reuses a method WRITTEN BY THE SECOND LAYER.
    successor_three=generated["ODD_PARITY3"]
    successor_four=build_four_input(successor_three,meta_program)
    four_receipt=reverify_four_input(
        successor_four,QuaternaryVerifier(),successor_three)
    if four_receipt["status"]!="VERIFIED_TYPED_FOUR_INPUT_ALGORITHM":
        raise AssertionError("Third-generation program failed full proof")

    # Real source graph crosswire: read existing LEGIT-007 packet structure.
    # Only claim a Boolean diagnostic of three declared origins, never
    # a diagnosis of actual truth, provenance or posterior changes.
    inspected=0
    disagreements=0
    examples=[]
    for index in range(N):
        packet=trial(index).public
        origins=validate(packet)["origin_signature"]
        if len(origins)<3: continue
        first_three=sorted(origins)[:3]
        values=tuple(origins[k][0] for k in first_three)
        source_old=posterior(packet)["posterior"]
        compiled=successor_three["compiled_NAND"]
        actual=interpret(compiled["gates"],compiled["output"],values)
        expected=bool(sum(values)%2)
        if actual!=expected:
            raise AssertionError("Generated graph triad method disagrees with reference")
        if posterior(packet)["posterior"]!=source_old:
            raise AssertionError("Generated code modified legacy witness posterior")
        inspected+=1
        disagreements+=int(actual)
        if index in (1,2,17,42):
            examples.append({"index":index,"declared_three_sources":first_three,
                             "computed_odd_number_true":actual,
                             "source_lineage_not_authenticated":True})
    flat=flat_nand_search("ODD_PARITY3",limit=5)
    if flat["within_budget"]:
        raise AssertionError("Flat five-NAND reference unexpectedly solved parity3")

    generated_bundle={
        "schema":"motif.self-bootstrapped-research-artifacts.v1",
        "status":"DRAFT_ONLY_HUMAN_REVIEW_REQUIRED",
        "generation_0_existing_engine":"LEGIT009_CEGIS_UNMODIFIED",
        "generation_1_generated_search_cartridge":meta_program,
        "generation_2_derived_three_input_algorithms":generated,
        "generation_3_reused_three_input_algorithm":successor_four,
        "no_python_source_was_rewritten":True,
        "no_unreviewed_generated_code_executed":True,
        "only_typed_boolean_interpreter_was_used":True,
        "source_authentication_performed":False,
        "autonomous_sandbox_escape":False,
        "real_world_authority":False,
    }
    return {
        "experiment":"MOTIF-LEGIT-010",
        "actual_old_synthesizer_imported_and_executed":True,
        "old_synthesizer_generated_binary_primitive_count":len(primitives),
        "total_two_call_composition_templates":len(catalog()),
        "meta_cegis_transcript":meta["counterexample_transcript"],
        "generated_meta_search_cartridge":meta_program,
        "meta_search_representatives":len(_compressed_candidates(meta_program)),
        "meta_search_pruning_scope":
            "ALL_TEMPLATES_EXHAUSTIVELY_CHECKED_FOR_8_ROW_EQUIVALENCE",
        "solver_3input_results":results,
        "unreachable_strict_hold":expected_failure,
        "fixed_flat_five_nand_control":flat,
        "generated_4input_algorithm":{
            "gate_count":successor_four["gate_count"],
            "status":four_receipt["status"],
            "cartridge_sha256":successor_four["sha256"],
            "all_sixteen_input_rows_verified":True,
            "two_previously_generated_subprograms_composed":True,
            "native_classical_xor_is_available_and_more_efficient":True},
        "actual_existing_LEGIT007_witness_graph_use":{
            "synthetic_graphs_total":N,
            "graphs_with_at_least_three_declared_origins":inspected,
            "graphs_with_odd_true_in_first_three_origins":disagreements,
            "source_assessment_changed":False,
            "origin_authentication_verified":False,
            "sample_receipts":examples},
        "comparison":{
            "independent_exact_classical_composer_matched":True,
            "algorithm_creation_limited_to_typed_DAG_and_composition":True,
            "surpassed_optimized_classical_algorithm":False,
            "computed_walltime_superiority_claim":False,
            "meta_verifier_independent_implementation_not_independent_author":True},
        "total_external_calls":0,
        "production_changes":0,
        "status":"RESEARCH_HOLD",
    },generated_bundle


def main():
    report,bundle=execute()
    if len(sys.argv)>2 or (len(sys.argv)==2 and sys.argv[1]!="--emit"):
        raise SystemExit("Usage: python benchmark.py [--emit]")
    if len(sys.argv)==2:
        path=Path("/tmp/motif-legit010-self-generated-algorithms.json")
        path.write_text(json.dumps(bundle,indent=2,sort_keys=True)+"\n",
                        encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
