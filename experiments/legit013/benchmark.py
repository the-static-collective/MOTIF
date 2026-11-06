"""LEGIT-013: training-only hotspot discovery, held-out correctness and timing.

Generated source is actually executed against the same structured graphs
as the prior LEGIT-012 program, conventional DP, and a *strong, separately
implemented zero/full shortcut classical DP*.

Formal Z3 proof is mandatory: if Z3 is unavailable or says unknown,
the entire experiment fails. Training/test seeds are separate, but all
tasks are researcher-generated synthetic cases, not third-party blind.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit012"))
from graph_reference import cases,make_graph,all_states,check_graph,scan

from examiner import construct,reverify,actual_parent,catalog,_make_columns,profile
from classical_control import StrongClassicalDP,UnoptimizedClassicalDP

def _runtime(fn,repeat=5):
    times=[]
    for _ in range(repeat):
        begin=perf_counter_ns()
        fn()
        times.append((perf_counter_ns()-begin)/1e6)
    return {"samples":repeat,"median_ms":round(median(times),5),
            "min_ms":round(min(times),5),"max_ms":round(max(times),5)}

def heldout():
    """Never used during synthesis. Different seeds, density and workload."""
    specs=[(61000+i,8+(i%4)*8) for i in range(24)]
    specs += [(62000+i,32+(i%4)*12) for i in range(32)]
    specs += [(63000+i,72+(i%4)*12) for i in range(24)]
    return [check_graph(cases(seed,n)) for seed,n in specs]

def evaluate():
    methods=catalog()
    newly=construct()
    proof=reverify(newly)
    reference=actual_parent()
    strong=StrongClassicalDP(methods)
    base=UnoptimizedClassicalDP(methods)
    columns=_make_columns(methods)
    generated=newly["solver"]
    graphs=heldout()
    total_nodes=0
    baseline_ands=0
    optimized_ands=0
    generated_ands=0
    generated_skips=0
    strong_skips=0
    heldout_disagreements=0
    for graph in graphs:
        old,old_counts=reference.solve(columns,len(methods),graph)
        new,new_counts=generated(columns,len(methods),graph)
        checked,strong_counts=strong.solve(graph)
        ordinary,base_counts=base.solve(graph)
        if not old==new==checked==ordinary:
            heldout_disagreements+=1
            raise AssertionError("Self-generated shortcut changed the reasoning answer")
        total_nodes+=len(graph)
        baseline_ands+=old_counts["bitset_updates"]
        optimized_ands+=strong_counts["bitset_intersections"]
        generated_ands+=new_counts["bitset_intersections"]
        generated_skips+=new_counts["branch_skips"]
        strong_skips+=strong_counts["branch_skips"]
        if generated_ands+new_counts["branch_skips"]!=old_counts["bitset_updates"]:
            raise AssertionError("Generated source missed DAG transition")
    # Complete bounded model against every partial Boolean input.
    lattice=check_graph(make_graph("EntireTruthLattice",all_states()))
    a,_=reference.solve(columns,len(methods),lattice)
    b,_=generated(columns,len(methods),lattice)
    c,_=strong.solve(lattice)
    d,_=scan(methods,lattice)
    if not a==b==c==d or len(a)!=6561:
        raise AssertionError("Whole finite evidence lattice mismatched")

    all_rows=graphs
    wall={
        "previous_self_generated_DAG_solver":_runtime(
            lambda:[reference.solve(columns,len(methods),g) for g in all_rows]),
        "new_Z3_certified_shortcut_solver":_runtime(
            lambda:[generated(columns,len(methods),g) for g in all_rows]),
        "strong_classical_optimized_DP":_runtime(
            lambda:[strong.solve(g) for g in all_rows]),
        "unoptimized_classical_DP":_runtime(
            lambda:[base.solve(g) for g in all_rows]),
    }
    raw=newly["manifest"]
    result={
        "experiment":"MOTIF-LEGIT-013",
        "title":"THE_SELF_IMPROVEMENT_EXAMINER",
        "source_profiler":raw["training_profiler"],
        "source_code_read":"REAL_COMMITTED_LEGIT012_GENERATED_SOLVER",
        "source_parent_sha256":raw["parent_generated_source_sha256"],
        "generated_source_sha256":raw["source_sha256"],
        "generated_rules":raw["rules"],
        "examiner_counterexamples":raw["examiner_transcript"],
        "genuine_SMT_counterexamples":raw["genuine_smt_counterexamples"],
        "third_party_formal_verifier":proof,
        "external_SMT_prover":"Z3",
        "full_finite_search_cases_checked":len(lattice),
        "heldout_graphs":len(graphs),
        "heldout_state_outputs_verified":total_nodes,
        "heldout_disagreements":heldout_disagreements,
        "heldout_data":"SEEDED_SYNTHETIC_FROM_DIFFERENT_SEEDS_NOT_EXTERNAL",
        "operations":{
            "previous_all_DAG_bitset_intersections":baseline_ands,
            "generated_rewrite_bitset_intersections":generated_ands,
            "generated_guarded_skips":generated_skips,
            "strong_classical_bitset_intersections":optimized_ands,
            "strong_classical_guarded_skips":strong_skips,
            "one_time_source_index_bit_comparisons":strong.index_bit_comparisons,
            "not_equal_wall_clock_work_units":True,
        },
        "wall_clock_repeated_ms":wall,
        "runtime_speedup_over_tuned_classical_proved":False,
        "algorithmic_superiority_over_optimized_classical_proved":False,
        "benchmark_median_is_not_stable_evidence":True,
        "independent_specification_authorship":False,
        "live_production_changes":False,
        "external_actions_dispatched":False,
        "generated_code_not_a_general_Python_sandbox":True,
        "status":"RESEARCH_HOLD",
    }
    bundle={
        "schema":"motif.proof-carrying-examiner-artifacts.v1",
        "status":"DRAFT_HUMAN_REVIEW_REQUIRED",
        "source_sha256":raw["source_sha256"],
        "source_manifest":raw,
        "formal_verification":proof,
        "production_write_permitted":False,
        "independent_test_authorship":False,
        "automatic_algorithm_promotion":False,
        "real_world_authority":False,
    }
    return result,{"source":newly["source"],"receipt":bundle}

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("python benchmark.py [--emit]")
    report,art=evaluate()
    if sys.argv[1:]:
        Path("/tmp/motif-legit013-generated-optimizer.py").write_text(
            art["source"],encoding="utf-8")
        Path("/tmp/motif-legit013-formal-receipt.json").write_text(
            json.dumps(art["receipt"],indent=2,sort_keys=True)+"\n",
            encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
