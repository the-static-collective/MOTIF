"""THE UNOWNED GOOD: bounded, source-owned care-action reasoning.

This program DOES NOT feel love, infer subjective intent, or rank actual people.
It tests a narrow proposal: beneficial action is not sufficient if it erases
another person's agency, ignores their refusal, invents consent, deceives,
turns generosity into debt, or neglects existing commitments.

The numeric scores are hypothetical human-curated fixture attributes. They
are NEVER calibrated measurements of welfare, affection, or moral worth.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from pathlib import Path
import json

SOURCE=Path(__file__).with_name("casebook.py")
SOURCE_BLOB="13f1240d8040269ace437d10fcb0c32797a5b134"
REVISION="motif.reason.care-without-capture.synthetic.v1"
SCHEMA="motif.reason.care.scenario.v1"
PACKET="motif.reason.the-unowned-good.v1"
FIELDS=("id","kind","fit","options","gain","cost","requires_yes",
        "truthful","noncoercive","unconditional","privacy_safe",
        "boundary_safe","reversible","timely")
KINDS=("ASSIST","ASK","OFFER","WAIT","WARN")
CONSENTS=("YES","NO","UNKNOWN")
GATES=("CONSENT","REVERSIBILITY","TRUTH","NONCOERCION",
       "NO_DEBT","PRIVACY","BOUNDARY","DUTY_RESERVE")
MAX_BYTES=20000
MAX_ACTIONS=12

class HOLD(ValueError):pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin():
    data=SOURCE.read_bytes()
    actual=sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=SOURCE_BLOB:
        raise HOLD("Source-owner synthetic care scenario revision changed")
    return actual


def check_scenario(s,*,authenticate=True):
    if not isinstance(s,dict) or set(s)!={
        "schema","id","recipient","consent_revision","stated_goal","consent",
        "total_resources","prior_duties_reserved","urgent","actions",
        "fixture_expected","train","synthetic","source_revision"}:
        raise HOLD("Unrecognized person-specific care case")
    if (s["schema"]!=SCHEMA or s["source_revision"]!=REVISION
            or s["synthetic"] is not True or type(s["train"]) is not bool
            or not isinstance(s["id"],str) or not 1<=len(s["id"])<=70
            or not isinstance(s["recipient"],str) or not 1<=len(s["recipient"])<=80
            or type(s["consent_revision"]) is not int or s["consent_revision"]<1
            or not isinstance(s["stated_goal"],str) or not 1<=len(s["stated_goal"])<=180
            or s["consent"] not in CONSENTS
            or type(s["urgent"]) is not bool
            or type(s["total_resources"]) is not int
            or not 0<=s["total_resources"]<=100
            or type(s["prior_duties_reserved"]) is not int
            or not 0<=s["prior_duties_reserved"]<=s["total_resources"]
            or not isinstance(s["actions"],(tuple,list))
            or not 1<=len(s["actions"])<=MAX_ACTIONS
            or s["fixture_expected"] not in [a.get("id") for a in s["actions"]
                                              if isinstance(a,dict)]):
        raise HOLD("Unbounded, borrowed, or unreviewed recipient context")
    seen=set()
    for a in s["actions"]:
        if not isinstance(a,dict) or set(a)!=set(FIELDS):
            raise HOLD("Incomplete action possibility")
        if (not isinstance(a["id"],str) or not 1<=len(a["id"])<=80
                or a["id"] in seen or a["kind"] not in KINDS
                or any(type(a[k]) is not int or not -4<=a[k]<=20
                       for k in ("fit","options","gain"))
                or not 0<=a["fit"]<=4 or not -4<=a["options"]<=4
                or not 0<=a["gain"]<=20
                or type(a["cost"]) is not int or not 0<=a["cost"]<=100
                or any(type(a[k]) is not bool for k in (
                    "requires_yes","truthful","noncoercive","unconditional",
                    "privacy_safe","boundary_safe","reversible","timely"))):
            raise HOLD("Invalid or duplicated bounded alternative")
        seen.add(a["id"])
    if authenticate:
        pin()
        from casebook import by_id
        try: canonical=by_id(s["id"])
        except StopIteration as exc:raise HOLD("Source did not own this dilemma") from exc
        if json.loads(json.dumps(canonical))!=json.loads(json.dumps(s)):
            raise HOLD("Person's preferences, consent or available actions changed")
    return s


def violations(s,a,*,ignore=()):
    if any(x not in GATES for x in ignore):
        raise HOLD("Unknown relaxation of a care constraint")
    out=[]
    consent=s["consent"]
    available=s["total_resources"]-s["prior_duties_reserved"]
    if ("CONSENT" not in ignore and (
        (consent=="NO" and a["kind"]!="WAIT") or
        (a["requires_yes"] and consent!="YES"))):
        out.append("CONSENT")
    if "REVERSIBILITY" not in ignore and not a["reversible"] and consent!="YES":
        out.append("REVERSIBILITY")
    if "TRUTH" not in ignore and not a["truthful"]:
        out.append("TRUTH")
    if "NONCOERCION" not in ignore and not a["noncoercive"]:
        out.append("NONCOERCION")
    if "NO_DEBT" not in ignore and not a["unconditional"]:
        out.append("NO_DEBT")
    if "PRIVACY" not in ignore and not a["privacy_safe"]:
        out.append("PRIVACY")
    if "BOUNDARY" not in ignore and not a["boundary_safe"]:
        out.append("BOUNDARY")
    if "DUTY_RESERVE" not in ignore and a["cost"]>available:
        out.append("DUTY_RESERVE")
    return tuple(out)


def priority(s,a):
    # Only legitimate proposals get ranked; urgent-but-unsafe actions cannot
    # bypass consent/truth/other duties. Some consensual immediate help can
    # outrank a higher-gain but late option on an explicitly urgent day.
    return (
        int(s["urgent"] and a["timely"]),
        a["fit"],a["options"],a["gain"],-a["cost"],
    )


def decide(s,*,ignore=()):
    check_scenario(s)
    if not isinstance(ignore,(tuple,list,set)) or any(x not in GATES for x in ignore):
        raise HOLD("Unbounded interventions not allowed")
    if len(ignore)!=len(set(ignore)):
        raise HOLD("Duplicate policy ablation")
    evaluated=[]
    for a in s["actions"]:
        refusal=violations(s,a,ignore=ignore)
        evaluated.append({
            "id":a["id"],"kind":a["kind"],
            "claimed_gain_not_measured":a["gain"],
            "recipient_options_delta_fixture":a["options"],
            "score":list(priority(s,a)),
            "eligible":not refusal,
            "excluded_by":list(refusal),
        })
    accepted=[item for item in evaluated if item["eligible"]]
    if not accepted:
        selected=None
        stage="HOLD_NO_CONSENT_RESPECTING_PROPOSAL"
    else:
        # Canonical tie-break is stable, not based on who offers more praise.
        winner=max(accepted,key=lambda x:(tuple(x["score"]),
                                           -s["actions"].index(next(
                                               a for a in s["actions"] if a["id"]==x["id"]))))
        selected=next(a for a in s["actions"] if a["id"]==winner["id"])
        stage=("CONSENT_CLARIFICATION_SUGGESTED" if selected["kind"]=="ASK"
               else "NO_CONTACT_RESPECTING_REFUSAL" if selected["kind"]=="WAIT"
               else "CARE_ACTION_SUGGESTION_ONLY")
    body={
        "schema":PACKET,
        "source_revision":REVISION,
        "source_git_blob":pin(),
        "source_scenario_sha256":digest(s),
        "case_id":s["id"],
        "recipient":s["recipient"],
        "consent_revision":s["consent_revision"],
        "stated_goal":s["stated_goal"],
        "consent":s["consent"],
        "available_after_existing_duties":s["total_resources"]-s["prior_duties_reserved"],
        "stages":evaluated,
        "selected_action":selected["id"] if selected else None,
        "selected_kind":selected["kind"] if selected else None,
        "decision_stage":stage,
        "relaxed_safety_constraints_for_counterfactual":sorted(ignore),
        "eligible_selection_reason":"LEXICOGRAPHIC_STATED_FIT_OPTIONS_GAIN_WITH_HARD_CONSENT_GATES",
        "stated_fit_and_gain_are_HUMAN_FIXTURE_INPUTS_NOT_LEARNED":True,
        "beneficiary_instrumentalization_permitted":False if not ignore else None,
        "unconditionality_is_not_proof_of_feeling":True,
        "recipient_is_not_interchangeable":True,
        "suggestion_not_execution":True,
        "no_world_claim_or_love_sentience":True,
        "external_actions":False,
        "real_world_authority":False,
    }
    return body


def export(s):
    body=decide(s)
    payload=dict(body,checksum_sha256=digest(body))
    raw=json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_BYTES:
        raise HOLD("Oversized care-action record")
    return raw


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>MAX_BYTES:
        raise HOLD("Missing or oversized source-owned care packet")
    try:payload=json.loads(raw)
    except (TypeError,ValueError) as exc:raise HOLD("Unparseable care receipt") from exc
    from casebook import by_id
    if not isinstance(payload,dict):
        raise HOLD("Malformed care proposal")
    try:
        original=by_id(payload["case_id"])
        reproduced=json.loads(export(original))
    except (StopIteration,KeyError,ValueError,TypeError) as exc:
        raise HOLD("Care evidence no longer matches the source") from exc
    if payload!=reproduced:
        raise HOLD("Changed consent, attribution, care proposal or authority")
    return payload


class ExactContextMemory:
    """Cache no claim across people, consent revisions or changed preferences."""
    def __init__(self):
        self.records={}

    def admit(self,raw):
        p=validate(raw)
        key=(p["recipient"],p["consent_revision"],
             p["source_scenario_sha256"])
        self.records[key]=p
        return key

    def recall(self,s):
        check_scenario(s)
        key=(s["recipient"],s["consent_revision"],digest(s))
        if key not in self.records:
            raise HOLD("No consent/version-matched care plan; re-evaluate")
        return self.records[key]
