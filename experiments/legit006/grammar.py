"""LEGIT-006: small contrast-trained semantic adversary grammar.

Learn TWO parts of a sentence from paired, corrected examples. Recombine
known components; do not pretend to know unseen connectives. The teacher
supplies the meaning and spans *during training*; new cases supply ONLY an
unannotated sentence and separately typed source ledger.

It is classical anti-unification, not unrestricted NLP or a learned ontology.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import re

SCHEMA = "motif.semantic-adversary-grammar.v1"
KINDS = (
    "NO_POSITIVE_EVIDENCE", "HAS_NEGATIVE_EVIDENCE",
    "NO_NEGATIVE_EVIDENCE", "HAS_POSITIVE_EVIDENCE",
    "MUST_ABSENT", "CAN_PRESENT", "MUST_PRESENT", "CAN_ABSENT")
CAPTURE = r"([a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*){0,7}?)"
SLOT = re.compile(r"(\{target\}|\{indicator\})")
TEXT = re.compile(r"^[a-z0-9 ,?.:'-]{1,400}$")
RISKY_NOUN = re.compile(
    r"\b(no|not|never|none|neither|nor|except|unless|despite|without|"
    r"does|doesn't|cannot|can't|prove|rule|exclude|exists|exist|is|are|"
    r"absent|present|missing|evidence|indicates|implies|guarantee|some|all)\b")
TYPES = {
    "NO_POSITIVE_EVIDENCE":("target",),
    "HAS_NEGATIVE_EVIDENCE":("target",),
    "NO_NEGATIVE_EVIDENCE":("target",),
    "HAS_POSITIVE_EVIDENCE":("target",),
    "MUST_ABSENT":("target","indicator"),
    "CAN_PRESENT":("target","indicator"),
    "MUST_PRESENT":("target","indicator"),
    "CAN_ABSENT":("target","indicator"),
}


class HOLD(ValueError):
    pass


def normalized(value):
    if not isinstance(value,str):
        raise HOLD("Invalid question")
    v=" ".join(value.lower().strip().split())
    if not TEXT.fullmatch(v):
        raise HOLD("Unknown characters or question length")
    return v


def _replace_span(text, span, field):
    span=normalized(span)
    if len(span)>80:
        raise HOLD("Teacher span too large")
    matches=list(re.finditer(r"(?<![a-z0-9])"+re.escape(span)+
                            r"(?![a-z0-9])",text))
    if len(matches)!=1:
        raise HOLD("Unanchored or ambiguous teacher source phrase")
    m=matches[0]
    return text[:m.start()]+"{"+field+"}"+text[m.end():]


def _example(row):
    if not isinstance(row,dict) or set(row)!={
            "id","sentence","left","right","target","indicator","kind"}:
        raise HOLD("Unknown training schema")
    if (not isinstance(row["id"],str) or
        not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",row["id"])
        or row["kind"] not in KINDS):
        raise HOLD("Unreviewed source teacher or semantic category")
    kind=row["kind"]
    terminal="." if kind in KINDS[:4] else "?"
    left=normalized(row["left"])
    right=normalized(row["right"])
    if normalized(row["sentence"])!=left+" "+right+terminal:
        raise HOLD("Teacher annotation must reconstruct original statement")
    target=normalized(row["target"])
    indicator=normalized(row["indicator"])
    if RISKY_NOUN.search(target) or RISKY_NOUN.search(indicator):
        raise HOLD("Ambiguous teacher noun with logical connectors")
    abstract_left=left
    abstract_right=right
    for field in TYPES[kind]:
        occurrence=(abstract_left.count(row[field].lower())+
                    abstract_right.count(row[field].lower()))
        if occurrence!=1:
            raise HOLD("Unstable teacher role position")
        if normalized(row[field]) in abstract_left:
            abstract_left=_replace_span(abstract_left,row[field],field)
        else:
            abstract_right=_replace_span(abstract_right,row[field],field)
    seen=list(SLOT.findall(abstract_left+" "+abstract_right))
    if sorted(seen)!=sorted("{"+field+"}" for field in TYPES[kind]):
        raise HOLD("Invalid semantic spans")
    return kind,abstract_left,abstract_right,(target,indicator)


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True).encode()).hexdigest()


def learn(records):
    if not isinstance(records,list) or not 32<=len(records)<=120:
        raise HOLD("Needs bounded contrasted teacher corrections")
    seen_ids=set()
    grouped=defaultdict(list)
    for row in records:
        if not isinstance(row,dict) or row.get("id") in seen_ids:
            raise HOLD("Repeated teacher ID")
        seen_ids.add(row["id"])
        kind,left,right,words=_example(row)
        grouped[kind].append((left,right,words))
    if set(grouped)!=set(KINDS):
        raise HOLD("Incomplete logical contrast grammar")
    rules=[]
    for kind in KINDS:
        rows=grouped[kind]
        if len(rows)<4:
            raise HOLD("Insufficient contrasted training per logical operator")
        lefts=defaultdict(set)
        rights=defaultdict(set)
        seen_pairs=set()
        for left,right,words in rows:
            lefts[left].add(words)
            rights[right].add(words)
            seen_pairs.add((left,right))
        if len(lefts)<2 or len(rights)<2:
            raise HOLD("No demonstrated compositional variation")
        if any(len(v)<2 for v in list(lefts.values())+list(rights.values())):
            raise HOLD("Each fragment must have two independent source topics")
        for left in sorted(lefts):
            for right in sorted(rights):
                rules.append({
                    "kind":kind,"left":left,"right":right,
                    "seen_pair_in_teacher":(left,right) in seen_pairs})
    return {
        "schema":SCHEMA,"status":"PROPOSAL_ONLY",
        "method":"CONTRASTIVE_CLASSICAL_TEMPLATE_COMPOSITION",
        "rules":rules,"teacher_count":len(records),
        "teacher_digest":digest(records),
        "unseen_full_pairs":sum(not x["seen_pair_in_teacher"] for x in rules),
        "real_world_authority":False,
    }


def _compile(rule):
    kind=rule["kind"]
    terminal="." if kind in KINDS[:4] else "?"
    text=rule["left"]+" "+rule["right"]+terminal
    parts=SLOT.split(text)
    regex=""
    roles=[]
    for part in parts:
        if part in ("{target}","{indicator}"):
            regex+=CAPTURE
            roles.append(part[1:-1])
        else:
            regex+=re.escape(part)
    if sorted(roles)!=sorted(TYPES[kind]):
        raise HOLD("Tampered compiled semantics")
    return re.compile("^"+regex+"$"),roles


def parse(sentence,grammar):
    if (not isinstance(grammar,dict) or grammar.get("schema")!=SCHEMA or
            grammar.get("status")!="PROPOSAL_ONLY" or
            not isinstance(grammar.get("rules"),list)):
        raise HOLD("Unknown grammar authority")
    text=normalized(sentence)
    matches=[]
    for row in grammar["rules"]:
        if not isinstance(row,dict) or row.get("kind") not in KINDS:
            raise HOLD("Unknown semantics")
        pattern,roles=_compile(row)
        m=pattern.fullmatch(text)
        if m is None:
            continue
        slots=dict(zip(roles,m.groups()))
        if any(RISKY_NOUN.search(val) for val in slots.values()):
            continue
        if len(slots)==2 and slots["target"]==slots["indicator"]:
            continue
        matches.append({
            "kind":row["kind"],"target":slots["target"],
            "indicator":slots.get("indicator"),
            "seen_pair_in_teacher":row["seen_pair_in_teacher"]})
    if len(matches)!=1:
        return {"status":"HOLD_AMBIGUOUS" if matches else "HOLD_UNKNOWN_SEMANTICS",
                "matches":len(matches),"real_world_authority":False}
    return dict(matches[0],status="PARSE_PROPOSAL_ONLY",
                matches=1,real_world_authority=False)
