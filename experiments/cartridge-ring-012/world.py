"""RING-012: ambiguity is a first-class source fact, not an error to erase.

New synthetic language, authored only for post-freeze tests. Every case has
ZERO, ONE, or SEVERAL explicitly *admissible* interpretations. Multiple
readings mean the author's constructed text is underspecified; they are not
simultaneously asserted true events, authenticated testimony, or measured
natural-language ambiguity. No text from the private How to Live manuscript
or prior personal conversation appears in this public fixture.
"""
from __future__ import annotations
from hashlib import sha256
import json
import random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"cartridge-ring-011"))
import corpus

SCHEMA="motif.ring012.open-world-authored-readings.v1"
TEST_LEX={
    "speaker":("nira","velo","tams","esor","lumi"),
    "agent":("kae","ren","sola","ivo","mai"),
    "verb":("engrave","unfurl","balance","carry","polish"),
    "patient":("bowl","lantern","window","scroll","vial"),
}
# The admissible meanings themselves are authored and withheld from routing.
# Each tuple is (ROOT_FORCE, EVENT_SCOPE, EVENT_POLARITY).
UNIQUE=(
    ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS")),
    ("{speaker} says {agent} did not {verb} {patient}",("ASSERTION","ROOT","NEG")),
    ("{speaker} quotes [{agent} saying please {verb} {patient}]",("MENTION","QUOTED","POS")),
    ("{speaker} wonders ([{agent} might {verb} {patient}])",("MENTION","IMAGINED","POS")),
    ("{speaker} asks {agent} to {verb} {patient} if the bell rings",("DIRECTIVE","CONDITIONAL","POS")),
    ("{speaker} asks {agent} to quote [{agent} saying please {verb} {patient}]",
     ("DIRECTIVE","QUOTED","POS")),
)
AMBIGUOUS=(
    ("{speaker} remembers ({agent} did {verb} {patient})",
     (("ASSERTION","ROOT","POS"),("MENTION","IMAGINED","POS"))),
    ("{speaker} writes [{agent} saying please {verb} {patient}]",
     (("MENTION","QUOTED","POS"),("ASSERTION","QUOTED","POS"))),
    ("{speaker} repeats ({agent} did not {verb} {patient})",
     (("ASSERTION","ROOT","NEG"),("MENTION","QUOTED","NEG"))),
    ("{speaker} wonders if {agent} might {verb} {patient}",
     (("MENTION","IMAGINED","POS"),("MENTION","CONDITIONAL","POS"))),
    ("{speaker} says {agent} did {verb} {patient} (or only imagined it)",
     (("ASSERTION","ROOT","POS"),("MENTION","IMAGINED","POS"))),
    ("{speaker} asks {agent} to {verb} {patient} (in the song)",
     (("DIRECTIVE","ROOT","POS"),("MENTION","QUOTED","POS"))),
)
UNBOUND=(
    "a lantern of silence is looking for the name of its witness",
    "perhaps the parenthesis speaks only to another parenthesis",
    "the story remembered a request without knowing who requested it",
)
# Some syntax is supported in training; other syntax is deliberately new.
FAMILIES=("KNOWN_SHAPES_NEW_SOURCE_EVENTS","OPEN_READING_CRYPTOGRAMMAR")


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def generate(family,*,seed,rounds=4):
    if family not in FAMILIES or type(seed) is not int or type(rounds) is not int or not 1<=rounds<=10:
        raise ValueError("Unsupported labeled synthetic world")
    rng=random.Random(seed)
    cases=[]
    for kind,forms in (("UNIQUE",UNIQUE),("AMBIGUOUS",AMBIGUOUS)):
        for template,readings in forms:
            for _ in range(rounds):
                event={k:rng.choice(v) for k,v in TEST_LEX.items()}
                carrier=rng.choice(corpus.CARRIERS)
                possible=(readings,) if kind=="UNIQUE" else readings
                # In KNOWN_SHAPES_NEW_SOURCE_EVENTS, keep the unknown action
                # lexemes and source event explicit while using common syntax.
                text=template.format(**event)
                if family=="OPEN_READING_CRYPTOGRAMMAR":
                    # New editorial framing, not a transformation of hidden
                    # labels. This changes lexical context for all categories.
                    text=(
                        f"{event['speaker']} writes (a second reading): "+
                        text)
                cases.append({
                    "text":text,
                    "observed_event":event,
                    "carrier":carrier,
                    "reading_count":len(possible),
                    "admissible_graphs":[corpus.frame(*x,carrier,event)
                                         for x in possible],
                    "author_tag":kind,
                })
    for text in UNBOUND:
        for _ in range(rounds):
            event={k:rng.choice(v) for k,v in TEST_LEX.items()}
            carrier=rng.choice(corpus.CARRIERS)
            cases.append({
                "text":text,
                "observed_event":event,
                "carrier":carrier,
                "reading_count":0,
                "admissible_graphs":[],
                "author_tag":"UNBOUND",
            })
    rng.shuffle(cases)
    out={
        "schema":SCHEMA,"family":family,
        "cases":cases,
        "synthetic_semantics_author_proposed_not_proven":True,
        "source_carrier_not_event_authenticity":True,
        "labels_never_used_to_freeze_route":True,
        "contains_private_manuscript_lines":False,
    }
    out["receipt_sha256"]=digest(out)
    return out


def validate(source):
    if (not isinstance(source,dict) or source.get("schema")!=SCHEMA
            or source.get("family") not in FAMILIES
            or not isinstance(source.get("cases"),list)
            or not 1<=len(source["cases"])<=300
            or source.get("synthetic_semantics_author_proposed_not_proven") is not True
            or source.get("labels_never_used_to_freeze_route") is not True
            or source.get("contains_private_manuscript_lines") is not False
            or source.get("receipt_sha256")!=digest({
                k:v for k,v in source.items() if k!="receipt_sha256"})):
        raise ValueError("Tampered or inappropriate author semantic source")
    for c in source["cases"]:
        if (set(c)!={"text","observed_event","carrier","reading_count",
                     "admissible_graphs","author_tag"}
                or type(c["text"]) is not str or not 1<=len(c["text"])<=320
                or c["carrier"] not in corpus.CARRIERS
                or set(c["observed_event"])!=set(corpus.LEX)
                or type(c["reading_count"]) is not int
                or c["reading_count"]!=len(c["admissible_graphs"])
                or c["author_tag"] not in ("UNIQUE","AMBIGUOUS","UNBOUND")
                or (c["author_tag"]=="UNIQUE")!=(c["reading_count"]==1)
                or (c["author_tag"]=="UNBOUND")!=(c["reading_count"]==0)
                or (c["author_tag"]=="AMBIGUOUS")!=(c["reading_count"]>=2)):
            raise ValueError("Invalid set-valued interpretation evidence")
        candidates=set()
        for g in c["admissible_graphs"]:
            m=corpus.graph_map(g)
            expected=corpus.frame(
                m[("ROOT","FORCE")],m[("EVENT","SCOPE")],
                m[("EVENT","POLARITY")],c["carrier"],c["observed_event"])
            if g!=expected:
                raise ValueError("Source carrier or speaker ownership forged")
            candidates.add(digest(g))
        if len(candidates)!=len(c["admissible_graphs"]):
            raise ValueError("Duplicate author readings pretending to be ambiguity")
    return source
