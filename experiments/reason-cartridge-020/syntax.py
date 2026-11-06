"""Self-improving *bounded text parser* for a previously unknown phrase format.

Learns a small grammar of exact prefix/suffix templates from synthetic,
teacher-labeled examples. The target phrase can be NEW, but the sentence
form must match previously sourced templates. This is supervised classical
pattern induction, not natural-language understanding or newly invented
ethical logic. It cannot infer whether the recipient wants anything without
their own statement, confirmation and scope-specific permission.

The withheld teacher examples and simulated recipients are in a DIFFERENT
module and never imported here.
"""
from __future__ import annotations

from hashlib import sha256
import json

SCHEMA="motif.reason.golden-mirror-learns.templates.v1"
SOURCE_VERSION="motif.reason.golden-mirror-learns.scripted-owner.v1"
MAX_TEMPLATES=8


class HOLD(ValueError):
    pass


def digest(v):
    return sha256(json.dumps(v,ensure_ascii=True,sort_keys=True,
                             separators=(",",":"),allow_nan=False).encode()).hexdigest()


def extract(templates,utterance):
    if not isinstance(utterance,str) or not 5<=len(utterance)<=240:
        return None
    if "\r" in utterance or "\n" in utterance:
        return None
    found=set()
    for entry in templates:
        if not isinstance(entry,dict) or set(entry)!={"prefix","suffix","training_support"}:
            raise HOLD("Unrecognized learned language relation")
        prefix=entry["prefix"];suffix=entry["suffix"]
        if (not isinstance(prefix,str) or not isinstance(suffix,str)
            or not prefix or not suffix):
            raise HOLD("An unconstrained partial parser would overgeneralize")
        if not utterance.startswith(prefix) or not utterance.endswith(suffix):
            continue
        phrase=utterance[len(prefix):len(utterance)-len(suffix)]
        if (3<=len(phrase)<=140 and phrase.strip()==phrase
                and any(x.isalpha() for x in phrase)):
            found.add(phrase)
    return next(iter(found)) if len(found)==1 else None


def learn(teacher):
    packet=teacher.training()
    if (not isinstance(packet,dict) or set(packet)!={
        "source_revision","training","negative","source_kind"}
        or packet["source_revision"]!=SOURCE_VERSION
        or packet["source_kind"]!="SIMULATED_TEACHER_SUPERVISED_SPANS"
        or not isinstance(packet["training"],list)
        or not 4<=len(packet["training"])<=18
        or not isinstance(packet["negative"],list)):
        raise HOLD("Unrecognized learning teacher or unlimited evidence")
    counts={}
    for example in packet["training"]:
        if not isinstance(example,dict) or set(example)!={"utterance","desired_span"}:
            raise HOLD("No source-labeled phrase boundary")
        s=example["utterance"];goal=example["desired_span"]
        if (not isinstance(s,str) or not isinstance(goal,str)
                or not 3<=len(goal)<=140 or s.count(goal)!=1):
            raise HOLD("Ambiguous or unsourced training phrase")
        index=s.index(goal)
        candidate=(s[:index],s[index+len(goal):])
        if not candidate[0] or not candidate[1]:
            raise HOLD("A learned template requires both delimiters")
        counts[candidate]=counts.get(candidate,0)+1
    templates=[
        {"prefix":a,"suffix":b,"training_support":v}
        for (a,b),v in sorted(counts.items())
        if v>=2
    ]
    if not 1<=len(templates)<=MAX_TEMPLATES:
        raise HOLD("Not enough repeated source evidence to learn syntax")
    if any(extract(templates,row["utterance"])!=row["desired_span"]
           for row in packet["training"]):
        raise HOLD("A source-owner labeled span cannot be reproduced")
    if any(extract(templates,bad) is not None for bad in packet["negative"]):
        raise HOLD("Induction incorrectly accepts an exposed negative")
    learned={
        "schema":SCHEMA,"teacher_source_version":SOURCE_VERSION,
        "training_examples":len(packet["training"]),
        "training_negatives":len(packet["negative"]),
        "templates":templates,
        "source_training_digest":digest(packet),
        "learned_from_teacher_spans_not_hidden_answers":True,
        "natural_language_understanding_not_demonstrated":True,
        "external_actions":False,
    }
    return learned


def interpret(model,utterance):
    if not isinstance(model,dict) or model.get("schema")!=SCHEMA:
        raise HOLD("No learned, admitted parser")
    return extract(model["templates"],utterance)
