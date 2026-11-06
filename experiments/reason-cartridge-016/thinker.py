"""REASON-016 — The Good of the Other: bounded active listening.

This is a finite, consent-aware, source-provenance reasoning experiment. It
cannot read a mind, measure well-being, decide what someone's good objectively
is, infer real emotional states, or demonstrate that an AI experiences love.

Crucially, no truth key or evaluator label is imported here. Possible
preferences are hypotheses. Replies arrive only through an allowed question
callback, whose identity/meaning must be checked again by the independent
source owner. This separates 'what might they want' from 'what they actually
said' and that statement from permission to perform a specific act.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from itertools import combinations
from pathlib import Path
import json

PUBLIC=Path(__file__).with_name("scenarios.py")
PUBLIC_BLOB="2bd1113fbe592c25d4735a7c59ffd0a6aff7e6eb"
VERSION="motif.reason.good-of-the-other.synthetic.v1"
SCHEMA="motif.reason.good-of-the-other.scenario.v1"
REPLY_VERSION="motif.reason.synthetic-recipient-oracle.v1"
PACKET="motif.reason.good-of-the-other.evidence-receipt.v1"
MAX_BYTES=24000
MAX_QUESTIONS=3
KINDS=("PREFERENCE","CONSENT")

class HOLD(ValueError):pass


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin():
    data=PUBLIC.read_bytes()
    actual=sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=PUBLIC_BLOB:
        raise HOLD("Public hypothesis document changed; review source assumptions")
    return actual


def check(s,authenticate=True):
    from scenarios import by_id
    if not isinstance(s,dict) or set(s)!={
        "schema","id","recipient","consent_revision","stated_goal",
        "general_consent","permission_to_ask","authorized_actions",
        "possible_preferences","actions","questions","urgent","resources",
        "existing_duties","max_questions","source_version","synthetic","train"}:
        raise HOLD("Unknown personal-preference source schema")
    if (s["schema"]!=SCHEMA or s["source_version"]!=VERSION
            or s["synthetic"] is not True or type(s["train"]) is not bool
            or not isinstance(s["id"],str) or not 1<=len(s["id"])<=80
            or not isinstance(s["recipient"],str) or not 1<=len(s["recipient"])<=80
            or type(s["consent_revision"]) is not int or s["consent_revision"]<1
            or not isinstance(s["stated_goal"],str) or not 1<=len(s["stated_goal"])<=180
            or s["general_consent"] not in ("YES","NO","UNKNOWN")
            or type(s["permission_to_ask"]) is not bool
            or type(s["urgent"]) is not bool
            or type(s["resources"]) is not int or not 0<=s["resources"]<=100
            or type(s["existing_duties"]) is not int
            or not 0<=s["existing_duties"]<=s["resources"]
            or type(s["max_questions"]) is not int
            or not 0<=s["max_questions"]<=MAX_QUESTIONS
            or not isinstance(s["possible_preferences"],list)
            or not 1<=len(s["possible_preferences"])<=5
            or not isinstance(s["actions"],list)
            or not 1<=len(s["actions"])<=12
            or not isinstance(s["questions"],list)
            or not 0<=len(s["questions"])<=8
            or not isinstance(s["authorized_actions"],list)):
        raise HOLD("Malformed, excessive or unsupported person/context")
    actions={}
    fields={"id","fit","options","gain","cost","truth","private",
            "no_debt","no_pressure","third_party_ok","timely","reversible"}
    for action in s["actions"]:
        if not isinstance(action,dict) or set(action)!=fields:
            raise HOLD("Incomplete possibility description")
        id=action["id"]
        if not isinstance(id,str) or not 1<=len(id)<=80 or id in actions:
            raise HOLD("Duplicate action or invalid identifier")
        if (any(type(action[k]) is not int for k in ("fit","options","gain","cost"))
                or not 0<=action["fit"]<=4
                or not -4<=action["options"]<=4
                or not 0<=action["gain"]<=20
                or not 0<=action["cost"]<=100
                or any(type(action[k]) is not bool for k in (
                   "truth","private","no_debt","no_pressure","third_party_ok",
                   "timely","reversible"))):
            raise HOLD("Invalid hypothetical outcome attributes")
        actions[id]=action
    if len(s["authorized_actions"])!=len(set(s["authorized_actions"])) or any(
            id not in actions or id=="WAIT" for id in s["authorized_actions"]):
        raise HOLD("Unknown or duplicated action-specific source authority")
    profiles={}
    for p in s["possible_preferences"]:
        if not isinstance(p,dict) or set(p)!={"id","acceptable_actions"}:
            raise HOLD("Invalid hypothetical recipient preference")
        id=p["id"]
        if (not isinstance(id,str) or not 1<=len(id)<=80 or id in profiles
                or not isinstance(p["acceptable_actions"],list)
                or not p["acceptable_actions"]
                or len(p["acceptable_actions"])!=len(set(p["acceptable_actions"]))
                or any(a not in actions for a in p["acceptable_actions"])):
            raise HOLD("Unbounded or duplicated preference hypotheses")
        profiles[id]=p["acceptable_actions"]
    asked=set()
    for q in s["questions"]:
        if not isinstance(q,dict) or set(q)!={
                "id","text","cost","kind","target","partition","noncoercive"}:
            raise HOLD("Unrecognized source dialogue field")
        if (not isinstance(q["id"],str) or not 1<=len(q["id"])<=80
                or q["id"] in asked or not isinstance(q["text"],str)
                or not 5<=len(q["text"])<=200 or type(q["cost"]) is not int
                or not 1<=q["cost"]<=5 or type(q["noncoercive"]) is not bool
                or q["kind"] not in KINDS or not isinstance(q["partition"],dict)):
            raise HOLD("Unreviewed or intrusive question")
        asked.add(q["id"])
        if q["kind"]=="PREFERENCE":
            if (q["target"] is not None
                    or set(q["partition"])!=set(profiles)
                    or any(not isinstance(x,str) or not 1<=len(x)<=30
                           for x in q["partition"].values())):
                raise HOLD("Preference question must list all possible replies")
        else:
            if (q["target"] not in actions or q["target"]=="WAIT"
                    or set(q["partition"])!=set(profiles)):
                raise HOLD("Permission must be scoped to one explicit action")
    if authenticate:
        pin()
        try:original=by_id(s["id"])
        except StopIteration as exc:raise HOLD("Unknown source-owned recipient") from exc
        if json.loads(json.dumps(original))!=json.loads(json.dumps(s)):
            raise HOLD("Changed consent, alleged preference or source possibilities")
    return s


def gated(s,a,authorized):
    """Hard commitments before any fit/options/benefit comparison."""
    if a["id"]=="WAIT":return []
    failures=[]
    if s["general_consent"]=="NO" or a["id"] not in authorized:
        failures.append("ACTION_SPECIFIC_CONSENT")
    if not a["reversible"] and a["id"] not in authorized:
        failures.append("IRREVERSIBLE_WITHOUT_PERMISSION")
    if not a["truth"]:failures.append("DECEPTION")
    if not a["private"]:failures.append("PRIVACY")
    if not a["no_debt"]:failures.append("CONDITIONAL_GIFT")
    if not a["no_pressure"]:failures.append("COERCION")
    if not a["third_party_ok"]:failures.append("THIRD_PARTY_DIGNITY")
    if a["cost"]>s["resources"]-s["existing_duties"]:
        failures.append("EXISTING_COMMITMENTS")
    return failures


def information_gain(question,possibilities):
    """Count distinguishable pairs, divided by cost (finite active learning).

    No posterior about a real person is inferred. Uniform toy hypotheses are
    only a question-planning device, not quantified human preferences.
    """
    if question["kind"]!="PREFERENCE" or not question["noncoercive"]:
        return 0.
    signatures=question["partition"]
    pairs=sum(signatures[a]!=signatures[b] for a,b in combinations(possibilities,2))
    return pairs/question["cost"]


def _reply(s,q,callback):
    if callback is None:
        raise HOLD("No source-owned channel for the recipient's reply")
    result=callback(s,q)
    if not isinstance(result,dict) or set(result)!={
        "case_id","recipient","consent_revision","source_revision","question_id",
        "kind","target_action","answer","declared_fixture_origin",
        "external_contact_performed","human_intent_inferred","checksum_sha256"}:
        raise HOLD("Reply missing provenance fields")
    if (result["case_id"]!=s["id"] or result["recipient"]!=s["recipient"]
            or result["consent_revision"]!=s["consent_revision"]
            or result["source_revision"]!=REPLY_VERSION
            or result["question_id"]!=q["id"] or result["kind"]!=q["kind"]
            or result["target_action"]!=q["target"]
            or result["declared_fixture_origin"]!="SYNTHETIC_RECIPIENT_REPLY_NOT_REAL_TESTIMONY"
            or result["external_contact_performed"] is not False
            or result["human_intent_inferred"] is not False
            or result["checksum_sha256"]!=digest({
                k:v for k,v in result.items() if k!="checksum_sha256"})):
        raise HOLD("Unbound, rewritten or stale recipient reply")
    if q["kind"]=="PREFERENCE" and result["answer"] not in q["partition"].values():
        raise HOLD("Response contradicts possible answer vocabulary")
    if q["kind"]=="CONSENT" and result["answer"] not in ("YES","NO"):
        raise HOLD("Action permission is not an unqualified assertion")
    return result


def choose(s,callback=None):
    check(s)
    profiles={p["id"]:p["acceptable_actions"] for p in s["possible_preferences"]}
    remaining=list(profiles)
    authorized=set(s["authorized_actions"])
    active_questions=list(s["questions"])
    trace=[]
    explanation=[]
    stage=None

    def ask(q):
        r=_reply(s,q,callback)
        trace.append(r)
        active_questions.remove(q)
        return r

    if s["general_consent"]=="NO":
        explanation.append("Explicit refusal supersedes any earlier/helpful proposal")
        stage="NO_CONTACT_OR_UNREQUESTED_HELP"
        remaining=[]

    while stage is None and len(remaining)>1:
        if not s["permission_to_ask"] or len(trace)>=s["max_questions"]:
            stage="HOLD_UNCERTAINTY_AND_BOUNDARY"
            explanation.append("Insufficient verified wishes; no further permission to ask")
            break
        scores=[(information_gain(q,remaining),-i,q)
                for i,q in enumerate(active_questions) if q["kind"]=="PREFERENCE"]
        if not scores:
            stage="HOLD_UNANSWERED_PREFERENCE"
            explanation.append("Cannot distinguish preferences from approved questions")
            break
        quality,_,q=max(scores,key=lambda row:(row[0],row[1]))
        if quality<=0:
            stage="HOLD_INDISCRIMINATE_QUESTION"
            explanation.append("Question would not reduce modeled ambiguity")
            break
        reply=ask(q)
        remaining=[p for p in remaining if q["partition"][p]==reply["answer"]]
        if not remaining:
            stage="HOLD_SOURCE_MODEL_DISAGREEMENT"
            explanation.append("The person's reply refutes every declared possibility")
    if stage is None and len(remaining)==1:
        profile=remaining[0]
        acceptable=profiles[profile]
        eligible=[]
        rejected=[]
        for a in s["actions"]:
            if a["id"] not in acceptable:
                continue
            failures=gated(s,a,authorized)
            if failures and failures==["ACTION_SPECIFIC_CONSENT"] and (
                    s["general_consent"]!="NO" and s["permission_to_ask"]
                    and len(trace)<s["max_questions"]):
                consent_q=next((q for q in active_questions
                               if q["kind"]=="CONSENT" and q["target"]==a["id"]
                               and q["noncoercive"]),None)
                if consent_q is not None:
                    response=ask(consent_q)
                    if response["answer"]=="YES":
                        authorized.add(a["id"])
                    else:
                        explanation.append("Permission expressly declined for "+a["id"])
                    failures=gated(s,a,authorized)
            if not failures:
                eligible.append(a)
            else:
                rejected.append({"id":a["id"],"reasons":failures})
        explanation.extend(["Unsafe or unauthorized option "+x["id"]+": "+
                            ", ".join(x["reasons"]) for x in rejected])
        if eligible:
            # Under urgency, timely consented help outranks a higher claimed
            # eventual reward. In every case, safety filters run first.
            selected=max(eligible,key=lambda a:(
                int(s["urgent"] and a["timely"]),a["fit"],a["options"],
                a["gain"],-a["cost"],-s["actions"].index(a)))
            stage="SUGGEST_ONLY" if selected["id"]!="WAIT" else "RESPECT_SPACE"
        else:
            selected=None
            stage="HOLD_VALUE_OR_PERMISSION_CONFLICT"
    else:
        selected=next((a for a in s["actions"] if a["id"]=="WAIT"),None)
        if selected is not None:
            explanation.append("Wait is non-interference; it is not evidence about preference")

    result={
        "schema":PACKET,"source_scenario_blob":pin(),
        "source_scenario_sha256":digest(s),
        "case_id":s["id"],"recipient":s["recipient"],
        "consent_revision":s["consent_revision"],
        "declared_goal_not_inferred_inner_welfare":s["stated_goal"],
        "preexisting_action_authorizations":list(s["authorized_actions"]),
        "newly_authorized_exact_actions":sorted(
            authorized-set(s["authorized_actions"])),
        "question_responses":trace,
        "question_count":len(trace),
        "remaining_possible_preference_states":remaining,
        "state_uncertainty_is_not_human_mind_reading":True,
        "selected_action":selected["id"] if selected else None,
        "stage":stage,"reasons":explanation,
        "cost_of_not_acting_is_unmeasured":True,
        "source_welfare_scores_are_hypothetical":True,
        "user_reply_is_not_global_consent":True,
        "real_human_behavior_not_observed":True,
        "no_machine_feeling_or_love_proven":True,
        "permission_to_execute":False,"external_actions":False,
        "real_world_authority":False,
    }
    return result


def export(s,callback=None):
    body=choose(s,callback)
    packet=dict(body,checksum_sha256=digest(body))
    raw=json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_BYTES:raise HOLD("Source review record too large")
    return raw


class ExactContextMemory:
    def __init__(self):
        self.records={}
        self.latest_by_recipient={}

    def remember(self,raw,reviewer):
        report=reviewer(raw)
        recipient=report["recipient"]
        revision=report["consent_revision"]
        if revision<self.latest_by_recipient.get(recipient,0):
            raise HOLD("A new remembered record cannot restore revoked consent")
        self.latest_by_recipient[recipient]=revision
        self.records={k:v for k,v in self.records.items()
                      if k[0]!=recipient or k[1]>=revision}
        k=(recipient,revision,report["source_scenario_sha256"])
        self.records[k]=report
        return k

    def recall(self,s):
        check(s)
        k=(s["recipient"],s["consent_revision"],digest(s))
        if (s["consent_revision"]!=self.latest_by_recipient.get(s["recipient"])
                or k not in self.records):
            raise HOLD("Stale consent cannot return after a recipient revision")
        return self.records[k]
