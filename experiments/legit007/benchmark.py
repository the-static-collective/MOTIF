"""LEGIT-007: matched 320-case synthetic witness provenance experiment.

The simulator owns true world and audit outcomes. The router sees only
public graph, independently sampled synthetic calibration, and audit design.
Compare naïve report vote, distinct-origin vote, calibrated no-audit Bayes,
source-aware audit router, and independent exact classical Bayes+VoI.
The latter must tie; no novel inference superiority is claimed.
"""
from __future__ import annotations

from collections import defaultdict
import json

from provenance import ABSTENTION_LOSS, posterior, route
from exact_reference import reference
from simulator import N, SEED, demonstration, trial

def vote(claims):
    positives=sum(claims)
    negatives=len(claims)-positives
    if positives==negatives:
        return "ABSTAIN"
    return "PREDICT_TRUE" if positives>negatives else "PREDICT_FALSE"

def realized(action,truth):
    if action=="ABSTAIN":
        return ABSTENTION_LOSS
    if action not in ("PREDICT_TRUE","PREDICT_FALSE"):
        raise ValueError("Unknown terminal action")
    return float((action=="PREDICT_TRUE")!=truth)

def evaluate_trial(t):
    packet=t.public
    planned=route(packet)
    classical=reference(packet)
    sources=posterior(packet)
    if planned["status"]=="HOLD_INPUT":
        raise AssertionError("Simulator produced invalid graph")
    if abs(planned["posterior_true_given_declared_calibration"]-classical["p_true"])>1e-8:
        raise AssertionError("Conditional Bayesian source posterior mismatch")
    if planned["decision"]!=classical["action"]:
        raise AssertionError("Strong classical reference disagrees on optimal action")
    if abs(planned["selected_expected_total_risk"]-classical["loss"])>1e-8:
        raise AssertionError("Expected source/audit risk differs")

    raw_majority=vote([n["claim"] for n in packet["nodes"]])
    root_majority=vote([claim for claim,_ in sources["origin_signature"].values()])
    no_audit=planned["terminal_without_audit"]
    losses={
        "raw_report_majority":realized(raw_majority,t.truth),
        "distinct_root_majority":realized(root_majority,t.truth),
        "calibrated_root_bayes_terminal":realized(no_audit,t.truth),
    }
    if planned["decision"]=="ASK_SYNTHETIC_AUDIT":
        query=planned["proposal"]["audit_id"]
        measured=t.audit_outcomes[query]
        price=next(a["cost"] for a in packet["audits"] if a["id"]==query)
        planned_cont=next(c for c in planned["proposal"]["possible_answers"]
                          if c["answer"] is measured)
        expected_p,exact_decision=classical["outcomes"][measured]
        if (planned_cont["terminal_action"]!=exact_decision or
                abs(planned_cont["updated_probability"]-expected_p)>1e-8):
            raise AssertionError("Audit contingency mismatch")
        losses["lineage_router_with_unsent_audit"]=price+realized(
            planned_cont["terminal_action"],t.truth)
        losses["independent_classical_exact_bayes_voi"]=price+realized(
            exact_decision,t.truth)
    else:
        losses["lineage_router_with_unsent_audit"]=realized(planned["decision"],t.truth)
        losses["independent_classical_exact_bayes_voi"]=realized(classical["action"],t.truth)
    if abs(losses["lineage_router_with_unsent_audit"]-
           losses["independent_classical_exact_bayes_voi"])>1e-12:
        raise AssertionError("False advantage claimed over identical Bayes reference")
    return {
        "family":t.family,"loss":losses,
        "requested_audit":planned["proposal"]["audit_id"] if planned["proposal"] else None,
        "naive_decision":raw_majority,"dedup_decision":root_majority,
        "root_count":planned["distinct_declared_upstream_origins"],
        "copy_or_echo_count":planned["duplicate_or_forwarded_report_nodes"],
        "classical_exact_tie":True,
        "correct_world_state_revealed_to_router":False,
    }

def run():
    scores=defaultdict(list)
    buckets=defaultdict(lambda:defaultdict(list))
    audits=defaultdict(int)
    examples=[]
    for i in range(N):
        report=evaluate_trial(trial(i))
        for name,value in report["loss"].items():
            scores[name].append(value)
            buckets[report["family"]][name].append(value)
        if report["requested_audit"]:
            audits[report["requested_audit"]]+=1
        if i in (0,17,64,128):
            examples.append({"trial_id":i,"family":report["family"],
                             "audit_proposed":report["requested_audit"],
                             "naive":report["naive_decision"],
                             "dedup":report["dedup_decision"],
                             "root_count":report["root_count"],
                             "copy_count":report["copy_or_echo_count"],
                             "realized_losses":report["loss"]})
    metrics={k:{"mean_realized_loss":round(sum(v)/len(v),6),
                "sum_realized_loss":round(sum(v),6),"trials":len(v)}
             for k,v in sorted(scores.items())}
    by_family={family:{name:round(sum(vals)/len(vals),6)
                       for name,vals in sorted(subset.items())}
               for family,subset in sorted(buckets.items())}
    illustrative=demonstration()
    result=route(illustrative)
    return {
        "experiment":"MOTIF-LEGIT-007",
        "source":"ASSISTANT_AUTHORED_SYNTHETIC_ORACLE_NOT_INDEPENDENT",
        "seed":SEED,"cases":N,
        "separate_calibration_partition":True,
        "source_dependent_forwardings":True,
        "source_identity_verified":False,
        "calibration_grounded_only_in_simulation":True,
        "strong_control":"INDEPENDENT_EXACT_BAYES_PLUS_ONE_STEP_VOI",
        "policies":metrics,"family_mean_losses":by_family,
        "audit_proposals_unexecuted_counts":dict(sorted(audits.items())),
        "demonstration_nine_reports_one_origin":{
            "total_reports":len(illustrative["nodes"]),
            "distinct_declared_origins":result["distinct_declared_upstream_origins"],
            "forwarded_or_duplicate":result["duplicate_or_forwarded_report_nodes"],
            "source_contributions":result["source_contributions"],
            "naive_vote":vote([n["claim"] for n in illustrative["nodes"]]),
            "distinct_origin_vote":vote([n["claim"] for n in illustrative["nodes"]
                                         if n["kind"]=="ROOT"]),
            "posterior_conditional":result["posterior_true_given_declared_calibration"],
            "proposed_action":result["decision"],"no_actual_truth_claim":True},
        "declared_real_world_authority":False,
        "external_actions_taken":False,
        "classical_bayes_superiority_claim":False,
        "status":"RESEARCH_HOLD","example_receipts":examples,
    }

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
