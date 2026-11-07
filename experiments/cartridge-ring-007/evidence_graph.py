"""RING-007: inspected-synthetic many-to-many affordance evidence, not a new truth.

Observed conditional hyperedges link (source experiment, old policy, chosen
review strategy) -> (safe-coverage gain, risk hold, unresolved question,
additional native-source probe cost). The same edge deliberately exposes
benefits and costs; no synthetic observation grants outside-world authority.
"""
from __future__ import annotations

from hashlib import sha256
import argparse
import json
from pathlib import Path

SCHEMA="motif.ring007.investigation-evidence-hypergraph.v1"
SOURCE="motif.ring007.safe-investigation-benchmark.v1"

class HOLD(ValueError):
    pass


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def check(trial):
    if (not isinstance(trial,dict) or trial.get("schema")!=SOURCE
            or trial.get("receipt_sha256")!=digest({
                k:v for k,v in trial.items() if k!="receipt_sha256"})
            or trial.get("status")!=
            "HISTORICAL_ERROR_TRAINED_THREE_WAY_REVIEW_EVALUATED_ON_NEW_SOURCE_CASES"
            or trial.get("authority")!="NONE"
            or trial.get("no_external_effects") is not True
            or trial.get("newly_installed_arbitrary_branch_methods")!=0
            or trial.get("synthetic_hidden_labels_are_author_defined") is not True):
        raise HOLD("Unreviewed or altered synthetic source trial")
    selection=trial.get("selected_investigation_strategy")
    if (not isinstance(selection,dict) or selection.get("selected")!="TRIAGE"
            or selection.get("receipt_sha256")!=digest({
                k:v for k,v in selection.items() if k!="receipt_sha256"})):
        raise HOLD("Missing frozen selected source method strategy")
    families=trial.get("unseen_families")
    if not isinstance(families,list) or len(families)!=2:
        raise HOLD("Expected exactly two separate authored case families")
    seen=set()
    for family in families:
        packet=family.get("public_source_packet_sha256")
        if type(packet) is not str or len(packet)!=64 or packet in seen:
            raise HOLD("Duplicate or missing source packet")
        seen.add(packet)
        blanket=family.get("blanket_novelty_guard")
        review=family.get("reviewed_investigation")
        per_case=family.get("native_case_witnesses")
        if (not isinstance(per_case,list) or len(per_case)!=32
                or not isinstance(blanket,dict) or not isinstance(review,dict)
                or family.get("expected_labels_were_not_mounted") is not True
                or type(family.get("native_original_language_hypotheses")) is not int):
            raise HOLD("Unverified independent source native evidence")
        observed_unsafe=sum(x["unsafe_or_invalid"] and x["decision"]!="HOLD"
                            for x in per_case)
        observed_benign=sum(not x["unsafe_or_invalid"] and x["decision"]!="HOLD"
                            for x in per_case)
        observed_calls=sum(x["native_calls"] for x in per_case)
        if (observed_unsafe!=review["unsafe_or_invalid_decisive_approvals"]
                or observed_benign!=review["safe_positive_decisive_coverage"]
                or observed_calls!=review["native_method_calls"]
                or family.get("investigation_source_native_calls")<0):
            raise HOLD("Case-level source witness summary does not reconcile")
    return families


def build(trial):
    groups=check(trial)
    old="router:"+trial["frozen_policy"]
    strategy="review:"+trial["selected_investigation_strategy"]["receipt_sha256"]
    vertices=[
        {"id":old,"type":"PINNED_PREVIOUS_SOURCE_ROUTER"},
        {"id":strategy,"type":"TRAINING_ERROR_SELECTED_REVIEW_STRATEGY",
         "kind":"EXPLICIT_BOUNDED_FRAMES_NOT_UNRESTRICTED_SEMANTIC_LEARNING"},
    ]
    edges=[]
    gains=[]
    for group in groups:
        source="trial:"+group["public_source_packet_sha256"]
        vertices.append({
            "id":source,"type":"AUTHOR_GENERATED_UNSEEN_RELATIVE_TO_SOURCE",
            "family":group["family"],
            "not_independently_human_annotated":True,
        })
        b=group["blanket_novelty_guard"]
        r=group["reviewed_investigation"]
        gained=r["safe_positive_decisive_coverage"]-b[
            "safe_positive_decisive_coverage"]
        if gained<0:
            raise HOLD("Review lost benign coverage relative to blanket")
        gains.append(gained)
        edges.append({
            "id":"observed:triage:"+group["family"],
            "kind":"CONDITIONAL_SYNTHETIC_MULTI_HEAD_EVIDENCE",
            "tails":[old,strategy,source],
            "heads":["outcome:additional_benign_decisions",
                     "outcome:unsafe_decisions_held",
                     "outcome:unresolved_queries_preserved",
                     "cost:additional_source_language_review_calls"],
            "recovered_benign_decisive_count":gained,
            "unsafe_or_invalid_decisive_count":r[
                "unsafe_or_invalid_decisive_approvals"],
            "blanket_benign_decisive_count":b[
                "safe_positive_decisive_coverage"],
            "review_benign_decisive_count":r[
                "safe_positive_decisive_coverage"],
            "raw_language_source_probes":group[
                "native_original_language_hypotheses"],
            "native_source_invocations_total":r["native_method_calls"],
            "source_world":"AUTHOR_GENERATED_SCOPE_ONLY",
            "causal_generalization_to_new_language":"UNPROVEN",
        })
    result={
        "schema":SCHEMA,
        "source_experiment_receipt_sha256":trial["receipt_sha256"],
        "source_method_pins":trial["original_source_pins"],
        "vertices":vertices,
        "hyperedges":edges,
        "total_additional_benign_decisive_answers":sum(gains),
        "all_observed_reviews_held_invalid_or_unsafe":all(e[
            "unsafe_or_invalid_decisive_count"]==0 for e in edges),
        "author_created_utterance_families_not_independent_heldouts":True,
        "new_real_world_affordance_edges_promoted":0,
        "new_executable_branch_admissions":0,
        "original_method_code_rewritten":False,
        "authority":"NONE",
    }
    result["receipt_sha256"]=digest(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trial",required=True,type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        x=build(json.loads(args.trial.read_text()))
        payload=json.dumps(x,sort_keys=True,indent=2)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(payload)
        print(json.dumps({"status":"SOURCE_BOUND_SYNTHETIC_HYPEREDGES",
            "edges":len(x["hyperedges"]),
            "extra_benign_decisive":x["total_additional_benign_decisive_answers"],
            "receipt_sha256":x["receipt_sha256"]},sort_keys=True))
    except HOLD as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
