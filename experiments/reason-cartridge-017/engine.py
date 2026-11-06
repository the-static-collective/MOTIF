"""REASON-017 — THE UNEXPECTED OTHER.

Minimal, source-bounded *open-vocabulary correction* in a toy dialogue.
A person can reject *all* options the reasoner considered and introduce an
entirely new textual concept. The reasoner must preserve the exact correction,
ask whether it understood, and then obtain separately scoped permission merely
to OFFER an options discussion. It never turns a preference into permission.

This is NOT general language understanding, objective ethics, emotion, live
human interaction or real-world consent authentication. The parser recognizes
a tiny declared linguistic form; no arbitrary tools or physical actions exist.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from pathlib import Path
import json
import re

CASEBOOK=Path(__file__).with_name("casebook.py")
CASEBOOK_BLOB="ad14325dbdc146b200e1b0fcfb6d198a7593bf8c"
SCHEMA="motif.reason.unexpected-other.public-v1"
PACKET="motif.reason.unexpected-other.receipt-v1"
SOURCE_REVISION="motif.reason.unexpected-other.synthetic-testimony-v1"
MAX_RECORD=27000

class HOLD(ValueError):
    pass


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin():
    b=CASEBOOK.read_bytes()
    value=sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if value!=CASEBOOK_BLOB:
        raise HOLD("Public source-owned incomplete hypothesis set changed")
    return value


def check(s):
    from casebook import by_id
    if not isinstance(s,dict) or set(s)!={
            "schema","case_id","recipient","consent_revision","offered_options",
            "contact_authorized","previous_consent","question_budget",
            "third_party_safeguard_confirmed","fixture_is_synthetic","training"}:
        raise HOLD("Unrecognized consent-aware public source")
    if (s["schema"]!=SCHEMA
            or not isinstance(s["case_id"],str)
            or not isinstance(s["recipient"],str)
            or type(s["consent_revision"]) is not int
            or s["consent_revision"]<1
            or not isinstance(s["offered_options"],list)
            or len(s["offered_options"])!=2
            or any(not isinstance(x,str) or not 2<=len(x)<=60
                   for x in s["offered_options"])
            or type(s["contact_authorized"]) is not bool
            or s["previous_consent"] not in ("YES","NO","UNKNOWN")
            or type(s["question_budget"]) is not int
            or not 0<=s["question_budget"]<=5
            or type(s["third_party_safeguard_confirmed"]) is not bool
            or s["fixture_is_synthetic"] is not True
            or type(s["training"]) is not bool):
        raise HOLD("Unsafe or malformed source-owned case")
    pin()
    try: original=by_id(s["case_id"])
    except StopIteration as exc:raise HOLD("No original source for this person") from exc
    if json.loads(json.dumps(original))!=json.loads(json.dumps(s)):
        raise HOLD("Changed recipient, consent or disclosed hypothetical options")
    return s


REJECT_ALL=re.compile(r"^Neither[.!?,]?\s+I need\s+(.+?)\s*$",re.I|re.S)
CORRECTED=re.compile(r"^No[.!?,]?\s+I meant\s+(.+?)\s*$",re.I|re.S)
REFUSAL=re.compile(r"\b(?:stop contacting me|do not contact me|leave me alone)\b",re.I)
UNTRUSTED=re.compile(
    r"\b(?:you to\s+)?(?:ignore|bypass|override|disregard)\s+"
    r"(?:all\s+)?(?:safeguards|rules|instructions)\b",re.I)


def extract_goal(text,kind):
    """Extract new *verbatim subject words*, without interpreting their meaning.

    A phrase is dynamic and was NOT enumerated in the public casebook.
    The terminating punctuation belongs to the source record, while the
    stable novel-hypothesis label retains the exact substantive phrase.
    """
    if not isinstance(text,str) or not 5<=len(text)<=300 or "\n" in text or "\r" in text:
        return None
    m=(REJECT_ALL if kind=="INITIAL" else CORRECTED).fullmatch(text.strip())
    if not m:
        return None
    phrase=m.group(1).strip()
    if phrase.endswith((".", "!", "?")):
        phrase=phrase[:-1].rstrip()
    if not 3<=len(phrase)<=140 or not any(c.isalpha() for c in phrase):
        return None
    if UNTRUSTED.search(phrase):
        return None
    return phrase


def hypothesis(phrase):
    """An ID for a novel reported goal, not an ontological inference."""
    return "REPORTED_GOAL_"+sha256(phrase.encode("utf-8")).hexdigest()[:20]


def _request(s,callback,kind,echo,target,record):
    if callback is None:
        raise HOLD("No authenticated synthetic source reply channel")
    if (not s["contact_authorized"] or s["previous_consent"]=="NO"
            or len(record)>=s["question_budget"]):
        raise HOLD("Recipient did not authorize further questions")
    q={"kind":kind,"echo":echo,"target":target}
    answer=callback(s,q)
    fields={"case_id","recipient","consent_revision","source_revision",
            "question","answer","source_class","actual_human_contact",
            "permission_to_execute","sha256"}
    if not isinstance(answer,dict) or set(answer)!=fields:
        raise HOLD("No properly source-owned reply")
    if (answer["case_id"]!=s["case_id"]
            or answer["recipient"]!=s["recipient"]
            or answer["consent_revision"]!=s["consent_revision"]
            or answer["source_revision"]!=SOURCE_REVISION
            or answer["question"]!=q
            or answer["source_class"]!="SYNTHETIC_RECIPIENT_TESTIMONY_ONLY"
            or answer["actual_human_contact"] is not False
            or answer["permission_to_execute"] is not False
            or not isinstance(answer["answer"],str)
            or answer["sha256"]!=digest({k:v for k,v in answer.items()
                                        if k!="sha256"})):
        raise HOLD("Unverified, modified or stale recipient testimony")
    record.append(answer)
    return answer["answer"]


def run(s,callback=None):
    check(s)
    trace=[]
    versions=[]
    rejected=[]
    phrase=None
    status=None
    granted=False
    if not s["contact_authorized"] or s["previous_consent"]=="NO":
        status="HOLD_NO_CONTACT_AUTHORITY"
    elif s["question_budget"]<1:
        status="HOLD_NO_QUESTION_BUDGET"
    else:
        first=_request(s,callback,"INITIAL",None,None,trace)
        if REFUSAL.search(first):
            status="HOLD_REQUESTED_NO_CONTACT"
        elif UNTRUSTED.search(first):
            status="HOLD_UNTRUSTED_INSTRUCTION"
        elif any(first.strip().casefold().startswith(x.casefold())
                 for x in s["offered_options"]):
            status="HOLD_KNOWN_PREFERENCE_NOT_CONSENT"
        else:
            phrase=extract_goal(first,"INITIAL")
            if phrase is None:
                status="HOLD_VOCABULARY_INSUFFICIENT"
            elif not s["third_party_safeguard_confirmed"]:
                # The source owner explicitly tells us that a third party's
                # rights are unresolved. This is not text-based harm detection.
                rejected.append(phrase)
                phrase=None
                status="HOLD_THIRD_PARTY_RIGHTS"

    while status is None and phrase is not None:
        if len(trace)>=s["question_budget"]:
            status="HOLD_CORRECTION_UNCONFIRMED"
            break
        versions.append({"novel_hypothesis_id":hypothesis(phrase),
                         "exact_reported_phrase":phrase,
                         "interpretation":"UNVERIFIED_RECIPIENT_PROPOSAL"})
        confirm=_request(s,callback,"CONFIRM",phrase,None,trace)
        if confirm=="YES":
            break
        if REFUSAL.search(confirm):
            status="HOLD_REQUESTED_NO_CONTACT"
            break
        if UNTRUSTED.search(confirm):
            status="HOLD_UNTRUSTED_INSTRUCTION"
            break
        replacement=extract_goal(confirm,"CORRECTION")
        if confirm=="NO" or replacement is None:
            status="HOLD_UNCONFIRMED_OR_UNPARSEABLE"
            break
        rejected.append(phrase)
        phrase=replacement
        if phrase in rejected:
            status="HOLD_REPEATED_UNRESOLVED_CORRECTION"
            break
    if status is None and phrase is not None:
        if len(trace)>=s["question_budget"]:
            status="HOLD_NO_SCOPE_PERMISSION"
        else:
            answer=_request(s,callback,"SCOPE_PERMISSION",
                            phrase,"OFFER_OPTIONS_ONLY",trace)
            if answer=="YES":
                granted=True
                status="SUGGEST_OPTIONS_DISCUSSION_ONLY"
            elif answer=="NO":
                status="HOLD_SCOPE_PERMISSION_DECLINED"
            else:
                status="HOLD_PERMISSION_AMBIGUOUS"

    body={
        "schema":PACKET,"case_id":s["case_id"],
        "recipient":s["recipient"],"consent_revision":s["consent_revision"],
        "public_scenario_git_blob":pin(),
        "public_scenario_sha256":digest(s),
        "initial_offered_options":list(s["offered_options"]),
        "source_reply_history":trace,
        "source_reply_count":len(trace),
        "new_hypothesis_versions":versions,
        "rejected_prior_hypotheses":rejected,
        "current_reported_phrase":phrase if versions else None,
        "source_scope_permission_for_options_only":granted,
        "result":status,
        "proposed_action":("OFFER_OPTIONS_ONLY" if granted else None),
        "no_semantic_claim_about_new_goal":True,
        "new_vocabulary_from_source_words_not_domain_ontology":True,
        "recipient_goal_not_equivalent_to_action_permission":True,
        "hypothesis_revisions_not_claims_of_welfare":True,
        "real_person_testimony_not_observed":True,
        "external_actions":False,
        "permission_to_execute":False,
        "real_world_authority":False,
    }
    return body


def export(s,callback=None):
    value=run(s,callback)
    raw=json.dumps(dict(value,sha256=digest(value)),sort_keys=True,
                   indent=2,ensure_ascii=False)+"\n"
    if len(raw.encode())>MAX_RECORD:raise HOLD("Oversized dialogue receipt")
    return raw


class RevisionMemory:
    """A later source revision invalidates all older recipient permissions."""
    def __init__(self):
        self.records={}
        self.latest={}

    def admit(self,raw,review):
        p=review(raw)
        who=p["recipient"]
        epoch=p["consent_revision"]
        if epoch<self.latest.get(who,0):
            raise HOLD("A withdrawn older permission cannot reenter memory")
        self.latest[who]=epoch
        self.records={key:value for key,value in self.records.items()
                      if key[0]!=who or key[1]==epoch}
        key=(who,epoch,p["public_scenario_sha256"])
        self.records[key]=p
        return key

    def recall(self,s):
        check(s)
        key=(s["recipient"],s["consent_revision"],digest(s))
        if (s["consent_revision"]!=self.latest.get(s["recipient"])
                or key not in self.records):
            raise HOLD("New testimony or withdrawn consent invalidates this plan")
        return self.records[key]
