"""MOTIF-011: the Evidence Frontier — dependency-aware Bayesian witness ledger.

Ten repeated messages are not ten independent measurements. Preserve the
report graph, count only source roots as distinct likelihood factors, compare
an intentionally invalid naive-counting model, and retain contradictory roots.

All identities, source separations, sensor reliabilities, outcomes and world
truths are SIMULATED TEST FIXTURES, not authenticated people or measurements.
Hashes protect content integrity, not independence or honesty of witnesses.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"door-foundry-010"))
sys.path.insert(0,str(HERE.parent/"door-foundry-009"))
import world_model as prior_model
import decision
from world_model import HOLD, need, digest, read, stored

SCHEMA="motif011.provenance-report.v0"
ROOTS=("A","B","C","D")
FIELD="wall_extent"
ACCURACY="4/5"
IDS=prior_model.WORLD_IDS
SAFE_SOURCE="SYNTHETIC_SOURCE_GRAPH_UNATTESTED"
REPORT_FIELDS={"schema","sequence","report_id","origin_id","parent_report_id",
               "declared_source_id","claim_field","claim_value",
               "root_sensor_event","assumed_root_reliability",
               "claimed_independent_root","synthetic_only",
               "actual_human_witness","source_independence_verified",
               "real_effects_allowed","content_sha256"}

def event(n,origin,reported_value,parent=None):
    need(type(n) is int and 1<=n<=32 and origin in ROOTS and
         reported_value in ("partial","full"),
         "HOLD_UNKNOWN_SOURCE_GRAPH_EVENT")
    root=parent is None
    sensor=(prior_model.make_event(ROOTS.index(origin)+1,FIELD,reported_value,ACCURACY)
            if root else None)
    core={
       "schema":SCHEMA,"sequence":n,"report_id":f"R{n:03d}",
       "origin_id":origin,"parent_report_id":parent,
       "declared_source_id":"SIMULATED_SENSOR_"+origin,
       "claim_field":FIELD,"claim_value":reported_value,
       "root_sensor_event":sensor,
       "assumed_root_reliability":ACCURACY,
       "claimed_independent_root":root,"synthetic_only":SAFE_SOURCE,
       "actual_human_witness":False,
       "source_independence_verified":False,
       "real_effects_allowed":False,
    }
    return {**core,"content_sha256":digest(core)}

def fixture(truth):
    need(truth in IDS,"HOLD_UNKNOWN_TEST_TRUTH")
    actual=truth.split("_")[1].lower()
    wrong="full" if actual=="partial" else "partial"
    reports=[event(1,"A",wrong)]
    for n in range(2,8):
        reports.append(event(n,"A",wrong,f"R{n-1:03d}"))
    for n,origin in ((8,"B"),(9,"C"),(10,"D")):
        reports.append(event(n,origin,actual))
    return reports

def verify_graph(reports):
    """Reject malformed edges, invented sensor authority and false independences.

    This checks declared *structural* dependence only: two origins could still
    secretly share a real upstream source. No physical independence attested.
    """
    need(type(reports) is list and 1<=len(reports)<=32,
         "HOLD_UNBOUNDED_OR_EMPTY_SOURCE_GRAPH")
    seen={}
    roots={}
    output=[]
    for pos,r in enumerate(reports,1):
        need(type(r) is dict and set(r)==REPORT_FIELDS,
             "HOLD_PROVENANCE_REPORT_SHAPE")
        body=dict(r);checksum=body.pop("content_sha256")
        need(checksum==digest(body),"HOLD_CHANGED_REPORT_BYTES")
        need(r["schema"]==SCHEMA and type(r["sequence"]) is int and
             r["sequence"]==pos and r["report_id"]==f"R{pos:03d}" and
             r["report_id"] not in seen and r["origin_id"] in ROOTS and
             r["declared_source_id"]=="SIMULATED_SENSOR_"+r["origin_id"] and
             r["claim_field"]==FIELD and
             r["claim_value"] in ("partial","full") and
             r["assumed_root_reliability"]==ACCURACY and
             r["synthetic_only"]==SAFE_SOURCE and
             r["actual_human_witness"] is False and
             r["source_independence_verified"] is False and
             r["real_effects_allowed"] is False,
             "HOLD_UNSUPPORTED_PROVENANCE_AUTHORITY")
        origin=r["origin_id"]
        is_root=r["parent_report_id"] is None
        need(r["claimed_independent_root"] is is_root,
             "HOLD_RETRANSMISSION_CLAIMS_INDEPENDENCE")
        if is_root:
            need(origin not in roots,"HOLD_DUPLICATED_INDEPENDENT_ORIGIN")
            sensor=r["root_sensor_event"]
            need(type(sensor) is dict,"HOLD_ROOT_LACKS_SENSOR_RECORD")
            prior_model.verify_event(sensor,ROOTS.index(origin)+1)
            need(sensor["observed_attribute"]==FIELD and
                 sensor["simulated_sensor_output"]==r["claim_value"] and
                 sensor["assumed_conditional_accuracy"]==ACCURACY and
                 sensor["real_human_answer"] is False,
                 "HOLD_ROOT_SENSOR_DISAGREES_WITH_CLAIM")
            roots[origin]=r
        else:
            parent=seen.get(r["parent_report_id"])
            need(parent is not None and parent["origin_id"]==origin and
                 parent["declared_source_id"]==r["declared_source_id"] and
                 parent["claim_field"]==r["claim_field"] and
                 parent["claim_value"]==r["claim_value"] and
                 r["root_sensor_event"] is None and
                 origin in roots,
                 "HOLD_ORPHAN_CYCLE_CROSS_SOURCE_OR_MUTATED_COPY")
        seen[r["report_id"]]=r
        output.append({"origin":origin,"root":is_root,
             "parent":r["parent_report_id"],"claim":r["claim_value"]})
    need(len(roots)>=1,"HOLD_NO_ORIGINAL_SENSOR")
    contradiction={
      "independent_roots_contradict":len({r["claim_value"] for r in roots.values()})>1,
      "opposing_roots_preserved":[r["report_id"] for r in roots.values()],
      "actual_independence_attested":False
    }
    return roots,output,contradiction

def root_likelihood(e,w):
    sensor=e["root_sensor_event"]
    need(sensor is not None,"HOLD_NONROOT_USED_AS_NEW_INDEPENDENT_FACTOR")
    return prior_model.likelihood(sensor,w)

def source_posterior(roots,worlds):
    """Independent source-only batch control: no linked copies multiplied."""
    events=[r["root_sensor_event"] for r in roots.values()]
    return prior_model.independent_batch_posterior(prior_model.PRIORS,worlds,events)

def sum_attribute(weights,worlds,attribute,value):
    return sum(weights[w["id"]] for w in worlds if w[attribute]==value)

def replay(original_dir,truth,out,reports=None):
    out=Path(out)
    need(not out.exists(),"HOLD_REFUSE_LEDGER_OVERWRITE")
    original,worlds=prior_model.verify_original(original_dir)
    need(truth in IDS,"HOLD_INVALID_SYNTHETIC_TRUTH")
    if reports is None:reports=fixture(truth)
    roots,graph,conflicts=verify_graph(reports)
    # Each new declared independent root may update the belief at most once.
    collapsed=dict(prior_model.PRIORS)
    naive=dict(prior_model.PRIORS)
    previously_seen_roots={}
    current_parent=original["content_sha256"]
    history=[]
    copies=0
    for r in reports:
        old=dict(collapsed)
        is_root=r["parent_report_id"] is None
        if is_root:
            previously_seen_roots[r["origin_id"]]=r
            sensor=r["root_sensor_event"]
            collapsed=prior_model.increment(collapsed,worlds,sensor)
        else:
            copies+=1
            # Naive wrongly counts this identical upstream observation again.
            sensor=previously_seen_roots[r["origin_id"]]["root_sensor_event"]
        naive=prior_model.increment(naive,worlds,sensor)
        expected=source_posterior(previously_seen_roots,worlds)
        need(collapsed==expected,
             "HOLD_DEPENDENCY_COLLAPSE_DISAGREES_WITH_BATCH_CLASSICAL_BAYES")
        next_value,next_policy=decision.optimal(
            worlds,collapsed,decision.standard_costs(),2)
        body={
            "schema":"motif011.provenance-belief-step.v0",
            "sequence":r["sequence"],
            "previous_receipt_sha256":current_parent,
            "report_sha256":r["content_sha256"],
            "report":r,
            "source_origin_id":r["origin_id"],
            "dependency_parent":r["parent_report_id"],
            "contributed_independent_factor":is_root,
            "prior":stored(old),
            "posterior":stored(collapsed),
            "naive_as_if_independent_posterior":stored(naive),
            "independent_source_count":len(previously_seen_roots),
            "retransmission_count":copies,
            "next_question_proposed_but_unsent":next_policy.get("question_id"),
            "next_question_expected_loss":float(next_value),
            "only_structural_dependency_verified":True,
            "human_observations":0,
            "physical_actions":0
        }
        step={**body,"content_sha256":digest(body)}
        history.append(step)
        current_parent=step["content_sha256"]
    need(len(previously_seen_roots)==len(roots),
         "HOLD_SOURCE_GRAPH_DISAGREES_WITH_REPLAY")
    if reports==fixture(truth):
        need(len(roots)==4 and copies==6 and
             conflicts["independent_roots_contradict"],
             "HOLD_EXPECTED_RUMOR_AND_COUNTEREVIDENCE_NOT_RETAINED")
    initial=prior_model.PRIORS
    true_extent=truth.split("_")[1].lower()
    frozen=sum_attribute(initial,worlds,FIELD,true_extent)
    collapsed_score=sum_attribute(collapsed,worlds,FIELD,true_extent)
    naive_score=sum_attribute(naive,worlds,FIELD,true_extent)
    terminal=lambda p:prior_model.best_decision(p,worlds)
    baseline_action=terminal(initial)["action"]
    dependent_action=terminal(collapsed)["action"]
    naive_action=terminal(naive)["action"]
    true_world=next(w for w in worlds if w["id"]==truth)
    body={
       "schema":"motif011.evidence-provenance-replay.v0",
       "status":"SYNTHETIC_DEPENDENCY_AWARE_BELIEF_REVISION_HELD",
       "original_009_source_sha256":original["content_sha256"],
       "original_png_world_hashes":{w["id"]:w["start_png_sha256"] for w in worlds},
       "synthetic_truth_known_only_to_test_scorer":truth,
       "source_graph":graph,
       "conflict_ledger":conflicts,
       "original_priors":stored(initial),
       "dependency_grouped_posterior":stored(collapsed),
       "naive_repeated_report_posterior":stored(naive),
       "steps":history,
       "last_evidence_chain_sha256":current_parent,
       "reports_seen":len(reports),
       "independent_roots_count":len(roots),
       "derived_retransmissions_ignored_as_new_likelihoods":copies,
       "scoring":{
          "frozen_true_extent_probability":float(frozen),
          "grouped_true_extent_probability":float(collapsed_score),
          "naive_true_extent_probability":float(naive_score),
          "frozen_brier":float((1-frozen)**2),
          "grouped_brier":float((1-collapsed_score)**2),
          "naive_brier":float((1-naive_score)**2),
          "frozen_log_loss":-math.log(float(frozen)),
          "grouped_log_loss":-math.log(float(collapsed_score)),
          "naive_log_loss":-math.log(float(naive_score)),
          "illustrates_a_designed_copy_attack_not_real_world_robustness":True
       },
       "decision":{
          "frozen":baseline_action,"source_grouped":dependent_action,
          "naive_copy_counterexample":naive_action,
          "frozen_simulated_regret":float(decision.loss(baseline_action,true_world)),
          "grouped_simulated_regret":float(decision.loss(dependent_action,true_world)),
          "naive_simulated_regret":float(decision.loss(naive_action,true_world)),
          "real_actions_executed":False
       },
       "assumptions":{
          "reliability_not_estimated_from_real_data":True,
          "source_roots_declared_by_simulator_not_authenticated":True,
          "shared_unreported_upstream_sources_can_escape_detector":True,
          "root_sensor_errors_assumed_independent_conditional_on_world":True,
          "unmodeled_worlds_possible":True
       },
       "authority":{
          "root_source_attestations_verified":False,
          "real_human_reports_received":0,"external_api_calls":0,
          "T5_calls":0,"real_world_actions":0,
          "automatic_repair":False,"automatic_canon_admission":False
       }
    }
    body["content_sha256"]=digest(body)
    out.mkdir(parents=True)
    for row in history:
        (out/f"step-{row['sequence']:02d}.json").write_text(
          json.dumps(row,indent=2)+"\n")
    (out/"replay.json").write_text(json.dumps(body,indent=2)+"\n")
    return body

def benchmark(original_dir,out):
    out=Path(out)
    need(not out.exists(),"HOLD_NO_BENCHMARK_OVERWRITE")
    out.mkdir(parents=True)
    cases=[]
    for truth in IDS:
        result=replay(original_dir,truth,out/truth)
        cases.append({
          "fixture_true_world":truth,
          "original_source_sha256":result["original_009_source_sha256"],
          "grouped_brier":result["scoring"]["grouped_brier"],
          "naive_brier":result["scoring"]["naive_brier"],
          "frozen_brier":result["scoring"]["frozen_brier"],
          "grouped_log_loss":result["scoring"]["grouped_log_loss"],
          "naive_log_loss":result["scoring"]["naive_log_loss"],
          "grouped_decision_regret":result["decision"]["grouped_simulated_regret"],
          "naive_decision_regret":result["decision"]["naive_simulated_regret"],
          "independence_declared_not_attested":True
        })
    average=lambda k:sum(x[k] for x in cases)/len(cases)
    result={
      "schema":"motif011.source-dependence-benchmark.v0",
      "status":"HOLD_SYNTHETIC_REPORT_GRAPH_DEPENDENCY_TESTED",
      "cases":cases,
      "mean_grouped_brier":average("grouped_brier"),
      "mean_naive_brier":average("naive_brier"),
      "mean_frozen_brier":average("frozen_brier"),
      "mean_grouped_decision_regret":average("grouped_decision_regret"),
      "mean_naive_decision_regret":average("naive_decision_regret"),
      "grouped_beats_naive_in_all_designed_cases":
         all(x["grouped_brier"]<x["naive_brier"] for x in cases),
      "matched_classical_root_collapse_baseline_exactly_equal":True,
      "not_a_claim_of_independent_witness_authentication":True,
      "not_generalized_real_world_accuracy":True,
      "external_actions":0
    }
    result["content_sha256"]=digest(result)
    (out/"benchmark.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    try:
        result=benchmark(args.question_dir,args.out)
        print(json.dumps({"status":result["status"],
          "mean_grouped_brier":result["mean_grouped_brier"],
          "mean_naive_brier":result["mean_naive_brier"],
          "mean_grouped_regret":result["mean_grouped_decision_regret"],
          "mean_naive_regret":result["mean_naive_decision_regret"],
          "test_cases":len(result["cases"]),"real_effects":0},indent=2))
    except (HOLD,ValueError,KeyError) as exc:
        print(json.dumps({"stage":"HOLD","reason":str(exc)}))
        raise SystemExit(1)

if __name__=="__main__":main()
