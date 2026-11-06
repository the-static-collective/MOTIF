"""A small, fully inspectable text-to-epistemic-type learner.

Recognizes brief opinion-text cues from a developer-supplied feature grammar.
Learns feature -> court-statement type from eight annotated training fragments.
Does NOT ingest full opinions, discover legal rules or consult review_keys.py.
An unseen feature class abstains rather than creating unsupported law.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from pathlib import Path
import json
import re

CORPUS=Path(__file__).with_name("corpus.py")
CORPUS_GIT_BLOB="7e11857b339ef0093a2438d8ae0018b3718e893b"
REVISION="motif.reason.actual-opinions.quoted-snippets.v1"
SCHEMA="motif.reason.court-quote-classifier.v1"
ALLOWED_LABELS=("LEGAL_TREATMENT","PROCEDURAL_POSTURE",
                "PARTY_ALLEGATION","SEPARATE_OPINION",
                "UNRESOLVED_FACT_ISSUE")
TRAIN_IDS=("S1","S2","L1","L2","N1","N2","P1","P2")
MAX_BYTES=22000

# These cues are supplied by the developer, NOT invented from raw English.
# Features have neutral IDs; type mappings are induced by the labeled sample.
CUES={
 "F_A":(r"\balleges\b",),
 "F_B":(r"\bopinion differs\b",),
 "F_C":(r"\bseek rescission\b",r"\baffirm\b",r"\breversed\b",
        r"\bdenied\b"),
 "F_D":(r"\bestopped\b",r"\bstanding\b",r"\bi hold\b",
        r"\badded.? ingredient\b"),
 "F_E":(r"\bquestion.{0,40}\bfact\b",),
}


class HOLD(ValueError):
    pass


def digest(o):
    return sha256(json.dumps(o,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin_source():
    b=CORPUS.read_bytes()
    sha=sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if sha!=CORPUS_GIT_BLOB:
        raise HOLD("Source-owned historical excerpt corpus changed")
    return sha


def feature(raw):
    if not isinstance(raw,str) or not 3<=len(raw)<=800:
        raise HOLD("Cannot interpret unbounded or missing source text")
    matches=[]
    for code,patterns in CUES.items():
        if any(re.search(p,raw,re.I) for p in patterns):
            matches.append(code)
    return matches


def fit(examples):
    pin_source()
    if (not isinstance(examples,tuple) or len(examples)!=8 or
            tuple(row["span_id"] for row,label in examples)!=TRAIN_IDS):
        raise HOLD("Wrong source-owned learning split or order")
    routes={}
    support={}
    rows=[]
    for row,label in examples:
        if (not isinstance(row,dict)
                or row.get("source_revision")!=REVISION
                or row.get("quote_kind")!="SHORT_VERBATIM_JUDICIAL_OPINION_FRAGMENT"
                or label not in ALLOWED_LABELS):
            raise HOLD("Unrecognized source excerpt or type label")
        cues=feature(row["text"])
        if len(cues)!=1:
            raise HOLD("Teaching fragment needs exactly one identifiable cue")
        code=cues[0]
        if code in routes and routes[code]!=label:
            raise HOLD("Conflicting witness assignments to a lexical feature")
        routes[code]=label
        support.setdefault(code,[]).append(row["span_id"])
        rows.append({"span_id":row["span_id"],"text":row["text"],
                     "feature":code,"label":label})
    if len(routes)<4 or len({label for label in routes.values()})<4:
        raise HOLD("Not enough distinct source-grounded epistemic roles")
    body={
        "schema":SCHEMA,
        "source_corpus_blob":pin_source(),
        "source_revision":REVISION,
        "feature_grammar":{k:list(v) for k,v in sorted(CUES.items())},
        "learned_feature_routes":dict(sorted(routes.items())),
        "training_evidence":rows,
        "features_supported_by":{k:sorted(v) for k,v in sorted(support.items())},
        "method":"FINITE_CUE_CONJUNCTION_ROUTE",
        "heldout_labels_seen_during_fit":False,
        "unlearned_features":"HOLD_NOT_GUESS",
        "scope":"HISTORICAL_QUOTATION_TYPE_ONLY",
        "status":"PROPOSE_FOR_INDEPENDENT_CURATION_REVIEW",
        "external_actions":False,"real_world_authority":False,
    }
    payload=dict(body,checksum_sha256=digest(body))
    raw=json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_BYTES:raise HOLD("Oversized evidence packet")
    return raw


def classify(method,text):
    cues=feature(text)
    if len(cues)!=1 or cues[0] not in method["learned_feature_routes"]:
        return {"status":"HOLD_UNKNOWN_OR_AMBIGUOUS_TYPE",
                "type":None,"observed_cues":cues}
    return {"status":"PROPOSE_TYPE","type":method["learned_feature_routes"][cues[0]],
            "observed_cues":cues}


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>MAX_BYTES:
        raise HOLD("Invalid classifier record")
    try:obj=json.loads(raw)
    except (ValueError,TypeError) as e:raise HOLD("Unparseable classifier") from e
    fields={"schema","source_corpus_blob","source_revision","feature_grammar",
            "learned_feature_routes","training_evidence","features_supported_by",
            "method","heldout_labels_seen_during_fit","unlearned_features",
            "scope","status","external_actions","real_world_authority",
            "checksum_sha256"}
    if not isinstance(obj,dict) or set(obj)!=fields:
        raise HOLD("Unknown type-inference fields")
    if (obj["schema"]!=SCHEMA or obj["source_corpus_blob"]!=pin_source()
            or obj["source_revision"]!=REVISION
            or obj["feature_grammar"]!={k:list(v) for k,v in sorted(CUES.items())}
            or obj["method"]!="FINITE_CUE_CONJUNCTION_ROUTE"
            or obj["heldout_labels_seen_during_fit"] is not False
            or obj["unlearned_features"]!="HOLD_NOT_GUESS"
            or obj["scope"]!="HISTORICAL_QUOTATION_TYPE_ONLY"
            or obj["status"]!="PROPOSE_FOR_INDEPENDENT_CURATION_REVIEW"
            or obj["external_actions"] is not False
            or obj["real_world_authority"] is not False):
        raise HOLD("Source, feature semantics or permissions changed")
    rows=obj["training_evidence"]
    if (not isinstance(rows,list) or len(rows)!=8
            or tuple(r["span_id"] for r in rows)!=TRAIN_IDS
            or not all(isinstance(r,dict) and set(r)=={
                "span_id","text","feature","label"} for r in rows)):
        raise HOLD("Malformed learning example")
    if (obj["checksum_sha256"]!=digest({k:v for k,v in obj.items()
                                       if k!="checksum_sha256"})):
        raise HOLD("Altered classifier checksum")
    # Recompute learned routing from embedded source text + labels.
    # Reviewer separately authenticates training labels and source quotations.
    from corpus import passages
    originals=passages(True)
    if tuple(r["text"] for r in rows)!=tuple(p["text"] for p in originals):
        raise HOLD("Source snippet changed even with a rehashed packet")
    reconstructed=json.loads(fit(tuple(
        (originals[i],rows[i]["label"]) for i in range(8))))
    if reconstructed!=obj:
        raise HOLD("Fabricated cue, output or evidence derivation")
    return obj
