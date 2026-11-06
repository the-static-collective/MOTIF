"""LEGIT-016: new measured evidence episode for actual MOTIF-012/013/014 code.

Run the previous three GENERATED Python solvers on newly registered
synthetic DAG seeds with an independent tuned classical implementation.
Validate the result of EVERY graph-state query. Re-run actual Z3 proof
for the unchanged 014 program. Record raw wall and CPU times, start-up
costs and a small allocation trace.

The 24 trial DAGs have NEW seeds but use the SAME researcher-authored
generator as earlier tests: they are NOT independent real-world or
third-party-authored cases. Repetition on one CI runner is NOT a series
of independent software innovations. This code creates evidence,
not self-improvement or auto-promotion.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from statistics import median
from time import perf_counter_ns,process_time_ns
import json
import os
import platform
import sys
import tracemalloc

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
for part in ("legit010","legit012","legit013","legit014", "legit016"):
    sys.path.insert(0,str(ROOT/part))
# Load explicit module files where names (e.g. transform) collide.
def load_module(label,path):
    spec=spec_from_file_location(label,path)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

from evidence import archive,HOLD
from graph_reference import cases,check_graph,scan
from classical_control import StrongClassicalDP
from examiner import catalog,_make_columns

REPEATS=9
GRAPH_SEED_START=120000
COUNTS=(("LIGHT",8),("MEDIUM",24),("DENSE",64))
BASELINE_SOURCE={
    "prior_012":ROOT/"legit012"/"generated"/"search_dag_v3.py",
    "prior_013":ROOT/"legit013"/"generated"/"optimized_search_v4.py",
    "candidate_014":ROOT/"legit014"/"generated"/"candidate_rewrite.py",
}
BASELINE_MANIFESTS={
    "prior_012":ROOT/"legit012"/"generated"/"search_dag_proof.json",
    "prior_013":ROOT/"legit013"/"generated"/"formal_certificate.json",
}

def registered_source_hashes():
    docs=archive()
    a=json.loads(BASELINE_MANIFESTS["prior_012"].read_text())
    b=json.loads(BASELINE_MANIFESTS["prior_013"].read_text())
    expected={
        "prior_012":a["proof_carrying_source_manifest"]["source_sha256"],
        "prior_013":b["source_manifest"]["source_sha256"],
        "candidate_014":docs["source_sha256"],
    }
    for name,path in BASELINE_SOURCE.items():
        if sha256(path.read_bytes()).hexdigest()!=expected[name]:
            raise HOLD("Prior generated program no longer matches verified provenance")
    return expected

def registered_challenge():
    graphs=[]
    for i in range(24):
        family,size=COUNTS[i%len(COUNTS)]
        graph=check_graph(cases(GRAPH_SEED_START+i,size+(i//3)%4*4))
        graphs.append((family,graph))
    if len({tuple(x for x,_ in data) for _,data in graphs})<2:
        raise HOLD("Registered test graphs failed diversity requirement")
    return graphs

def timed(fn,inputs):
    wall=perf_counter_ns()
    cpu=process_time_ns()
    for _,graph in inputs:
        fn(graph)
    return ((perf_counter_ns()-wall)/1e6,
            (process_time_ns()-cpu)/1e6)

def measure():
    source_hashes=registered_source_hashes()
    observations=registered_challenge()
    rows=catalog()
    if len(rows)!=152:
        raise HOLD("Unexpected source synthesis domain")
    # The archived 014 winner is re-generated under the actual prior
    # bounded source compiler; this invokes real external Z3.
    transform014=load_module("verified014_transform_for016",
                             ROOT/"legit014"/"transform.py")
    frozen=json.loads((ROOT/"legit014"/"generated"/"candidate_manifest.json").read_text())
    start=perf_counter_ns()
    generated=transform014.compile_proved(frozen["source_plan"])
    external_proof_ms=(perf_counter_ns()-start)/1e6
    if generated["source_sha256"]!=source_hashes["candidate_014"]:
        raise HOLD("External Z3-reverified generated source differs from archive")
    solver014=generated["function"]
    implementations={}
    for name in ("prior_012","prior_013"):
        module=load_module("pinned016_"+name,BASELINE_SOURCE[name])
        implementations[name]=module.solve
    implementations["candidate_014"]=solver014

    build=perf_counter_ns()
    columns=_make_columns(rows)
    shared_index_setup_ms=(perf_counter_ns()-build)/1e6
    build=perf_counter_ns()
    strong=StrongClassicalDP(rows)
    strong_index_setup_ms=(perf_counter_ns()-build)/1e6
    arms={name:(lambda graph,solve=fn:solve(columns,len(rows),graph))
          for name,fn in implementations.items()}
    arms["strong_classical"]=strong.solve

    exact_scans=0
    total_states=0
    by_family={k:{"graphs":0,"states":0} for k,_ in COUNTS}
    for family,graph in observations:
        gold,_=scan(rows,graph)
        exact_scans+=1
        total_states+=len(graph)
        by_family[family]["graphs"]+=1
        by_family[family]["states"]+=len(graph)
        for name,run in arms.items():
            got,ops=run(graph)
            if got!=gold:
                raise HOLD("A previous generated algorithm disagrees with exact oracle: "+name)

    # Independent run BEFORE measurement excludes import and warmup from
    # per-batch comparison. Startup costs explicitly saved separately.
    for arm in arms.values():
        timed(arm,observations[:3])

    samples={n:{"wall_ms":[],"cpu_ms":[]} for n in arms}
    names=sorted(arms)
    for i in range(REPEATS):
        order=names[i%len(names):]+names[:i%len(names)]
        if i%2:order=list(reversed(order))
        for name in order:
            wall,cpu=timed(arms[name],observations)
            samples[name]["wall_ms"].append(round(wall,6))
            samples[name]["cpu_ms"].append(round(cpu,6))

    # Peak traced allocations for a SMALL representative batch; tracemalloc
    # changes runtime behavior, so this is a separate memory experiment.
    representative=observations[:3]
    allocated={}
    for name in names:
        tracemalloc.start()
        try:
            timed(arms[name],representative)
            current,peak=tracemalloc.get_traced_memory()
            allocated[name]={"sample_graphs":3,"peak_traced_python_bytes":peak}
        finally:
            tracemalloc.stop()

    return {
        "schema":"motif.empirical-improvement-episode.v1",
        "source":"EXECUTED_ACTUAL_GENERATED_SOLVERS",
        "experiment":"MOTIF-LEGIT-016",
        "status":"RESEARCH_HOLD_UNBLINDED",
        "source_sha256":source_hashes,
        "external_z3_reverified_prior_finite_rewrite":True,
        "external_proof_and_source_compile_ms":round(external_proof_ms,6),
        "shared_precomputed_source_index_setup_ms":round(shared_index_setup_ms,6),
        "strong_classical_index_setup_ms":round(strong_index_setup_ms,6),
        "new_seed_graphs":len(observations),
        "new_seed_start":GRAPH_SEED_START,
        "new_seed_graph_states":total_states,
        "graph_families":by_family,
        "exact_scan_reference_graphs":exact_scans,
        "output_mismatches":0,
        "raw_repeat_samples":samples,
        "descriptive_medians_ms":{
            name:{
                "wall":round(median(data["wall_ms"]),6),
                "cpu":round(median(data["cpu_ms"]),6),
            } for name,data in samples.items()
        },
        "peak_traced_python_allocation_sample":allocated,
        "environment":{"python":platform.python_version(),
                       "platform_system":platform.system(),
                       "platform_machine":platform.machine(),
                       "logical_cpu_count":os.cpu_count()},
        "sample_count_per_arm":REPEATS,
        "test_set_independently_authored":False,
        "generator_family_shared_with_prior":True,
        "sources_authenticating_external_author":False,
        "independent_innovation_episode_count":0,
        "not_matched_cpu_affinity_or_GC":True,
        "source_self_improved_in_this_experiment":False,
        "automatic_promotion":False,
        "real_world_authority":False,
    }
