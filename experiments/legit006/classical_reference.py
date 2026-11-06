"""LEGIT-006 strong conventional rule parser and independent finite truth oracle.

No imports from induced teacher grammar or source-ledger solver. The parser
is hand-written classical pattern composition with extra lexical coverage.
The model checker independently enumerates the two possible target states.
"""
from __future__ import annotations

import re

PATTERNS={
    "NO_POSITIVE_EVIDENCE":[
        ("there is no evidence that","{target} exists"),
        ("there is no evidence that","{target} is present"),
        ("no evidence indicates that","{target} exists"),
        ("no evidence indicates that","{target} is present"),
        ("no proof supports","{target} existing")],
    "HAS_NEGATIVE_EVIDENCE":[
        ("there is evidence that","{target} does not exist"),
        ("there is evidence that","{target} is absent"),
        ("evidence indicates that","{target} does not exist"),
        ("evidence indicates that","{target} is absent"),
        ("a negative report supports","{target} being absent")],
    "NO_NEGATIVE_EVIDENCE":[
        ("there is no evidence that","{target} does not exist"),
        ("there is no evidence that","{target} is absent"),
        ("no evidence indicates that","{target} does not exist"),
        ("no evidence indicates that","{target} is absent")],
    "HAS_POSITIVE_EVIDENCE":[
        ("there is evidence that","{target} exists"),
        ("there is evidence that","{target} is present"),
        ("evidence indicates that","{target} exists"),
        ("evidence indicates that","{target} is present")],
    "MUST_ABSENT":[
        ("does a negative {indicator}","prove {target} is absent"),
        ("does a negative {indicator}","exclude {target}"),
        ("does failing to detect {indicator}","prove {target} is absent"),
        ("does failing to detect {indicator}","exclude {target}")],
    "CAN_PRESENT":[
        ("can {target} exist","despite a negative {indicator}"),
        ("can {target} exist","without detecting {indicator}"),
        ("could {target} be present","despite a negative {indicator}"),
        ("could {target} be present","without detecting {indicator}"),
        ("can {target} still exist","if {indicator} is not detected")],
    "MUST_PRESENT":[
        ("does a positive {indicator}","prove {target} exists"),
        ("does a positive {indicator}","guarantee {target}"),
        ("does detecting {indicator}","prove {target} exists"),
        ("does detecting {indicator}","guarantee {target}"),
        ("does a successful {indicator} measurement","ensure {target} exists")],
    "CAN_ABSENT":[
        ("can {target} be absent","despite a positive {indicator}"),
        ("can {target} be absent","even when detecting {indicator}"),
        ("could {target} fail to exist","despite a positive {indicator}"),
        ("could {target} fail to exist","even when detecting {indicator}")],
}
SLOT=re.compile(r"(\{target\}|\{indicator\})")
CAPTURE=r"([a-z][a-z0-9-]*(?: [a-z][a-z0-9-]*){0,7}?)"
UNSAFE=re.compile(
    r"\b(no|not|never|none|neither|nor|except|unless|despite|without|"
    r"does|doesn't|cannot|can't|prove|rule|exclude|exists|exist|is|are|"
    r"absent|present|missing|evidence|indicates|implies|guarantee|some|all)\b")


def _regex(kind,one,two):
    ending="." if kind in list(PATTERNS)[:4] else "?"
    pieces=SLOT.split(one+" "+two+ending)
    regexp=""
    slots=[]
    for part in pieces:
        if part in ("{target}","{indicator}"):
            regexp+=CAPTURE
            slots.append(part[1:-1])
        else:
            regexp+=re.escape(part)
    return re.compile("^"+regexp+"$"),slots


def parse_reference(text,target,indicator):
    if not all(isinstance(x,str) for x in (text,target,indicator)):
        return None
    statement=" ".join(text.lower().split())
    target=" ".join(target.lower().split())
    indicator=" ".join(indicator.lower().split())
    proposals=[]
    for kind,pairs in PATTERNS.items():
        for left,right in pairs:
            pattern,labels=_regex(kind,left,right)
            result=pattern.fullmatch(statement)
            if result is None:
                continue
            meanings=dict(zip(labels,result.groups()))
            if any(UNSAFE.search(s) for s in meanings.values()):
                continue
            if meanings.get("target")!=target or meanings.get("indicator",indicator)!=indicator:
                continue
            proposals.append(kind)
    return proposals[0] if len(proposals)==1 else None


def reference_truth(ledger,kind):
    # Exactly the two possible target states. Trust labels are synthetic
    # declared premises and are not independent validation.
    roots={}
    for row in ledger["reports"]:
        sig=(row["kind"],row["assurance"],row["coverage"],row["detection"])
        old=roots.get(row["root"])
        if old is not None and old!=sig:
            raise ValueError("Conflicting source root")
        roots[row["root"]]=sig
    admitted=[r for r in roots.values() if r[1]=="DECLARED_VALID"]
    pos=sum(r[0]=="POSITIVE_WITNESS" for r in admitted)
    neg=sum(r[0]=="NEGATIVE_SENSOR" for r in admitted)
    decisive_neg=sum(r[0]=="NEGATIVE_SENSOR" and r[2]=="EXHAUSTIVE" and
                     r[3]=="GUARANTEED" for r in admitted)
    worldset={False,True}
    if pos:
        worldset &= {True}
    if decisive_neg:
        worldset &= {False}
    if not worldset:
        return None
    return {
        "NO_POSITIVE_EVIDENCE":pos==0,
        "HAS_NEGATIVE_EVIDENCE":neg>0,
        "NO_NEGATIVE_EVIDENCE":neg==0,
        "HAS_POSITIVE_EVIDENCE":pos>0,
        "MUST_ABSENT":worldset=={False},
        "CAN_PRESENT":True in worldset,
        "MUST_PRESENT":worldset=={True},
        "CAN_ABSENT":False in worldset,
    }[kind]
