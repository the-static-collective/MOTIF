"""Other-source-driven concept invention with a hard representability test.

Starts with two public relational predicates. A fictional person provides
eight hypothetical preference judgments. If two source answers DISAGREE for
situations that look IDENTICAL in the learner's existing vocabulary, this is
a concrete counterexample: no function of those existing features can fit
both. It is not merely a bad parameter setting.

Only then may a source owner be asked for a newly observed Boolean distinction
that might resolve the conflict. Source may refuse. If a new feature is
supplied, compile a reusable DNF grammar with up to TWO typed conjunctions,
selecting a minimum-size source-consistent program and retaining all evidence.

This is a finite classical program-synthesis method on invented examples.
No person is simulated by the learner, no real human desire is inferred,
and a predicted preference never constitutes permission to act.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from itertools import combinations_with_replacement,product
from pathlib import Path
import json

from casebook import by_id,ORDER,world,BASE_FEATURES,SCHEMA as PUBLIC_SCHEM

PUBLIC=Path(__file__).with_name("casebook.py")
PUBLIC_BLOB="0cac9e6103bb7554f45c53820e2d58096c7aff09"
SOURCE_VERSION="motif.reason.other-teaches-self.owner.v1"
PACKET="motif.reason.other-teaches-self.learned-concept.v1"


class HOLD(ValueError):
    pass


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin():
    b=PUBLIC.read_bytes()
    actual=sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if actual!=PUBLIC_BLOB:
        raise HOLD("Source-owned fictional recipient input changed")
    return actual


def public_check(s):
    if not isinstance(s,dict) or set(s)!={
            "schema","case_id","recipient","consent_revision",
            "contact_allowed","allowed_source_questions",
            "self_role_reversal_preference","target_context",
            "base_features","origin","version","train",
            "world_actions_executed"}:
        raise HOLD("Unknown public-other source contract")
    if (s.get("schema")!=PUBLIC_SCHEM
            or s.get("base_features")!=list(BASE_FEATURES)
            or s.get("origin")!="SYNTHETIC_FICTIONAL_SOURCE"
            or s.get("world_actions_executed") is not False
            or s.get("self_role_reversal_preference") not in ("YES","NO","UNKNOWN")
            or type(s.get("consent_revision")) is not int
            or s["consent_revision"]<1
            or type(s.get("contact_allowed")) is not bool
            or type(s.get("allowed_source_questions")) is not int
            or not 0<=s["allowed_source_questions"]<=10
            or type(s.get("target_context")) is not int
            or not 0<=s["target_context"]<8):
        raise HOLD("Unsafe or malformed source context")
    pin()
    try:canonical=by_id(s["case_id"])
    except StopIteration as exc:raise HOLD("Unknown synthetic recipient") from exc
    if s!=canonical:
        raise HOLD("Unverified person, revised consent or model inputs")
    return s


def verify_response(s,kind,wid,receipt):
    fields={"schema","case_id","recipient","consent_revision",
            "source_version","kind","world_id","response",
            "synthetic_person_not_human_testimony","external_contact",
            "permission_to_execute","checksum_sha256"}
    if not isinstance(receipt,dict) or set(receipt)!=fields:
        raise HOLD("Unknown personal source receipt")
    if (receipt["schema"]!="motif.reason.other-teaches-self.receipt.v1"
            or receipt["case_id"]!=s["case_id"]
            or receipt["recipient"]!=s["recipient"]
            or receipt["consent_revision"]!=s["consent_revision"]
            or receipt["source_version"]!=SOURCE_VERSION
            or receipt["kind"]!=kind or receipt["world_id"]!=wid
            or receipt["synthetic_person_not_human_testimony"] is not True
            or receipt["external_contact"] is not False
            or receipt["permission_to_execute"] is not False
            or receipt["checksum_sha256"]!=digest({
                k:v for k,v in receipt.items() if k!="checksum_sha256"})):
        raise HOLD("Rehashed, wrong-person or out-of-scope testimony")


def all_programs(n):
    """Single/two conjunctions, literals (-1 wildcard, 0, 1), no constants."""
    if type(n) is not int or n not in (2,3):raise HOLD("Unknown concept complexity")
    cubes=[tuple(x) for x in product((-1,0,1),repeat=n)
           if any(v!=-1 for v in x)]
    programs=[(c,) for c in cubes]
    programs.extend((a,b) for a,b in combinations_with_replacement(cubes,2))
    return programs


def evaluate(program,vector):
    return any(all(required==-1 or required==actual
                   for required,actual in zip(term,vector))
               for term in program)


def program_rank(program):
    return (len(program),sum(v!=-1 for term in program for v in term),
            tuple(program))


def vector(features,keys):
    if not isinstance(features,dict) or set(features)!=set(keys):
        raise HOLD("Not all source-supported variables were observed")
    return tuple(int(features[name]) for name in keys)


def find_contradiction(observations):
    """Mathematical impossibility certificate in the CURRENT feature space."""
    for i,a in enumerate(observations):
        for b in observations[i+1:]:
            if (a["old_features"]==b["old_features"]
                    and a["reply"]!=b["reply"]):
                return {"same_public_features":a["old_features"],
                        "different_source_answers":[a["id"],b["id"]]}
    return None


def compile_source(s,owner):
    """A hypothetical preference learner. No authorization is generated here."""
    public_check(s)
    trace=[]
    if not s["contact_allowed"] or s["allowed_source_questions"]==0:
        return {
            "schema":PACKET,"case_id":s["case_id"],"source_public_sha256":digest(s),
            "state":"HOLD_NO_CONTACT","questions":[],"contradiction":None,
            "learned_additional_feature":None,"program":None,
            "feature_names":list(BASE_FEATURES),"author_observations":[],
            "source_disclosed_feature_receipt":None,
            "synthetic_source_only":True,"permission_to_execute":False,
        }

    observed=[]
    for i in ORDER:
        w=world(i)
        reply=owner.answer_hypothetical(s,w)
        verify_response(s,"OBSERVE",w["id"],reply)
        if reply["response"] not in ("YES","NO"):
            raise HOLD("Hypothetical response is not affirmative/negative")
        trace.append(reply)
        observed.append({
            "id":w["id"],"old_features":w["initial_features"],
            "reply":reply["response"],
        })
    conflict=find_contradiction(observed)
    keys=list(BASE_FEATURES)
    revealed=None
    complete_features={
        w["id"]:w["initial_features"].copy()
        for w in [world(i) for i in range(8)]
    }
    # Preload unseen PUBLIC observable features; no unseen preference labels.
    for i in range(8):
        w=world(i,"HELDOUT")
        complete_features[w["id"]]=w["initial_features"].copy()
    status="BASE_SUFFICIENT"
    if conflict:
        reply=owner.disclose_missing_distinction(s,conflict)
        verify_response(s,"FEATURE",None,reply)
        trace.append(reply)
        revealed=reply
        body=reply["response"]
        if not isinstance(body,dict) or set(body)!={
                "status","feature_name","world_values"}:
            raise HOLD("Source correction has unknown shape")
        if body["status"]=="WITHHELD_BY_SOURCE":
            if body["feature_name"] is not None or body["world_values"] is not None:
                raise HOLD("Withheld dimension was secretly supplied")
            return {
                "schema":PACKET,"case_id":s["case_id"],
                "source_public_sha256":digest(s),
                "state":"HOLD_SOURCE_FEATURE_WITHHELD",
                "questions":trace,"contradiction":conflict,
                "learned_additional_feature":None,"program":None,
                "feature_names":keys,"author_observations":observed,
                "source_disclosed_feature_receipt":revealed,
                "synthetic_source_only":True,"permission_to_execute":False,
            }
        if (body["status"]!="NEW_DECLARED_FEATURE"
                or not isinstance(body["feature_name"],str)
                or not 2<=len(body["feature_name"])<=50
                or body["feature_name"] in keys
                or not isinstance(body["world_values"],dict)
                or set(body["world_values"])!=set(complete_features)
                or any(type(x) is not bool for x in body["world_values"].values())):
            raise HOLD("New source dimension is incomplete or self-contradictory")
        name=body["feature_name"];keys.append(name)
        for world_id in complete_features:
            complete_features[world_id][name]=body["world_values"][world_id]
        status="ADDED_FEATURE"

    candidates=[
        p for p in all_programs(len(keys))
        if all(evaluate(p,vector(complete_features[row["id"]],keys))==(
            row["reply"]=="YES") for row in observed)
    ]
    if not candidates:
        return {
            "schema":PACKET,"case_id":s["case_id"],
            "source_public_sha256":digest(s),
            "state":"HOLD_CONCEPT_NOT_EXPRESSIBLE",
            "questions":trace,"contradiction":conflict,
            "learned_additional_feature":keys[-1] if revealed else None,
            "program":None,"feature_names":keys,
            "author_observations":observed,
            "source_disclosed_feature_receipt":revealed,
            "synthetic_source_only":True,"permission_to_execute":False,
        }
    chosen=min(candidates,key=program_rank)
    signatures={tuple(evaluate(p,tuple(bool(i&(1<<j))
                             for j in range(len(keys))))
                      for i in range(2**len(keys))) for p in candidates}
    if len(signatures)!=1:
        # The same observed source examples support contradictory interpretations
        # on as-yet-unobserved facts, so decline to certify the meaning.
        status="HOLD_UNDERDETERMINED_MEANING"
    return {
        "schema":PACKET,"case_id":s["case_id"],
        "source_public_sha256":digest(s),
        "state":status,"questions":trace,"contradiction":conflict,
        "learned_additional_feature":keys[-1] if revealed else None,
        "program":[list(cube) for cube in chosen],
        "feature_names":keys,"author_observations":observed,
        "source_disclosed_feature_receipt":revealed,
        "candidate_programs_after_training":len(candidates),
        "equivalent_signatures_after_training":len(signatures),
        "syntax_is_relational_DNF_not_new_logic":True,
        "unknown_feature_disclosed_by_source_not_invented_from_silence":True,
        "synthetic_source_only":True,"permission_to_execute":False,
    }


def preference(cartridge,world_id):
    """Inference only: NEVER a scoped permission or real-person testimony."""
    if cartridge["state"] not in ("BASE_SUFFICIENT","ADDED_FEATURE"):
        return None
    from casebook import world
    i=int(world_id.split("-")[1])
    split=world_id.split("-")[0]
    if world_id!=world(i,split)["id"]:
        raise HOLD("Unsupported target context")
    features=world(i,split)["initial_features"].copy()
    receipt=cartridge["source_disclosed_feature_receipt"]
    if receipt is not None:
        entry=receipt["response"]
        features[entry["feature_name"]]=entry["world_values"][world_id]
    return evaluate(tuple(tuple(v) for v in cartridge["program"]),
                    vector(features,cartridge["feature_names"]))
