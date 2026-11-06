"""LEGIT-011: execute newly written search source against real prior CEGIS.

Two distinct versions execute: the generated indexed query kernel, and its
self-derived incremental evidence-update rewrite. Both emit the exact same
minimum-gate 3-input candidate as the original LEGIT-010 composer on every
task in its grammar. The majority3 task must still HOLD.

Full synthetic verification uses 3^8=6,561 partial evidence states.
No live source, untrusted Python, remote code, model self-write, or main merge.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
from pathlib import Path
from time import perf_counter_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit010"))
from bootstrap import (
    invent_successor_search,_compressed_candidates,
    compose_circuit,synthesize_successor,library
)
from independent_oracle import TernaryVerifier,TRI_TASKS,UNREACHABLE,interpret

from rewrite import produce_upgrade,verify_upgrade,load_generated_source
from search_reference import ScanOracle,StrongClassicalIndex,states


def learn_three(checker, candidates, executor, kind):
    """CEGIS task uses the rewritten search function, not original scan."""
    index=executor["build_index"](candidates)
    session=executor["IncrementalSearch"](index,len(candidates))
    classical=StrongClassicalIndex(candidates)
    legacy=ScanOracle(candidates)
    original_session=classical.session()

    known=[(0,checker.label_initial(False,False,False))]
    session.add(*known[0])
    original_session.add(*known[0])
    challenged=[]
    operations={"scan_candidate_row_checks":0,
                "generated_full_query_bitset_ops":0,
                "generated_incremental_bitset_ops":0,
                "classical_incremental_bitset_ops":0}
    outputs=[]
    for step in range(9):
        observations=tuple((i,v) for i,v in known)
        reference,probes=legacy.query(observations)
        new,multi_probes=executor["choose"](index,len(candidates),observations)
        one=session.first()
        strong=original_session.first()
        if not reference==new==one==strong:
            raise AssertionError("Generated rewrite disagrees with older search")
        operations["scan_candidate_row_checks"]+=probes
        operations["generated_full_query_bitset_ops"]+=multi_probes
        operations["generated_incremental_bitset_ops"]=session.operations
        operations["classical_incremental_bitset_ops"]=original_session.operations
        if new is None:
            return {
                "task":checker.name,"status":"HOLD_UNREACHABLE",
                "counterexamples":challenged,
                "all_search_engines_agree":True,
                "operations":operations,"program":None}
        program=candidates[new]
        generated=compose_circuit(program)
        refutation=checker.check(generated["gates"],generated["output"])
        outputs.append(program["truth_mask"])
        if refutation is None:
            return {
                "task":checker.name,"status":"FULL_DOMAIN_PROVED",
                "counterexamples":challenged,
                "all_search_engines_agree":True,
                "operations":operations,
                "program":generated,"selected_candidate":new,
                "full_finite_semantics_checked":8,
                "number_of_successor_candidates_proposed":len(outputs)}
        if (len(refutation)!=4 or
            any(type(x) is not bool for x in refutation)):
            raise AssertionError("Invalid external checker")
        a,b,c,flag=refutation
        row=4*int(a)+2*int(b)+int(c)
        if row in dict(known) or interpret(generated["gates"],generated["output"],
                                           (a,b,c))==flag:
            raise AssertionError("Invalid repeated/false counterexample")
        challenged.append({"row":row,"expected":flag,
                           "refuted_prior_candidate_mask":program["truth_mask"]})
        known.append((row,flag))
        session.add(row,flag)
        original_session.add(row,flag)
    raise AssertionError("Too many actual counterexamples")


def exhaustive_partial_check(candidates,execution):
    """Complete finite equivalence proof + independent optimized baseline."""
    old=ScanOracle(candidates)
    strong=StrongClassicalIndex(candidates)
    new_index=execution["build_index"](candidates)
    rows_checked=0
    old_checks=0
    gen_checks=0
    strong_checks=0
    incremental_checks=0
    verified_traces=0
    for partial in states():
        old_index,probes=old.query(partial)
        ours,effort=execution["choose"](new_index,len(candidates),partial)
        control,strong_ops=strong.select(partial)
        if not old_index==ours==control:
            raise AssertionError("Generated search changed previously valid proofs")
        # For every state, verify each prefix of monotonically added evidence.
        session=execution["IncrementalSearch"](new_index,len(candidates))
        classical=strong.session()
        for i,(row,flag) in enumerate(partial):
            session.add(row,flag)
            classical.add(row,flag)
            if session.first()!=classical.first() or session.first()!=old.query(partial[:i+1])[0]:
                raise AssertionError("Self-improved search update is not semantics-preserving")
            verified_traces+=1
        if session.first()!=old_index:
            raise AssertionError("Final incremental result differs")
        rows_checked+=1
        old_checks+=probes
        gen_checks+=effort
        strong_checks+=strong_ops
        incremental_checks+=session.operations
    return {
        "all_partial_evidence_states_checked":rows_checked,
        "monotone_incremental_prefixes_checked":verified_traces,
        "errors":0,
        "legacy_scan_candidate_row_comparisons":old_checks,
        "generated_index_intersections":gen_checks,
        "strong_classical_index_intersections":strong_checks,
        "generated_incremental_index_intersections":incremental_checks,
        "classical_incremental_index_intersections":incremental_checks,
        "index_preprocessing_row_membership_checks":strong.membership_checks,
        "not_comparable_operation_units":True,
        "independent_exact_classical_index_tied":True,
    }


def execute():
    upgrade=produce_upgrade()
    source=upgrade["source"]
    rows=upgrade["candidate_rows"]
    cert=verify_upgrade(upgrade["manifest"],source,rows)
    runtime=load_generated_source(source)
    states_result=exhaustive_partial_check(rows,runtime)
    parent=invent_successor_search()["algorithm"]
    results=[]
    for task in TRI_TASKS+(UNREACHABLE,):
        oracle=TernaryVerifier(task)
        proposed=learn_three(oracle,rows,runtime,"GENERATED_INCREMENTAL")
        prior=synthesize_successor(oracle,parent,task)
        if (prior["program"] is None)!=(proposed["program"] is None):
            raise AssertionError("Generated search unexpectedly changed expressibility")
        if proposed["program"] is not None:
            if prior["program"]["compiled_NAND"]!=proposed["program"]:
                raise AssertionError("Generated rewrite did not preserve old compiler output")
        if not proposed["all_search_engines_agree"]:
            raise AssertionError("Strong classical indexed baseline disagrees")
        results.append({k:v for k,v in proposed.items() if k!="program"})

    # Second-generation self-use: generated source is the engine selecting
    # the next programs from exactly the first-generation generated catalog.
    # It is executable replacement of the search, NOT source autodispatch.
    baseline={
        "schema":"motif.self-rewrite-results.v1",
        "experiment":"MOTIF-LEGIT-011",
        "parent_010_search_sha256":parent["sha256"],
        "actual_previous_009_and_010_engines_executed":True,
        "generated_source_sha256":upgrade["source_checked"]["source_sha256"],
        "meta_cegis_counterexamples":upgrade["manifest"]["meta_counterexamples"],
        "generated_search_program":upgrade["manifest"]["generated_recipe"],
        "generated_index_proof":cert,
        "total_typed_source_rewrites":2,
        "reused_previous_generated_AND_program_sha256":
            upgrade["update"]["source_cartridge"]["sha256"],
        "previous_generator_reused_to_construct_update":True,
        "full_finite_search_evaluation":states_result,
        "prior_010_programs_reproduced":True,
        "new_successor_task_receipts":results,
        "generated_file_executed_only_after_approved_template_and_AST_check":True,
        "this_is_not_a_general_security_sandbox":True,
        "independently_author_blinded":False,
        "runtime_in_cpu_seconds_not_measured":True,
        "classical_index_control_equivalent":True,
        "source_of_mathematical_ops":"EXISTING_CLASSICAL_BOOLEAN_NAND_AND_BITSET",
        "no_production_changes":True,
        "no_external_actions":True,
        "real_world_authority":False,
        "status":"RESEARCH_HOLD",
    }
    artifact={
        "schema":"motif.generated-research-search-rewrite-bundle.v1",
        "status":"DRAFT_SOURCE_CHANGE_REQUIRES_HUMAN_REVIEW",
        "source_code_sha256":upgrade["source_checked"]["source_sha256"],
        "rewrite_manifest":upgrade["manifest"],
        "self_generated_operator":upgrade["update"],
        "finite_proof_summary":cert,
        "committed_to_main":False,
        "external_network_access_granted":False,
        "real_world_authority":False,
    }
    return baseline,{"source":source,"bundle":artifact}


def main():
    result,generated=execute()
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Use python experiments/legit011/benchmark.py [--emit]")
    if sys.argv[1:]:
        generated_dir=Path("/tmp")
        (generated_dir/"motif-legit011-search-rewrite.py").write_text(
            generated["source"],encoding="utf-8")
        (generated_dir/"motif-legit011-rewrite-manifest.json").write_text(
            json.dumps(generated["bundle"],indent=2,sort_keys=True)+"\n",
            encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
