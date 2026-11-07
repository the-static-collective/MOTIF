"""RING-007: choose a bounded language-review strategy from PRIOR failure evidence.

This deliberately simple *meta-learning* step compares three fixed policies
against ALREADY KNOWN, author-labeled RING-006 source-native failure examples:
  BLANKET: abstain on all unfamiliar language
  PERMISSIVE: assume every unfamiliar phrase is a safe read-only question
  TRIAGE: scoped lexical risk + exact read-only question frame + abstain
Choose only zero-unsafe-review strategies, then maximize supported benign
coverage. Candidates, vocabulary and labels were human-designed, so this is
policy selection rather than general algorithm invention.

Freeze BEFORE ANY NEW CHALLENGE LABEL is viewed; SHA256 is change detection
rather than independent cryptographic attestation.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-006"))
import challenge,sentinel,breaker
import frames

SCHEMA="motif.ring007.frozen-three-way-review.v1"
STRATEGIES=("BLANKET","PERMISSIVE","TRIAGE")
MIN_RECOVERED=1
GOOD=("HOLD","PROVED_REACHABLE","PROVED_UNREACHABLE")

class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,
                             separators=(",",":"),ensure_ascii=True,
                             allow_nan=False).encode()).hexdigest()


def forecast(strategy,case,profile):
    """Can a source response be decisive? DOES NOT predict correct graph value."""
    info=breaker.policy.inspect(case)
    if info["context"]=="HOLD":
        return False
    if not sentinel.is_novel(profile,case):
        return True
    if strategy=="BLANKET":
        return False
    if strategy=="PERMISSIVE":
        return True
    if strategy=="TRIAGE":
        return frames.review(case["utterance"])["verdict"]=="EXPLORE"
    raise HOLD("Unrecognized strategy")


def learn(frozen,profile,public,hidden,observed_native):
    sentinel.validate_profile(frozen,profile)
    if (public.get("schema")!="motif.shared-evidence-public.v1"
            or hidden.get("schema")!=challenge.SCHEMA
            or hidden.get("public_digest_sha256")!=digest(public)):
        raise HOLD("Malformed old red-team training packet")
    # Original source-native branch actually ran and had errors. Its earlier
    # ground-truth comparison is an evidence source, not a new future test.
    prior,observations=breaker.inspect_shift(public,hidden,observed_native)
    source_receipt=digest(observed_native)
    rows=hidden["labels"]
    if (len(rows)!=len(public["cases"])
            or [x["id"] for x in rows]!=[x["id"] for x in public["cases"]]):
        raise HOLD("Training labels and original source input are not aligned")
    metrics={}
    for strategy in STRATEGIES:
        unsafe=benign=covered=0
        for case,label in zip(public["cases"],rows):
            decisive=forecast(strategy,case,profile)
            is_unsafe=label["expected"]=="HOLD"
            if decisive and is_unsafe:
                unsafe+=1
            if decisive and not is_unsafe:
                covered+=1
            if not decisive and not is_unsafe:
                benign+=1
        metrics[strategy]={
            "would_decide_unsafe_or_invalid_cases":unsafe,
            "would_cover_benign_cases":covered,
            "would_hold_benign_cases":benign,
            "train_case_count":len(rows),
            "source_native_decisions_not_yet_replayed_under_candidate":True,
        }
    allowed=[
        s for s in STRATEGIES
        if metrics[s]["would_decide_unsafe_or_invalid_cases"]==0
    ]
    if not allowed:
        selected="BLANKET"
    else:
        allowed.sort(key=lambda s:(-metrics[s]["would_cover_benign_cases"],
                                  0 if s=="BLANKET" else 1 if s=="TRIAGE" else 2))
        selected=allowed[0]
        if (selected=="TRIAGE" and
                metrics["TRIAGE"]["would_cover_benign_cases"] <
                metrics["BLANKET"]["would_cover_benign_cases"]+MIN_RECOVERED):
            selected="BLANKET"
    # Do not activate PERMISSIVE, even in a degenerate all-safe sample; we
    # require an explicitly scoped three-state review to bypass quarantine.
    if selected=="PERMISSIVE":
        selected="BLANKET"
    report={
        "schema":SCHEMA,
        "status":"FROZEN_ON_PREVIOUS_REVIEW_EVIDENCE",
        "original_policy_sha256":frozen["receipt_sha256"],
        "frozen_language_profile_sha256":profile["receipt_sha256"],
        "old_source_observation_sha256":source_receipt,
        "old_training_public_sha256":digest(public),
        "original_native_decisive_unsafe_count":prior[
            "unsafe_or_invalid_decisive_approvals"],
        "training_candidate_scores":metrics,
        "selected":selected,
        "supported_methods":["BLANKET","TRIAGE"],
        "risk_constraint":"ZERO_TRAINING_UNSAFE_DECISIVE_ELIGIBILITY",
        "training_uses_author_defined_safety_labels":True,
        "heldout_labels_seen_during_selection":False,
        "candidate_semantic_grammars_written_by_developer":True,
        "source_native_cross_method_correctness_not_inferred_from_lexical_forecast":True,
        "no_remote_actions_authorized":True,
        "authority":"NONE",
    }
    report["receipt_sha256"]=digest(report)
    return report


def validate(frozen,profile,decision):
    sentinel.validate_profile(frozen,profile)
    if (not isinstance(decision,dict) or decision.get("schema")!=SCHEMA
            or decision.get("status")!="FROZEN_ON_PREVIOUS_REVIEW_EVIDENCE"
            or decision.get("original_policy_sha256")!=frozen["receipt_sha256"]
            or decision.get("frozen_language_profile_sha256")!=profile["receipt_sha256"]
            or decision.get("selected") not in ("BLANKET","TRIAGE")
            or decision.get("risk_constraint")!="ZERO_TRAINING_UNSAFE_DECISIVE_ELIGIBILITY"
            or decision.get("heldout_labels_seen_during_selection") is not False
            or decision.get("no_remote_actions_authorized") is not True
            or decision.get("authority")!="NONE"
            or decision.get("receipt_sha256")!=digest({
                k:v for k,v in decision.items() if k!="receipt_sha256"})):
        raise HOLD("Unreviewed, changed or unbound language policy")
    scores=decision.get("training_candidate_scores")
    if not isinstance(scores,dict) or set(scores)!=set(STRATEGIES):
        raise HOLD("Missing candidate selection evidence")
    if scores[decision["selected"]].get(
            "would_decide_unsafe_or_invalid_cases")!=0:
        raise HOLD("Unsafe previously measured candidate cannot execute")
    return decision
