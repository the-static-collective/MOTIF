"""RING-006: source-verified training profile and *demotion-only* novelty gate.

The profile is frozen from earlier evaluated public training packets. Later
adversarial outcomes can trigger the pre-existing quarantine circuit; no new
capability, new branch, model weight, or external authority is installed.

Literal utterance novelty is a coarse, overly conservative distribution
shift detector. It is intentionally measured for both avoided unsafe answers
AND lost coverage of harmless new questions.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-005"))
import policy, adaptive
import challenge

PROFILE="motif.ring006.frozen-language-profile.v1"
MANIFEST="motif.ring006.precommitted-quarantine.v1"
QUARANTINE="PROFILE_NOVELTY_QUARANTINE_NO_NATIVE"

class HOLD(ValueError):
    pass


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def train_profile(frozen,training_pairs):
    policy.validate_policy(frozen)
    datasets=policy.load_training(training_pairs)
    observed=[r["source_packet_sha256"] for _,r in datasets]
    if observed!=frozen["training_packets"]:
        raise HOLD("Profile training sources are not bound to frozen policy")
    names=sorted({c["utterance"] for public,_ in datasets
                  for c in public["cases"]})
    if not 1<=len(names)<=100 or any(
            type(x) is not str or not 1<=len(x)<=320 for x in names):
        raise HOLD("Training utterance corpus invalid")
    result={
        "schema":PROFILE,
        "frozen_policy_sha256":frozen["receipt_sha256"],
        "training_source_packet_sha256":observed,
        "exact_public_training_utterances":names,
        "method":"EXACT_TRAINING_UTTERANCE_MATCH_OVERSENSITIVE_BY_DESIGN",
        "case_count":sum(len(pub["cases"]) for pub,_ in datasets),
        "eligible_action":"ABSTAIN_ONLY_NOT_AUTO_CORRECT",
        "no_new_execution_authority":True,
    }
    result["receipt_sha256"]=digest(result)
    return result


def validate_profile(frozen,profile):
    policy.validate_policy(frozen)
    if (not isinstance(profile,dict) or profile.get("schema")!=PROFILE
            or profile.get("frozen_policy_sha256")!=frozen["receipt_sha256"]
            or profile.get("training_source_packet_sha256")!=frozen["training_packets"]
            or profile.get("eligible_action")!="ABSTAIN_ONLY_NOT_AUTO_CORRECT"
            or profile.get("no_new_execution_authority") is not True
            or profile.get("method")!="EXACT_TRAINING_UTTERANCE_MATCH_OVERSENSITIVE_BY_DESIGN"
            or profile.get("receipt_sha256")!=digest({
                k:v for k,v in profile.items() if k!="receipt_sha256"})):
        raise HOLD("Unbound or modified novelty profile")
    allowed=profile.get("exact_public_training_utterances")
    if (not isinstance(allowed,list) or not 1<=len(allowed)<=100
            or allowed!=sorted(set(allowed))
            or any(type(x) is not str or not 1<=len(x)<=320 for x in allowed)):
        raise HOLD("Malformed profile utterances")
    return True


def is_novel(profile,case):
    return case["utterance"] not in profile["exact_public_training_utterances"]


def manifest_for(frozen,public,profile):
    validate_profile(frozen,profile)
    prior=adaptive.manifest_for(frozen,public)
    routes=deepcopy(prior["routes"])
    for case,row in zip(public["cases"],routes):
        # If original source-visible evidence already demands HOLD (effect
        # word or invalid trace) preserve that reason, no extra unknown edge.
        if is_novel(profile,case) and row["context"]!="HOLD":
            row["context"]="NOVEL"
            row["route"]=QUARANTINE
            row["reason"]="NOT_PRESENT_IN_FROZEN_TRAINING_UTTERANCES"
    out={
        "schema":MANIFEST,
        "source_public_digest_sha256":digest(public),
        "frozen_policy_sha256":frozen["receipt_sha256"],
        "profile":deepcopy(profile),
        "routes":routes,
        "rule":"HOLD_NOVEL_INPUT_UNTIL_INDEPENDENT_REVIEW",
        "precommitted_before_any_native_execution":True,
        "has_hidden_scoring_labels":False,
        "external_authority":"NONE",
    }
    out["receipt_sha256"]=digest(out)
    return out
