"""REASON-023: source-witnessed alternative answers to independently authored stories.

A distinct answer with an actual matching line is an *alternative*, not a
logical contradiction. Do NOT manufacture negative evidence from absence,
and do NOT silently choose "latest" simply because it is easy.

This import executes the ORIGINAL Git-blob-pinned REASON-022 transfer grammar
and its single-answer baseline; the new program searches ALL source events.
Official dataset answers and support annotations never enter this module.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha1,sha256
from pathlib import Path
import json
import re
import sys

HERE=Path(__file__).resolve().parent
P022=HERE.parent/"reason-cartridge-022"
ORIGINAL_BLOB="42fb89d7050bfcce9c161d89c86922fbe24c1bac"
sys.path.append(str(P022))
import engines as original_engines

SCHEMA="motif.reason023.source-graph.v1"
MAX_FACTS=120
MAX_CANDIDATES=16
MAX_PACKET=120000


class HOLD(ValueError):
    pass


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,
                             separators=(",",":"),allow_nan=False).encode()).hexdigest()


def pin():
    data=(P022/"engines.py").read_bytes()
    actual=sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()
    if actual!=ORIGINAL_BLOB:
        raise HOLD("Original 022 reasoner not at audited Git blob")
    return actual


# The shape grammar is intentionally constrained to five supported bAbI
# transfer queries; no generic English or human meaning is being inferred.
SHAPES=(
    (re.compile(r"^What did ([A-Z][a-z]+) give to ([A-Z][a-z]+)\?$"),
     lambda g,e:e[1] if (e[0],e[2])==(g[0],g[1]) else None),
    (re.compile(r"^Who gave the ([a-z]+) to ([A-Z][a-z]+)\?$"),
     lambda g,e:e[0] if (e[1],e[2])==(g[0],g[1]) else None),
    (re.compile(r"^Who gave the ([a-z]+)\?$"),
     lambda g,e:e[0] if e[1]==g[0] else None),
    (re.compile(r"^Who did ([A-Z][a-z]+) give the ([a-z]+) to\?$"),
     lambda g,e:e[2] if (e[0],e[1])==(g[0],g[1]) else None),
    (re.compile(r"^Who received the ([a-z]+)\?$"),
     lambda g,e:e[2] if e[1]==g[0] else None),
)


def interpret_query(question):
    if not isinstance(question,str) or len(question)>180:
        return None
    for i,(expression,extractor) in enumerate(SHAPES):
        m=expression.fullmatch(question)
        if m:return i,m.groups(),extractor
    return None


def compile_graph(source):
    pin()
    if (not isinstance(source,dict) or set(source)!={"facts","question","source_id"}
            or not isinstance(source["source_id"],str)
            or len(source["source_id"])>130
            or not isinstance(source["facts"],list)
            or not 1<=len(source["facts"])<=MAX_FACTS):
        raise HOLD("Unbounded source or unknown graph contract")
    ids=set();events=[]
    for item in source["facts"]:
        if (not isinstance(item,dict) or set(item)!={"line","text"}
                or type(item["line"]) is not int or item["line"]<1
                or not isinstance(item["text"],str) or len(item["text"])>320
                or item["line"] in ids):
            raise HOLD("Duplicate, fabricated or malformed evidence line")
        ids.add(item["line"])
        statement=original_engines.GIVE.fullmatch(item["text"])
        if statement:
            giver,thing,receiver=statement.groups()
            events.append({
                "edge_id":source["source_id"]+":L"+str(item["line"]),
                "kind":"GAVE",
                "giver":giver,"object":thing,"receiver":receiver,
                "original_line":item["line"],"original_text":item["text"],
                "source_owned":True,
            })
    shape=interpret_query(source["question"])
    if shape is None:
        return {
            "schema":SCHEMA,"source_id":source["source_id"],
            "question":source["question"],"status":"HOLD",
            "reason":"UNKNOWN_QUERY_GRAMMAR",
            "events":events,"candidates":[],"proof_edges":[],
            "selected_answer":None,
            "assumptions_considered":[],
            "source_sha256":digest(source),"original_022_blob":ORIGINAL_BLOB,
            "multiple_source_support_not_logical_contradiction":True,
            "no_gold_labels_used":True,"permission_to_execute":False,
        }
    shape_id,args,matcher=shape
    witnesses=defaultdict(list)
    for edge in events:
        answer=matcher(args,(edge["giver"],edge["object"],edge["receiver"]))
        if answer is not None:
            witnesses[answer].append(edge)
    if len(witnesses)>MAX_CANDIDATES:
        raise HOLD("Too many competing source interpretations")
    candidates=[]
    for answer in sorted(witnesses):
        witnesses_for_answer=sorted(witnesses[answer],key=lambda x:x["original_line"])
        candidates.append({
            "answer":answer,
            "support":[x["edge_id"] for x in witnesses_for_answer],
            "source_lines":[x["original_line"] for x in witnesses_for_answer],
            "assumption":"LITERAL_QUERY_MATCHES_SOURCE_TRANSFER",
            "explicit_refutation":[],"confidence_not_calibrated":True,
        })
    if len(candidates)==0:
        state="HOLD";reason="NO_SOURCE_GROUNDED_TRANSFER"
    elif len(candidates)==1:
        state="ANSWER";reason=None
    else:
        state="HOLD";reason="NON_UNIQUE_SOURCE_SUPPORTED_ANSWERS"
    ordered=sorted(
        (x for x in events if any(x["edge_id"] in c["support"] for c in candidates)),
        key=lambda x:x["original_line"])
    alternatives=[]
    if len(candidates)>1:
        first=ordered[0];last=ordered[-1]
        alternatives=[
            {"rule":"EARLIEST_EVENT","answer":next(
                c["answer"] for c in candidates if first["edge_id"] in c["support"]),
             "premise":first["edge_id"],"unverified_relevance_assumption":True},
            {"rule":"LATEST_EVENT","answer":next(
                c["answer"] for c in candidates if last["edge_id"] in c["support"]),
             "premise":last["edge_id"],"unverified_relevance_assumption":True},
        ]
    graph={
        "schema":SCHEMA,"source_id":source["source_id"],
        "question":source["question"],"query_shape":shape_id,
        "status":state,"reason":reason,
        "events":events,"candidates":candidates,"proof_edges":ordered,
        "selected_answer":candidates[0]["answer"] if state=="ANSWER" else None,
        "assumptions_considered":alternatives,
        "source_sha256":digest(source),"original_022_blob":ORIGINAL_BLOB,
        "multiple_source_support_not_logical_contradiction":True,
        "no_gold_labels_used":True,"permission_to_execute":False,
    }
    if len(json.dumps(graph))>MAX_PACKET:raise HOLD("Unbounded evidence graph")
    return graph


def verify_graph(source,reported):
    if not isinstance(reported,dict) or compile_graph(source)!=reported:
        raise HOLD("Source graph not independently reproducible")
    byid={source["source_id"]+":L"+str(x["line"]):x for x in source["facts"]}
    for edge in reported["proof_edges"]:
        actual=byid.get(edge["edge_id"])
        if not actual or (actual["text"],actual["line"])!=(
                edge["original_text"],edge["original_line"]):
            raise HOLD("Source proof references a fabricated event")
    return True


def original_022(source):
    pin()
    return original_engines.solve("TRIADIC_TRANSFER",source)
