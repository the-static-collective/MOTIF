"""MOTIF LEGIT-018: sequential capability discovery experiment.

Episode A builds exact-weight path reasoning by combining LEGIT-017's
verified graph and subset-sum facilities. The obvious composition
(REACHABLE AND GLOBAL_SUBSET_SUM) is UNSOUND; the independent path oracle
produces actual counterexamples. A typed candidate generator then uses
the inherited bit-shift/graph semantics to compose a new exact-cost DAG
dynamic program.

Episode B adds forbidden-node constraints. A verified Episode-A source
unlocks a typed adaptation of that DP; without prior generated programs,
the deliberately restricted grammar supplies a correct DFS fallback.
This is a resource-matched within-grammar ablation of access to a
verified previous capability, not blind or open-ended new-algorithm
invention. The experiment also compares a strong independently coded
classical indexed DP, which can implement the same known algorithm.

All source is researcher-authored and emitted from bounded typed parts.
No production changes or claimed self-improvement success rate.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
from statistics import median
from time import perf_counter_ns,process_time_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from challenge import (
    Challenge,FAMILIES,check,generate,suite,reference,classical_index,
    classical_answer,finite_cases
)
from synth import (
    ancestry,typed,emit,compile_spec,explore_specs,check_tool,HOLD
)

REPEATS=7
HELDOUT_REPEATS=11
ASSUMED_FUTURE_BATCHES=24
STATUS="HOLD_NO_INDEPENDENT_CAUSAL_COMPOUNDING_PROOF"

def timed(action):
    start=perf_counter_ns()
    cpu=process_time_ns()
    n=action()
    return n,(round((perf_counter_ns()-start)/1e6,6),
              round((process_time_ns()-cpu)/1e6,6))

def measure(action,repeats):
    walls=[]
    cpus=[]
    for _ in range(repeats):
        _,(wall,cpu)=timed(action)
        walls.append(wall)
        cpus.append(cpu)
    return {
        "wall_ms":walls,"cpu_ms":cpus,
        "median_wall_ms":round(median(walls),6),
        "median_cpu_ms":round(median(cpus),6),
        "repeats":repeats
    }

def execute_source(tool,tasks):
    found=0
    for t in tasks:
        ctx=tool["build"](t)
        for q in t.queries:
            tool["answer"](ctx,q)
            found+=1
    return found

def independent(tasks):
    return sum(reference(t,q) for t in tasks for q in t.queries)

def strong(tasks):
    positives=0
    for t in tasks:
        idx=classical_index(t)
        for q in t.queries:
            positives+=classical_answer(idx,q)
    return positives

def exhaustive(family,program):
    count=0
    mismatches=0
    counterexample=None
    for raw in finite_cases():
        if family=="EXACT":
            queries=tuple(q for q in raw.queries if q[3]==-1)
        else:
            queries=raw.queries
        task=Challenge(family,raw.name,raw.edges,queries,raw.n)
        ctx=program["build"](task)
        for q in task.queries:
            got=program["answer"](ctx,q)
            truth=reference(task,q)
            count+=1
            if type(got) is not bool or got!=truth:
                mismatches+=1
                if counterexample is None:
                    counterexample={
                        "edges":list(task.edges),
                        "query":list(q),
                        "proposed":got,"exact_reference":truth
                    }
                return {
                    "exhaustive_cases_checked_before_first_failure":count,
                    "full_small_domain_verified":False,
                    "first_counterexample":counterexample
                }
    return {
        "exhaustive_cases_checked_before_first_failure":count,
        "full_small_domain_verified":True,
        "first_counterexample":None
    }

def trial(family,prior=None,ancestorA_source=None):
    if family not in FAMILIES:
        raise HOLD("Unknown innovation episode")
    if family=="FORBIDDEN" and prior is not None and ancestorA_source is None:
        raise HOLD("Cannot claim inherited Episode A capability without verified source")
    train=suite("TRAIN",family)
    check(train)
    candidate_specs=explore_specs(family,prior,ancestorA_source)
    baseline={
        "DIRECT":measure(lambda:independent(train),REPEATS),
        "STRONG":measure(lambda:strong(train),REPEATS)
    }
    reviews=[]
    approved=[]
    bad_witnesses=[]
    for spec in candidate_specs:
        start=perf_counter_ns()
        code=compile_spec(spec,prior,ancestorA_source)
        checked=check_tool(code,train)
        countermodel=exhaustive(family,code) if checked["correct"] else {
            "full_small_domain_verified":False,
            "first_counterexample":checked["first_counterexample"],
            "exhaustive_cases_checked_before_first_failure":0
        }
        proof_ms=(perf_counter_ns()-start)/1e6
        record={
            "spec":{**spec,"prechecks":list(spec["prechecks"])},
            "source_sha256":code["source_sha256"],
            "source_author":"BOUNDED_RESEARCHER_AUTHORED_COMPOSITION_GRAMMAR",
            "compilation_and_independent_verification_ms":round(proof_ms,6),
            "training_queries_checked":checked["checked_queries"],
            "semantics_correct_on_train":checked["correct"],
            "finite_truth_check":countermodel,
            "selected_on_training_only":True
        }
        if checked["correct"] and countermodel["full_small_domain_verified"]:
            cost=measure(lambda:execute_source(code,train),REPEATS)
            record["training_runtime"]=cost
            record["selection_score_ms"]=round(
                ASSUMED_FUTURE_BATCHES*(
                    baseline["DIRECT"]["median_wall_ms"]-
                    cost["median_wall_ms"])-proof_ms,6)
            record["status"]="PROVED_IN_SMALL_DOMAIN_AND_TRAIN"
            approved.append((record,code))
        else:
            record["status"]="REJECTED_BY_COUNTEREXAMPLE"
            if record["finite_truth_check"]["first_counterexample"]:
                bad_witnesses.append(record["finite_truth_check"]["first_counterexample"])
        reviews.append(record)
    if not approved:
        raise HOLD("No executable tool survived independent correctness checking")
    best,compiled=max(approved,key=lambda item:(
        item[0]["selection_score_ms"],item[0]["source_sha256"]))
    for rec in reviews:
        if rec["status"]=="PROVED_IN_SMALL_DOMAIN_AND_TRAIN":
            rec["status"]=("FROZEN_TRAINING_SELECTION"
                            if rec["source_sha256"]==best["source_sha256"]
                            else "CORRECT_NOT_SELECTED")
    if prior is not None and not bad_witnesses:
        raise HOLD("The easy ancestral AND composition must actually be falsified")
    dp=[(rec,code) for rec,code in approved
        if rec["spec"]["kernel"]=="BITSET_PATH"]
    return {
        "family":family,"train":train,
        "baselines":baseline,"reviews":reviews,
        "selected_tool":compiled,"selected_record":best,
        "verified_bitset_tool":dp[0][1] if dp else None,
        "correct_candidates":len(approved),
        "refuted_candidates":len(reviews)-len(approved),
        "counterexamples":bad_witnesses,
        "candidate_proposals":len(reviews),
        "resource_assumption_future_batches":ASSUMED_FUTURE_BATCHES
    }

def heldout(trial_data):
    family=trial_data["family"]
    tasks=suite("HELDOUT",family)
    check(tasks)
    if {x.name for x in tasks}&{x.name for x in trial_data["train"]}:
        raise HOLD("Train/test source overlap")
    selected=trial_data["selected_tool"]
    valid=check_tool(selected,tasks)
    if not valid["correct"] or valid["checked_queries"]!=len(tasks)*len(tasks[0].queries):
        raise HOLD("Selected solver failed unseen queries")
    # Strong optimised classical DP is compared against the exact oracle,
    # on every heldout query, not merely timed.
    for t in tasks:
        idx=classical_index(t)
        for q in t.queries:
            if classical_answer(idx,q)!=reference(t,q):
                raise HOLD("Strong classical implementation is not correct")
    timed_data={
        "DIRECT":measure(lambda:independent(tasks),HELDOUT_REPEATS),
        "STRONG_CLASSICAL":measure(lambda:strong(tasks),HELDOUT_REPEATS),
        "GENERATED":measure(lambda:execute_source(selected,tasks),HELDOUT_REPEATS),
    }
    return {
        "cases":len(tasks),"queries":valid["checked_queries"],
        "zero_wrong_answers":True,
        "same_generator_author":True,
        "timings":timed_data,
        "speedup_over_direct":round(
            timed_data["DIRECT"]["median_wall_ms"]/
            timed_data["GENERATED"]["median_wall_ms"],6),
        "speedup_over_strong":round(
            timed_data["STRONG_CLASSICAL"]["median_wall_ms"]/
            timed_data["GENERATED"]["median_wall_ms"],6)
    }

def compare_sources(runA,with_prior,without_prior):
    if runA["verified_bitset_tool"] is None:
        raise HOLD("Episode A never established an exact path-cost recurrence")
    if (without_prior["selected_record"]["spec"]["kernel"]!="DFS_EXACT" or
        with_prior["selected_tool"]["spec"]["family"]!="FORBIDDEN"):
        raise HOLD("No fair bounded-grammar control")
    return {
        "with_A_training":with_prior["selected_record"]["training_runtime"],
        "without_A_training":without_prior["selected_record"]["training_runtime"],
        "with_A_candidates_examined":with_prior["candidate_proposals"],
        "without_A_candidates_examined":without_prior["candidate_proposals"],
        "with_A_source_sha256":with_prior["selected_tool"]["source_sha256"],
        "without_A_source_sha256":without_prior["selected_tool"]["source_sha256"],
        "source_inheritance_available_only_with_A":True,
        "same_training_distribution":True,
        "model_selection_used_test_work":False,
        "different_search_grammars_by_design":True,
        "causal_effect_on_unrestricted_discovery_unproven":True,
    }

def run():
    old=ancestry()
    # Generation A: composite graph-path-cost reasoning. The bad attempt
    # to AND the two old tool results must produce a real counterexample.
    A=trial("EXACT",old)
    if A["verified_bitset_tool"] is None:
        raise HOLD("Cannot transfer nonexistent generation-A exact-cost DP")
    legacy_source=A["verified_bitset_tool"]["source"]
    # Generation B: completely different constraint. The same challenge
    # instances are used in both arms; only availability of the verified
    # previously generated research tool changes.
    B_with=trial("FORBIDDEN",old,legacy_source)
    B_without=trial("FORBIDDEN")
    results={
        "A":heldout(A),
        "B_WITH_ANCESTRY":heldout(B_with),
        "B_NO_ANCESTRY":heldout(B_without),
    }
    # Productive capability transfer can be measured even when performance
    # fails to improve or a strong classical reference is faster.
    transferred={
        "episode_A_verified_bitset_source_sha256":
            A["verified_bitset_tool"]["source_sha256"],
        "episode_B_sees_verified_A_bitset":True,
        "episode_B_bounded_grammar_without_A_excludes_bitset_recurrence":True,
        "actual_prior_017_source":old["source_sha256"],
        "heldout_compared_with_and_without_A":True,
        **compare_sources(A,B_with,B_without),
    }
    frozen_sources={
        "schema":"motif.legit018.generated-compositional-sources.v1",
        "programs":{
            "A_EXACT":A["selected_tool"]["source"],
            "A_VERIFIED_BITSET_LIBRARY":legacy_source,
            "B_WITH_ANCESTRY":B_with["selected_tool"]["source"],
            "B_NO_ANCESTRY":B_without["selected_tool"]["source"],
        },
        "manifests":{
            "A_EXACT":A["selected_record"]["spec"],
            "A_VERIFIED_BITSET_LIBRARY":A["verified_bitset_tool"]["spec"],
            "B_WITH_ANCESTRY":B_with["selected_record"]["spec"],
            "B_NO_ANCESTRY":B_without["selected_record"]["spec"],
        },
        "prior_017_hashes":old["source_sha256"],
        "production_authority":False,
    }
    witness={
        "schema":"motif.legit018.capability-discovery.v1",
        "experiment":"MOTIF-LEGIT-018",
        "title":"COMPOSITIONAL_CAPABILITY_DISCOVERY",
        "status":STATUS,
        "source_bank":"ACTUAL_VERIFIED_LEGIT017_GENERATED_PYTHON",
        "families":"EXACT_WEIGHTED_PATH_AND_FORBIDDEN_NODE_EXACT_PATH",
        "training_proposals":{
            key:{
                "family":stage["family"],
                "proposed":stage["candidate_proposals"],
                "formally_in_small_domain_verified":stage["correct_candidates"],
                "counterexample_rejected":stage["refuted_candidates"],
                "source_pinned_selected_sha256":stage["selected_tool"]["source_sha256"],
                "selected_plan":{**stage["selected_tool"]["spec"],
                                 "prechecks":list(stage["selected_tool"]["spec"]["prechecks"])},
                "records":stage["reviews"],
                "concrete_bad_join_counterexamples":stage["counterexamples"],
            }
            for key,stage in (("A",A),("B_WITH_ANCESTRY",B_with),
                              ("B_NO_ANCESTRY",B_without))
        },
        "heldout":results,
        "adaptation":transferred,
        "original_task_generator_authorship":"SAME_RESEARCHER_ALL_TASKS",
        "independent_external_challenge_author":False,
        "repeated_new_discoveries_under_blind_evaluation":False,
        "full_human_development_cost_measured":False,
        "unrestricted_algorithm_invention":False,
        "small_finite_falsifiers_only":True,
        "actual_working_source_composed_and_reused":True,
        "strong_classical_compared":True,
        "causal_compounding_of_open_ended_research_proved":False,
        "new_open_world_capability_claimed":False,
        "automatically_merged_or_deployed":False,
        "real_world_authority":False
    }
    return witness,frozen_sources

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("python experiments/legit018/trial.py [--emit]")
    witness,sources=run()
    if sys.argv[1:]:
        Path("/tmp/motif-legit018-discovery-report.json").write_text(
            json.dumps(witness,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        Path("/tmp/motif-legit018-programs.json").write_text(
            json.dumps(sources,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "experiment":witness["experiment"],
        "status":witness["status"],
        "selected":{k:v["selected_plan"] for k,v in witness["training_proposals"].items()},
        "counterexamples":{k:v["counterexample_rejected"] for k,v in witness["training_proposals"].items()},
        "heldout":{k:{
            "queries":v["queries"],
            "medians":{kk:vv["median_wall_ms"] for kk,vv in v["timings"].items()}
        }for k,v in witness["heldout"].items()},
        "provenance":witness["source_bank"],
    },indent=2,sort_keys=True))

if __name__=="__main__":main()
