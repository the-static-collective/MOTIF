"""REASON-008: a bounded missing-grammar detector and typed macro synthesizer.

The learner does NOT import the independent source's BFS evaluator. It sees
five public source observations and only an allowlisted Boolean grammar.
It first exhausts the strongest legacy 2+2 flat grammar on *five* inputs,
then tests one minimal typed grammar expansion: 3-AND OR 2-AND.

This is invention of a missing *macro in the restricted DSL*, not a new
fundamental Boolean primitive or general unrestricted code generation.
"""
from __future__ import annotations

from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path
import json

SOURCE_PATH = Path(__file__).with_name("source.py")
SOURCE_GIT_BLOB = "b723dea02e2ec0e030a9f01d2e1416ac1af8fe6f"
SOURCE_REVISION = "motif.reason.eight.five-edge-source.v1"
OBS_SCHEMA = "motif.reason.eight.public-source-observation.v1"
SCHEMA = "motif.reason.missing-primitive.v1"
MAX_BYTES = 32000

PAIRS = tuple(combinations(range(5), 2))
TRIPLES = tuple(combinations(range(5), 3))
LEGACY = tuple(combinations(PAIRS, 2))
EXPANDED = tuple((three, two) for three in TRIPLES for two in PAIRS)
TRAIN_MASKS = (3, 5, 6, 7, 24)


class HOLD(ValueError):
    pass


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def pin():
    raw = SOURCE_PATH.read_bytes()
    actual = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if actual != SOURCE_GIT_BLOB:
        raise HOLD("Source-owner implementation changed; reapprove semantics")
    return actual


def bits(mask):
    if type(mask) is not int or not 0 <= mask < 32:
        raise HOLD("Missing five-bit graph feature vector")
    return tuple(bool(mask & (1 << k)) for k in range(5))


def old_eval(program, mask):
    if program not in LEGACY:
        raise HOLD("Legacy program outside prior 2+2 grammar")
    x = bits(mask)
    return any(x[a] and x[b] for a,b in program)


def expanded_eval(program, mask):
    if program not in EXPANDED:
        raise HOLD("Unsupported typed three-hop extension")
    x = bits(mask)
    triple, pair = program
    return all(x[k] for k in triple) or all(x[k] for k in pair)


def lessons(observations):
    pin()
    if not isinstance(observations, (tuple, list)) or len(observations) != 5:
        raise HOLD("Insufficient source-owner public lessons")
    if any(not isinstance(o, dict) or set(o) != {
        "schema", "mask", "features", "reachable", "source_revision",
        "source_type", "real_world_authority",
    } for o in observations):
        raise HOLD("Source lessons malformed")
    ordered = sorted(observations, key=lambda o:o["mask"])
    if tuple(o["mask"] for o in ordered) != TRAIN_MASKS:
        raise HOLD("Teaching/holdout split or witness coverage changed")
    for row in ordered:
        if (row["schema"] != OBS_SCHEMA
                or row["source_revision"] != SOURCE_REVISION
                or row["source_type"] != "SYNTHETIC_BFS_NOT_REAL_WORLD_EVIDENCE"
                or row["real_world_authority"] is not False
                or type(row["reachable"]) is not bool
                or row["features"] != [int(bit) for bit in bits(row["mask"])]):
            raise HOLD("Changed or reinterpreted source observation")
    return ordered


def detect_gap(rows):
    """Every old candidate gets one concrete counterexample from 5 lessons."""
    training = lessons(rows)
    witnesses = []
    for program in LEGACY:
        failing = next((row for row in training
                        if old_eval(program,row["mask"]) != row["reachable"]),None)
        if failing is not None:
            witnesses.append({
                "old_program": [list(pair) for pair in program],
                "counterexample_mask": failing["mask"],
                "source_reachable": failing["reachable"],
                "old_prediction": old_eval(program,failing["mask"]),
            })
    return {
        "old_grammar": "OR(AND2,AND2)_FIVE_INPUTS",
        "old_candidate_count": len(LEGACY),
        "old_candidates_refuted": len(witnesses),
        "all_old_candidates_refuted": len(witnesses) == len(LEGACY),
        "refutations": witnesses,
        "classical_proof_scope": "EXHAUSTIVE_FOR_DECLARED_FINITE_DSL_ONLY",
    }


def synthesize(rows):
    teaching = lessons(rows)
    gap = detect_gap(teaching)
    if not gap["all_old_candidates_refuted"]:
        raise HOLD("Old grammar already explains lessons; no justified extension")
    survivors = [program for program in EXPANDED if all(
        expanded_eval(program,row["mask"]) == row["reachable"] for row in teaching)]
    if len(survivors) != 1:
        raise HOLD("New grammar method ambiguous or insufficient")
    chosen = survivors[0]
    body = {
        "schema": SCHEMA,
        "source_revision": SOURCE_REVISION,
        "source_owner_git_blob": pin(),
        "training_evidence": teaching,
        "training_evidence_digest": digest(teaching),
        "old_language_refutation": gap,
        "proposed_extension": {
            "name": "AND3_OR_AND2_MACRO",
            "arity": 5,
            "program": {"triple":list(chosen[0]),"pair":list(chosen[1])},
            "expanded_candidate_count": len(EXPANDED),
            "programs_consistent_with_lessons": 1,
            "adds_new_fundamental_boolean_primitive": False,
            "source_of_primitives": "STANDARD_FINITE_CONJUNCTION_DISJUNCTION",
        },
        "status":"PROPOSE_ONLY",
        "scope":"FIVE_EDGE_GRAPH_SYNTHETIC_READ_ONLY",
        "external_execution":False,
        "real_world_authority":False,
    }
    packet = dict(body,checksum_sha256=digest(body))
    raw = json.dumps(packet, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if len(raw.encode("utf-8")) > MAX_BYTES:
        raise HOLD("Over-sized primitive proposal")
    return raw


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise HOLD("Missing or oversized primitive packet")
    try:
        packet = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Malformed primitive packet") from exc
    fields = {
        "schema","source_revision","source_owner_git_blob","training_evidence",
        "training_evidence_digest","old_language_refutation",
        "proposed_extension","status","scope","external_execution",
        "real_world_authority","checksum_sha256",
    }
    if not isinstance(packet,dict) or set(packet) != fields:
        raise HOLD("Unknown method or authority fields")
    if (packet["schema"] != SCHEMA
            or packet["source_revision"] != SOURCE_REVISION
            or packet["source_owner_git_blob"] != pin()
            or packet["status"] != "PROPOSE_ONLY"
            or packet["scope"] != "FIVE_EDGE_GRAPH_SYNTHETIC_READ_ONLY"
            or packet["external_execution"] is not False
            or packet["real_world_authority"] is not False):
        raise HOLD("Method source, scope, or privileges changed")
    try:
        regenerated = json.loads(synthesize(packet["training_evidence"]))
    except (ValueError,KeyError,TypeError) as exc:
        raise HOLD("Method could not be reconstructed from training") from exc
    if packet != regenerated or packet["checksum_sha256"] != digest({
            key: value for key,value in packet.items() if key != "checksum_sha256"}):
        raise HOLD("Method, proof of gap, or evidence altered even with a new hash")
    return packet


def suggest(raw,mask):
    packet=validate(raw)
    method=packet["proposed_extension"]["program"]
    program=(tuple(method["triple"]),tuple(method["pair"]))
    return {"prediction":expanded_eval(program,mask),
            "stage":"SUGGEST_ONLY",
            "external_execution":False,"real_world_authority":False}
