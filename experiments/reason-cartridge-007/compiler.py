"""REASON-007: a strictly bounded capability inventor using Boolean primitives.

The learner NEVER imports source.py or consults withheld answers. The only
language is (x[a] AND x[b]) OR (x[c] AND x[d]), four witnessed binary inputs.
It composes known primitives, not novel general-purpose executable code.
"""
from __future__ import annotations

from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path
import json
import re

SOURCE = Path(__file__).with_name("source.py")
SOURCE_BLOB = "00f73d1f6dc73f1c0706179a81113e18ba1800c9"
REVISION = "reason-007-four-edge-graph-source-v1"
SCHEMA = "motif.reason.discovery-sensor.v1"
MAX_BYTES = 24000
PAIRS = tuple(combinations(range(4), 2))
PROGRAMS = tuple(combinations(PAIRS, 2))  # 15 source-owned candidate circuits
MASKS = (0, 3, 5, 10, 12)


class HOLD(ValueError):
    pass


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def pin_source():
    raw = SOURCE.read_bytes()
    actual = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if actual != SOURCE_BLOB:
        raise HOLD("Source owner changed: no silent promotion")
    return actual


def circuit(features, program):
    if (not isinstance(features, (tuple, list)) or len(features) != 4
            or any(type(b) not in (bool, int) or b not in (0, 1)
                   for b in features)
            or program not in PROGRAMS):
        raise HOLD("Unsupported read-only circuit or feature language")
    return any(bool(features[a]) and bool(features[b]) for a,b in program)


def classify(program, mask):
    if type(mask) is not int or not 0 <= mask < 16:
        raise HOLD("Unsupported synthetic feature vector")
    return circuit(tuple(int(bool(mask & (1 << i))) for i in range(4)), program)


def _lessons(rows):
    pin_source()
    if (not isinstance(rows, (tuple, list)) or len(rows) != 5
            or any(not isinstance(x, dict) or
                   set(x) != {"mask","reachable","source_revision","kind","real_world_authority"}
                   for x in rows)):
        raise HOLD("Missing or unrecognized source teaching receipts")
    ordered = sorted(rows, key=lambda x:x["mask"])
    if [x["mask"] for x in ordered] != list(MASKS):
        raise HOLD("Teacher episode coverage changed")
    for x in ordered:
        if (type(x["reachable"]) is not bool or
                x["source_revision"] != REVISION or
                x["kind"] != "SYNTHETIC_CLASSICAL_GRAPH_RESULT" or
                x["real_world_authority"] is not False):
            raise HOLD("Untrusted or over-authorized teacher label")
    return ordered


def infer(rows):
    lessons = _lessons(rows)
    survivors = tuple(program for program in PROGRAMS if all(
        classify(program, row["mask"]) == row["reachable"]
        for row in lessons))
    if len(survivors) != 1:
        raise HOLD("Teacher labels do not identify a unique bounded method")
    return survivors[0]


def propose(rows):
    episodes = _lessons(rows)
    method = infer(episodes)
    body = {
        "schema": SCHEMA, "source_owner_blob": pin_source(),
        "source_revision": REVISION,
        "learner": "ENUMERATE_TWO_ANDS_IN_ONE_OR",
        "program": [list(pair) for pair in method],
        "candidate_count": len(PROGRAMS),
        "training_receipts": episodes,
        "training_digest": digest(episodes),
        "status": "PROPOSE_ONLY",
        "scope": "FOUR_BOOLEAN_EDGE_FEATURES_SYNTHETIC_ONLY",
        "external_execution": False,
        "real_world_authority": False,
    }
    packet = dict(body, checksum_sha256=digest(body))
    out = json.dumps(packet, sort_keys=True, indent=2) + "\n"
    if len(out.encode()) > MAX_BYTES:
        raise HOLD("Bounded circuit transfer exceeded contract")
    return out


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>MAX_BYTES:
        raise HOLD("Missing or oversized method cartridge")
    try:
        obj=json.loads(raw)
    except (ValueError,TypeError) as exc:
        raise HOLD("Malformed method cartridge") from exc
    fields={"schema","source_owner_blob","source_revision","learner",
            "program","candidate_count","training_receipts","training_digest",
            "status","scope","external_execution","real_world_authority",
            "checksum_sha256"}
    if not isinstance(obj,dict) or set(obj)!=fields:
        raise HOLD("Unknown method instructions")
    if (obj["schema"]!=SCHEMA or obj["source_owner_blob"]!=pin_source()
            or obj["source_revision"]!=REVISION
            or obj["learner"]!="ENUMERATE_TWO_ANDS_IN_ONE_OR"
            or obj["status"]!="PROPOSE_ONLY"
            or obj["scope"]!="FOUR_BOOLEAN_EDGE_FEATURES_SYNTHETIC_ONLY"
            or obj["external_execution"] is not False
            or obj["real_world_authority"] is not False
            or type(obj["candidate_count"]) is not int
            or obj["candidate_count"]!=len(PROGRAMS)):
        raise HOLD("Authority, source or capability boundary changed")
    if (obj["training_digest"]!=digest(obj["training_receipts"])
            or obj["checksum_sha256"]!=digest({k:v for k,v in obj.items()
                                              if k!="checksum_sha256"})):
        raise HOLD("Changed evidence or artifact integrity")
    # A rebuilt artifact must agree byte-for-byte in parsed content, not just SHA.
    try:
        regenerated=json.loads(propose(obj["training_receipts"]))
    except (ValueError,TypeError,KeyError) as exc:
        raise HOLD("Unreplayable teacher episode") from exc
    if obj!=regenerated:
        raise HOLD("Rehashed or fabricated program not derived from teacher")
    program=tuple(tuple(x) for x in obj["program"])
    if program not in PROGRAMS:
        raise HOLD("Unrecognized circuit")
    return obj


def run_read_only(packet, mask):
    obj=validate(json.dumps(packet)) if isinstance(packet,dict) else validate(packet)
    program=tuple(tuple(pair) for pair in obj["program"])
    return {"status":"SUGGEST_ONLY", "prediction":classify(program,mask),
            "external_execution":False,"real_world_authority":False}
