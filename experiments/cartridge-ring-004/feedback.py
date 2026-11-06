"""Evidence-gated RING-003 hypergraph feedback from shared-world RING-004 trials.

A measured *synthetic outcome* is not a verified general-purpose affordance.
Each edge explicitly names its conditional ablation and source receipts. The
graph weights of future real-world actions and the installed executor registry
are NEVER mutated by this module.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import comparator

SOURCE_NATIVE_TRIAD=(
    "geometry.procedure-repair","thought.language-dev","reason.proof-objection"
)
CONTROLS={
    "all_three_native": (SOURCE_NATIVE_TRIAD, "native_source_methods"),
    "all_three_without_tiny_model": (SOURCE_NATIVE_TRIAD, "native_no_tiny_classifier"),
    "reason_only_raw_witnesses": (
        ("reason.proof-objection",),"native_with_classical_raw_measurement_adapter"),
    "geometry_plus_reason_no_language": (
        ("geometry.procedure-repair","reason.proof-objection"),"native_no_language_guard"),
    "language_plus_reason_raw": (
        ("thought.language-dev","reason.proof-objection"),"native_classical_raw_measurement"),
    "geometry_only_no_graph": (
        ("geometry.procedure-repair",),"native_no_graph_proof"),
    "language_only_no_sensor_or_graph": (
        ("thought.language-dev",),"native_no_measurement_or_graph"),
    "language_plus_geometry_classical_graph": (
        ("thought.language-dev","geometry.procedure-repair"),"classical_graph_substitute"),
    "classical_raw_record_parity": (
        (),"fully_classical_no_dedup_raw"),
    "strong_classical_dedup_and_bfs": (
        (),"strong_complete_classical_baseline"),
}

class HOLD(ValueError):
    pass


def _hash(doc):
    return sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def validate(report):
    if not isinstance(report,dict) or report.get("schema")!=comparator.SCHEMA:
        raise HOLD("Missing common-world trial schema")
    checksum=report.get("receipt_sha256")
    if checksum!=_hash({k:v for k,v in report.items() if k!="receipt_sha256"}):
        raise HOLD("Altered trial receipt")
    if (report.get("status")!="SOURCE_NATIVE_COMMON_WORLD_SYNTHETIC_EVALUATION"
            or report.get("independent_human_labeled_real_data") is not False
            or report.get("synthetic_author_generated_fixture") is not True
            or report.get("actual_independent_native_task_outputs_compared") is not True
            or report.get("training_labels_not_passed_to_native_container") is not True
            or report.get("external_action_executed") is not False
            or report.get("real_world_authority") is not False):
        raise HOLD("Unpermitted claim or unbound measurement")
    pins={c.id:c.commit for c in comparator.triad.ADAPTERS}
    if report.get("method_source_pins")!=pins:
        raise HOLD("Experiment source pins do not match admitted native methods")
    cases=report.get("per_case")
    count=report.get("count")
    if (type(count) is not int or not 1<=count<=48
            or not isinstance(cases,list) or len(cases)!=count
            or not isinstance(report.get("method_results"),dict)
            or set(report["method_results"])!=set(CONTROLS)
            or type(report.get("source_packet_sha256")) is not str):
        raise HOLD("Malformed experiment population")
    found=set()
    sums={k:{"correct":0,"wrong_decisive":0,"abstained":0,
             "correct_hold":0,"coverage":0} for k in CONTROLS}
    for case in cases:
        cid=case.get("case_id")
        expect=case.get("hidden_expected_scoring_label")
        preds=case.get("results")
        if (type(cid) is not str or cid in found
                or expect not in ("HOLD","PROVED_REACHABLE","PROVED_UNREACHABLE")
                or not isinstance(preds,dict) or set(preds)!=set(CONTROLS)
                or case.get("native_source_methods_on_same_case")!=[
                    "GEOM-013.Revision.measure",
                    "THOUGHT-014.LanguageSpace.explore",
                    "REASON-006.run_council"]):
            raise HOLD("Unverifiable or repeated case witness")
        found.add(cid)
        for method,pred in preds.items():
            if pred not in ("HOLD","PROVED_REACHABLE","PROVED_UNREACHABLE"):
                raise HOLD("Unexpected control conclusion")
            v=sums[method]
            if pred==expect:v["correct"]+=1
            elif pred=="HOLD":v["abstained"]+=1
            else:v["wrong_decisive"]+=1
            if pred!="HOLD":v["coverage"]+=1
            if pred==expect=="HOLD":v["correct_hold"]+=1
    if sums!=report["method_results"]:
        raise HOLD("Summary disagrees with exact case witnesses")
    if sums["all_three_native"]["correct"]>sums[
            "strong_classical_dedup_and_bfs"]["correct"]:
        raise HOLD("Unreviewed claim of surpassing strong classical control")
    return sums


def feedback(reports):
    if not isinstance(reports,(list,tuple)) or not 1<=len(reports)<=10:
        raise HOLD("Expected 1–10 audited common-world trials")
    observed=set()
    for r in reports:
        validate(r)
        packet=r["source_packet_sha256"]
        if packet in observed:
            raise HOLD("Duplicate evidence packet would artificially increase support")
        observed.add(packet)
    total=sum(r["count"] for r in reports)
    outcome={}
    for name in CONTROLS:
        outcome[name]={k:sum(r["method_results"][name][k] for r in reports)
                       for k in ("correct","wrong_decisive","abstained",
                                 "correct_hold","coverage")}
    primary=outcome["all_three_native"]
    deltas={
        name:{
            "paired_correct_count_difference":primary["correct"]-outcome[name]["correct"],
            "paired_wrong_decisive_difference":primary["wrong_decisive"]-
                                                outcome[name]["wrong_decisive"],
            "same_cases_and_labels":True,
            "not_independent_causal_attribution":True,
        }
        for name in CONTROLS if name!="all_three_native"
    }
    witness_nodes=[
        {"id":"trial:"+r["source_packet_sha256"][:20],
         "type":"SYNTHETIC_SHARED_WORLD_CASE_PACKET",
         "source_receipt_sha256":r["receipt_sha256"],
         "case_count":r["count"],
         "heldout_only_relative_to_original_native_training":True,
         "truth_from_author_defined_simulator_not_external_source":True,
        }
        for r in reports
    ]
    measured_edges=[]
    for name,(methods,mechanism) in CONTROLS.items():
        measured_edges.append({
            "id":"observed-conditional:"+name,
            "tails":["trial:"+r["source_packet_sha256"][:20] for r in reports]
                    +["method:"+m for m in methods],
            "heads":["outcome:"+name],
            "kind":"OBSERVED_SYNTHETIC_CONDITIONAL_ABLATION",
            "mechanism":mechanism,
            "outcome":outcome[name],
            "total_cases":total,
            "meaning":"authored-simulator outcome only, not a general ability guarantee",
            "source_owned_operators_in_subsets_are_only_those_listed":True,
            "external_actions_authorized":False,
        })
    result={
        "schema":"motif.hypergraph-shared-evidence-feedback.v1",
        "world":"AUTHORED_SYNTHETIC_ONLY",
        "source_pins":{c.id:c.commit for c in comparator.triad.ADAPTERS},
        "tested_case_count":total,
        "independent_seed_packets":len(reports),
        "vertices":witness_nodes,
        "hyperedges":measured_edges,
        "paired_differences_vs_full_native":deltas,
        "strong_classical_baseline_matches_or_exceeds_full_native": (
            outcome["strong_classical_dedup_and_bfs"]["correct"]>=primary["correct"]),
        "simple_language_plus_geometry_classical_substitute_matches_or_exceeds": (
            outcome["language_plus_geometry_classical_graph"]["correct"]>=primary["correct"]),
        "verified_real_world_affordance_edges_added":0,
        "installed_executable_adapters_added":0,
        "unseen_natural_language_generalization":"UNTESTED",
        "causal_interaction_strength":"NOT_IDENTIFIED_FROM_THIS_SMALL_SYNTHETIC_DESIGN",
        "source_model_self_training_did_not_see_these_holdout_labels":True,
        "authority":"NONE",
    }
    result["receipt_sha256"]=_hash(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trials",type=Path,nargs="+",required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        reports=[json.loads(x.read_text()) for x in args.trials]
        report=feedback(reports)
        data=json.dumps(report,indent=2,sort_keys=True)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(data)
            print(json.dumps({"tested_cases":report["tested_case_count"],
                 "native_minus_classical":report[
                    "paired_differences_vs_full_native"][
                        "strong_classical_dedup_and_bfs"][
                            "paired_correct_count_difference"],
                 "receipt":report["receipt_sha256"]},sort_keys=True))
        else:
            print(data,end="")
    except HOLD as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
