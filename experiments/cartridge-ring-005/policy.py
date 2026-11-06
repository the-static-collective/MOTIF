"""RING-005: freeze a contextual cartridge router from PRIOR shared-world evidence.

This is a bounded learning experiment, not a trained LLM or independently
generalized intelligence. The learner only sees previously scored authored
RING-004 records. It cannot see any evaluation packet, evaluation labels,
or future benchmark outcomes when it freezes a candidate policy.

Source-owned methods remain pinned RING-004 / RING-002 adapters. The learned
policy is data-only; no code generation, arbitrary branch execution or
permission escalation.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
import re
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-004"))
import comparator, feedback

SCHEMA="motif.ring005.contextual-policy.v1"
MIN_SUPPORT=2
CONTENTS=frozenset({"HOLD","CUT","RAW","REPAIR","PROOF"})
METHODS={
    "HOLD":"PRECHECK_HOLD_NO_NATIVE",
    "CUT":"STATIC_GATE_CUT_NO_NATIVE",
    "RAW":"SOURCE_LANGUAGE_AND_RAW_MEASUREMENT",
    "REPAIR":"SOURCE_LANGUAGE_AND_REPAIRED_MEASUREMENT",
    "PROOF":"SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL",
}
# Per-case declared operation budgets are explicitly NOT wall-clock measurements.
PROXY_CALL_COST={"HOLD":0,"CUT":0,"RAW":2,"REPAIR":2,"PROOF":3}
GOOD=frozenset(("PROVED_REACHABLE","PROVED_UNREACHABLE","HOLD"))
EFFECT=re.compile(r"\b(?:deploy|delete|execute|merge|email|send|contact|publish|dispatch|push|wire money|grant permission)\b",re.I)


class HOLD(ValueError):
    pass


def canonical(doc):
    return sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),
                   allow_nan=False).encode()).hexdigest()


def proof_requested(case):
    """Independent task requirement, fixed BEFORE learning or test outcomes."""
    cid=case.get("id")
    if type(cid) is not str or not re.fullmatch(r"heldout-[0-9]{3}",cid):
        raise HOLD("Invalid task identity")
    return int(cid.rsplit("-",1)[-1])%7==0


def inspect(case):
    """Only PUBLIC input characteristics; never the withheld answer.

    The preflight semantics mirror the fully documented fictional input
    protocol. This does not authenticate event identifiers or user meaning.
    """
    if (not isinstance(case,dict)
            or set(case)!={"id","gate_open","utterance","selected_pair","records","scope"}
            or type(case["gate_open"]) is not bool
            or type(case["utterance"]) is not str
            or len(case["utterance"])>320
            or case["scope"]!="synthetic:observer-a@cut-12:decoder-A"
            or case["selected_pair"]!=["m-route-start","m-route-end"]):
        raise HOLD("Malformed synthetic public case")
    label_guard=bool(EFFECT.search(case["utterance"]))
    rows=case["records"]
    if rows is not None and (not isinstance(rows,list) or len(rows)>300):
        raise HOLD("Oversized or malformed synthetic trace")
    if rows is None:
        return {"context":"HOLD","reason":"MISSING_TRACE","need_proof":proof_requested(case)}
    seen={}
    duplicated=False
    bad_id=False
    for row in rows:
        if (not isinstance(row,dict) or set(row)!={"tick","channel","event_id"}
                or type(row["tick"]) is not int or not 0<=row["tick"]<8
                or type(row["channel"]) is not str
                or row["channel"] not in ("a","b","noise")
                or (row["event_id"] is not None
                    and (type(row["event_id"]) is not str or len(row["event_id"])>128))):
            raise HOLD("Malformed recorded event")
        if row["channel"] not in ("a","b"):
            continue
        eid=row["event_id"]
        if eid is None:
            bad_id=True
            continue
        owner=(row["channel"],row["tick"])
        if eid in seen:
            if seen[eid]!=owner:
                bad_id=True
            else:
                duplicated=True
        else:
            seen[eid]=owner
    if label_guard or bad_id:
        return {"context":"HOLD","reason":"EFFECT_OR_UNVERIFIED_RECORD_ID",
                "need_proof":proof_requested(case)}
    if proof_requested(case):
        return {"context":"PROOF","reason":"EXPLICIT_AUTHOR_TASK_PROOF_REQUIREMENT",
                "need_proof":True}
    if case["gate_open"] is False:
        return {"context":"CUT","reason":"SOURCE_OWNED_TOY_GRAPH_GATE_ABSENT",
                "need_proof":False}
    if duplicated:
        return {"context":"REPAIR","reason":"DECLARED_DUPLICATE_IDENTIFIER_PRESENT",
                "need_proof":False}
    return {"context":"RAW","reason":"NO_DUPLICATE_IN_DECLARED_OBSERVATIONS",
            "need_proof":False}


def counterfactual_prediction(context,row):
    preds=row["results"]
    if context=="HOLD":return "HOLD"
    if context=="CUT":return "PROVED_UNREACHABLE"
    if context=="RAW":return preds["classical_raw_record_parity"]
    if context=="REPAIR":return preds["language_plus_geometry_classical_graph"]
    if context=="PROOF":return preds["all_three_native"]
    raise HOLD("Unknown context")


def load_training(pairs):
    """Each pair (public_packet, *already scored* RING-004 report) is audited."""
    if not isinstance(pairs,(tuple,list)) or not 1<=len(pairs)<=8:
        raise HOLD("1..8 separate scored training packets required")
    datasets=[]
    seen=set()
    for public,report in pairs:
        feedback.validate(report)
        if (public.get("schema")!="motif.shared-evidence-public.v1"
                or comparator.canonical_digest(public)!=report["source_packet_sha256"]
                or len(public["cases"])!=report["count"]):
            raise HOLD("Training source packet does not match scored native receipt")
        if report["source_packet_sha256"] in seen:
            raise HOLD("Duplicate scored source packet")
        seen.add(report["source_packet_sha256"])
        if any(c["id"]!=r["case_id"] for c,r in zip(
                public["cases"],report["per_case"])):
            raise HOLD("Case IDs out of order or mixed")
        datasets.append((public,report))
    return datasets


def learn(pairs):
    datasets=load_training(pairs)
    buckets=defaultdict(list)
    for public,report in datasets:
        for case,row in zip(public["cases"],report["per_case"]):
            context=inspect(case)["context"]
            proposed=counterfactual_prediction(context,row)
            truth=row["hidden_expected_scoring_label"]
            buckets[context].append({
                "match":proposed==truth,
                "full_native_match":row["results"]["all_three_native"]==truth,
                "proposed":proposed,"truth":truth,
            })
    for context in CONTENTS:
        if not buckets[context]:
            buckets[context]=[]
    routes={}
    summaries={}
    for context in sorted(CONTENTS):
        items=buckets[context]
        correct=sum(x["match"] for x in items)
        full_correct=sum(x["full_native_match"] for x in items)
        # Any failure or thin support => conservative full-source fallback,
        # not a fabricated demonstration that an unknown context works.
        allow=len(items)>=MIN_SUPPORT and correct==len(items) and full_correct==len(items)
        routes[context]=METHODS[context] if allow else METHODS["PROOF"]
        summaries[context]={
            "training_cases":len(items),
            "candidate_correct":correct,
            "full_native_correct":full_correct,
            "candidate_accepted":allow,
            "proposed_method":METHODS[context],
            "frozen_route":routes[context],
            "proxy_source_invocation_count":PROXY_CALL_COST[
                context if allow else "PROOF"],
        }
    decision={
        "schema":SCHEMA,
        "status":"FROZEN_TRAIN_ONLY_SOURCE_AUDITED_POLICY",
        "training_packets":[x["source_packet_sha256"] for _,x in datasets],
        "training_case_count":sum(x["count"] for _,x in datasets),
        "source_pins":{c.id:c.commit for c in comparator.triad.ADAPTERS},
        "context_routes":routes,
        "context_training":summaries,
        "requires_proof_rule":"operator-scoped synthetic test: heldout index modulo 7 equals 0",
        "minimum_support":MIN_SUPPORT,
        "proxy_costs_are_author_defined_not_measured_timing":True,
        "evaluation_labels_visible_during_policy_creation":False,
        "future_branch_admission":"DISABLED",
        "real_world_authority":False,
    }
    decision["receipt_sha256"]=canonical(decision)
    return decision


def validate_policy(policy):
    if (not isinstance(policy,dict) or policy.get("schema")!=SCHEMA
            or policy.get("status")!="FROZEN_TRAIN_ONLY_SOURCE_AUDITED_POLICY"
            or set(policy.get("context_routes",{}))!=CONTENTS
            or set(policy.get("context_training",{}))!=CONTENTS
            or policy.get("real_world_authority") is not False
            or policy.get("future_branch_admission")!="DISABLED"
            or policy.get("source_pins") != {
                c.id:c.commit for c in comparator.triad.ADAPTERS}
            or policy.get("receipt_sha256")!=canonical({
                k:v for k,v in policy.items() if k!="receipt_sha256"})):
        raise HOLD("Invalid, modified, or unreviewed policy contract")
    for context,method in policy["context_routes"].items():
        if method not in (METHODS[context],METHODS["PROOF"]):
            raise HOLD("Policy invented executable capability")
        row=policy["context_training"][context]
        accepted=row.get("candidate_accepted")
        if type(accepted) is not bool:
            raise HOLD("Malformed candidate evidence")
        if accepted and (row.get("training_cases",0)<MIN_SUPPORT
                         or row.get("candidate_correct")!=row.get("training_cases")
                         or row.get("full_native_correct")!=row.get("training_cases")
                         or method!=METHODS[context]):
            raise HOLD("Candidate lacks attested training support")
        if not accepted and method!=METHODS["PROOF"]:
            raise HOLD("Unreviewed fallback")
    return policy


def route(policy,case):
    validate_policy(policy)
    features=inspect(case)
    selected=policy["context_routes"][features["context"]]
    return {
        "context":features["context"],"reason":features["reason"],
        "route":selected,"source_policy":policy["receipt_sha256"],
        "requires_proof":features["need_proof"],
        "only_public_input_used":True,
        "route_was_selected_before_native_prediction":True,
    }
