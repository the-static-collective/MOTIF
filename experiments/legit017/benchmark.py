"""MOTIF-LEGIT-017: actual portfolio trial across three engineering domains.

A typed research-tool factory generates executable source in six known
algorithm styles and ONE cross-domain second-order verification cache.
The program verifies source against independent task oracles, measures
real engineering/proof/index costs, allocates a two-tool research budget
from TRAINING data only, then tests the frozen tools on heldout inputs.

The direct-no-tool counterfactual and a strong conventional indexed
portfolio are both measured. The verification-cache tool is evaluated
separately by a full-cost causal ablation against direct rechecking and
standard classical oracle preprocessing.

All tasks were authored by this experiment. They are not independently
blind or formerly unseen mathematical domains. This is genuine executable
tool reuse, not proof of open-ended recursive improvement.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
from pathlib import Path
from statistics import median
from time import perf_counter_ns,process_time_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from tasks import (FAMILIES,suite,check_suite,direct,strong_build,strong_ask)
from toolsmith import (STRATEGIES,compile_tool,verify,bounded_falsification,HOLD)
from metatool import (compile_verifier,check_variants,VERIFIER_SOURCE)
 
# A training-only HYPOTHESIS of 64 future same-size work batches and a
# RESEARCH budget of two accelerator families. This is not a predicted
# real workload distribution, successful discovery odds or a time discount.
ASSUMED_FUTURE_BATCHES=64
TOOL_BUDGET=2
PERFORMANCE_REPEATS=7
HELDOUT_REPEATS=11
VERIFICATION_REPEATS=7

def _timed(fn):
    start=perf_counter_ns()
    cpu=process_time_ns()
    result=fn()
    return result,((perf_counter_ns()-start)/1e6,
                   (process_time_ns()-cpu)/1e6)

def times(fn,repeats=7):
    wall=[]
    cpu=[]
    for _ in range(repeats):
        result,(w,c)=_timed(fn)
        wall.append(round(w,6))
        cpu.append(round(c,6))
    return {"samples_ms":wall,"cpu_samples_ms":cpu,
            "median_wall_ms":round(median(wall),6),
            "median_cpu_ms":round(median(cpu),6),
            "repeat_count":repeats}

def work(tasks,mode,selected=None):
    answers=0
    for task in tasks:
        if mode=="DIRECT":
            for q in task.queries:
                direct(task,q)
                answers+=1
        elif mode=="STRONG":
            ctx=strong_build(task)
            for q in task.queries:
                strong_ask(task,ctx,q)
                answers+=1
        elif mode=="PORTFOLIO":
            tool=selected.get(task.family) if selected else None
            if tool is None:
                for q in task.queries:
                    direct(task,q);answers+=1
            else:
                ctx=tool["build"](task.instance)
                for q in task.queries:
                    tool["answer"](ctx,q)
                    answers+=1
        else:
            raise HOLD("Unknown performance comparator")
    return answers

def _select(scored):
    """Independent classical exhaustive budgeted subset selection.

    Every candidate's first-stage cost and projected throughput are
    included. This planner is an ordinary exact knapsack enumerator.
    """
    items=list(scored)
    possibilities=[]
    for r in range(TOOL_BUDGET+1):
        for group in combinations(items,r):
            total=sum(scored[f]["projected_net_ms"] for f in group)
            possibilities.append((total,group))
    return tuple(max(possibilities,key=lambda e:(e[0],-len(e[1]),e[1]))[1])

def training():
    train=suite("TRAIN")
    check_suite(train)
    members={f:[t for t in train if t.family==f] for f in FAMILIES}
    baseline={}
    candidates={f:[] for f in FAMILIES}
    all_tools={f:[] for f in FAMILIES}
    for family in FAMILIES:
        tasks=members[family]
        baseline[family]={
            "direct":times(lambda:work(tasks,"DIRECT"),PERFORMANCE_REPEATS),
            "strong":times(lambda:work(tasks,"STRONG"),PERFORMANCE_REPEATS),
        }
        for strategy in STRATEGIES[family]:
            tool=compile_tool(family,strategy)
            verification=verify(tool,tasks)
            finite=bounded_falsification(tool)
            measured=times(lambda:work(tasks,"PORTFOLIO",
                                        {family:tool}),PERFORMANCE_REPEATS)
            # All known experimental verification and compile costs; excludes
            # human authorship, packaging, CI provisioning, maintenance.
            setup=tool["compile_ms"]+verification["verification_wall_ms"]
            candidate={
                "family":family,
                "strategy":strategy,
                "source_sha256":tool["source_sha256"],
                "training_compiled_wall_ms":tool["compile_ms"],
                "training_independent_verification_ms":
                    verification["verification_wall_ms"],
                "training_tool_cost_ms":round(setup,6),
                "verified_query_answers":verification["tests"],
                "bounded_exhaustive_cases":finite["exact_cases_checked"],
                "training_throughput":measured,
                "training_direct_throughput":baseline[family]["direct"]
                    ["median_wall_ms"],
                "training_strong_throughput":baseline[family]["strong"]
                    ["median_wall_ms"],
                "assumed_future_batches":ASSUMED_FUTURE_BATCHES,
                "training_forecast_net_ms":round(
                    ASSUMED_FUTURE_BATCHES*(
                      baseline[family]["direct"]["median_wall_ms"]-
                      measured["median_wall_ms"])-setup,6),
                "source_templates_hand_written":True,
                "complete_external_formal_proof":False,
            }
            candidates[family].append(candidate)
            all_tools[family].append(tool)
    best={}
    for family in FAMILIES:
        winner=min(candidates[family],key=lambda x:(
            -x["training_forecast_net_ms"],
            x["source_sha256"]))
        best[family]={
            "strategy":winner["strategy"],
            "projected_net_ms":winner["training_forecast_net_ms"],
            "cost_ms":winner["training_tool_cost_ms"],
        }
    chosen=_select(best)
    frozen={}
    for family in chosen:
        idx=next(i for i,c in enumerate(candidates[family])
                 if c["strategy"]==best[family]["strategy"])
        frozen[family]=all_tools[family][idx]
    return {
        "train":train,
        "all_tools":all_tools,
        "training_baselines":baseline,
        "training_candidates":candidates,
        "ranked_best_per_family":best,
        "selected_families":list(chosen),
        "frozen":frozen,
        "frozen_source_sha256":{f:t["source_sha256"]
                                for f,t in frozen.items()},
        "selection_used_heldout":False,
        "assumed_future_batches_not_empirically_predicted":ASSUMED_FUTURE_BATCHES,
    }

def _verify_new_tasks(test,tools):
    outputs=0
    for task in test:
        baseline_context=strong_build(task)
        group=tools[task.family]
        contexts=[(t,t["build"](task.instance)) for t in group]
        for q in task.queries:
            actual=direct(task,q)
            if strong_ask(task,baseline_context,q)!=actual:
                raise HOLD("Independent optimized classical wrong")
            for tool,ctx in contexts:
                value=tool["answer"](ctx,q)
                if type(value) is not bool or value!=actual:
                    raise HOLD("Source compiler produced a wrong new-domain answer")
            outputs+=1
    return outputs

def _withheld_analyses(trial,heldout):
    frozen=trial["frozen"]
    outcomes={
        "DIRECT":times(lambda:work(heldout,"DIRECT"),HELDOUT_REPEATS),
        "STRONG":times(lambda:work(heldout,"STRONG"),HELDOUT_REPEATS),
        "FROZEN_PORTFOLIO":times(
            lambda:work(heldout,"PORTFOLIO",frozen),HELDOUT_REPEATS),
    }
    family_splits={}
    for family in FAMILIES:
        sub=[t for t in heldout if t.family==family]
        family_splits[family]={
            "tasks":len(sub),
            "queries":sum(len(x.queries) for x in sub),
            "direct":times(lambda:work(sub,"DIRECT"),5),
            "strong":times(lambda:work(sub,"STRONG"),5),
            "portfolio":times(lambda:work(sub,"PORTFOLIO",frozen),5),
            "selected_tool_source":frozen[family]["source_sha256"]
                if family in frozen else None,
        }
    return outcomes,family_splits

def prepare_verifier(trial):
    """Select a verification tool and oracle strategy using TRAINING ONLY.

    The first cache was initially primed by expensive independent direct
    oracle calls. The new meta-level candidate can instead prime the SAME
    generated cache with the strongly optimized conventional reference,
    after the program has independently checked that oracle's correctness.
    Both methods are predeclared, classical and fully inspectable.
    """
    meta=compile_verifier()
    rehearsal={m:times(lambda:check_variants(
        trial["train"],trial["all_tools"],m,meta),3)
        for m in ("RECHECK","CACHE","IMPROVED_CACHE","STRONG")}
    choice=min(("CACHE","IMPROVED_CACHE"),key=lambda m:(
        rehearsal[m]["median_wall_ms"],m))
    return {"meta":meta,"choice":choice,"rehearsal":rehearsal,
            "training_selected_not_using_heldout":True}

def verifier_trial(trial,test,prepared):
    """Causal same-workload ablation of a generated meta-research tool.

    An independent oracle is rechecked on the actual withheld task set
    before witness reuse. The chosen mode was frozen on training data.
    The closest competitor is strong, optimized CLASSICAL memoization.
    """
    meta=prepared["meta"]
    chosen=prepared["choice"]
    training=prepared["rehearsal"]
    future={m:times(lambda:check_variants(
        test,trial["all_tools"],m,meta),VERIFICATION_REPEATS)
        for m in ("RECHECK","CACHE","IMPROVED_CACHE","STRONG")}
    baseline_receipt=check_variants(test,trial["all_tools"],"RECHECK")
    cached_receipt=check_variants(test,trial["all_tools"],chosen,meta)
    strong_receipt=check_variants(test,trial["all_tools"],"STRONG")
    if (baseline_receipt["checked_tool_query_pairs"]!=
        cached_receipt["checked_tool_query_pairs"] or
        cached_receipt["checked_tool_query_pairs"]!=
        strong_receipt["checked_tool_query_pairs"]):
        raise HOLD("Research witness cache skipped checking candidate programs")
    n=cached_receipt["checked_tool_query_pairs"]
    if not baseline_receipt["reference_calls"]>cached_receipt["reference_calls"]:
        raise HOLD("Meta research tool did not actually reuse evidence")
    benefit=(future["RECHECK"]["median_wall_ms"]-
             future[chosen]["median_wall_ms"])
    comparison_to_strong=(future["STRONG"]["median_wall_ms"]-
                          future[chosen]["median_wall_ms"])
    return {
        "source":meta["source"],
        "source_sha256":meta["source_sha256"],
        "source_generated_by_fixed_template":True,
        "compiled_ms":meta["compile_ms"],
        "training_selected_verifier_mode":chosen,
        "training_preselected_cache":(
            training[chosen]["median_wall_ms"]<
            training["RECHECK"]["median_wall_ms"]),
        "training_ms":training,
        "test_ms":future,
        "per_trial_candidate_query_checks":n,
        "no_cache_reference_calls":baseline_receipt["reference_calls"],
        "with_tool_reference_calls":cached_receipt["reference_calls"],
        "strong_classical_reference_calls":strong_receipt["reference_calls"],
        "heldout_median_saving_vs_rechecking_ms":round(benefit,6),
        "heldout_median_saving_vs_strong_classical_ms":
            round(comparison_to_strong,6),
        "heldout_timing_was_not_used_for_verifier_selection":True,
        "improved_cache_uses_independently_checked_classical_oracle":True,
        "within_assistant_authored_workload":True,
        "proves_future_research_discovery_time_reduced":False,
        "does_not_establish_superiority_to_classical_memoization":True,
    }

def previous_evidence_boundary():
    """Read the ACTUAL previous empirical witness, preserve its HOLD.

    A new fast source-template test does not erase the previous failure
    to establish independent, adopted, causal compounding of discovery.
    """
    old=HERE.parent/"legit016"/"generated"/"empirical_witness_report.json"
    report=json.loads(old.read_text(encoding="utf-8"))
    original=HERE.parent/"legit014"/"generated"/"candidate_rewrite.py"
    identity=sha256(original.read_bytes()).hexdigest()
    prior=report.get("real_014_retrospective",{})
    if (report.get("experiment")!="MOTIF-LEGIT-016"
        or report.get("observed_compounding_rate")!="NOT_ESTIMABLE"
        or report.get("promotion_decision")!="HOLD_NOT_ENOUGH_INDEPENDENT_EVIDENCE"
        or report.get("promotion_gate",{}).get("production_promotion_allowed") is not False
        or prior.get("source_sha256")!=identity
        or report.get("new_016_observed_episode",{}).get("output_mismatches")!=0):
        raise HOLD("Prior experimental evidence is not trustworthy or was promoted")
    return {
        "experiment":report["experiment"],
        "compounding_rate":report["observed_compounding_rate"],
        "promotion_decision":report["promotion_decision"],
        "source_sha256":identity,
        "prior_real_improvement_rate_not_calibrated":True,
    }

def run():
    prior=previous_evidence_boundary()
    trial=training()  # task suite for HELDOUT not evaluated or built yet
    prepared_verifier=prepare_verifier(trial)
    frozen_plan={
        "research_verifier_mode":prepared_verifier["choice"],
        "selected":trial["selected_families"],
        "sources":trial["frozen_source_sha256"],
        "training_only_forecast":trial["ranked_best_per_family"],
        "budget":TOOL_BUDGET,
        "hypothetical_horizon":ASSUMED_FUTURE_BATCHES,
    }
    freeze_hash=sha256(json.dumps(frozen_plan,sort_keys=True,
                                   separators=(",",":")).encode()).hexdigest()
    heldout=suite("HELDOUT")
    check_suite(heldout)
    if set(x.identifier for x in heldout)&set(
            x.identifier for x in trial["train"]):
        raise HOLD("Training/heldout tasks overlap")
    validated_outputs=_verify_new_tasks(heldout,trial["all_tools"])
    measured,by_family=_withheld_analyses(trial,heldout)
    meta=verifier_trial(trial,heldout,prepared_verifier)
    prev=measured["FROZEN_PORTFOLIO"]["median_wall_ms"]
    direct_cost=measured["DIRECT"]["median_wall_ms"]
    strong_cost=measured["STRONG"]["median_wall_ms"]
    proof_setup=sum(trial["ranked_best_per_family"][f]["cost_ms"]
                    for f in trial["selected_families"])+meta["compiled_ms"]
    # Set an aggressive predeclared gate. This is still research-only:
    # no source is promoted without external blinded independent authors.
    performance_gain=(direct_cost-prev)/direct_cost
    versus_strong=(strong_cost-prev)/strong_cost
    gates={
        "all_tools_bounded_exact_correct":validated_outputs==sum(
            len(t.queries) for t in heldout),
        "at_least_10pct_gain_over_no_tool":performance_gain>=.10,
        "at_least_10pct_gain_over_strong_classical":versus_strong>=.10,
        "meta_verifier_training_gain":meta["training_preselected_cache"],
        "full_test_development_cost_measured":False,
        "independent_blinded_task_author":False,
        "source_custody_external_verified":False,
        "causal_successive_discoveries_demonstrated":False,
        "automatic_source_promotion":False,
    }
    verdict="HOLD_RESEARCH_ONLY_INDEPENDENT_COMPOUNDING_NOT_DEMONSTRATED"
    packet={
        "schema":"motif.research-productivity-engine.v1",
        "experiment":"MOTIF-LEGIT-017",
        "title":"THE_RESEARCH_PRODUCTIVITY_ENGINE",
        "status":verdict,
        "source_from":"ACTUAL_EXECUTABLE_STATIC_GENERATOR_TEMPLATES",
        "previous_empirical_evidence_boundary":prior,
        "training_tasks":len(trial["train"]),
        "heldout_tasks":len(heldout),
        "heldout_verified_query_answers":validated_outputs,
        "training_candidate_strategies_per_family":
            {f:[x["strategy"] for x in trial["training_candidates"][f]]
             for f in FAMILIES},
        "training_candidates":trial["training_candidates"],
        "training_direct_and_strong_baselines":trial["training_baselines"],
        "exact_classical_budgeted_portfolio_selection":True,
        "frozen_plan":frozen_plan,
        "frozen_plan_sha256":freeze_hash,
        "selected_source_manifest":{
            f:{"strategy":t["strategy"],"sha256":t["source_sha256"]}
            for f,t in trial["frozen"].items()},
        "heldout_portfolio_ms":measured,
        "heldout_family_ms":by_family,
        "estimated_one_time_selected_tool_compile_verify_ms":
            round(proof_setup,6),
        "setup_cost_does_not_include_human_development":True,
        "observed_heldout_gain_vs_direct_fraction":round(performance_gain,6),
        "observed_heldout_gain_vs_strong_classical_fraction":
            round(versus_strong,6),
        "second_order_generated_verifier":{k:v for k,v in meta.items()
                                            if k!="source"},
        "second_order_tool_verifies_new_candidates_across_three_families":True,
        "second_order_causal_ablation_done":True,
        "second_order_research_discovery_compounding_confirmed":False,
        "resource_accounting":{
            "tool_generation_compile_and_oracle_verification_ms":round(
                proof_setup,6),
            "verification_cache_created_in_research_trial":True,
            "actual_future_research_episode_count":0,
            "separately_authenticated_external_tasks":0,
            "cost_of_not_investing_proved_on_live_open_world_tasks":False,
        },
        "gates":gates,
        "all_task_families_author_created":True,
        "training_source_selection_never_used_heldout":True,
        "general_superiority_over_classical":False,
        "automatically_installed_tools":False,
        "production_actions":0,
        "external_mathematical_prover_invoked_for_general_tools":False,
        "real_world_authority":False,
    }
    sources={
        "schema":"motif.research-tools-source-bundle.v1",
        "selected_tools":{f:t["source"] for f,t in trial["frozen"].items()},
        "selected_research_verifier_mode":prepared_verifier["choice"],
        "selected_sources_verified":{f:t["source_sha256"]
                                     for f,t in trial["frozen"].items()},
        "research_meta_tool":meta["source"],
        "research_meta_tool_sha256":meta["source_sha256"],
        "frozen_plan_sha256":freeze_hash,
        "production_write_approved":False,
        "independent_external_validation":False,
    }
    return packet,sources

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python experiments/legit017/benchmark.py [--emit]")
    report,source=run()
    if sys.argv[1:]:
        Path("/tmp/motif-legit017-research-trial.json").write_text(
            json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        Path("/tmp/motif-legit017-generated-tools.json").write_text(
            json.dumps(source,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "experiment":report["experiment"],
        "status":report["status"],
        "training_tasks":report["training_tasks"],
        "heldout_tasks":report["heldout_tasks"],
        "heldout_verified_query_answers":report["heldout_verified_query_answers"],
        "selected":report["frozen_plan"],
        "heldout_medians":{k:v["median_wall_ms"] for k,v in report[
            "heldout_portfolio_ms"].items()},
        "second_order_ablation":{
            k:report["second_order_generated_verifier"][k]
            for k in ("heldout_median_saving_vs_rechecking_ms",
                      "heldout_median_saving_vs_strong_classical_ms",
                      "no_cache_reference_calls","with_tool_reference_calls")
        },
        "gates":report["gates"],
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
