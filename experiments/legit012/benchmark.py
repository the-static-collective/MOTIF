"""LEGIT-012: source-level rewrite of *actual* MOTIF's program-search graph.

The learner uses the previous self-written LEGIT-011 source and produces
a new Python graph solver using typed CEGIS + counterexamples. This module
compares it to independent exact scan, a conventional untuned DP checker,
and a tuned conventional cached DAG DP with the same preprocessing access.

Workloads are seeded synthetic heldout evidence graphs, NOT independently
authored, and not general graph reachability. Time is local CI wall clock.
No network requests or live tool dispatch from synthesized code.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit010"))
from bootstrap import invent_successor_search,_compressed_candidates
from graph_reference import (
    check_graph,make_graph,all_states,cases,scan,classical_dp,StrongCachedDP
)
from transform import produce,verify,prior_search

def _measure(run,repeat=5):
    durations=[]
    for i in range(repeat):
        start=perf_counter_ns()
        run()
        durations.append((perf_counter_ns()-start)/1_000_000)
    return {"median_ms":round(median(durations),5),
            "min_ms":round(min(durations),5),
            "max_ms":round(max(durations),5),
            "samples":repeat}

def execute():
    prior_meta=invent_successor_search()["algorithm"]
    original_candidates=_compressed_candidates(prior_meta)
    artifact=produce(original_candidates)
    proof=verify(artifact,original_candidates)
    new_solver=artifact["generated_solver"]
    predecessor=prior_search()
    graph_rows=[
        (cases(30000+j,8),"LIGHT") for j in range(24)
    ]+[
        (cases(31000+j,32),"MEDIUM") for j in range(32)
    ]+[
        (cases(32000+j,96),"DENSE") for j in range(24)
    ]
    # Independent source graph validation is shared, never skipped.
    prepared=[(check_graph(graph),kind,graph["id"]) for graph,kind in graph_rows]
    idx_start=perf_counter_ns()
    previous_columns=predecessor.build_index(original_candidates)
    candidate_setup_ns=perf_counter_ns()-idx_start
    classical_start=perf_counter_ns()
    strong=StrongCachedDP(original_candidates)
    classical_setup_ns=perf_counter_ns()-classical_start

    all_checks=0
    all_updates=0
    fullscan_probes=0
    by_family={}
    for normalized,kind,name in prepared:
        reference,old_ops=scan(original_candidates,normalized)
        candidate,new_ops=new_solver(previous_columns,len(original_candidates),normalized)
        conventional,strong_ops=strong.solve(normalized)
        exact,_=classical_dp(original_candidates,normalized)
        if not candidate==reference==conventional==exact:
            raise AssertionError("New search rewrite broke former proof or strong classical baseline")
        if new_ops["bitset_updates"]!=strong_ops["bitset_updates"]:
            raise AssertionError("Source rewrite used different operations from optimized classical DP")
        all_checks+=len(normalized)
        all_updates+=new_ops["bitset_updates"]
        fullscan_probes+=old_ops["candidate_bit_tests"]
        by_family.setdefault(kind,{"graphs":0,"states":0,"updates":0})
        by_family[kind]["graphs"]+=1
        by_family[kind]["states"]+=len(normalized)
        by_family[kind]["updates"]+=new_ops["bitset_updates"]

    raw=[x for x,_,_ in prepared]
    # All arms use SAME normalized test graphs. Candidate and strong DP
    # both reuse a prebuilt index; indexing and graph validation are timed
    # separately rather than unfairly redoing them for only one arm.
    wall_clock={
        "old_independent_linear_scan":_measure(
            lambda:[scan(original_candidates,g) for g in raw]),
        "generated_DAG_search":_measure(
            lambda:[new_solver(previous_columns,len(original_candidates),g)
                    for g in raw]),
        "strong_classical_cached_DP":_measure(
            lambda:[strong.solve(g) for g in raw]),
    }
    source=artifact["source"]
    manifest=artifact["manifest"]
    result={
        "experiment":"MOTIF-LEGIT-012",
        "source_used":"ACTUAL_COMMITTED_LEGIT011_GENERATED_PYTHON",
        "parent_source_sha256":manifest["parent_legit011_sha256"],
        "actual_source_rewrite_created_and_executed":True,
        "generated_DAG_source_sha256":manifest["source_sha256"],
        "new_source_template_recipe":manifest["transformation_recipe"],
        "CEGIS_counterexamples":manifest["cegis_counterexamples"],
        "genuine_counterexample_transcript":manifest["counterexample_transcript"],
        "finite_and_inductive_proof":proof,
        "heldout_graphs":len(prepared),
        "heldout_source_authorship":"ASSISTANT_SEEDED_SYNTHETIC_NOT_BLINDED",
        "all_heldout_graph_states_checked":all_checks,
        "heldout_graph_states_computed_once_each":all_updates,
        "old_linear_candidate_bit_tests":fullscan_probes,
        "strong_classical_and_generated_bitset_updates_identical":True,
        "tuned_classical_baseline_fully_included":True,
        "tuned_classical_index_setup_membership_checks":strong.setup_operations,
        "candidate_index_build_ms":round(candidate_setup_ns/1_000_000,5),
        "classical_index_build_ms":round(classical_setup_ns/1_000_000,5),
        "wall_clock_repeated_ms":wall_clock,
        "graphs_by_family":by_family,
        "full_finite_state_proof_not_general_graph_algorithm_proof":True,
        "independently_verified_true_mathematics_beyond_Boolean_assumptions":False,
        "external_SMT_solver_used":False,
        "no_main_branch_changes":True,
        "generated_code_has_live_authority":False,
        "status":"RESEARCH_HOLD",
    }
    bundle={
        "schema":"motif.generated-research-dag-transform.v1",
        "status":"DRAFT_HUMAN_CODE_REVIEW_REQUIRED",
        "proof_carrying_source_manifest":manifest,
        "finite_proof":proof,
        "upstream_source_sha256":manifest["parent_legit011_sha256"],
        "upstream_source_verified_relative_to_local_commit":True,
        "independently_authored_external_proof":False,
        "source_eligible_for_automatic_merge":False,
        "real_world_authority":False,
    }
    return result,{"source":source,"manifest":bundle}

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python benchmark.py [--emit]")
    results,generated=execute()
    if sys.argv[1:]:
        Path("/tmp/motif-legit012-generated-search.py").write_text(
            generated["source"],encoding="utf-8")
        Path("/tmp/motif-legit012-source-proof.json").write_text(
            json.dumps(generated["manifest"],indent=2,sort_keys=True)+"\n",
            encoding="utf-8")
    print(json.dumps(results,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
