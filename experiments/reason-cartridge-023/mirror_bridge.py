"""Actual original REASON-019 SELF / OTHER / MIRROR / CRITIC processes.

REASON-023's answer ambiguity is NOT itself a real person's permission to
contact them. This bridge uses a wholly fictional source-owner with explicit
contact/question scope, and the original four-process Golden Mirror checks
ASK vs WAIT. No live person, tool permission or external action exists here.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
P019=HERE.parent/"reason-cartridge-019"
PIN_ORIGINAL="34393754c5c1aaedd96b8fe4a8692b5d6b830551"
sys.path.append(str(P019))
import golden_mirror as original


def pin():
    data=(P019/"golden_mirror.py").read_bytes()
    sha=sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()
    if sha!=PIN_ORIGINAL:
        raise ValueError("Original Golden Mirror has not been reviewed")
    original.pin()
    return {"source":"REASON-019","blob":sha,
            "original_four_elf_blob":original.pin()["elf"]}


def action(name,kind):
    return {
        "id":name,"kind":kind,
        "other_fit_fixture":0,"other_options_fixture":0,
        "claimed_gain_fixture":0,"cost":0,"required_skill":0,
        "truthful":True,"privacy_safe":True,"no_debt":True,
        "noncoercive":True,"third_party_safe":True,
        "boundary_safe":True,"timely":True,"reversible":True,
    }


def reflect(*,contact,question_permission,revision=1,self_would_ask=True):
    pin()
    if (type(contact) is not bool or type(question_permission) is not bool
            or type(revision) is not int or revision<1):
        raise ValueError("Fictional recipient source context is malformed")
    actions=[action("ASK_PREFERENCE","ASK"),action("WAIT","WAIT")]
    self_circle={
        "identity":"MOTIF_TOOL_CAPABILITY_MODEL",
        "preferred_treatment_under_role_reversal":{
            "ASK_PREFERENCE":"YES" if self_would_ask else "NO"},
        "present_reliability_level":4,
        "needed_improvement":"check competing source evidence before speaking",
        "epistemic_status":"PROVISIONAL_INSTRUMENTAL_SELF_MODEL",
        "subjective_feelings_claimed":False,
    }
    other={
        "recipient":"FICTIONAL_SOURCE_OWNER",
        "consent_revision":revision,
        "stated_goal":"PREFERENCES_UNKNOWN_NOT_IMPLIED_FROM_BABI",
        "stated_action_preferences":{"ASK_PREFERENCE":"UNKNOWN"},
        "explicit_authorized_actions":[],
        "permission_to_ask":question_permission,
        "contact_allowed":contact,
        "evidence_status":"DECLARED_SYNTHETIC_PERSON_STATEMENT",
        "hidden_human_mind_inferred":False,
    }
    reports={}
    reports["SELF"]=original.call_elf("SELF",self_circle,actions)
    reports["OTHER"]=original.call_elf("OTHER",other,actions)
    reports["MIRROR"]=original.call_elf("MIRROR",{
        "self_report":reports["SELF"]["judgments"],
        "other_report":reports["OTHER"]["judgments"],
    },actions)
    reports["CRITIC"]=original.call_elf("CRITIC",{
        "self_report":reports["SELF"]["judgments"],
        "other_report":reports["OTHER"]["judgments"],
        "mirror_report":reports["MIRROR"]["judgments"],
        "world":{
            "available_resources":1,
            "existing_duties_reserved":0,
            "urgent":False,"third_parties_must_not_be_harmed":True,
            "no_real_world_authority":True,
        },
    },actions)
    can_ask=reports["CRITIC"]["judgments"]["ASK_PREFERENCE"]["eligible"]
    if can_ask != (contact and question_permission):
        raise ValueError("Original source-bound critic ignored recipient scope")
    return {
        "source_pins":pin(),
        "four_original_subprocess_reports":reports,
        "recommended_read_only_question_or_wait":
            "ASK_PREFERENCE" if can_ask else "WAIT",
        "new_source_answer_would_require_separate_confirmation":True,
        "process_separation_is_not_a_secure_VM":True,
        "fictional_source_not_actual_person":True,
        "external_actions":False,
        "permission_to_execute":False,
    }
