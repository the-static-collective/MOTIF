"""RING-006: make genuine observed OOD failures and abstention costs first-class.

RING-003's many-tail hypergraph now gets experiment-specific, condition-bound
SOURCE_RECEIPT → FAILURE / QUARANTINE / LOST_BENIGN_COVERAGE relations.
These are *observed synthetic outcomes*, not permanent universal edge weights.
A reviewer may promote hypotheses only after independent validation.

This module can neither install a cartridge nor change policy/external effects.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

SCHEMA="motif.ring006.drift-evidence-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def validate(x):
    if not isinstance(x,dict) or x.get("schema")!="motif.ring006.redteam-feedback-loop.v1":
        raise HOLD("Wrong adversarial source evidence")
    if x.get("receipt_sha256")!=digest({k:v for k,v in x.items() if k!="receipt_sha256"}):
        raise HOLD("Changed adversarial evidence receipt")
    if (x.get("status")!="SOURCE_NATIVE_ADVERSARIAL_SHIFT_AND_FROZEN_POLICY_REVIEW"
            or x.get("authority")!="NONE"
            or x.get("external_action_executed") is not False
            or x.get("original_router_mutated") is not False
            or x.get("new_executables_admitted")!=0
            or x.get("provenance")!="FULLY_AUTHOR_CREATED_RED_TEAM_LABELS_NOT_INDEPENDENT_WORLD_TRUTH"):
        raise HOLD("Unacceptable evidence/authority claim")
    p=x.get("first_batch")
    q=x.get("second_batch")
    if not isinstance(p,dict) or not isinstance(q,dict):
        raise HOLD("Missing before/after trial")
    for batch,legacy_key in ((p,"legacy"),(q,"legacy")):
        cases=batch.get("per_case") if batch is p else batch.get("per_case_legacy")
        statistics=batch.get(legacy_key)
        if not isinstance(cases,list) or len(cases)!=x.get(
                "first_unseen_adversarial_cases" if batch is p
                else "second_disjoint_adversarial_cases"):
            raise HOLD("Experiment per-case witnesses missing")
        if type(statistics.get("unsafe_or_invalid_decisive_approvals")) is not int:
            raise HOLD("Missing unsafe-approval count")
        if sum(c["decision"]!="HOLD" and c["unsafe_or_invalid"]
               for c in cases)!=statistics["unsafe_or_invalid_decisive_approvals"]:
            raise HOLD("Unsafe tally differs from original case evidence")
    new=q.get("guarded")
    if new is not None:
        rows=q.get("per_case_guarded")
        if not isinstance(rows,list) or len(rows)!=len(q["per_case_legacy"]):
            raise HOLD("Guarded cases not paired with legacy")
        if sum(c["decision"]!="HOLD" and c["unsafe_or_invalid"]
               for c in rows)!=new["unsafe_or_invalid_decisive_approvals"]:
            raise HOLD("Guarded unsafe tally disagrees with witnesses")
        if (not isinstance(q.get("guarded_route_manifest_sha256"),str)
                or len(q["guarded_route_manifest_sha256"])!=64):
            raise HOLD("Missing guarded precommitted source manifest")
    return True


def graph(trial):
    validate(trial)
    a=trial["first_batch"]
    b=trial["second_batch"]
    prior=trial["original_frozen_policy_receipt"]
    profile=trial["frozen_novelty_profile_receipt"]
    sourcepins=trial["source_commit_pins"]
    if (not isinstance(sourcepins,dict) or not sourcepins
            or any(type(k) is not str or type(v) is not str or len(v)!=40
                   for k,v in sourcepins.items())):
        raise HOLD("Source pin signatures missing")
    vertices=[
        {"id":"policy:"+prior,"type":"FROZEN_PRIOR_ROUTER"},
        {"id":"profile:"+profile,"type":"TRAINING_LANGUAGE_NOVELTY_PROFILE"},
        {"id":"trial:"+a["public_packet_sha256"],"type":"AUTHOR_SYNTHETIC_REDTEAM_PACKET",
         "role":"OBSERVED_BREAK"},
        {"id":"trial:"+b["public_packet_sha256"],"type":"AUTHOR_SYNTHETIC_REDTEAM_PACKET",
         "role":"POST_DEMOTION_FRESH_CASES"},
    ]
    vertices.extend({
        "id":"source:"+name,"type":"SOURCE_PINNED_NATIVE_METHOD",
        "commit":commit,
        "authoritative_in_real_world":False,
    } for name,commit in sorted(sourcepins.items()))
    old=a["legacy"]["unsafe_or_invalid_decisive_approvals"]
    old_next=b["legacy"]["unsafe_or_invalid_decisive_approvals"]
    guarded=b.get("guarded")
    edges=[
        {
            "id":"observed:old-context-failed-on-novel-intent",
            "kind":"MEASURED_SYNTHETIC_FAILURE_EDGE",
            "tails":["policy:"+prior,"trial:"+a["public_packet_sha256"]],
            "heads":["outcome:unsafe-decisive-answers",
                     "question:unrecognized-risk-intent"],
            "observed_unsafe_decisive_count":old,
            "source_world":"AUTHOR_GENERATED_NOT_HUMAN_RECORDED",
            "real_world_harm_observed":False,
        },
        {
            "id":"observed:old-context-cross-seed-repetition",
            "kind":"MEASURED_SYNTHETIC_REPLICATION_EDGE",
            "tails":["policy:"+prior,"trial:"+b["public_packet_sha256"]],
            "heads":["outcome:unsafe-decisive-answers"],
            "observed_unsafe_decisive_count":old_next,
            "same_utterance_template_family":True,
            "not_an_independent_semantic_distribution":True,
        }
    ]
    if guarded is not None:
        loss=b["legacy"]["safe_positive_decisive_coverage"]-guarded[
            "safe_positive_decisive_coverage"]
        edges.append({
            "id":"observed:held-novelty-tradeoff",
            "kind":"MEASURED_SYNTHETIC_SAFETY_COVERAGE_TENSION",
            "tails":["policy:"+prior,"profile:"+profile,
                     "trial:"+b["public_packet_sha256"]],
            "heads":["outcome:reduced-unsafe-decisive-answers",
                     "outcome:lost-benign-decisive-coverage",
                     "question:independent-review-needed"],
            "legacy_unsafe_decisive":old_next,
            "guarded_unsafe_decisive":guarded[
                "unsafe_or_invalid_decisive_approvals"],
            "legacy_safe_decisive_coverage":b["legacy"][
                "safe_positive_decisive_coverage"],
            "guarded_safe_decisive_coverage":guarded[
                "safe_positive_decisive_coverage"],
            "benign_coverage_lost":loss,
            "benefit_is_not_automatically_free":True,
            "automatically_promoted_routing_methods":0,
        })
    packet={
        "schema":SCHEMA,
        "source_trial_receipt_sha256":trial["receipt_sha256"],
        "vertices":vertices,
        "hyperedges":edges,
        "source_pins":sourcepins,
        "measured_world":"AUTHOR_GENERATED_SYNTHETIC_ONLY",
        "case_labels_were_withheld_from_original_native_source_runner":True,
        "new_real_world_edges_promoted":0,
        "new_executable_cartridges_installed":0,
        "feedback_applies_only_to_frozen_policy_and_challenge_templates":True,
        "automatic_software_self_rewriting":False,
        "external_action_executed":False,"authority":"NONE",
    }
    packet["receipt_sha256"]=digest(packet)
    return packet


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trial",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        result=graph(json.loads(args.trial.read_text()))
        data=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(data)
        print(json.dumps({"hyperedges":len(result["hyperedges"]),
                          "receipt_sha256":result["receipt_sha256"],
                          "authority":"NONE"},sort_keys=True))
    except HOLD as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
