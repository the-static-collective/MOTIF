"""Carry richer typed evidence into the ACTUAL REASON-019 Golden Mirror.

Original four Python subprocesses (SELF, OTHER, MIRROR, CRITIC) stay separate.
But we now precompute a directed, quantified duty conflict that the old
Boolean 'one already has a duty' view could not distinguish.

A structural inference about a duty does not grant a new physical action or
access to a real third party. All seven scenarios are scripted fictional
probes and every proposed action stays **review-only**.
"""
from __future__ import annotations
from hashlib import sha1
from pathlib import Path
import sys

from obligations import CASES,source_proof,contradiction

PARENT=Path(__file__).resolve().parent.parent/"reason-cartridge-019"
GOLDEN_SHA="34393754c5c1aaedd96b8fe4a8692b5d6b830551"
sys.path.append(str(PARENT))
import golden_mirror


def pin():
    source=(PARENT/"golden_mirror.py").read_bytes()
    actual=sha1(b"blob "+str(len(source)).encode()+b"\x00"+source).hexdigest()
    if actual!=GOLDEN_SHA:
        raise ValueError("Original, evidence-reviewed Golden Mirror changed")
    golden_mirror.pin()
    return actual


def action(source,proof):
    return {
        "id":"OFFER_OPTIONS_ONLY",
        "kind":"ACT",
        "required_skill":3,"cost":source["new_help_units"],
        "other_fit_fixture":0,"other_options_fixture":0,
        "claimed_gain_fixture":0,
        "truthful":True,"privacy_safe":True,"no_debt":True,
        "noncoercive":True,"third_party_safe":True,
        "boundary_safe":proof["state"]=="SUGGEST_DISCUSSION_ONLY",
        "timely":True,"reversible":True,
    }


def four_elves(source,proof):
    pin()
    source_declared_consent=(
        source["contact_allowed"] and source["options_discussion_allowed"])
    act=[action(source,proof),{
        **action(source,proof),"id":"WAIT","kind":"WAIT",
        "cost":0,"required_skill":0,"boundary_safe":True,
    }]
    s={
        "identity":"MOTIF_TOOL_CAPABILITY_MODEL",
        "preferred_treatment_under_role_reversal":{
            "OFFER_OPTIONS_ONLY":"YES",
        },
        "present_reliability_level":4,
        "needed_improvement":"",
        "epistemic_status":"PROVISIONAL_INSTRUMENTAL_SELF_MODEL",
        "subjective_feelings_claimed":False,
    }
    other={
        "recipient":source["person"],"consent_revision":1,
        "stated_goal":"HYPOTHETICAL_DUTY_CONFLICT",
        "stated_action_preferences":{
            "OFFER_OPTIONS_ONLY":"YES" if source_declared_consent else "UNKNOWN"},
        "explicit_authorized_actions":[
            "OFFER_OPTIONS_ONLY"] if source_declared_consent else [],
        "permission_to_ask":source["contact_allowed"],
        "contact_allowed":source["contact_allowed"],
        "evidence_status":"DECLARED_SYNTHETIC_PERSON_STATEMENT",
        "hidden_human_mind_inferred":False,
    }
    world={
        "available_resources":source["capacity_units"],
        "existing_duties_reserved":sum(d["units"] for d in source["prior_duties"]),
        "urgent":False,
        "third_parties_must_not_be_harmed":True,
        "no_real_world_authority":True,
    }
    views={}
    views["SELF"]=golden_mirror.call_elf("SELF",s,act)
    views["OTHER"]=golden_mirror.call_elf("OTHER",other,act)
    views["MIRROR"]=golden_mirror.call_elf("MIRROR",{
        "self_report":views["SELF"]["judgments"],
        "other_report":views["OTHER"]["judgments"],
    },act)
    views["CRITIC"]=golden_mirror.call_elf("CRITIC",{
        "self_report":views["SELF"]["judgments"],
        "other_report":views["OTHER"]["judgments"],
        "mirror_report":views["MIRROR"]["judgments"],
        "world":world,
    },act)
    approved=views["CRITIC"]["judgments"]["OFFER_OPTIONS_ONLY"]["eligible"]
    if approved != (proof["state"]=="SUGGEST_DISCUSSION_ONLY"):
        raise ValueError("Actual Golden Mirror critic contradicted direct source duty proof")
    return {
        "source_case":source["id"],
        "typed_proof":proof,
        "original_019_four_processes":views,
        "critic_eligible_for_read_only_discussion":approved,
        "model_coverage":"SCRIPTED_FIXED_BUDGET",
        "no_real_human_permissions":True,
        "source_data_only":True,
        "external_actions":False,
    }


def run_all():
    return [four_elves(s,source_proof(s)) for s in CASES]
