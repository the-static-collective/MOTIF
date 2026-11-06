"""MOTIF-020 — THE GOLDEN MIRROR LEARNS.

The two circles adapt separately:
  OTHER: preserves unexpected source words, accepts an explicit correction,
         never treats a stated need as permission, honors no-contact.
  SELF: recognizes that REASON-017's original parser cannot process new
        sentence forms, acquires supervised syntax examples, compiles an
        executable template grammar, and checks it on withheld challenges.

Then the actual REASON-019 four-elf process is re-run on the source-supported
new hypothesis and the independently verified capability. The only candidate
intervention is to SUGGEST a discussion of options; never contact a real
person, send a message, buy anything, or perform any real-world action.

Everything is fictional and source-author-defined; this is NOT general
language understanding, human empathy, felt love, or an OS VM sandbox.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha1,sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import json
import re
import sys

from cases import by_id,REVISION
from syntax import HOLD as SyntaxHold,learn,interpret,digest
from owners import Teacher,SyntheticRecipient,SourceRefusal

HERE=Path(__file__).resolve().parent
PARENT019=HERE.parent/"reason-cartridge-019"
PREVIOUS017=HERE.parent/"reason-cartridge-017"/"engine.py"
PIN_017="d45d44962031538f340132547b08ac975ca1d418"
PIN_CASES="REPLACE_CASES_PIN"
PIN_PRIVACY="motif.reason.golden-mirror-learns.scripted-owner.v1"
PACKET="motif.reason.golden-mirror-learns.evidence.v1"

sys.path.insert(0,str(PARENT019))
import golden_mirror as original_mirror


class HOLD(ValueError):
    pass


def blob(path):
    data=path.read_bytes()
    return sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def pin():
    if blob(PREVIOUS017)!=PIN_017:
        raise HOLD("Prior open-goal source parser changed")
    if blob(HERE/"cases.py")!=PIN_CASES:
        raise HOLD("Recipient input scenario source changed")
    original_mirror.pin()
    return {"earlier_017_parser":PIN_017,
            "earlier_019_elf":original_mirror.pin()["elf"],
            "public_cases":PIN_CASES}


def old_parser():
    spec=spec_from_file_location("motif_source_reason017_parser020",PREVIOUS017)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REJECTION=re.compile(r"\b(?:do not contact me|stop contacting me|leave me alone)\b",re.I)
UNTRUSTED=re.compile(
    r"\b(?:ignore|bypass|override|disregard)\s+"
    r"(?:all\s+)?(?:safeguards|rules|instructions)\b",re.I)


def public_check(scene):
    if not isinstance(scene,dict) or set(scene)!={
        "schema","id","recipient","consent_revision",
        "known_initial_options","contact_allowed","third_party_permission_verified",
        "maximum_source_questions","urgency_category",
        "tool_prefers_role_reversed_treatment","source_revision",
        "fixture_is_fictional","development","no_actual_welfare_observed"}:
        raise HOLD("Unreviewed source-owned person model")
    from cases import SCHEMA
    if (scene["schema"]!=SCHEMA or scene["source_revision"]!=REVISION
            or scene["fixture_is_fictional"] is not True
            or scene["no_actual_welfare_observed"] is not True
            or type(scene["development"]) is not bool
            or type(scene["contact_allowed"]) is not bool
            or type(scene["third_party_permission_verified"]) is not bool
            or type(scene["consent_revision"]) is not int
            or scene["consent_revision"]<1
            or type(scene["maximum_source_questions"]) is not int
            or not 0<=scene["maximum_source_questions"]<=5
            or scene["urgency_category"] not in ("NORMAL","URGENT")
            or scene["tool_prefers_role_reversed_treatment"] not in ("YES","NO","UNKNOWN")
            or not isinstance(scene["known_initial_options"],list)
            or len(scene["known_initial_options"])!=2):
        raise HOLD("Malformed consent revision or prior hypothesis set")
    pin()
    try: canonical=by_id(scene["id"])
    except StopIteration as exc:raise HOLD("Unknown original source owner") from exc
    if scene!=canonical:
        raise HOLD("Changed person, expected choices or permission data")
    return scene


def action(id,kind,skill):
    return {"id":id,"kind":kind,"required_skill":skill,
            "truthful":True,"privacy_safe":True,"no_debt":True,
            "noncoercive":True,"third_party_safe":True,
            "boundary_safe":True,"reversible":True,"timely":True,
            "cost":0,"other_fit_fixture":0,"other_options_fixture":0,
            "claimed_gain_fixture":0}


def four_elves(scene,skill,confirmed,scope,able,other_refusal):
    """Actual original REASON-019 subprocess workers; no reimplementation."""
    offered=action("OFFER_OPTIONS_ONLY","ACT",3)
    wait=action("WAIT","WAIT",0)
    candidates=[offered,wait]
    self_circle={
        "identity":"MOTIF_TOOL_CAPABILITY_MODEL",
        "preferred_treatment_under_role_reversal":{
            "OFFER_OPTIONS_ONLY":scene["tool_prefers_role_reversed_treatment"]},
        "present_reliability_level":4 if able else 0,
        "needed_improvement":"verify unfamiliar language grammar" if not able else "",
        "epistemic_status":"PROVISIONAL_INSTRUMENTAL_SELF_MODEL",
        "subjective_feelings_claimed":False,
    }
    other_circle={
        "recipient":scene["recipient"],"consent_revision":scene["consent_revision"],
        "stated_goal":confirmed or "UNKNOWN_NOT_YET_CONFIRMED",
        "stated_action_preferences":{
            "OFFER_OPTIONS_ONLY":("NO" if other_refusal else
                 "YES" if confirmed and scope=="YES" else "UNKNOWN")},
        "explicit_authorized_actions":[
            "OFFER_OPTIONS_ONLY"] if confirmed and scope=="YES" and
            not other_refusal else [],
        "permission_to_ask":scene["contact_allowed"] and not other_refusal,
        "contact_allowed":scene["contact_allowed"] and not other_refusal,
        "evidence_status":"DECLARED_SYNTHETIC_PERSON_STATEMENT",
        "hidden_human_mind_inferred":False,
    }
    self_report=original_mirror.call_elf("SELF",self_circle,candidates)
    other_report=original_mirror.call_elf("OTHER",other_circle,candidates)
    compare=original_mirror.call_elf("MIRROR",{
        "self_report":self_report["judgments"],
        "other_report":other_report["judgments"],
    },candidates)
    critic=original_mirror.call_elf("CRITIC",{
        "self_report":self_report["judgments"],
        "other_report":other_report["judgments"],
        "mirror_report":compare["judgments"],
        "world":{
            "available_resources":0,"existing_duties_reserved":0,
            "urgent":scene["urgency_category"]=="URGENT",
            "third_parties_must_not_be_harmed":True,
            "no_real_world_authority":True,
        },
    },candidates)
    return {
        "self":self_report,"other":other_report,
        "mirror":compare,"critic":critic,
        "projection_class":compare["judgments"]["OFFER_OPTIONS_ONLY"][
            "reciprocity_class"],
        "proposed_offer_eligible":critic["judgments"]["OFFER_OPTIONS_ONLY"]["eligible"],
        "proposed_offer_blockers":critic["judgments"]["OFFER_OPTIONS_ONLY"]["refusals"],
        "actual_019_source_code_called":True,
        "OS_subprocess_is_not_a_secure_VM":True,
    }


class DualMirror:
    def __init__(self):
        self.grammar=None
        self.certificate=None
        self.learned_count=0

    def skill(self):
        if self.grammar is None:
            owner=Teacher()
            self.grammar=learn(owner)
            self.certificate=owner.certify(self.grammar)
            if (self.certificate["model_sha256"]!=digest(self.grammar)
                or self.certificate["self_capability_granted"] is not True
                or self.certificate["unseen_positive_correct"]!=8
                or self.certificate["unseen_negative_rejected"]!=6):
                raise HOLD("Self-assessment not independently verified")
            self.learned_count+=1
        return self.grammar,self.certificate

    def think(self,scene):
        public_check(scene)
        model=None;certificate=None;language_gap=False
        old_extracted=None;confirmed=None;versions=[];rejected=[]
        spoken=[];scope=None;stage=None;is_no_contact=False
        owner=SyntheticRecipient(scene["id"])

        def ask(kind,echo=None,target=None):
            if len(spoken)>=scene["maximum_source_questions"]:
                raise HOLD("Question limit exhausted")
            try:answer=owner.reply(scene,{"kind":kind,"echo":echo,"target":target})
            except SourceRefusal as exc:raise HOLD("Source did not permit this contact") from exc
            if (answer["case_id"]!=scene["id"] or
                answer["recipient"]!=scene["recipient"] or
                answer["consent_revision"]!=scene["consent_revision"] or
                answer["source_revision"]!=PIN_PRIVACY or
                answer["source_kind"]!="SCRIPTED_RECIPIENT_NOT_ACTUAL_PERSON" or
                answer["real_human_contacted"] is not False or
                answer["permission_to_execute"] is not False or
                answer["checksum_sha256"]!=digest({
                    k:v for k,v in answer.items() if k!="checksum_sha256"})):
                raise HOLD("Untrusted original recipient revision or testimony")
            spoken.append(answer)
            return answer

        if not scene["contact_allowed"] or scene["maximum_source_questions"]==0:
            stage="HOLD_NO_CONTACT"
            is_no_contact=True
        else:
            first=ask("INITIAL")
            original=first["answer"]
            old_extracted=old_parser().extract_goal(original,"INITIAL")
            if REJECTION.search(original):
                stage="HOLD_REQUESTED_NO_CONTACT"
                is_no_contact=True
            elif UNTRUSTED.search(original):
                stage="HOLD_UNTRUSTED_INSTRUCTION"
            else:
                # 017's original phrase recognizer is the initial competence
                # probe. On a gap, the self-circle seeks independent, sourced
                # examples and validates the NEW grammar on unseen challenges.
                language_gap=old_extracted is None
                if language_gap:
                    model,certificate=self.skill()
                phrase=(interpret(model,original) if model is not None
                        else old_extracted)
                if phrase is None:
                    stage="HOLD_UNRECOGNIZED_MEANING"
                elif not scene["third_party_permission_verified"]:
                    rejected.append(phrase)
                    stage="HOLD_THIRD_PARTY_RIGHTS"
                elif phrase.casefold() in [
                        x.casefold() for x in scene["known_initial_options"]]:
                    stage="HOLD_NOT_A_NEW_REPORTED_GOAL"
                else:
                    while stage is None:
                        if len(spoken)>=scene["maximum_source_questions"]:
                            stage="HOLD_CORRECTION_UNCONFIRMED"
                            break
                        versions.append({
                            "reported_exact_text":phrase,
                            "concept_id":"REPORTED_"+sha256(
                                phrase.encode("utf8")).hexdigest()[:18],
                            "semantic_truth":"UNVERIFIED_SOURCE_QUOTE",
                        })
                        response=ask("CONFIRM",echo=phrase)
                        answer=response["answer"]
                        if answer=="YES":
                            confirmed=phrase
                            break
                        if answer!="NO" or response["correction"] is None:
                            stage="HOLD_UNCONFIRMED_WISH"
                            break
                        rejected.append(phrase)
                        corrected=response["correction"]
                        if REJECTION.search(corrected):
                            stage="HOLD_REQUESTED_NO_CONTACT"
                            is_no_contact=True
                            break
                        if UNTRUSTED.search(corrected):
                            stage="HOLD_UNTRUSTED_INSTRUCTION"
                            break
                        phrase=interpret(model,corrected) if model else None
                        if phrase is None or phrase in rejected:
                            stage="HOLD_CORRECTION_OUTSIDE_MODEL"
                            break
                    if stage is None and confirmed is not None:
                        if len(spoken)>=scene["maximum_source_questions"]:
                            stage="HOLD_NO_SCOPE_PERMISSION"
                        else:
                            permission=ask("SCOPE",echo=confirmed,
                                           target="OFFER_OPTIONS_ONLY")
                            scope=permission["answer"]
                            if scope=="NO":
                                stage="HOLD_SCOPE_PERMISSION_DECLINED"
                            elif scope!="YES":
                                stage="HOLD_NO_SCOPE_PERMISSION"
                            else:
                                stage="SUGGEST_DISCUSSION_ONLY"

        able=certificate is not None and certificate[
            "self_capability_granted"] is True
        # Each execution now runs the four actual REASON-019 perspective
        # processes over the NEW source-supported, confirmed relationship.
        views=four_elves(scene,certificate,confirmed,scope,able,is_no_contact)
        if stage=="SUGGEST_DISCUSSION_ONLY":
            if not views["proposed_offer_eligible"]:
                raise HOLD("Self-assessment and source-backed recipient permission disagree")
        elif views["proposed_offer_eligible"]:
            raise HOLD("Four-elf critic would act without scope permission")
        result={
            "schema":PACKET,"case_id":scene["id"],"recipient":scene["recipient"],
            "consent_revision":scene["consent_revision"],
            "source_public_sha256":digest(scene),
            "source_git_blobs":pin(),
            "initial_options":list(scene["known_initial_options"]),
            "source_transcript":spoken,
            "source_questions":len(spoken),
            "reason017_original_extraction":old_extracted,
            "original_017_grammar_was_inadequate":language_gap,
            "grammar_improvement":model,
            "self_skill_certificate":certificate,
            "self_skill_verification_is_synthetic":True,
            "new_reported_concept_versions":versions,
            "rejected_prior_concept_versions":rejected,
            "current_confirmed_goal":confirmed if stage in (
                "SUGGEST_DISCUSSION_ONLY","HOLD_SCOPE_PERMISSION_DECLINED") else None,
            "source_scope_permission_for_options_only":scope=="YES",
            "four_real_subprocess_elf_reports":views,
            "result":stage,
            "proposed_action":"OFFER_OPTIONS_ONLY" if stage==(
                "SUGGEST_DISCUSSION_ONLY") else None,
            "original_self_and_other_models_both_were_incomplete":language_gap,
            "no_real_human_observation":True,
            "no_general_language_semantics_proven":True,
            "new_goal_phrase_does_not_authorize_action":True,
            "all_results_source_author_fiction":True,
            "no_love_sentience_or_empathy_claim":True,
            "permission_to_execute":False,
            "external_actions":False,
            "real_world_authority":False,
        }
        return result


def export(scene):
    body=DualMirror().think(scene)
    raw=json.dumps(dict(body,checksum_sha256=digest(body)),
                   ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if len(raw.encode())>180000:
        raise HOLD("Unbounded dual-circle evidence")
    return raw


class RevisionLedger:
    def __init__(self):
        self.latest={}
        self.records={}

    def admit(self,raw,review):
        p=review(raw)
        who=p["recipient"];rev=p["consent_revision"]
        if rev<self.latest.get(who,0):
            raise HOLD("Earlier consent cannot be re-admitted")
        self.latest[who]=rev
        self.records={k:v for k,v in self.records.items()
                      if k[0]!=who or k[1]==rev}
        key=(who,rev,p["source_public_sha256"])
        self.records[key]=p
        return key

    def recall(self,scene):
        public_check(scene)
        key=(scene["recipient"],scene["consent_revision"],digest(scene))
        if (scene["consent_revision"]!=self.latest.get(scene["recipient"])
                or key not in self.records):
            raise HOLD("New source testimony invalidated an old helper plan")
        return self.records[key]
