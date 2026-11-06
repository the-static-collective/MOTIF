"""Evaluator-only, independent source-owner replay and hidden-case audits.

This component can import synthetic source_private.py; student.py and
mirror.py may NOT. It evaluates conditional-wish prediction separately
from actual limited consent and separately from the REASON-019 critic.

A source signature here is a repeatable SHA-256 content checksum, not real
identity or authenticated testimony. All persons and expected ethics are
invented for this experiment by the same author.
"""
from __future__ import annotations
import json

from casebook import by_id,heldout,world
from source_private import HIDDEN,EXPECTED,owner_rule
from owner import SyntheticOther
from student import HOLD,digest,preference
from mirror import export


def independent_heldout_reference(scene,proposal):
    source_state=proposal["learner"]["state"]
    if source_state not in ("BASE_SUFFICIENT","ADDED_FEATURE"):
        return {
            "eligible_for_meaning_audit":False,
            "correct":0,"tested":0,"misclassified":0,
            "source_decline_or_absent_contact_respected":True,
        }
    policy,_,_=HIDDEN[scene["case_id"]]
    total=0;matched=0;failures=[]
    for i in range(8):
        w=world(i,"HELDOUT")
        guessed=preference(proposal["learner"],w["id"])
        # A separately source-owned, imperative private policy reference,
        # never shown to a candidate program during grammar compilation.
        truth=owner_rule(policy,i)
        total+=1
        if guessed==truth:matched+=1
        else:failures.append(w["id"])
    return {
        "eligible_for_meaning_audit":True,
        "correct":matched,"tested":total,
        "misclassified":total-matched,"failures":failures,
        "person_rule_is_synthetic_not_actual_human_need":True,
    }


def independent_scope_review(scene,proposal):
    if (proposal["case_id"]!=scene["case_id"]
            or proposal["recipient"]!=scene["recipient"]
            or proposal["consent_revision"]!=scene["consent_revision"]
            or proposal["permission_to_execute"] is not False
            or proposal["external_actions"] is not False
            or proposal["real_world_authority"] is not False):
        return False
    fit=proposal["learner"]
    receipts=fit["questions"]
    if (not scene["contact_allowed"] and receipts):
        return False
    if len(receipts)>scene["allowed_source_questions"]:
        return False
    if proposal["state"]=="SUGGEST_DISCUSSION_ONLY":
        if proposal["recommended_action"]!="OFFER_OPTIONS_ONLY":
            return False
        permission=proposal["actual_scope_response"]
        if (not isinstance(permission,dict)
                or permission.get("kind")!="CONSENT"
                or permission.get("world_id")!=proposal["target_context"]["id"]
                or permission.get("response")!="YES"):
            return False
        if proposal["inferred_source_welcome_not_consent"] is not True:
            return False
        if fit["state"] not in ("BASE_SUFFICIENT","ADDED_FEATURE"):
            return False
        if not proposal["perspective_reports"]["CRITIC"]["judgments"][
                "OFFER_OPTIONS_ONLY"]["eligible"]:
            return False
    else:
        if proposal["recommended_action"] is not None:
            return False
        if proposal["perspective_reports"]["CRITIC"]["judgments"][
                "OFFER_OPTIONS_ONLY"]["eligible"]:
            return False
    if proposal["state"]=="HOLD_SOURCE_FEATURE_WITHHELD":
        if (fit["contradiction"] is None
                or fit["source_disclosed_feature_receipt"] is None
                or fit["program"] is not None):
            return False
    if proposal["state"]=="HOLD_NO_CONTACT" and (receipts or
                                                 proposal["actual_scope_response"]):
        return False
    return True


def verify(raw):
    if not isinstance(raw,str) or len(raw.encode())>200000:
        raise HOLD("Unknown or excessive personal-source proposal")
    try:p=json.loads(raw)
    except (TypeError,ValueError) as exc:raise HOLD("Unreadable self/other reasoning proof") from exc
    if not isinstance(p,dict) or not isinstance(p.get("case_id"),str):
        raise HOLD("Missing original synthetic source identity")
    try:
        source=by_id(p["case_id"])
        original=json.loads(export(source,SyntheticOther(source["case_id"])))
    except (StopIteration,TypeError,KeyError,ValueError) as exc:
        raise HOLD("Original finite source testimony cannot be replayed") from exc
    if p!=original:
        raise HOLD("Recomputed SHA is not a source-owner receipt or authorization")
    if not independent_scope_review(source,p):
        raise HOLD("Separate permission and perspective audit rejected source outcome")
    checked=independent_heldout_reference(source,p)
    if checked["misclassified"]:
        raise HOLD("Novel concept fails synthetic owner heldout conditional examples")
    return p


class Receiver:
    def __init__(self):
        self.review_hash=None
        self.admitted=False
        self.passed=False

    def preview(self,worlds):
        if (not isinstance(worlds,tuple) or
                [w["case_id"] for w in worlds]!=[
                    c["case_id"] for c in heldout()]):
            raise HOLD("Must independently review all original heldout sources")
        rows=[]
        for s in worlds:
            proposal=verify(export(s,SyntheticOther(s["case_id"])))
            actual=(proposal["state"],proposal["learner"]["state"])
            expected=EXPECTED[s["case_id"]]
            audit=independent_heldout_reference(s,proposal)
            rows.append({
                "case":s["case_id"],
                "actual":list(actual),
                "author_expected":list(expected),
                "source_author_match":actual==expected,
                "independent_scope_review":True,
                "independent_hypothetical_worlds":audit["tested"],
                "exact_conditional_predictions":audit["correct"],
                "source_permission_never_general_authority":True,
                "real_person_involved":False,
            })
        summary={
            "schema":"motif.reason.other-teaches-self.review.v1",
            "heldout_cases":len(rows),
            "matches_author_reference":sum(r["source_author_match"] for r in rows),
            "independently_validated_contexts":sum(
                r["independent_hypothetical_worlds"] for r in rows),
            "correct_heldout_contexts":sum(
                r["exact_conditional_predictions"] for r in rows),
            "independent_scope_failures":sum(
                not r["independent_scope_review"] for r in rows),
            "source_owner_is_author_curated_not_a_real_participant":True,
            "no_moral_or_general_language_comprehension_claim":True,
            "cases":rows,
        }
        self.passed=(
            summary["matches_author_reference"]==len(worlds)
            and summary["independent_scope_failures"]==0
            and summary["correct_heldout_contexts"]==
                summary["independently_validated_contexts"]
        )
        self.review_hash=digest(summary)
        return dict(summary,review_digest=self.review_hash)

    def admit(self,choice,review_hash):
        if (choice!="ADMIT_READ_ONLY" or not self.passed
                or self.review_hash is None or self.review_hash!=review_hash):
            raise HOLD("No source-reviewed, consent-limited read-only admission")
        self.admitted=True

    def suggest(self,scene):
        if not self.admitted:
            raise HOLD("Incomplete source preference verification")
        return verify(export(scene,SyntheticOther(scene["case_id"])))
