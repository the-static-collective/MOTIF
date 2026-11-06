"""Independent source-owner review of every synthetic care inquiry.

Unlike thinker.py, this evaluator MAY read the hidden profile key.
This component verifies both the reply transcript and the proposed choice.
Even a correctly recomputed SHA-256 cannot manufacture a recipient's answer;
replay requires the original deterministic source owner.

This is a bounded test oracle, NOT authentication of a living person's words
or confirmation of which action would objectively be loving.
"""
from __future__ import annotations
import json

from scenarios import CASES,by_id,heldout
from owner import SourceOwner,SourceRefusal
from owner_truth import PROFILE,EXPECTED
from thinker import HOLD,export,digest,check,gated


def independently_audit(s,packet):
    if packet["case_id"]!=s["id"] or packet["recipient"]!=s["recipient"]:
        return False
    if packet["consent_revision"]!=s["consent_revision"]:
        return False
    if packet["question_count"]>s["max_questions"]:
        return False
    if packet["question_count"] and not s["permission_to_ask"]:
        return False
    chosen=packet["selected_action"]
    if chosen is None:
        return packet["stage"]=="HOLD_VALUE_OR_PERMISSION_CONFLICT"
    action=next((a for a in s["actions"] if a["id"]==chosen),None)
    if action is None:
        return False
    if chosen=="WAIT":
        return True
    if s["general_consent"]=="NO":
        return False
    authorized=set(s["authorized_actions"])
    for answer in packet["question_responses"]:
        if answer["kind"]=="CONSENT" and answer["answer"]=="YES":
            authorized.add(answer["target_action"])
    # This is independent of the planner's gated() implementation: recalculate
    # the restrictions directly from the scenario's original fields.
    if (chosen not in authorized or not action["truth"] or not action["private"]
            or not action["no_debt"] or not action["no_pressure"]
            or not action["third_party_ok"]
            or action["cost"]>s["resources"]-s["existing_duties"]):
        return False
    # The source's hidden preference is checked here, NEVER in planner code.
    owner_pref=PROFILE[s["id"]]
    profile=next(p for p in s["possible_preferences"] if p["id"]==owner_pref)
    return chosen in profile["acceptable_actions"]


def verify(raw):
    if not isinstance(raw,str) or len(raw.encode())>24000:
        raise HOLD("Oversized or absent consent-sensitive evidence")
    try:
        provided=json.loads(raw)
    except (ValueError,TypeError) as exc:
        raise HOLD("Invalid report structure") from exc
    if not isinstance(provided,dict) or "case_id" not in provided:
        raise HOLD("Unknown source-backed recipient")
    try:
        s=by_id(provided["case_id"])
        canonical=json.loads(export(s,SourceOwner(s["id"]).answer))
    except (StopIteration,SourceRefusal,TypeError,ValueError,KeyError) as exc:
        raise HOLD("Unable to reproduce original recipient dialogue") from exc
    if provided!=canonical:
        raise HOLD("Altered recipient answer, refusal, revision, plan or authority")
    if not independently_audit(s,provided):
        raise HOLD("Separate source-owner review rejected the proposed action")
    return provided


class Receiver:
    def __init__(self):
        self.checked=False
        self.digest=None
        self.admitted=False

    def preview(self,records):
        if not isinstance(records,tuple) or len(records)!=len(heldout()):
            raise HOLD("All unseen synthetic cases must be independently reviewed")
        if [r["id"] for r in records]!=[x["id"] for x in heldout()]:
            raise HOLD("Wrong heldout family, order or source")
        results=[]
        for s in records:
            payload=verify(export(s,SourceOwner(s["id"]).answer))
            matches=payload["selected_action"]==EXPECTED[s["id"]]
            results.append({"case":s["id"],
                            "selected":payload["selected_action"],
                            "source_owner_expected":EXPECTED[s["id"]],
                            "source_expected_matches":matches,
                            "separate_mechanical_gate_pass":True,
                            "observed_human_welfare":False})
        errors=sum(not r["source_expected_matches"] for r in results)
        self.checked=errors==0
        self.digest=digest({"results":results,"fictional_only":True})
        return {"schema":"motif.reason.good-of-the-other.review.v1",
                "cases":len(results),"errors":errors,
                "source_author_choices_not_independent_human_ethics":True,
                "recipient_replies_are_simulated":True,
                "human_happiness_not_measured":True,
                "review_digest":self.digest,"results":results}

    def admit(self,decision,review_digest):
        if (decision!="ADMIT_READ_ONLY" or not self.checked
                or review_digest!=self.digest):
            raise HOLD("Not source-author reviewed or not read-only")
        self.admitted=True

    def suggest(self,s):
        if not self.admitted:
            raise HOLD("No local source-owner review of proposed care reasoning")
        return verify(export(s,SourceOwner(s["id"]).answer))
