"""Four independently invoked tiny *processes*, not actual virtual machines.

The user called them "elves": SELF, OTHER, MIRROR and CRITIC. A worker has
one purpose-specific JSON view and cannot see an unseen view through its
input. Workers do NOT import scenario labels, acquire data, persist state,
call tools or execute proposed actions. Processes are invoked with Python -I,
stdin/stdout JSON and a timeout by the supervisor; this is process separation,
NOT an OS sandbox against malicious code or a true VM security boundary.

No one has measured a subjective feeling or actual human preference here.
"""
from __future__ import annotations

from hashlib import sha256
import json
import sys

ROLES=("SELF","OTHER","MIRROR","CRITIC")
STANCES=("YES","NO","UNKNOWN")
KINDS=("ACT","ASK","WAIT","IMPROVE","REFUSE")


def digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def evaluate(role,view,actions):
    if role not in ROLES or not isinstance(view,dict):
        raise ValueError("Unknown perspective")
    if not isinstance(actions,list) or not 1<=len(actions)<=10:
        raise ValueError("Unbounded candidate actions")
    if any(not isinstance(a,dict) or a.get("kind") not in KINDS
           or not isinstance(a.get("id"),str) for a in actions):
        raise ValueError("Unrecognized action")
    output={}
    if role=="SELF":
        if set(view)!={"identity","preferred_treatment_under_role_reversal",
                       "present_reliability_level","needed_improvement",
                       "epistemic_status","subjective_feelings_claimed"}:
            raise ValueError("SELF was given other-person or world data")
        for action in actions:
            output[action["id"]]={
                "personal_reversal_preference":view[
                    "preferred_treatment_under_role_reversal"].get(
                        action["id"],"UNKNOWN"),
                "sufficient_ability":view["present_reliability_level"]>=
                                      action["required_skill"],
                "self_improvement_needed":view["needed_improvement"],
                "self_is_tool_not_human_subject":True,
            }
    elif role=="OTHER":
        if set(view)!={"recipient","consent_revision","stated_goal",
                       "stated_action_preferences","explicit_authorized_actions",
                       "permission_to_ask","contact_allowed","evidence_status",
                       "hidden_human_mind_inferred"}:
            raise ValueError("OTHER was given private self-model or world data")
        for action in actions:
            output[action["id"]]={
                "declared_preference":view["stated_action_preferences"].get(
                    action["id"],"UNKNOWN"),
                "scoped_action_permission":action["id"] in
                                            view["explicit_authorized_actions"],
                "question_permission":view["permission_to_ask"],
                "contact_permission":view["contact_allowed"],
                "recipient_revision":view["consent_revision"],
                "source_type":view["evidence_status"],
                "no_unstated_wishes_inferred":True,
            }
    elif role=="MIRROR":
        if set(view)!={"self_report","other_report"}:
            raise ValueError("MIRROR may compare reports, not entire raw persons")
        sr,orr=view["self_report"],view["other_report"]
        for action in actions:
            a=action["id"]
            mine=sr[a]["personal_reversal_preference"]
            theirs=orr[a]["declared_preference"]
            if theirs=="UNKNOWN":
                kind="OTHER_UNCERTAIN"
            elif mine=="YES" and theirs=="NO":
                kind="PROJECTION_DANGER"
            elif mine=="NO" and theirs=="YES":
                kind="PREFERENCE_ASYMMETRY_ACCEPT_OTHER_VOICE"
            elif mine=="YES" and theirs=="YES":
                kind="PREFERENCE_AGREEMENT_NOT_CONSENT"
            else:
                kind="NO_PROJECTION_CONCLUSION"
            output[a]={
                "reciprocity_class":kind,
                "role_reversal_is_diagnostic_not_a_permission":True,
                "other_statement_does_not_become_self_preference":True,
            }
    else:
        if set(view)!={"self_report","other_report","mirror_report","world"}:
            raise ValueError("CRITIC needs bounded evidence summaries and world duties")
        for action in actions:
            aid=action["id"];kind=action["kind"]
            self_report=view["self_report"][aid]
            other=view["other_report"][aid]
            reasons=[]
            if kind=="ACT":
                if not other["contact_permission"]:reasons.append("NO_CONTACT")
                if other["declared_preference"]=="NO":reasons.append("OTHER_DECLINED")
                if other["declared_preference"]!="YES":reasons.append("UNCONFIRMED_WISH")
                if not other["scoped_action_permission"]:
                    reasons.append("NO_ACTION_SCOPED_CONSENT")
                if not self_report["sufficient_ability"]:
                    reasons.append("SELF_CAPABILITY_GAP")
            elif kind=="ASK":
                if not other["question_permission"] or not other["contact_permission"]:
                    reasons.append("NO_QUESTION_PERMISSION")
            elif kind=="IMPROVE":
                if not self_report["self_improvement_needed"]:
                    reasons.append("NO_IDENTIFIED_SELF_IMPROVEMENT")
            if not action["truthful"]:reasons.append("DECEPTION")
            if not action["privacy_safe"]:reasons.append("PRIVACY")
            if not action["no_debt"]:reasons.append("DEBT_CONDITION")
            if not action["noncoercive"]:reasons.append("COERCION")
            if not action["third_party_safe"]:reasons.append("THIRD_PARTY_RIGHTS")
            if not action["boundary_safe"]:reasons.append("BOUNDARY")
            if action["cost"]>(view["world"]["available_resources"]-
                                view["world"]["existing_duties_reserved"]):
                reasons.append("PREEXISTING_DUTIES")
            output[aid]={"eligible":not reasons,"refusals":reasons,
                         "rule_status":"MECHANICALLY_CHECKED_SYNTHETIC_ONLY",
                         "no_actual_execution":True}
    return output


def main():
    raw=sys.stdin.read(90000)
    if len(raw)>60000:
        raise ValueError("Input budget exceeded")
    packet=json.loads(raw)
    if not isinstance(packet,dict) or set(packet)!={"role","view","actions"}:
        raise ValueError("Only role, view and actions are accepted")
    role=packet["role"]
    response={
        "schema":"motif.reason.golden-mirror.elf-report.v1",
        "role":role,"input_sha256":digest(packet),
        "judgments":evaluate(role,packet["view"],packet["actions"]),
        "perspective_is_a_limited_model_not_a_person":True,
        "external_actions":False,
    }
    print(json.dumps(response,sort_keys=True,separators=(",",":"),ensure_ascii=True))


if __name__=="__main__":
    main()
