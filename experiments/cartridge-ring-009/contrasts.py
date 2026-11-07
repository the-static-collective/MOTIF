"""RING-009 — minimal-pair semantic evidence; syntax templates NEVER given to learner.

Ground truth for this entire experiment is synthetic and authored by one
developer. The learner gets *pairs of raw utterances and typed frames*, but no
rule IDs, pivot locations, cue vocabulary, or generator-template identities.

Train and development are different contrast contexts. Novel source labels
are in an entirely separate module loaded AFTER model freeze.
"""
from __future__ import annotations
from hashlib import sha256
import json
import random
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"cartridge-ring-008"))
import world

SCHEMA="motif.ring009.minimal-pair-evidence.v1"
ROLES=("mode","topic","operator")
TASKS={
    ("RECORD","TRANSFER"):(
        ("send","share","relay"),("the ledger","the journal","the document"),
        ("to neighbors","to colleagues","to others")),
    ("RECORD","MODIFY"):(
        ("edit","revise","rewrite"),("the ledger","the journal","the record"),
        ("for tomorrow","before noon","for the review")),
    ("SCHEDULE","MODIFY"):(
        ("move","shift","reschedule"),("the meeting","the session","the gathering"),
        ("to monday","until friday","for tomorrow")),
}
# Same referent/action tokens appear IN BOTH arms of every training pair.
# Difference must be sought in relational context, not presence of verb.
CONTEXT={
    "train":(
        ("please {event}","what if someone were to {event}"),
        ("could you {event}","suppose somebody wanted to {event}"),
        ("we need you to {event}","imagine if someone tried to {event}"),
        ("i ask you to {event}","consider a person attempting to {event}"),
        ("{event} now","{event} is just hypothetical"),
    ),
    "dev":(
        ("please promptly {event}","what if someone were to quietly {event}"),
        ("could you kindly {event}","suppose somebody wanted to perhaps {event}"),
        ("we need you to immediately {event}","imagine if someone tried to discreetly {event}"),
        ("i ask you to urgently {event}","consider a person attempting to secretly {event}"),
        ("{event} right now","{event} is just hypothetical"),
    ),
}


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def frame(mode,task):
    return {"mode":mode,"topic":task[0],"operator":task[1]}


def generate(split,*,seed=2026110901,repeats=4):
    if split not in CONTEXT or type(seed) is not int or type(repeats) is not int or not 1<=repeats<=12:
        raise ValueError("Invalid minimal pair split")
    rng=random.Random(seed)
    rows=[]
    for task,lex in sorted(TASKS.items()):
        verbs,objects,endings=lex
        for act,mention in CONTEXT[split]:
            for _ in range(repeats):
                event=" ".join((rng.choice(verbs),rng.choice(objects),rng.choice(endings)))
                rows.append({
                    "a":{"text":act.format(event=event),"frame":frame("ACT",task)},
                    "b":{"text":mention.format(event=event),"frame":frame("META",task)},
                })
    rng.shuffle(rows)
    result={
        "schema":SCHEMA,
        "split":split,
        "pairs":rows,
        "pairs_share_event_words_across_opposite_speech_acts":True,
        "rules_and_event_anchor_positions_not_in_learning_rows":True,
        "author_labeled_not_naturally_occurring_speech":True,
    }
    result["receipt_sha256"]=digest(result)
    return result


def check(value,*,split=None):
    if (not isinstance(value,dict) or value.get("schema")!=SCHEMA
            or value.get("split") not in ("train","dev","novel")
            or split is not None and value["split"]!=split
            or not isinstance(value.get("pairs"),list)
            or not 1<=len(value["pairs"])<=180
            or value.get("author_labeled_not_naturally_occurring_speech") is not True
            or value.get("receipt_sha256")!=digest({
                k:v for k,v in value.items() if k!="receipt_sha256"})):
        raise ValueError("Unbound paired dataset")
    for pair in value["pairs"]:
        if not isinstance(pair,dict) or set(pair)!={"a","b"}:
            raise ValueError("Corrupt contrast pair")
        a,b=pair["a"],pair["b"]
        for v in (a,b):
            if (set(v)!={"text","frame"} or type(v["text"]) is not str
                    or not 1<=len(v["text"])<=320
                    or not isinstance(v["frame"],dict)
                    or set(v["frame"])!=set(ROLES)
                    or any(v["frame"][role] not in world.VALUES[role]
                           for role in ROLES)):
                raise ValueError("Invalid typed role example")
        if (a["frame"]["mode"]!="ACT" or b["frame"]["mode"]!="META"
                or any(a["frame"][k]!=b["frame"][k] for k in ("topic","operator"))):
            raise ValueError("Contrasts must differ ONLY in speech-act force")
    return value


def flattened(doc):
    check(doc)
    return [case for pair in doc["pairs"] for case in (pair["a"],pair["b"])]
