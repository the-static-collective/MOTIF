"""REASON-004: Self-objecting conclusions as bounded, executable disproof plans.

A classical proof remains correct relative to its premises; we annotate it with
what would defeat those premises, which observations distinguish remaining
worlds, and what follows if those observations arrive.

Source-owned integration: original REASON-003 objection.py is checked by Git
blob identity before importing. It is not rewritten or granted authority.
Python 3.10+, standard library, synthetic directed graphs only.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha1, sha256
from heapq import heappush, heappop
from pathlib import Path
from collections import deque
import json
import re
import sys

OWNER_PATH = Path(__file__).resolve().parents[1] / "reason-cartridge-003" / "objection.py"
OWNER_GIT_BLOB = "063e8a0839d41fcadfb5ad1cc3510be63bce725a"
SCHEMA = "motif.reason.self-objecting-cartridge.v1"
REVISION = "reason-004-synthetic-source-v1"
MAX_BYTES = 32000
SAFE = re.compile(r"^[A-Za-z0-9_.:-]{1,96}$")


class HOLD(ValueError):
    pass


def assert_owner_source():
    raw = OWNER_PATH.read_bytes()
    identity = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if identity != OWNER_GIT_BLOB:
        raise HOLD("REASON-003 source changed: re-review before reuse")
    return identity


assert_owner_source()
sys.path.insert(0, str(OWNER_PATH.parent))
from objection import Inquiry, evidence, decide, path, check_certificate  # noqa: E402


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False)


def digest(obj):
    return sha256(canonical(obj).encode("utf-8")).hexdigest()


def encode(q):
    if not isinstance(q, Inquiry):
        raise HOLD("Only original source-owned Inquiry supported")
    return {"nodes": list(q.nodes), "universe": [list(x) for x in q.universe],
            "claims": [list(x) for x in q.claims], "removed": list(q.removed),
            "closed_scope": q.closed_scope, "source": q.source, "target": q.target}


def decode(v):
    if not isinstance(v, dict) or set(v) != {
        "nodes", "universe", "claims", "removed", "closed_scope", "source", "target"
    }:
        raise HOLD("Unknown inquiry structure")
    if (not isinstance(v["nodes"], list) or not isinstance(v["universe"], list)
            or not isinstance(v["claims"], list) or not isinstance(v["removed"], list)
            or any(not isinstance(x, list) for x in v["universe"] + v["claims"])):
        raise HOLD("Invalid structured evidence")
    try:
        return Inquiry(tuple(v["nodes"]), tuple(tuple(x) for x in v["universe"]),
                       tuple(tuple(x) for x in v["claims"]), tuple(v["removed"]),
                       v["closed_scope"], v["source"], v["target"])
    except (TypeError, ValueError) as exc:
        raise HOLD("Source-owned evidence refused") from exc


def _minimal_added_path(q, definite):
    """Least premise changes for a route in the declared finite universe.

    An edge not confirmed present costs 1, including an explicit ABSENT edge.
    This is a counterfactual revision cost, NOT a valid new observation.
    """
    if not q.closed_scope:
        return None
    available = tuple(sorted(e for e in q.universe if e != q.removed))
    adjacency = {n: [] for n in q.nodes}
    for edge in available:
        adjacency[edge[0]].append(edge)
    queue = [(0, 0, (q.source,), q.source)]
    best = {}
    while queue:
        count, hops, walk, node = heappop(queue)
        if node in best and best[node] < (count, hops, walk):
            continue
        if node == q.target:
            additions = [e for e in zip(walk, walk[1:]) if e not in definite]
            return {"path": list(walk), "premises_to_revise": [list(e) for e in additions],
                    "minimum_unconfirmed_edges": count,
                    "status": "HYPOTHETICAL_REVISION_NOT_OBSERVED"}
        for a, b in adjacency[node]:
            candidate = (count + int((a, b) not in definite), hops + 1,
                         walk + (b,), b)
            if b not in best or candidate[:3] < best[b]:
                best[b] = candidate[:3]
                heappush(queue, candidate)
    return None


def _assumptions(q):
    definite, possible, conflicted, unknown = evidence(q)
    return {
        "closed_scope": q.closed_scope,
        "post_removal": list(q.removed),
        "confirmed_edges": [list(e) for e in sorted(definite)],
        "possible_edges": [list(e) for e in sorted(possible)],
        "conflicted_edges": [list(e) for e in sorted(conflicted)],
        "unresolved_edges": [list(e) for e in unknown],
        "witness_count": len(q.claims),
        "source_evidence_hash": digest(encode(q)),
    }


def _falsifier(q, decision):
    definite, possible, conflicted, unknown = evidence(q)
    status = decision["status"]
    if status == "PROVED_REACHABLE":
        frag = decision["fragility"]
        return {
            "kind": "RETRACT_CONFIRMED_MIN_CUT",
            "counterexample_program": [
                {"step": "INDEPENDENTLY_RECHECK_EDGE", "edge": edge,
                 "condition": "A_SOURCE_WITNESS_PROVES_THIS_EDGE_ABSENT"}
                for edge in frag["counterfactual_break_edges"]
            ],
            "minimum_premise_retractions": frag["minimum_confirmed_edge_retractions"],
            "effect_if_all_retractions_are_justified": "CURRENT_PATH_PROOF_INVALIDATED",
            "proof_of_unreachability_after_retraction": False,
        }
    if status == "PROVED_UNREACHABLE":
        alternate = _minimal_added_path(q, definite)
        if alternate is None:
            return {"kind": "REVISE_DECLARED_UNIVERSE",
                    "effect": "REQUIRES_SOURCE_SCOPE_REVISION",
                    "outside_current_contract": True}
        return {"kind": "REOPEN_BLOCKED_ROUTE",
                "counterexample_program": alternate,
                "effect_if_revision_is_verified": "NEW_REACHABILITY_WITNESS_POSSIBLE",
                "requires_source_owned_revision": True}
    if status == "UNKNOWN":
        analysis = decision["omission_analysis"]
        question = analysis.get("recommended_question")
        if question is None:
            return {"kind": "HOLD_UNCERTAIN", "reason": analysis["status"],
                    "no_automatic_probe": True}
        edge = tuple(question["edge"])
        if edge in conflicted:
            return {"kind": "REQUEST_HUMAN_CONFLICT_REVIEW",
                    "edge": list(edge),
                    "do_not_overwrite_witnesses": True}
        return {"kind": "OBSERVE_DISCRIMINATING_EDGE",
                "edge": list(edge), "inquiry_cost_model": analysis,
                "requires_new_source_witness": True}
    if status == "HOLD_OPEN_WORLD":
        return {"kind": "ASK_FOR_SCOPE_CONTRACT",
                "reason": "Unlisted possibilities prevent a sound negative proof",
                "must_not_assume_closed_world": True}
    raise HOLD("Unrecognized objection engine conclusion")


def _future(q, edge, stance):
    """What would follow from an expressly hypothetical *new* observation.

    For a conflicted edge, new votes do NOT adjudicate the contradiction.
    """
    before = set((a, b) for a, b, _, _ in q.claims)
    if edge in before:
        return {"hypothetical_observation": stance,
                "status": "HOLD_EXISTING_WITNESS_REQUIRES_OWNER_REVIEW",
                "source_changed": False}
    simulated = replace(q, claims=q.claims + (
        (edge[0], edge[1], stance, "SIMULATED_UNOBSERVED_FUTURE"),))
    conclusion = decide(simulated)
    return {"hypothetical_observation": stance,
            "status": conclusion["status"], "source_changed": False,
            "new_witness_is_real": False}


def make(q, *, false_negative_cost=5.0, false_positive_cost=4.0,
         question_cost=0.2):
    assert_owner_source()
    costs = {"false_negative": float(false_negative_cost),
             "false_positive": float(false_positive_cost),
             "question": float(question_cost)}
    # Source owner validates non-finite / negative costs, not a made-up
    # probability of a real-world outcome.
    result = decide(q, false_negative_cost=costs["false_negative"],
                    false_positive_cost=costs["false_positive"],
                    question_cost=costs["question"])
    falsifier = _falsifier(q, result)
    futures = None
    if falsifier["kind"] == "OBSERVE_DISCRIMINATING_EDGE":
        edge = tuple(falsifier["edge"])
        futures = {"PRESENT": _future(q, edge, "PRESENT"),
                   "ABSENT": _future(q, edge, "ABSENT")}
    certificate = result.get("certificate")
    if certificate is not None and not check_certificate(q, result):
        raise HOLD("Source owner returned an invalid certificate")
    body = {
        "schema": SCHEMA, "source_revision": REVISION,
        "source_owner_git_blob": OWNER_GIT_BLOB,
        "inquiry": encode(q), "costs": costs,
        "premises": _assumptions(q),
        "conclusion": result["status"],
        "proof_certificate": certificate,
        "refutation_program": falsifier,
        "hypothetical_futures": futures,
        "stage": "PROPOSED_FOR_LOCAL_REVIEW",
        "external_actions_taken": False,
        "real_world_authority": False,
    }
    packet = dict(body, checksum_sha256=digest(body))
    raw = json.dumps(packet, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if len(raw.encode("utf-8")) > MAX_BYTES:
        raise HOLD("Objecting dossier exceeds bounded schema")
    return raw


def validate(raw):
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise HOLD("Invalid or oversized conclusion")
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Malformed conclusion") from exc
    fields = {"schema", "source_revision", "source_owner_git_blob",
              "inquiry", "costs", "premises", "conclusion", "proof_certificate",
              "refutation_program", "hypothetical_futures", "stage",
              "external_actions_taken", "real_world_authority", "checksum_sha256"}
    if not isinstance(obj, dict) or set(obj) != fields:
        raise HOLD("Unknown new conclusion fields")
    if (obj["schema"] != SCHEMA or obj["source_revision"] != REVISION
            or obj["source_owner_git_blob"] != assert_owner_source()
            or obj["stage"] != "PROPOSED_FOR_LOCAL_REVIEW"
            or obj["external_actions_taken"] is not False
            or obj["real_world_authority"] is not False):
        raise HOLD("Unsupported authority or changed source contract")
    if not isinstance(obj["costs"], dict) or set(obj["costs"]) != {
        "false_negative", "false_positive", "question"
    }:
        raise HOLD("Unexpected declared cost contract")
    q = decode(obj["inquiry"])
    regenerated = json.loads(make(
        q, false_negative_cost=obj["costs"]["false_negative"],
        false_positive_cost=obj["costs"]["false_positive"],
        question_cost=obj["costs"]["question"]))
    if obj != regenerated:
        raise HOLD("Conclusion, proof or hypothetical futures cannot be replayed")
    return obj


def observe(q, edge, stance, evidence_ref):
    """Only new independent local evidence. No conflicting-witness overwrite."""
    if (not isinstance(edge, tuple) or len(edge) != 2
            or edge not in q.universe or edge == q.removed
            or stance not in ("PRESENT", "ABSENT")
            or not isinstance(evidence_ref, str) or
            not SAFE.fullmatch(evidence_ref) or
            evidence_ref.startswith("SIMULATED_")):
        raise HOLD("Unknown or synthetic owner observation")
    if any(claim[:2] == edge for claim in q.claims):
        raise HOLD("Evidence already exists: owner reconciliation required")
    new = replace(q, claims=q.claims + ((edge[0], edge[1], stance, evidence_ref),))
    return {"before": digest(encode(q)), "after": digest(encode(new)),
            "prior_conclusion": json.loads(make(q))["conclusion"],
            "new_conclusion": json.loads(make(new))["conclusion"],
            "updated_inquiry": new, "external_observation_performed": False}


class Receiver:
    """An actual independent operator, not a digest, authorizes a local proposal."""
    def __init__(self, raw):
        self.artifact = validate(raw)
        self.admitted = False
        self._review_digest = None
        self._passed = False

    def preview(self, heldout_cases):
        if not isinstance(heldout_cases, tuple) or not heldout_cases:
            raise HOLD("Independent reviewer cases required")
        seen = set()
        statuses = []
        for q, expected in heldout_cases:
            if not isinstance(q, Inquiry) or expected not in (
                    "PROVED_REACHABLE", "PROVED_UNREACHABLE", "UNKNOWN",
                    "HOLD_OPEN_WORLD"):
                raise HOLD("Unrecognized independent review case")
            fingerprint = digest(encode(q))
            if fingerprint in seen or fingerprint == digest(self.artifact["inquiry"]):
                raise HOLD("Duplicated or leaked teaching case")
            seen.add(fingerprint)
            got = json.loads(make(q))["conclusion"]
            statuses.append([fingerprint, expected, got])
        if {status[1] for status in statuses} != {
                "PROVED_REACHABLE", "PROVED_UNREACHABLE", "UNKNOWN",
                "HOLD_OPEN_WORLD"}:
            raise HOLD("Reviewer omitted an epistemic boundary")
        errors = sum(actual != expected for _, expected, actual in statuses)
        self._passed = errors == 0
        self._review_digest = digest({
            "source_packet": self.artifact["checksum_sha256"], "cases": statuses})
        return {"stage": "HOLD_REVIEW", "cases": len(statuses),
                "errors": errors, "review_digest": self._review_digest,
                "owner_admitted": False}

    def admit(self, decision, review_digest):
        if (decision != "ADMIT_READ_ONLY" or not self._passed
                or review_digest != self._review_digest):
            raise HOLD("No locally authorized, independently reviewed proposal")
        self.admitted = True

    def suggest(self):
        if not self.admitted:
            raise HOLD("Unreviewed refutation cartridge")
        return {"stage": "SUGGEST_ONLY",
                "conclusion": self.artifact["conclusion"],
                "refutation_program": self.artifact["refutation_program"],
                "hypothetical_futures": self.artifact["hypothetical_futures"],
                "external_actions_taken": False,
                "real_world_authority": False}
