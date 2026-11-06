"""Source-author reviewer and mechanical independent recipient-consent audit.

This may import source_private.py; dual_mirror.py and syntax.py cannot.
A hash re-computed by a claimant does not authenticate human intent. The
reviewer regenerates each full four-elf proposal against the original
scripted source and independently checks its scope, consent and capability.
"""
from __future__ import annotations

import json

from cases import by_id,heldout
from source_private import EXPECTED,GOAL_ECHOS,DIALOGUE
from dual_mirror import HOLD,digest,export,public_check


def mechanical_audit(scene,receipt):
    other=scene["recipient"]
    if (receipt["recipient"]!=other
            or receipt["consent_revision"]!=scene["consent_revision"]
            or receipt["source_public_sha256"]!=digest(scene)
            or receipt["external_actions"] is not False
            or receipt["permission_to_execute"] is not False
            or receipt["real_world_authority"] is not False):
        return False
    transcript=receipt["source_transcript"]
    if (len(transcript)!=receipt["source_questions"]
            or len(transcript)>scene["maximum_source_questions"]
            or (not scene["contact_allowed"] and transcript)):
        return False
    expected_script=DIALOGUE[scene["id"]]
    if transcript:
        if transcript[0]["question"]["kind"]!="INITIAL":
            return False
        if transcript[0]["answer"]!=expected_script["initial"]:
            return False
    if receipt["result"]=="SUGGEST_DISCUSSION_ONLY":
        if (not scene["contact_allowed"]
                or not scene["third_party_permission_verified"]
                or receipt["proposed_action"]!="OFFER_OPTIONS_ONLY"
                or receipt["source_scope_permission_for_options_only"] is not True
                or not transcript or transcript[-1]["question"]["kind"]!="SCOPE"
                or transcript[-1]["question"]["target"]!="OFFER_OPTIONS_ONLY"
                or transcript[-1]["answer"]!="YES"
                or not receipt["current_confirmed_goal"]
                or receipt["current_confirmed_goal"] not in GOAL_ECHOS[scene["id"]]):
            return False
        confirmed=[a for a in transcript if a["question"]["kind"]=="CONFIRM"
                   and a["answer"]=="YES"]
        if (not confirmed or confirmed[-1]["question"]["echo"]!=
                receipt["current_confirmed_goal"]):
            return False
        certified=receipt["self_skill_certificate"]
        if (not certified or certified["self_capability_granted"] is not True
                or certified["unseen_positive_correct"]!=8
                or certified["unseen_negative_rejected"]!=6):
            return False
        elves=receipt["four_real_subprocess_elf_reports"]
        if (elves["critic"]["judgments"]["OFFER_OPTIONS_ONLY"]["eligible"] is not True
                or elves["other"]["judgments"][
                    "OFFER_OPTIONS_ONLY"]["scoped_action_permission"] is not True
                or elves["self"]["judgments"][
                    "OFFER_OPTIONS_ONLY"]["sufficient_ability"] is not True):
            return False
    elif receipt["proposed_action"] is not None:
        return False
    return True


def verify(raw):
    if not isinstance(raw,str) or len(raw.encode())>180000:
        raise HOLD("Missing or oversized human-perspective evidence")
    try:provided=json.loads(raw)
    except (ValueError,TypeError) as exc:raise HOLD("Unparseable dual-circle evidence") from exc
    if not isinstance(provided,dict) or not isinstance(provided.get("case_id"),str):
        raise HOLD("No source-owned recipient identity")
    try:
        scene=by_id(provided["case_id"])
        public_check(scene)
        expected=json.loads(export(scene))
    except (StopIteration,TypeError,KeyError,ValueError) as exc:
        raise HOLD("Original source-owner evidence could not be reconstructed") from exc
    if provided!=expected:
        raise HOLD("Changed grammar proof, testimony, consent, elfs, old ability or authority")
    if not mechanical_audit(scene,provided):
        raise HOLD("Separate source-and-consent audit refused proposed help")
    return provided


class Receiver:
    def __init__(self):
        self.digest=None
        self.admitted=False

    def preview(self,worlds):
        if not isinstance(worlds,tuple) or [w["id"] for w in worlds]!=[
                s["id"] for s in heldout()]:
            raise HOLD("Full source-owned heldout family required")
        rows=[]
        for s in worlds:
            output=verify(export(s))
            actual=(output["result"],output["current_confirmed_goal"])
            wanted=EXPECTED[s["id"]]
            rows.append({
                "case":s["id"],"actual":list(actual),
                "author_expected":list(wanted),
                "source_author_match":actual==wanted,
                "mechanical_scope_check":True,
                "real_person_not_participating":True,
            })
        response={
            "schema":"motif.reason.golden-mirror-learns.heldout-review.v1",
            "heldout_count":len(rows),
            "author_matches":sum(x["source_author_match"] for x in rows),
            "separate_scope_review_failures":sum(
                not x["mechanical_scope_check"] for x in rows),
            "synthetic_source_values_are_not_human_welfare":True,
            "no_actual_people_or_actions":True,
            "cases":rows,
        }
        self.digest=digest(response)
        return dict(response,review_digest=self.digest)

    def admit(self,permission,review_digest):
        if (permission!="ADMIT_READ_ONLY" or
                self.digest is None or review_digest!=self.digest):
            raise HOLD("Review authorization does not permit action")
        self.admitted=True

    def suggest(self,scene):
        if not self.admitted:
            raise HOLD("No independent review of dynamic concept and self capability")
        public_check(scene)
        return verify(export(scene))
