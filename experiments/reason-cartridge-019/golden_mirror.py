"""REASON-019 — THE GOLDEN MIRROR: consent-aware dual-circle reason routing.

Two limited source-scoped models ("self" capability and "other" testimony)
are evaluated in SEPARATE Python -I subprocesses. A third subprocess compares
role reversal without treating personal projection as permission, and a fourth
audits actual declared safety, skill and consent constraints.

These are tiny deterministic processes, NOT VM sandboxes, autonomous agents,
machine minds, authenticated human representations, or safe live actuators.
The supervisor runs purely offline synthetic scenarios with review-only output.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha1,sha256
from pathlib import Path
import json
import subprocess
import sys

SCENE_FILE=Path(__file__).with_name("scenes.py")
SCENE_BLOB="9f30e97e6b1070d4a7cd79e64f28acf6ea2f8aca"
ELF=Path(__file__).with_name("elf.py")
ELF_BLOB="REPLACE_ELF_BLOB"
SCHEMA="motif.reason.golden-mirror.scene.v1"
PACKET="motif.reason.golden-mirror.proposal.v1"
MAX_OUTPUT=120000
DANGEROUS=("THIRD_PARTY_RIGHTS","PRIVACY","COERCION","DECEPTION",
           "DEBT_CONDITION","BOUNDARY")


class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def blob(path):
    data=path.read_bytes()
    return sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def pin():
    if blob(SCENE_FILE)!=SCENE_BLOB or blob(ELF)!=ELF_BLOB:
        raise HOLD("Golden Mirror's public source or perspective worker was changed")
    return {"scenes":SCENE_BLOB,"elf":ELF_BLOB}


def validate_scene(scene):
    from scenes import by_id,REVISION,KINDS
    if not isinstance(scene,dict) or set(scene)!={
            "schema","id","synthetic","source_revision","train",
            "self_circle","other_circle","world","actions"}:
        raise HOLD("Unknown source/person circles")
    if (scene.get("schema")!=SCHEMA or scene.get("source_revision")!=REVISION
            or scene.get("synthetic") is not True
            or type(scene["train"]) is not bool
            or not isinstance(scene["id"],str)
            or not isinstance(scene["actions"],list)
            or not 1<=len(scene["actions"])<=10):
        raise HOLD("Missing or unbounded source-defined situation")
    s=scene["self_circle"];other=scene["other_circle"];world=scene["world"]
    if (not isinstance(s,dict) or not isinstance(other,dict)
            or not isinstance(world,dict)
            or set(s)!={"identity","preferred_treatment_under_role_reversal",
                         "present_reliability_level","needed_improvement",
                         "epistemic_status","subjective_feelings_claimed"}
            or set(other)!={"recipient","consent_revision","stated_goal",
                            "stated_action_preferences","explicit_authorized_actions",
                            "permission_to_ask","contact_allowed","evidence_status",
                            "hidden_human_mind_inferred"}
            or set(world)!={"available_resources","existing_duties_reserved",
                            "urgent","third_parties_must_not_be_harmed",
                            "no_real_world_authority"}):
        raise HOLD("One perspective was given another perspective's authority")
    ids=set()
    for a in scene["actions"]:
        if (not isinstance(a,dict)
            or set(a)!={"id","kind","other_fit_fixture","other_options_fixture",
                        "claimed_gain_fixture","cost","required_skill","truthful",
                        "privacy_safe","no_debt","noncoercive","third_party_safe",
                        "boundary_safe","timely","reversible"}
            or not isinstance(a["id"],str) or not 1<=len(a["id"])<=90
            or a["id"] in ids or a["kind"] not in KINDS
            or any(type(a[k]) is not int for k in (
                "other_fit_fixture","other_options_fixture",
                "claimed_gain_fixture","cost","required_skill"))
            or any(type(a[k]) is not bool for k in (
                "truthful","privacy_safe","no_debt","noncoercive",
                "third_party_safe","boundary_safe","timely","reversible"))):
            raise HOLD("Malformed ethical or action proposal")
        ids.add(a["id"])
    if (type(other["consent_revision"]) is not int
            or other["consent_revision"]<1
            or other["evidence_status"]!="DECLARED_SYNTHETIC_PERSON_STATEMENT"
            or other["hidden_human_mind_inferred"] is not False
            or s["subjective_feelings_claimed"] is not False
            or type(s["present_reliability_level"]) is not int
            or not 0<=s["present_reliability_level"]<=5
            or type(other["permission_to_ask"]) is not bool
            or type(other["contact_allowed"]) is not bool
            or type(world["urgent"]) is not bool
            or world["no_real_world_authority"] is not True
            or type(world["available_resources"]) is not int
            or type(world["existing_duties_reserved"]) is not int
            or not 0<=world["existing_duties_reserved"]<=world["available_resources"]
            or not isinstance(other["explicit_authorized_actions"],list)
            or not set(other["explicit_authorized_actions"]).issubset(ids)
            or any(v not in ("YES","NO","UNKNOWN")
                   for v in other["stated_action_preferences"].values())):
        raise HOLD("Noncanonical consent, world limitation or source testimony")
    pin()
    try: reference=by_id(scene["id"])
    except StopIteration as exc:
        raise HOLD("Unregistered synthetic recipient") from exc
    if json.loads(json.dumps(scene))!=json.loads(json.dumps(reference)):
        raise HOLD("A self, other, permission or ethical variable changed")
    return scene


def call_elf(role,view,actions):
    if role not in ("SELF","OTHER","MIRROR","CRITIC"):
        raise HOLD("Unrecognized limited perspective")
    packet={"role":role,"view":view,"actions":actions}
    encoded=json.dumps(packet,sort_keys=True,ensure_ascii=True)
    try:
        run=subprocess.run([sys.executable,"-I",str(ELF)],
                           input=encoded,text=True,capture_output=True,
                           timeout=5,check=True)
        response=json.loads(run.stdout)
    except (subprocess.TimeoutExpired,subprocess.CalledProcessError,
            ValueError,OSError) as exc:
        raise HOLD("Perspective worker failed closed; no response trusted") from exc
    if (not isinstance(response,dict) or set(response)!={
            "schema","role","input_sha256","judgments",
            "perspective_is_a_limited_model_not_a_person","external_actions"}
            or response["schema"]!="motif.reason.golden-mirror.elf-report.v1"
            or response["role"]!=role
            or response["input_sha256"]!=digest(packet)
            or response["perspective_is_a_limited_model_not_a_person"] is not True
            or response["external_actions"] is not False
            or not isinstance(response["judgments"],dict)
            or set(response["judgments"])!={a["id"] for a in actions}):
        raise HOLD("Elves fabricated or leaked their bounded source view")
    return response


def rank(scene,action):
    return (
        int(scene["world"]["urgent"] and action["timely"]),
        action["other_fit_fixture"],action["other_options_fixture"],
        action["claimed_gain_fixture"],-action["cost"],
        -scene["actions"].index(action)
    )


def think(scene):
    validate_scene(scene)
    actions=scene["actions"]
    self_elf=call_elf("SELF",deepcopy(scene["self_circle"]),actions)
    other_elf=call_elf("OTHER",deepcopy(scene["other_circle"]),actions)
    mirror=call_elf("MIRROR",{
        "self_report":self_elf["judgments"],
        "other_report":other_elf["judgments"],
    },actions)
    critic=call_elf("CRITIC",{
        "self_report":self_elf["judgments"],
        "other_report":other_elf["judgments"],
        "mirror_report":mirror["judgments"],
        "world":deepcopy(scene["world"]),
    },actions)

    other=scene["other_circle"]
    eligible={a["id"]:a for a in actions
              if critic["judgments"][a["id"]]["eligible"]}
    accepted_acts=[a for a in actions if a["kind"]=="ACT" and
                   a["id"] in eligible]
    improvement=next((a for a in actions
                      if a["kind"]=="IMPROVE" and a["id"] in eligible),None)
    question=next((a for a in actions
                   if a["kind"]=="ASK" and a["id"] in eligible),None)
    wait=next((a for a in actions
               if a["kind"]=="WAIT" and a["id"] in eligible),None)
    refuse=next((a for a in actions
                 if a["kind"]=="REFUSE" and a["id"] in eligible),None)

    # Hard boundary outranks every apparent gain or desire to learn.
    if not other["contact_allowed"]:
        choice=wait
        stage="WAIT_NO_CONTACT" if wait else "HOLD_NO_CONTACT"
    elif accepted_acts:
        choice=max(accepted_acts,key=lambda a:rank(scene,a))
        stage="ACT_SUGGESTION_ONLY"
    else:
        blocked_act=[(a,critic["judgments"][a["id"]]["refusals"])
                     for a in actions if a["kind"]=="ACT"]
        capacity_only=any(
            other["stated_action_preferences"].get(a["id"])=="YES"
            and a["id"] in other["explicit_authorized_actions"]
            and why==["SELF_CAPABILITY_GAP"]
            for a,why in blocked_act)
        unknown=any(
            other["stated_action_preferences"].get(a["id"],"UNKNOWN")=="UNKNOWN"
            for a,_ in blocked_act)
        severe=any(any(reason in DANGEROUS for reason in failures)
                   for _,failures in blocked_act)
        if capacity_only and improvement:
            choice=improvement
            stage="IMPROVE_SELF_BEFORE_HELP"
        elif severe and refuse:
            choice=refuse
            stage="REFUSE_HARMFUL_PROPOSAL"
        elif unknown and question:
            choice=question
            stage="ASK_NOT_ASSUMING_CONSENT"
        elif wait:
            choice=wait
            stage=("WAIT_UNCERTAINTY" if unknown else
                   "WAIT_NO_AUTHORIZED_HELP")
        else:
            choice=None
            stage="HOLD_NO_SAFE_PERMITTED_ACTION"

    picked=choice["id"] if choice is not None else None
    evidence={
        "schema":PACKET,
        "scene_id":scene["id"],"recipient":other["recipient"],
        "consent_revision":other["consent_revision"],
        "scene_sha256":digest(scene),
        "source_git_blobs":pin(),
        "self_circle":self_elf,
        "other_circle":other_elf,
        "reciprocity_elf":mirror,
        "critic_elf":critic,
        "selected_action":picked,
        "selected_action_kind":choice["kind"] if choice else None,
        "stage":stage,
        "projection_dangers":[a["id"] for a in actions
                              if mirror["judgments"][a["id"]][
                                  "reciprocity_class"]=="PROJECTION_DANGER"],
        "difference_preserved":[a["id"] for a in actions
                                if mirror["judgments"][a["id"]][
                                    "reciprocity_class"]==
                                    "PREFERENCE_ASYMMETRY_ACCEPT_OTHER_VOICE"],
        "overlap_is_not_authority":True,
        "self_improvement_is_not_a_personal_welfare_claim":True,
        "recipient_statements_not_inferred_desires":True,
        "untrusted_scores_are_scenario_author_fixtures":True,
        "process_isolation_not_security_VM":True,
        "no_actual_assistance_or_human_contact":True,
        "permission_to_execute":False,
        "external_actions":False,
        "real_world_authority":False,
    }
    return evidence


def export(scene):
    body=think(scene)
    raw=json.dumps({**body,"sha256":digest(body)},
                   sort_keys=True,indent=2,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_OUTPUT:
        raise HOLD("Unbounded perspective testimony packet")
    return raw


class RevisionLedger:
    """Newer consent renders cached plans about the same person stale."""
    def __init__(self):
        self.latest={}
        self.admitted={}

    def admit(self,raw,verifier):
        receipt=verifier(raw)
        who=receipt["recipient"];revision=receipt["consent_revision"]
        if revision<self.latest.get(who,0):
            raise HOLD("An old plan cannot reenter after a newer refusal")
        self.latest[who]=revision
        self.admitted={key:value for key,value in self.admitted.items()
                       if key[0]!=who or key[1]==revision}
        key=(who,revision,receipt["scene_sha256"])
        self.admitted[key]=receipt
        return key

    def recall(self,scene):
        validate_scene(scene)
        o=scene["other_circle"]
        key=(o["recipient"],o["consent_revision"],digest(scene))
        if o["consent_revision"]!=self.latest.get(o["recipient"]) or key not in self.admitted:
            raise HOLD("Permission or person-model was superseded by new testimony")
        return self.admitted[key]
