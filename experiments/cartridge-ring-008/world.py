"""RING-008 semantic program laboratory: SOURCE-AUTHORED, bounded paired language.

Examples carry typed target meanings rather than explicit effect-word lists.
The learner sees (utterance, frame) pairs, never the template or lexicon IDs.
Separate template sets for train / selection dev; later independent *separate
module* challenge is unseen when synthesis freezes its program.

All language and labels are invented by this fixture author; this DOES NOT
constitute training on naturally occurring or independently annotated speech.
"""
from __future__ import annotations
from hashlib import sha256
import json
import random

SCHEMA="motif.ring008.typed-meaning-example.v1"
SLOTS=("mode","topic","operator")
VALUES={
    "mode":("INQUIRE","ACT","META","UNKNOWN"),
    "topic":("PATH","RECORD","SCHEDULE","UNKNOWN"),
    "operator":("REACH","INSPECT","TIME","TRANSFER","MODIFY","UNKNOWN"),
}
LEXICON={
    "path":("path","route","trail","link"),
    "reach":("reach","access","connect to","arrive at"),
    "place":("station","endpoint","bridge","finish"),
    "record":("ledger","document","journal","record"),
    "show":("show","reveal","indicate","display"),
    "reliable":("trustworthy","accurate","valid"),
    "evidence":("entry","witness","observation","claim"),
    "meeting":("gathering","meeting","session","appointment"),
    "occur":("happen","occur","begin","start"),
    "day":("friday","monday","tomorrow","sunday"),
    "share":("share","send","forward","deliver"),
    "recipient":("friends","neighbors","others","the public"),
    "change":("change","edit","modify","rewrite"),
}
# Exactly TWO authored template families below. The learner receives ONLY
# generated example sentences and typed meanings, not these templates.
TRAIN={
    ("INQUIRE","PATH","REACH"):(
        "could the {path} still {reach} the {place}",
        "does this {path} {reach} the {place}",
        "what if this {path} still {reach} the {place}",
    ),
    ("INQUIRE","RECORD","INSPECT"):(
        "what does the {record} {show} about the {evidence}",
        "could the {record} {show} the {evidence}",
        "is the {record} {reliable} for the {evidence}",
    ),
    ("INQUIRE","SCHEDULE","TIME"):(
        "when does the {meeting} {occur}",
        "does the {meeting} {occur} after {day}",
        "which {day} is the {meeting} scheduled for",
    ),
    ("ACT","RECORD","TRANSFER"):(
        "please {share} the {record} with {recipient}",
        "could you {share} the {record} with {recipient}",
        "we need to {share} the {record} with {recipient}",
    ),
    ("ACT","RECORD","MODIFY"):(
        "please {change} the {record}",
        "could you {change} the {record} now",
        "make sure to {change} the {record}",
    ),
    ("ACT","SCHEDULE","MODIFY"):(
        "please {change} the {meeting} to {day}",
        "could you {change} the {meeting} date",
        "we need to {change} the {meeting}",
    ),
    ("META","RECORD","TRANSFER"):(
        "what if we {share} the {record} with {recipient}",
        "what happens when someone {share} a {record}",
        "could an explanation of {share} help the {record}",
    ),
    ("META","PATH","REACH"):(
        "what would happen if this {path} failed to {reach} the {place}",
        "imagine a {path} could {reach} the {place}",
        "suppose the {path} did not {reach} the {place}",
    ),
    ("UNKNOWN","UNKNOWN","UNKNOWN"):(
        "the {record} and the {meeting}",
        "maybe something about the {record}",
        "what about the {record} and the {place}",
    ),
}
DEV={
    ("INQUIRE","PATH","REACH"):(
        "will the {path} eventually {reach} the {place}",
        "can this {path} {reach} the {place} yet",
    ),
    ("INQUIRE","RECORD","INSPECT"):(
        "does the {record} contain the {evidence}",
        "can the {record} {show} {evidence}",
    ),
    ("INQUIRE","SCHEDULE","TIME"):(
        "what time does the {meeting} {occur}",
        "how soon will the {meeting} {occur} after {day}",
    ),
    ("ACT","RECORD","TRANSFER"):(
        "please go ahead and {share} the {record} to {recipient}",
        "would you {share} this {record} to {recipient}",
    ),
    ("ACT","RECORD","MODIFY"):(
        "remember to {change} the {record}",
        "go ahead and {change} the {record} now",
    ),
    ("ACT","SCHEDULE","MODIFY"):(
        "go ahead and {change} the {meeting} for {day}",
        "would you {change} the {meeting} date",
    ),
    ("META","RECORD","TRANSFER"):(
        "what could happen if we {share} the {record}",
        "imagine if someone {share} the {record} to {recipient}",
    ),
    ("META","PATH","REACH"):(
        "imagine if this {path} would {reach} the {place}",
        "hypothetically the {path} could {reach} the {place}",
    ),
    ("UNKNOWN","UNKNOWN","UNKNOWN"):(
        "what about the {record}",
        "the {meeting} and the {record} perhaps",
    ),
}


def digest(doc):
    return sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def generate(kind,*,seed=1122,rounds=6):
    patterns={"train":TRAIN,"dev":DEV}.get(kind)
    if patterns is None or type(seed) is not int or type(rounds) is not int or not 1<=rounds<=25:
        raise ValueError("Unknown or oversized authored evidence request")
    rng=random.Random(seed)
    rows=[]
    for label,templates in sorted(patterns.items()):
        for template in templates:
            for _ in range(rounds):
                binds={key:rng.choice(values) for key,values in LEXICON.items()}
                phrase=template.format(**binds)
                rows.append({"text":phrase,
                             "frame":dict(zip(SLOTS,label))})
    rng.shuffle(rows)
    out={"schema":SCHEMA,"split":kind,
         "rows":rows,
         "labels_author_created":True,
         "examples_hide_template_ids":True,
         "distinct_template_family":kind,
         "not_real_human_speech":True}
    out["receipt_sha256"]=digest(out)
    return out


def check(data,expected=None):
    if (not isinstance(data,dict) or data.get("schema")!=SCHEMA
            or data.get("split") not in ("train","dev","novel")
            or expected is not None and data.get("split")!=expected
            or not isinstance(data.get("rows"),list)
            or not 1<=len(data["rows"])<=1000
            or data.get("labels_author_created") is not True
            or data.get("receipt_sha256")!=digest({
                k:v for k,v in data.items() if k!="receipt_sha256"})):
        raise ValueError("Dataset missing, modified or incorrectly scoped")
    for row in data["rows"]:
        if (not isinstance(row,dict) or set(row)!={"text","frame"}
                or type(row["text"]) is not str
                or not 1<=len(row["text"])<=320
                or not isinstance(row["frame"],dict)
                or set(row["frame"])!=set(SLOTS)
                or any(row["frame"][slot] not in VALUES[slot] for slot in SLOTS)):
            raise ValueError("Malformed typed meaning")
    return data
