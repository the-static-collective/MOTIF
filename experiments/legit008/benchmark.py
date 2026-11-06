"""LEGIT-008 frozen synthetic metareasoning benchmark.

A genuine performance target is measured under an explicit source model:
can an automatically selected deeper REASONING PROCEDURE improve decisions
under fixed compute price versus fixed one-step reasoning?

It cannot surpass exact mathematical truth or exact depth-2 classical DP.
The strongest baseline should match the proposed two-step planner exactly.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit007"))
from provenance import route as legacy_route
from simulator import trial,demonstration,N
from planner import plan,rollout,decide
from strong_reference import exhaustive,simulate
from custody import seal_simulated,guarded
from synthesis import synthesize,selected_plan,COMPUTE_PRICE_PER_STATE,TRAIN_SAMPLES

def _average(rows):
    if not rows: return None
    return round(sum(rows)/len(rows),8)

def benchmark():
    if N!=320 or TRAIN_SAMPLES!=160:
        raise AssertionError("Frozen evaluation design changed")
    # Only public packet dictionaries passed to the strategy learner.
    train=[trial(i).public for i in range(TRAIN_SAMPLES)]
    strategy=synthesize(train)
    report=defaultdict(lambda:defaultdict(list))
    by_family=defaultdict(lambda:defaultdict(list))
    count=defaultdict(int)
    examples=[]
    for index in range(TRAIN_SAMPLES,N):
        tr=trial(index)
        packet=tr.public
        pins=seal_simulated(packet)  # Synthetic evaluator's separate anchor.
        identity=guarded(packet,pins)
        if identity["status"]!="PINNED_RECORD_INTEGRITY_ONLY":
            raise AssertionError("Simulated source custody drift")
        old=legacy_route(packet)
        a1=plan(old["posterior_true_given_declared_calibration"],
                packet["audits"],1)
        # Use full unrounded conditional posterior for all policies.
        from provenance import posterior
        p=posterior(packet)["posterior"]
        one=plan(p,packet["audits"],1)
        two=decide(packet,pins,2)
        ref=exhaustive(packet)
        learned=selected_plan(packet,strategy)
        if abs(ref["expected_risk"]-two["expected_research_loss"])>1e-9:
            raise AssertionError("Failed independent exact two-step Bellman check")
        if abs(one["tree"]["expected_risk"]-
               old["selected_expected_total_risk"])>1e-8:
            raise AssertionError("Failed independent previous one-step reference")
        if two["expected_research_loss"]>one["tree"]["expected_risk"]+1e-9:
            raise AssertionError("Deeper optimum cannot have larger Bayes risk")
        if len(packet["audits"])<2:
            raise AssertionError("Missing future branching audit options")
        plan_map={
            "fixed_one_step":one,
            "fixed_two_step":two,
            "synthesized_meta_recipe":learned,
        }
        for name,obj in plan_map.items():
            tree=(obj["policy"] if name=="fixed_two_step" else
                  obj["plan"]["tree"] if name=="synthesized_meta_recipe"
                  else obj["tree"])
            states=(obj["states_visited"] if name=="fixed_two_step" else
                    obj["plan"]["states_visited"] if name=="synthesized_meta_recipe"
                    else obj["states_visited"])
            observed=rollout(tree,tr.audit_outcomes,tr.truth)
            risk=tree["expected_risk"]
            report[name]["realized_loss"].append(observed["loss"])
            report[name]["conditional_expected_risk"].append(risk)
            report[name]["states"].append(states)
            report[name]["objective_with_declared_compute"].append(
                risk+COMPUTE_PRICE_PER_STATE*states)
            report[name]["number_of_audits_simulated"].append(
                observed["audits_simulated"])
            by_family[tr.family][name].append(observed["loss"])
            if name=="synthesized_meta_recipe":
                count["two_step_selected"]+=int(learned["depth"]==2)
        exact_realized,exact_audits=simulate(
            ref["root"],tr.audit_outcomes,tr.truth,
            {a["id"]:a["cost"] for a in packet["audits"]})
        report["independent_exact_classical_two_step"]["realized_loss"].append(exact_realized)
        report["independent_exact_classical_two_step"]["conditional_expected_risk"].append(
            ref["expected_risk"])
        if abs(exact_realized-rollout(two["policy"],
                                      tr.audit_outcomes,tr.truth)["loss"])>1e-10:
            raise AssertionError("Synthetic hidden-world rollout disagrees")
        if index in (160,161,163,201,257,319):
            examples.append({
                "case":index,"family":tr.family,
                "one_step_expected":one["tree"]["expected_risk"],
                "two_step_expected":two["expected_research_loss"],
                "two_step_root_action":two["policy"]["action"],
                "meta_selected_depth":learned["depth"],
                "simulated_true_world_excluded_from_policy":True,
            })

    summary={name:{k+"_mean":_average(v) for k,v in sorted(metrics.items())}
             for name,metrics in sorted(report.items())}
    demo=demonstration()
    sealed=seal_simulated(demo)
    outcome=decide(demo,sealed,2)
    return {
        "experiment":"MOTIF-LEGIT-008",
        "train_public_packets":TRAIN_SAMPLES,
        "heldout_cases":N-TRAIN_SAMPLES,
        "dataset_authorship":"ASSISTANT_GENERATED_SYNTHETIC_NOT_EXTERNAL",
        "trained_strategy":strategy,
        "score_policy":"ONE_UNIT_WRONG_PREDICTION;_POINT27_ABSTENTION;AUDIT_PRICE",
        "declared_compute_price_per_search_state":COMPUTE_PRICE_PER_STATE,
        "policies":summary,
        "per_family_realized_loss":{
            family:{name:_average(values) for name,values in sorted(policies.items())}
            for family,policies in sorted(by_family.items())},
        "selected_meta_two_step_cases":count["two_step_selected"],
        "demonstration_source_manifest":{
            "root_count":outcome["custody"]["root_count"],
            "copy_nodes":outcome["custody"]["copy_nodes"],
            "integrity_only":outcome["custody"]["status"],
            "actual_identity_authenticated":False,
        },
        "source_pin_trust_externally_verified":False,
        "strongest_classical_baseline_has_same_proof_power":True,
        "audits_dispatched":0,
        "automated_code_admission":False,
        "claim_to_surpass_classical_mathematics":False,
        "status":"RESEARCH_HOLD",
        "example_heldout_receipts":examples,
    }

if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
