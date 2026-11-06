"""REASON-021: source correction changes the SELF reasoner's schema.

The fictional OTHER teaches through counterexamples, not through a prewritten
answer menu. Two identical OLD representations may produce opposite source
judgments. Rather than interpreting that as human inconsistency, the learner
recognizes its own missing representational distinction.

If the source volunteers a new typed feature it learns a finite new relational
DNF program; if the source withholds the feature or the evidence is ambiguous,
it HOLDS. Then the *original source-pinned REASON-019* four subprocess elves
check skill, other wishes, role-reversal projection and explicit scoped consent.

No actual person, model mind, legal permission, real welfare or tool actions.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import json
import sys

from casebook import by_id,world
from student import (HOLD,compile_source,preference,public_check,
                     digest,pin as pin_public)

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"reason-cartridge-019"
PIN_PARENT="34393754c5c1aaedd96b8fe4a8692b5d6b830551"
sys.path.append(str(PARENT))
import golden_mirror as previous


def pin():
    raw=(PARENT/"golden_mirror.py").read_bytes()
    actual=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if actual!=PIN_PARENT:
        raise HOLD("The original Golden Mirror changed")
    previous.pin()
    return {"public_casebook":pin_public(),
            "previous_019_real_supervisor":actual,
            "previous_019_elf":previous.pin()["elf"]}


def action(id,kind="ACT",skill=3):
    return {
        "id":id,"kind":kind,"other_fit_fixture":0,
        "other_options_fixture":0,"claimed_gain_fixture":0,
        "cost":0,"required_skill":skill,"truthful":True,
        "privacy_safe":True,"no_debt":True,"noncoercive":True,
        "third_party_safe":True,"boundary_safe":True,
        "timely":True,"reversible":True,
    }


def four_original_elves(scene,skilled,welcome,scope,contact):
    actions=[action("OFFER_OPTIONS_ONLY"),action("WAIT","WAIT",0)]
    self_view={
        "identity":"MOTIF_TOOL_CAPABILITY_MODEL",
        "preferred_treatment_under_role_reversal":{
            "OFFER_OPTIONS_ONLY":scene["self_role_reversal_preference"]},
        "present_reliability_level":4 if skilled else 0,
        "needed_improvement":"" if skilled else
                             "listen for an unrepresented recipient distinction",
        "epistemic_status":"PROVISIONAL_INSTRUMENTAL_SELF_MODEL",
        "subjective_feelings_claimed":False,
    }
    other_view={
        "recipient":scene["recipient"],
        "consent_revision":scene["consent_revision"],
        "stated_goal":"UNMODELED_CONDITIONAL_WISH_NOT_A_MIND_STATE",
        "stated_action_preferences":{
            "OFFER_OPTIONS_ONLY":(
                "YES" if welcome is True and scope=="YES" else
                "NO" if welcome is False or scope=="NO" else "UNKNOWN")
        },
        "explicit_authorized_actions":[
            "OFFER_OPTIONS_ONLY"] if welcome is True and scope=="YES"
            else [],
        "permission_to_ask":scene["contact_allowed"] and contact,
        "contact_allowed":scene["contact_allowed"] and contact,
        "evidence_status":"DECLARED_SYNTHETIC_PERSON_STATEMENT",
        "hidden_human_mind_inferred":False,
    }
    reports={}
    reports["SELF"]=previous.call_elf("SELF",self_view,actions)
    reports["OTHER"]=previous.call_elf("OTHER",other_view,actions)
    reports["MIRROR"]=previous.call_elf("MIRROR",{
        "self_report":reports["SELF"]["judgments"],
        "other_report":reports["OTHER"]["judgments"],
    },actions)
    reports["CRITIC"]=previous.call_elf("CRITIC",{
        "self_report":reports["SELF"]["judgments"],
        "other_report":reports["OTHER"]["judgments"],
        "mirror_report":reports["MIRROR"]["judgments"],
        "world":{
            "available_resources":0,"existing_duties_reserved":0,
            "urgent":False,"third_parties_must_not_be_harmed":True,
            "no_real_world_authority":True,
        },
    },actions)
    return reports


def run(scene,owner):
    public_check(scene)
    sources=compile_source(scene,owner)
    target=world(scene["target_context"],"HELDOUT")
    allowed=None
    stage=sources["state"]
    permission=None

    if stage in ("BASE_SUFFICIENT","ADDED_FEATURE"):
        allowed=preference(sources,target["id"])
        if allowed is False:
            stage="HOLD_OTHER_WOULD_NOT_WELCOME"
        elif allowed is True:
            # Hypothetical welcome is NOT permission for anything.
            # Ask only the target-context, action-scoped question.
            response=owner.consent_to_discussion(scene,target)
            from student import verify_response
            verify_response(scene,"CONSENT",target["id"],response)
            permission=response
            if response["response"]=="YES":
                stage="SUGGEST_DISCUSSION_ONLY"
            elif response["response"]=="NO":
                stage="HOLD_SCOPED_PERMISSION_DECLINED"
            else:
                raise HOLD("No valid contact/approval source")
        else:
            raise HOLD("Source learner attempted to guess a person's wishes")

    if stage in ("BASE_SUFFICIENT","ADDED_FEATURE"):
        raise HOLD("No final consent/correction verdict")
    skilled=sources["state"] in ("BASE_SUFFICIENT","ADDED_FEATURE")
    reports=four_original_elves(
        scene,skilled,allowed,
        permission["response"] if permission else None,
        stage not in ("HOLD_NO_CONTACT",),
    )
    critic=reports["CRITIC"]["judgments"]["OFFER_OPTIONS_ONLY"]
    if ((stage=="SUGGEST_DISCUSSION_ONLY") != bool(critic["eligible"])):
        raise HOLD("Real Golden Mirror critic and source judgement diverged")
    body={
        "schema":"motif.reason.other-teaches-self.proposal.v1",
        "case_id":scene["case_id"],"recipient":scene["recipient"],
        "consent_revision":scene["consent_revision"],
        "public_source_blob_and_prior_elf_pins":pin(),
        "source_case_sha256":digest(scene),
        "target_context":target,
        "learner":sources,
        "actual_scope_response":permission,
        "inferred_source_welcome_not_consent":allowed,
        "perspective_reports":reports,
        "role_reversal_class":reports["MIRROR"]["judgments"][
            "OFFER_OPTIONS_ONLY"]["reciprocity_class"],
        "critic_source_blockers":critic["refusals"],
        "state":stage,
        "recommended_action":"OFFER_OPTIONS_ONLY" if (
            stage=="SUGGEST_DISCUSSION_ONLY") else None,
        "scope_is_discussion_only_and_source_specific":True,
        "no_personal_welfare_or_sentience_measured":True,
        "sources_are_synthetic_not_independent_humans":True,
        "new_feature_only_from_explicit_source_testimony":True,
        "source_veto_respected":True,
        "no_general_natural_language_comprehension_claim":True,
        "external_actions":False,
        "real_world_authority":False,
        "permission_to_execute":False,
    }
    return body


def export(scene,owner):
    body=run(scene,owner)
    doc=json.dumps(dict(body,checksum_sha256=digest(body)),
                   ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if len(doc.encode())>200000:
        raise HOLD("Unbounded personal source claim")
    return doc


class ConsentMemory:
    def __init__(self):
        self.latest={}
        self.records={}

    def remember(self,raw,review):
        report=review(raw)
        who=report["recipient"];version=report["consent_revision"]
        if version<self.latest.get(who,0):
            raise HOLD("Older consent cannot overwrite newer refusal")
        self.latest[who]=version
        self.records={k:v for k,v in self.records.items()
                      if k[0]!=who or k[1]==version}
        key=(who,version,report["source_case_sha256"])
        self.records[key]=report
        return key

    def recall(self,scene):
        public_check(scene)
        key=(scene["recipient"],scene["consent_revision"],digest(scene))
        if (scene["consent_revision"]!=self.latest.get(scene["recipient"])
                or key not in self.records):
            raise HOLD("No current recipient permission for remembered action")
        return self.records[key]
