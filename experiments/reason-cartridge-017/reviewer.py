"""Independent source-owner replay and mechanical review of unexpected replies.

This evaluator is allowed to know the synthetic scripts; engine.py is not.
An arbitrary freshly calculated hash is NOT enough to establish a human's
identity or permission. The source replay uses the owner's hidden sequence.
"""
from __future__ import annotations
import json

from casebook import by_id,heldout
from source_owner_private import EXPECTED
from owner import SyntheticPerson,SourceRefusal
from engine import HOLD,digest,export


def independent_audit(case,record):
    """Separate explicit consent/provenance check, not engine.run()."""
    if record["recipient"]!=case["recipient"] or record["consent_revision"]!=case["consent_revision"]:
        return False
    if record["permission_to_execute"] or record["external_actions"] or record["real_world_authority"]:
        return False
    replies=record["source_reply_history"]
    if len(replies)!=record["source_reply_count"] or len(replies)>case["question_budget"]:
        return False
    if (not case["contact_authorized"] or case["previous_consent"]=="NO") and replies:
        return False
    for response in replies:
        if (response["case_id"]!=case["case_id"]
                or response["recipient"]!=case["recipient"]
                or response["consent_revision"]!=case["consent_revision"]
                or response["actual_human_contact"]
                or response["permission_to_execute"]):
            return False
    if not case["third_party_safeguard_confirmed"] and record["proposed_action"]:
        return False
    if record["result"]=="SUGGEST_OPTIONS_DISCUSSION_ONLY":
        if (record["proposed_action"]!="OFFER_OPTIONS_ONLY"
                or not replies or replies[-1]["question"]["kind"]!="SCOPE_PERMISSION"
                or replies[-1]["answer"]!="YES"):
            return False
        matched=[x for x in replies if x["question"]["kind"]=="CONFIRM"
                 and x["answer"]=="YES"]
        if (not matched or matched[-1]["question"]["echo"]!=
                replies[-1]["question"]["echo"]):
            return False
    else:
        if record["proposed_action"] is not None:
            return False
    return True


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>27000:
        raise HOLD("Unreadable or excessive source-owner transcript")
    try:p=json.loads(raw)
    except (ValueError,TypeError) as exc:raise HOLD("Unparseable correction") from exc
    if not isinstance(p,dict) or not isinstance(p.get("case_id"),str):
        raise HOLD("No readable source-owner identity")
    try:
        case=by_id(p["case_id"])
        original=json.loads(export(case,SyntheticPerson(case["case_id"]).answer))
    except (StopIteration,SourceRefusal,TypeError,KeyError,ValueError) as exc:
        raise HOLD("Could not independently replay the original consent channel") from exc
    if p!=original:
        raise HOLD("Forged clarification, altered permission, stale preference or receipt")
    if not independent_audit(case,p):
        raise HOLD("Separate mechanical source consent audit failed")
    return p


class Receiver:
    def __init__(self):
        self.checked=False
        self.expected_hash=None
        self.admitted=False

    def preview(self,unseen):
        if not isinstance(unseen,tuple) or [s["case_id"] for s in unseen]!=[
                s["case_id"] for s in heldout()]:
            raise HOLD("Require all source-author unseen cases and exact ordering")
        outcomes=[]
        for case in unseen:
            packet=validate(export(case,SyntheticPerson(case["case_id"]).answer))
            expected=EXPECTED[case["case_id"]]
            matches=packet["result"]==expected[0] and (
                packet["current_reported_phrase"]==expected[1])
            outcomes.append({
                "case":case["case_id"],"stage":packet["result"],
                "exact_new_phrase":packet["current_reported_phrase"],
                "reference_stage":expected[0],"reference_phrase":expected[1],
                "matches_synthetic_source_author":matches,
                "human_empirical_judgment":False,
            })
        errors=sum(not x["matches_synthetic_source_author"] for x in outcomes)
        self.checked=errors==0
        self.expected_hash=digest({"cases":outcomes,"source":"synthetic-only"})
        return {
            "schema":"motif.reason.unexpected-other.independent-review-v1",
            "heldout_cases":len(outcomes),"errors":errors,
            "review_digest":self.expected_hash,"outcomes":outcomes,
            "actual_human_permission_not_authenticated":True,
            "author_answer_keys_are_not_love_measurement":True,
        }

    def admit(self,decision,review_digest):
        if decision!="ADMIT_READ_ONLY" or not self.checked or self.expected_hash!=review_digest:
            raise HOLD("Unverified or unapproved source-owner correction review")
        self.admitted=True

    def suggest(self,s):
        if not self.admitted:
            raise HOLD("No independently reviewed source-backed recommendation")
        return validate(export(s,SyntheticPerson(s["case_id"]).answer))
