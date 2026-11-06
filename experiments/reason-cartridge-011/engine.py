"""REASON-011: typed, four-valued, explicitly non-explosive legal hypotheticals.

This engine reasons ONLY from a pinned repository-owned fictional casebook.
Two-sided evidence (YES and NO) is retained; missing evidence is UNKNOWN, not NO.
Time, forum and subject are strict scope dimensions. Allegations are visible
but do not become stipulated premises. Rules never cross scope implicitly.

No real court, lawyer or rights assignment is inferred by this engine.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from pathlib import Path
import json
import re

SOURCE=Path(__file__).with_name("casebook.py")
SOURCE_BLOB="7aad1966545b1c6336726a20667a65f5d634daef"
SCHEMA="motif.reason.impossible-court.provenance.v1"
REVISION="motif.reason.impossible-court.fictional-v1"
FIELDS=("forum","epoch","subject","predicate","sign")
ALLOW_SIGNS=("YES","NO")
SAFE=re.compile(r"^[A-Z0-9_-]{1,72}$")
MAX_BYTES=48000
MAX_ROUNDS=50

class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin():
    raw=SOURCE.read_bytes()
    current=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if current!=SOURCE_BLOB:
        raise HOLD("Source-owned fictional casebook changed: re-review labels/rules")
    return current


def key(literal):
    if not isinstance(literal,dict) or set(literal)!=set(FIELDS):
        raise HOLD("Unrecognized typed proposition")
    if (any(not isinstance(literal[k],str) or not SAFE.fullmatch(literal[k])
            for k in FIELDS) or literal["sign"] not in ALLOW_SIGNS):
        raise HOLD("Unknown sign, temporal reference, subject or forum")
    return tuple(literal[name] for name in FIELDS)


def context(literal):
    return key(literal)[:3]


def reverse(literal):
    z=dict(literal)
    z["sign"]="NO" if literal["sign"]=="YES" else "YES"
    return z


def validate_case(case, *, authenticate=True):
    if not isinstance(case,dict) or set(case)!={
            "id","title","fictional","question","claims","rules",
            "queries","priority"}:
        raise HOLD("Unsupported hypothetical-case schema")
    if (case["fictional"] is not True
            or not isinstance(case["id"],str) or not SAFE.fullmatch(case["id"])
            or not isinstance(case["title"],str) or not 1<=len(case["title"])<=180
            or not isinstance(case["question"],str) or not 1<=len(case["question"])<=260
            or not isinstance(case["claims"],list) and not isinstance(case["claims"],tuple)
            or not isinstance(case["rules"],list) and not isinstance(case["rules"],tuple)
            or not isinstance(case["queries"],list) and not isinstance(case["queries"],tuple)
            or not 1<=len(case["claims"])<=32
            or not 0<=len(case["rules"])<=16
            or not 1<=len(case["queries"])<=10):
        raise HOLD("Unbounded, non-fictional, or unrecognized court fixture")
    names=set()
    for claim in case["claims"]:
        if not isinstance(claim,dict) or set(claim)!={
            "id","literal","source_status","revisable"}:
            raise HOLD("Unknown evidence statement")
        cid=claim["id"]
        if not isinstance(cid,str) or not SAFE.fullmatch(cid) or cid in names:
            raise HOLD("Duplicate/invalid source assertion identity")
        names.add(cid)
        key(claim["literal"])
        if (claim["source_status"] not in ("STIPULATED_HYPOTHESIS","PARTY_ALLEGATION")
                or type(claim["revisable"]) is not bool
                or (claim["source_status"]=="PARTY_ALLEGATION"
                    and claim["revisable"])):
            raise HOLD("Unknown claim provenance or incorrectly promoted allegation")
    for rule in case["rules"]:
        if (not isinstance(rule,dict) or set(rule)!={
                "id","premises","conclusion","rule_status"}):
            raise HOLD("Unrecognized inferential rule")
        rid=rule["id"]
        if not isinstance(rid,str) or not SAFE.fullmatch(rid) or rid in names:
            raise HOLD("Duplicate/invalid rule source identity")
        names.add(rid)
        if (rule["rule_status"]!="HYPOTHETICAL_NORM_NOT_REAL_LAW"
                or not isinstance(rule["premises"],(list,tuple))
                or not 1<=len(rule["premises"])<=4):
            raise HOLD("Unreviewed actual-law assertion or unbounded rule")
        result_context=context(rule["conclusion"])
        for antecedent in rule["premises"]:
            if context(antecedent)!=result_context:
                raise HOLD("Temporal, person or court transfer without explicit source rule")
    questions=set()
    for item in case["queries"]:
        if not isinstance(item,dict) or set(item)!={
                "id","literal","expected_four_value"}:
            raise HOLD("Unrecognized legal issue")
        if (not isinstance(item["id"],str)
                or not SAFE.fullmatch(item["id"]) or item["id"] in questions
                or key(item["literal"])[-1]!="YES"
                or item["expected_four_value"] not in (
                    "SUPPORTED","REFUTED","BOTH","UNDETERMINED")):
            raise HOLD("Invalid query or preassigned answer type")
        questions.add(item["id"])
    if (not isinstance(case["priority"],str) or not SAFE.fullmatch(case["priority"])):
        raise HOLD("Unknown conflict-handling priority")
    if authenticate:
        # This is content equality to a pinned fictional source, NOT an
        # official court-opinion record, signature, or factual attestation.
        pin()
        from casebook import by_id
        try:
            genuine=by_id(case["id"])
        except StopIteration as exc:
            raise HOLD("Source has no such fictional legal scenario") from exc
        if json.loads(json.dumps(case,sort_keys=True))!=json.loads(
                json.dumps(genuine,sort_keys=True)):
            raise HOLD("Unrecognized amended/forged fictional source")
    return case


def proof_order(proof):
    return (len(proof["claims"])+len(proof["rules"]),
            len(proof["claims"]),tuple(proof["claims"]),tuple(proof["rules"]))


def derive(case, omitted=()):
    """Finite least fixed point of explicit positive and negative evidence.

    Only authenticated stipulations enter the premise set. A party allegation
    does not get an edge into the proof graph. Proofs are minimal under one
    deterministic ordering, not globally minimal inconsistency diagnoses.
    """
    validate_case(case)
    if not isinstance(omitted,(tuple,list,set)):
        raise HOLD("Unsupported intervention")
    dropped=set(omitted)
    editable={c["id"] for c in case["claims"] if c["revisable"]}
    if not dropped.issubset(editable):
        raise HOLD("Can only hypothetically retract explicitly revisable premises")
    known={}
    for fact in case["claims"]:
        if fact["source_status"]!="STIPULATED_HYPOTHESIS" or fact["id"] in dropped:
            continue
        k=key(fact["literal"])
        candidate={"claims":[fact["id"]],"rules":[]}
        if k not in known or proof_order(candidate)<proof_order(known[k]):
            known[k]=candidate
    for attempt in range(MAX_ROUNDS):
        updated=False
        for r in case["rules"]:
            inputs=[known.get(key(p)) for p in r["premises"]]
            if any(item is None for item in inputs):
                continue
            witness={"claims":sorted(set(cid for item in inputs
                                           for cid in item["claims"])),
                     "rules":sorted(set([r["id"]]+[
                         rid for item in inputs for rid in item["rules"]]))}
            target=key(r["conclusion"])
            if target not in known or proof_order(witness)<proof_order(known[target]):
                known[target]=witness
                updated=True
        if not updated:
            return known
    raise HOLD("Unbounded inference, unsupported recursive cycle or unstable provenance")


def verdict(facts,literal):
    token=key(literal)
    yes=token[:-1]+("YES",)
    no=token[:-1]+("NO",)
    positive=facts.get(yes)
    negative=facts.get(no)
    status=("BOTH" if positive and negative else
            "SUPPORTED" if positive else
            "REFUTED" if negative else "UNDETERMINED")
    core=None
    if positive and negative:
        core={"claim_witness_ids":sorted(set(positive["claims"]+negative["claims"])),
              "rule_witness_ids":sorted(set(positive["rules"]+negative["rules"])),
              "minimality_claim":"ONE_EXPLICIT_PAIR_OF_WITNESSES_NOT_GLOBAL_MINIMUM"}
    return {"four_value":status,"positive_proof":positive,"negative_proof":negative,
            "contradiction_witness":core,
            "explosion_permitted":False,
            "real_court_holding":False}


def remedial_questions(case,query,facts):
    actual=verdict(facts,query)["four_value"]
    if actual!="BOTH":
        return []
    proof=verdict(facts,query)
    premise_ids=set(proof["contradiction_witness"]["claim_witness_ids"])
    alternatives=[]
    for id in sorted(premise_ids):
        claim=next((c for c in case["claims"] if c["id"]==id),None)
        if claim is None or not claim["revisable"]:
            continue
        variant=verdict(derive(case,(id,)),query)["four_value"]
        if variant!=actual:
            alternatives.append({
                "question":"Would the source-owner withdraw this disputed stipulation?",
                "source_claim":id,
                "counterfactual_if_withdrawn":variant,
                "observation_performed":False,
                "still_hypothetical":True,
            })
    return alternatives


def decide(case):
    validate_case(case)
    facts=derive(case)
    results=[]
    for q in case["queries"]:
        outcome=verdict(facts,q["literal"])
        results.append({
            "query_id":q["id"],"literal":q["literal"],
            "result":outcome,
            "fictional_expected_for_test":q["expected_four_value"],
            "counterfactual_review_questions":remedial_questions(case,q["literal"],facts),
            "matches_fixture":outcome["four_value"]==q["expected_four_value"],
        })
    return {
        "schema":SCHEMA,"case_id":case["id"],"fictional":True,
        "case_title":case["title"],
        "source_owner_revision":REVISION,
        "source_owner_blob":pin(),
        "source_contract_digest":digest(case),
        "results":results,
        "all_expected_checks_match":all(row["matches_fixture"] for row in results),
        "proof_count":len(facts),
        "party_allegations_excluded":sum(c["source_status"]=="PARTY_ALLEGATION"
                                        for c in case["claims"]),
        "explicit_negation_not_negation_as_failure":True,
        "time_forum_identity_separated":True,
        "current_law_inferred":False,
        "external_actions":False,"real_world_authority":False,
    }


def export(case):
    base=decide(case)
    packet=dict(base,checksum_sha256=digest(base))
    raw=json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_BYTES:
        raise HOLD("Overlarge fictional court packet")
    return raw


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>MAX_BYTES:
        raise HOLD("Malformed or oversized court report")
    try:
        packet=json.loads(raw)
    except (TypeError,ValueError) as exc:
        raise HOLD("Invalid report JSON") from exc
    fields={"schema","case_id","fictional","case_title","source_owner_revision",
            "source_owner_blob","source_contract_digest","results",
            "all_expected_checks_match","proof_count","party_allegations_excluded",
            "explicit_negation_not_negation_as_failure","time_forum_identity_separated",
            "current_law_inferred","external_actions","real_world_authority",
            "checksum_sha256"}
    if not isinstance(packet,dict) or set(packet)!=fields:
        raise HOLD("Unknown report fields or forgery")
    if (packet["schema"]!=SCHEMA or packet["fictional"] is not True
            or packet["source_owner_blob"]!=pin()
            or packet["source_owner_revision"]!=REVISION
            or packet["external_actions"] is not False
            or packet["real_world_authority"] is not False
            or packet["current_law_inferred"] is not False):
        raise HOLD("Unreviewed source or legal authority")
    from casebook import by_id
    try:
        replay=json.loads(export(by_id(packet["case_id"])))
    except (StopIteration,ValueError,TypeError) as exc:
        raise HOLD("Missing source-owned fictional case") from exc
    if packet!=replay:
        raise HOLD("Altered result, proof, scope, or counterfactual—even if rehashed")
    return packet
