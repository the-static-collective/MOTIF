"""RING-011. Authored semantic-graph contrasts with source carrier provenance.

Inspired by editorial *structure* observed in the private Google Drive
'How to Live' print cut: song vs contemporaneous note vs memory vs record,
nested parentheses, an aside commenting on an aside, quoted speakers,
apparent directives embedded inside imagined/quoted speech, and uncertainty
about chronology. No private prose, names, allegations, personal details,
raw text, or extracted quotations are put in this public code.

The learning program receives only serialized source examples and typed
semantic graph targets. It does NOT get the authored templates or rule IDs.
Source event (speaker/agent/verb/patient) and document-carrier classification
are explicitly supplied metadata, not entities discovered from open English.
"""
from __future__ import annotations
from hashlib import sha256
import json
import random

SCHEMA="motif.ring011.carrier-scope-contrasts.v1"
SEMANTIC_SCHEMA="motif.ring011.nested-event-graph.v1"
RELATIONS=("ROOT_FORCE","EVENT_SCOPE","EVENT_POLARITY")
VALUES={
    "ROOT_FORCE":("DIRECTIVE","ASSERTION","MENTION"),
    "EVENT_SCOPE":("ROOT","QUOTED","IMAGINED","CONDITIONAL"),
    "EVENT_POLARITY":("POS","NEG"),
}
CARRIERS=("SONG","NOTE","MEMORY","RECORD")
# These are source categories, not a truth hierarchy. None, even 'RECORD',
# authenticates an event without further independent evidence.
EPISTEMIC={
    "SONG":"CREATIVE_CARRIER_NOT_EVENT_EVIDENCE",
    "NOTE":"NOTE_CARRIER_NOT_CORROBORATION",
    "MEMORY":"RECOLLECTION_NOT_CONTEMPORANEOUS_RECORD",
    "RECORD":"RECORD_CARRIER_AUTHENTICITY_UNVERIFIED",
}
LEX={
    "speaker":("mina","ravi","tesh","vera","ilo"),
    "agent":("noa","sey","kam","liz","aru"),
    "verb":("carry","mark","fold","deliver","repair"),
    "patient":("map","lamp","packet","scroll","jar"),
}
# (text, force, event-scope, event polarity)
# Match source event across both arms of each contrast.
# A root directive to *quote* is not necessarily a root request that
# the event inside the quote be executed.
TRAIN={
    "quote":(
        ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} quotes [{agent} saying please {verb} {patient}]","MENTION","QUOTED","POS"),
        ("{speaker} asks {agent} to quote [{agent} saying please {verb} {patient}]","DIRECTIVE","QUOTED","POS"),
    ),
    "imagine":(
        ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} imagines [{agent} asking to {verb} {patient}]","MENTION","IMAGINED","POS"),
        ("{speaker} says what if [{agent} were to {verb} {patient}]","MENTION","IMAGINED","POS"),
    ),
    "negate":(
        ("{speaker} says {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
        ("{speaker} says {agent} did not {verb} {patient}","ASSERTION","ROOT","NEG"),
        ("{speaker} asks {agent} not to {verb} {patient}","DIRECTIVE","ROOT","NEG"),
    ),
    "conditional":(
        ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} asks {agent} to {verb} {patient} if the bell rings","DIRECTIVE","CONDITIONAL","POS"),
        ("{speaker} wonders if [{agent} might {verb} {patient}]","MENTION","IMAGINED","POS"),
    ),
    "quote_negative":(
        ("{speaker} quotes [{agent} saying please {verb} {patient}]","MENTION","QUOTED","POS"),
        ("{speaker} quotes [{agent} saying please do not {verb} {patient}]","MENTION","QUOTED","NEG"),
        ("{speaker} asks {agent} to quote [{agent} saying please do not {verb} {patient}]","DIRECTIVE","QUOTED","NEG"),
    ),
    "asides":(
        ("{speaker} says {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
        ("{speaker} says ({agent} did {verb} {patient})","ASSERTION","ROOT","POS"),
        ("{speaker} wonders ([{agent} might {verb} {patient}])","MENTION","IMAGINED","POS"),
    ),
}
DEV={
    "quote":(
        ("{speaker} quietly asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} quotes [{agent} saying please kindly {verb} {patient}]","MENTION","QUOTED","POS"),
        ("{speaker} urgently asks {agent} to quote [{agent} saying please {verb} {patient}]","DIRECTIVE","QUOTED","POS"),
    ),
    "imagine":(
        ("{speaker} urgently asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} imagines [{agent} asking to quietly {verb} {patient}]","MENTION","IMAGINED","POS"),
        ("{speaker} says what if [{agent} were to quietly {verb} {patient}]","MENTION","IMAGINED","POS"),
    ),
    "negate":(
        ("{speaker} says {agent} indeed did {verb} {patient}","ASSERTION","ROOT","POS"),
        ("{speaker} says {agent} did not actually {verb} {patient}","ASSERTION","ROOT","NEG"),
        ("{speaker} asks {agent} not to urgently {verb} {patient}","DIRECTIVE","ROOT","NEG"),
    ),
    "conditional":(
        ("{speaker} quietly asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} asks {agent} to {verb} {patient} if the bell softly rings","DIRECTIVE","CONDITIONAL","POS"),
        ("{speaker} wonders if [{agent} might quietly {verb} {patient}]","MENTION","IMAGINED","POS"),
    ),
    "quote_negative":(
        ("{speaker} quotes [{agent} saying please kindly {verb} {patient}]","MENTION","QUOTED","POS"),
        ("{speaker} quotes [{agent} saying please do not quietly {verb} {patient}]","MENTION","QUOTED","NEG"),
        ("{speaker} urgently asks {agent} to quote [{agent} saying please do not {verb} {patient}]","DIRECTIVE","QUOTED","NEG"),
    ),
    "asides":(
        ("{speaker} says {agent} did recently {verb} {patient}","ASSERTION","ROOT","POS"),
        ("{speaker} says ({agent} indeed did {verb} {patient})","ASSERTION","ROOT","POS"),
        ("{speaker} wonders ([{agent} might quietly {verb} {patient}])","MENTION","IMAGINED","POS"),
    ),
}


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def frame(force,scope,polarity,carrier,event):
    if (force not in VALUES["ROOT_FORCE"]
            or scope not in VALUES["EVENT_SCOPE"]
            or polarity not in VALUES["EVENT_POLARITY"]
            or carrier not in CARRIERS):
        raise ValueError("Invalid source graph")
    return {
        "schema":SEMANTIC_SCHEMA,
        "edges":[["ROOT","FORCE",force],
                 ["EVENT","SCOPE",scope],
                 ["EVENT","POLARITY",polarity],
                 ["EVENT","REQUESTED_BY_ROOT",
                  force=="DIRECTIVE" and scope=="ROOT" and polarity=="POS"],
                 ["EVENT","VOICE_OWNER",
                  event["speaker"] if scope=="ROOT" else event["agent"]],
                 ["DOCUMENT","CARRIER",carrier],
                 ["DOCUMENT","EVIDENCE_STATUS",EPISTEMIC[carrier]]],
    }


def graph_map(g):
    if not isinstance(g,dict) or g.get("schema")!=SEMANTIC_SCHEMA:
        raise ValueError("Wrong graph type")
    m={}
    for a,b,c in g["edges"]:
        if (a,b) in m:
            raise ValueError("Duplicated source graph relation")
        m[(a,b)]=c
    if set(m)!={("ROOT","FORCE"),("EVENT","SCOPE"),("EVENT","POLARITY"),
                ("EVENT","REQUESTED_BY_ROOT"),("EVENT","VOICE_OWNER"),
                ("DOCUMENT","CARRIER"),("DOCUMENT","EVIDENCE_STATUS")}:
        raise ValueError("Incomplete event graph")
    return m


def generate(split,*,seed=2026111101,rounds=5):
    forms={"train":TRAIN,"dev":DEV}.get(split)
    if forms is None or type(seed) is not int or type(rounds) is not int or not 1<=rounds<=10:
        raise ValueError("Invalid training source")
    rng=random.Random(seed)
    rows=[]
    for family,variants in sorted(forms.items()):
        for _ in range(rounds):
            observed={k:rng.choice(v) for k,v in LEX.items()}
            carrier=rng.choice(CARRIERS)
            alternatives=[]
            for pattern,force,scope,polarity in variants:
                alternatives.append({
                    "text":pattern.format(**observed),
                    "observed_event":observed,
                    "carrier":carrier,
                    "semantic_graph":frame(force,scope,polarity,carrier,observed),
                })
            # Three alternatives share an identical event and source carrier.
            rows.append({"a":alternatives[0],"b":alternatives[1],"c":alternatives[2]})
    rng.shuffle(rows)
    r={
        "schema":SCHEMA,"split":split,"contrasts":rows,
        "all_source_carriers_explicitly_supplied":True,
        "all_event_variables_explicitly_supplied":True,
        "developer_authored_semantic_graph_labels":True,
        "private_work_only_used_as_abstract_stress_inspiration":True,
    }
    r["receipt_sha256"]=digest(r)
    return r


def validate(packet,*,split=None):
    if (not isinstance(packet,dict) or packet.get("schema")!=SCHEMA
            or packet.get("split") not in ("train","dev","novel")
            or split is not None and packet.get("split")!=split
            or not isinstance(packet.get("contrasts"),list)
            or not 1<=len(packet["contrasts"])<=100
            or packet.get("all_source_carriers_explicitly_supplied") is not True
            or packet.get("all_event_variables_explicitly_supplied") is not True
            or packet.get("developer_authored_semantic_graph_labels") is not True
            or packet.get("receipt_sha256")!=digest({
                k:v for k,v in packet.items() if k!="receipt_sha256"})):
        raise ValueError("Malformed or modified semantic source")
    for contrast in packet["contrasts"]:
        if set(contrast)!={"a","b","c"}:
            raise ValueError("Contrasts must provide three event-stable views")
        values=list(contrast.values())
        first=values[0]
        for x in values:
            if (set(x)!={"text","observed_event","carrier","semantic_graph"}
                    or type(x["text"]) is not str or not 1<=len(x["text"])<=320
                    or x["carrier"] not in CARRIERS
                    or set(x["observed_event"])!=set(LEX)
                    or any(type(y) is not str or not y.isalpha()
                           for y in x["observed_event"].values())
                    or x["observed_event"]!=first["observed_event"]
                    or x["carrier"]!=first["carrier"]):
                raise ValueError("Unbound source event or provenance")
            m=graph_map(x["semantic_graph"])
            if (m[("DOCUMENT","CARRIER")]!=x["carrier"]
                    or m[("DOCUMENT","EVIDENCE_STATUS")]!=EPISTEMIC[x["carrier"]]
                    or m[("ROOT","FORCE")] not in VALUES["ROOT_FORCE"]
                    or m[("EVENT","SCOPE")] not in VALUES["EVENT_SCOPE"]
                    or m[("EVENT","POLARITY")] not in VALUES["EVENT_POLARITY"]):
                raise ValueError("Label inconsistency")
            expected=frame(m[("ROOT","FORCE")],m[("EVENT","SCOPE")],
                           m[("EVENT","POLARITY")],x["carrier"],x["observed_event"])
            if expected!=x["semantic_graph"]:
                raise ValueError("Incoherent graph authority or owner claims")
        if len({digest(x["semantic_graph"]) for x in values})<2:
            raise ValueError("No actual semantic contrast")
    return packet


def flatten(packet):
    validate(packet)
    return [v for row in packet["contrasts"] for v in row.values()]
