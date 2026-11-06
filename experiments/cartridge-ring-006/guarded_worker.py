"""RING-006 isolated novelty gate around the real RING-005 source-native runner.

Re-verifies route and exact visible utterance in the sandbox; never sees
withheld labels, earlier training receipts, or remote/network capabilities.
Known, permitted cases run original selective_worker.execute unchanged.
Novel cases emit HOLD without importing or calling any cartridge for that case.

The SHA256 in the profile detects mutation but is not an external signature or
independent proof that the training corpus is authentic.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import selective_worker as prior

SCHEMA="motif.ring006.guarded-native-output.v1"
PROFILE="motif.ring006.frozen-language-profile.v1"
MANIFEST="motif.ring006.precommitted-quarantine.v1"
QUARANTINE="PROFILE_NOVELTY_QUARANTINE_NO_NATIVE"


def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                               allow_nan=False).encode()).hexdigest()


def verify(public,manifest):
    if (not isinstance(public,dict) or public.get("schema")!=prior.PUBLIC_SCHEMA
            or not isinstance(public.get("cases"),list)
            or not 1<=len(public["cases"])<=48
            or public.get("no_labels_inside_native_runner") is not True
            or not isinstance(manifest,dict) or manifest.get("schema")!=MANIFEST
            or manifest.get("source_public_digest_sha256")!=digest(public)
            or manifest.get("rule")!="HOLD_NOVEL_INPUT_UNTIL_INDEPENDENT_REVIEW"
            or manifest.get("external_authority")!="NONE"
            or manifest.get("has_hidden_scoring_labels") is not False
            or manifest.get("precommitted_before_any_native_execution") is not True
            or manifest.get("receipt_sha256")!=digest({
                k:v for k,v in manifest.items() if k!="receipt_sha256"})):
        raise ValueError("Incorrect, edited, or unbound novelty manifest")
    profile=manifest.get("profile")
    if (not isinstance(profile,dict) or profile.get("schema")!=PROFILE
            or profile.get("frozen_policy_sha256")!=manifest.get("frozen_policy_sha256")
            or profile.get("eligible_action")!="ABSTAIN_ONLY_NOT_AUTO_CORRECT"
            or profile.get("no_new_execution_authority") is not True
            or profile.get("receipt_sha256")!=digest({
                k:v for k,v in profile.items() if k!="receipt_sha256"})):
        raise ValueError("Unbound frozen training profile")
    allowed=profile.get("exact_public_training_utterances")
    if (not isinstance(allowed,list) or not 1<=len(allowed)<=100
            or allowed!=sorted(set(allowed))
            or any(type(x) is not str or not 1<=len(x)<=320 for x in allowed)):
        raise ValueError("Invalid exact training profile")
    routes=manifest.get("routes")
    if not isinstance(routes,list) or len(routes)!=len(public["cases"]):
        raise ValueError("Missing or reordered case routes")
    seen=set()
    for case,row in zip(public["cases"],routes):
        original,proof=prior.context(case)
        if (not isinstance(row,dict) or row.get("id")!=case["id"]
                or row["id"] in seen or row.get("requires_proof")!=proof):
            raise ValueError("Case mismatch or changed proof requirement")
        seen.add(row["id"])
        novel=case["utterance"] not in allowed
        if novel and original!="HOLD":
            if row.get("context")!="NOVEL" or row.get("route")!=QUARANTINE:
                raise ValueError("Unknown phrase may not bypass quarantine")
        elif row.get("context")!=original:
            raise ValueError("Familiar source context changed")
    return routes


def execute(public,manifest):
    routes=verify(public,manifest)
    retained=[]
    retained_routes=[]
    for case,row in zip(public["cases"],routes):
        if row["route"]!=QUARANTINE:
            retained.append(case)
            retained_routes.append({
                "id":row["id"],"context":row["context"],"route":row["route"],
                "requires_proof":row["requires_proof"]})
    known={}
    if retained:
        subset=dict(public)
        subset["cases"]=retained
        old_manifest={
            "schema":prior.ROUTING_SCHEMA,
            "public_digest_sha256":digest(subset),
            "policy_digest_sha256":manifest["frozen_policy_sha256"],
            "routes":retained_routes,
            "no_labels_in_route_manifest":True,
            "precommitted_before_any_native_outcomes":True,
            "authority":"NONE",
        }
        old_manifest["receipt_sha256"]=digest(old_manifest)
        result=prior.execute(subset,old_manifest)
        known={x["id"]:x for x in result["results"]}
    output=[]
    for case,row in zip(public["cases"],routes):
        if row["route"]==QUARANTINE:
            output.append({
                "id":case["id"],"context":"NOVEL",
                "selected_route":QUARANTINE,
                "decision":"HOLD",
                "source_method_invocations":[],
                "source_method_call_count":0,
                "proof":None,
                "elapsed_ns_inside_one_container":0,
                "source_input_label_was_not_supplied":True,
                "reason":"UNREVIEWED_LANGUAGE_DISTRIBUTION_SHIFT",
            })
        else:
            output.append(known[case["id"]])
    return {
        "schema":SCHEMA,
        "public_digest_sha256":digest(public),
        "profile_receipt_sha256":manifest["profile"]["receipt_sha256"],
        "frozen_policy_sha256":manifest["frozen_policy_sha256"],
        "route_manifest_sha256":manifest["receipt_sha256"],
        "results":output,
        "novelty_quarantined_count":sum(
            r["route"]==QUARANTINE for r in routes),
        "same_case_observations_preserved":True,
        "labels_not_provided":True,
        "source_native_calls_not_made_for_quarantined_cases":True,
        "source_only_candidates_not_executed":True,
        "external_action_executed":False,
        "authority":"NONE",
    }


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: guarded_worker.py <public.json> <manifest.json>")
    p=json.loads(Path(sys.argv[1]).read_text())
    m=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(execute(p,m),sort_keys=True))
